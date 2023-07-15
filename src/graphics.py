# src/graphics.py

from create_bot import bot
from db_models import Player, Guild
from settings import async_session_maker
from plotly import graph_objs as go
from plotly import io as pio
import io

from dateutil.relativedelta import relativedelta
from sqlalchemy import select, or_

from src.utils import get_new_day_start
from aiogram import types


async def get_player_gp_graphic(player_name, period):
    """Создает график галактической мощи игрока по месяцу или году"""
    new_day_start = get_new_day_start()
    if period == "month":
        one_month_ago = new_day_start - relativedelta(months=1)  # Вычислить дату один месяц назад
        async with async_session_maker() as session:
            player_data = await session.execute(
                select(Player).filter_by(name=player_name).filter(
                    Player.update_time >= one_month_ago))  # Использовать эту дату в фильтре
            player_data = player_data.scalars().all()
    else:
        one_year_ago = new_day_start - relativedelta(months=12)
        async with async_session_maker() as session:
            # Получаем все данные для игрока
            stmt = select(Player).filter(Player.name == player_name, Player.update_time >= one_year_ago)

            all_data = await session.execute(stmt)
            all_data = all_data.scalars().all()

            # Сортируем данные по дате обновления
            all_data.sort(key=lambda x: x.update_time)

            # Берем первую запись для каждого месяца
            player_data = []
            current_month = None
            for record in all_data:
                if record.update_time.month != current_month:
                    player_data.append(record)
                    current_month = record.update_time.month


    # Создаем график с использованием plotly
    x_values = [player.update_time.strftime("%d-%m-%Y") for player in player_data]
    y_values = [player.galactic_power for player in player_data]
    # Сначала объединяем списки в список кортежей
    data = list(zip(x_values, y_values))

    # Сортируем список кортежей по дате
    data.sort(key=lambda x: x[0])
    if period == "month":
        data.pop()

    # Разделяем отсортированный список кортежей обратно на два списка
    x_values, y_values = zip(*data)



    fig = go.Figure(data=go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        textposition='top center',
    ))

    fig.update_layout(
        title=f'<b>{player_name}\'s</b> galactic power per <b>{period}</b>',
        xaxis_title='Update Time',
        yaxis_title='Galactic Power',
    )

    # Вычисляем разницу между самым поздним и самым ранним значением
    difference_gp = y_values[-1] - y_values[0]

    # Добавляем аннотацию с этой разницей
    fig.add_annotation(
        xref='paper', x=1, yref='paper', y=0,
        text=f"Total difference: {difference_gp:,}",
        showarrow=False,
        font=dict(
            size=14,
            color="#ffffff"
        ),
        align="right",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8
    )

    fig.add_annotation(
        xref='paper', x=0, yref='paper', y=1,
        text=f"Last value: {y_values[-1]:,}",
        showarrow=False,
        font=dict(
            size=14,
            color="#ffffff"
        ),
        align="right",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#666bff",
        opacity=0.8
    )

    buf = io.BytesIO()
    pio.write_image(fig, buf, format='png')
    buf.seek(0)

    return buf


async def get_month_player_graphic(message: types.Message, player_name: str) -> io.BytesIO or None:
    """Создает график рейдов игрока"""
    # Извлечение данных из базы данных
    async with async_session_maker() as session:
        query = await session.execute(
            select(Player).filter(or_(Player.name == player_name, Player.tg_nic == player_name))
        )
        player_data = query.scalars().all()

    # Проверка, есть ли данные
    if not player_data:
        await bot.send_message(message.chat.id,
                               text=f"Неверно введено имя \"{player_name}\". Попробуйте проверить правильность написания")
        return

    # Подготовка данных для построения графика
    data = sorted([(player.update_time, int(player.reid_points)) for player in player_data])
    update_times, reid_points = zip(*data)

    # Построение графика
    fig = go.Figure(data=go.Scatter(
        x=update_times,
        y=reid_points,
        mode='lines+markers+text',
        text=reid_points,
        textposition='top center'))

    fig.update_layout(
        title=f'<b>Reid Points</b> Over Month for <b>{player_name}</b>',
        xaxis_title='Update Time',
        yaxis_title='Reid Points',
        yaxis=dict(
            range=[-100, 700],
            tickmode='linear',
            tick0=0,
            dtick=50
        )
    )

    # Сохранение графика в виде файла изображения
    buf = io.BytesIO()
    pio.write_image(fig, buf, format='png')
    buf.seek(0)

    return buf


async def get_guild_galactic_power(period: str) -> io.BytesIO:
    """Создает график роста ГМ гильдии за месяц или за год"""
    new_day_start = get_new_day_start()
    if period == 'month':
        one_month_ago = new_day_start - relativedelta(months=1)  # Вычислить дату один месяц назад
        async with async_session_maker() as session:
            guild_data = await session.execute(
                select(Guild).filter(
                    Guild.last_db_update_time >= one_month_ago))  # Использовать эту дату в фильтре
            guild_data = guild_data.scalars().all()
    else:
        one_year_ago = new_day_start - relativedelta(months=12)
        async with async_session_maker() as session:
            # Получаем все данные для игрока
            stmt = select(Guild).filter(Guild.last_db_update_time >= one_year_ago)

            all_data = await session.execute(stmt)
            all_data = all_data.scalars().all()

            # Сортируем данные по дате обновления
            all_data.sort(key=lambda x: x.last_db_update_time)

            # Берем первую запись для каждого месяца
            guild_data = []
            current_month = None
            for record in all_data:
                if record.last_db_update_time.month != current_month:
                    guild_data.append(record)
                    current_month = record.last_db_update_time.month


    # Создаем график с использованием plotly
    x_values = [guild.last_db_update_time.strftime("%d-%m-%Y") for guild in guild_data]
    y_values = [guild.galactic_power for guild in guild_data]
    # Сначала объединяем списки в список кортежей
    data = list(zip(x_values, y_values))

    # Сортируем список кортежей по дате
    data.sort(key=lambda x: x[0])
    if period == "month":
        data.pop()

    # Разделяем отсортированный список кортежей обратно на два списка
    x_values, y_values = zip(*data)

    difference_gp = int(y_values[-1]) - int(y_values[0])

    fig = go.Figure(data=go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        textposition='top center'))

    fig.update_layout(
        title=f'Raise <b>Guild</b> galactic power per <b>{period}</b>',
        xaxis_title='Update Time',
        yaxis_title='Galactic Power',

    )

    # Добавляем аннотацию с этой разницей
    fig.add_annotation(
        xref='paper', x=1, yref='paper', y=0,
        text=f"Total difference: {difference_gp:,}",
        showarrow=False,
        font=dict(
            size=14,
            color="#ffffff"
        ),
        align="right",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8
    )

    fig.add_annotation(
        xref='paper', x=0, yref='paper', y=1,
        text=f"Last value: {int(y_values[-1]):,}",
        showarrow=False,
        font=dict(
            size=14,
            color="#ffffff"
        ),
        align="right",
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#666bff",
        opacity=0.8
    )


    buf = io.BytesIO()
    pio.write_image(fig, buf, format='png')
    buf.seek(0)

    return buf