# handlers/send_group_message.py

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy import select

from create_bot import bot
from handlers.add_player_state import get_keyboard, cancel_state
from settings import async_session_maker
from src.decorators import member_admin_state_call_check, member_admin_state_message_check
from src.player import Player
from src.utils import get_new_day_start, is_valid_name


class Form(StatesGroup):
    users = State()
    message = State()


@member_admin_state_call_check
async def start_group_command(call: types.CallbackQuery, state: FSMContext):    # state не удалять
    keyboard = get_keyboard()
    await call.message.answer("Введите никнеймы в игре или имена игроков через @,"
                              " кому вы хотите отправить сообщение, через пробел.",
                              reply_markup=keyboard)
    await Form.users.set()


@member_admin_state_message_check
async def process_users(message: types.Message, state: FSMContext):
    """Этап ввода имен игроков"""
    keyboard = get_keyboard()
    async with state.proxy() as data:
        # Заменяем символ "@" на пустую строку перед разделением имен пользователей
        data['users'] = message.text.replace("@", "").split(" ")
        # Заменяем символ "@" на пустую строку перед разделением имен пользователей
        user_names = message.text.replace("@", "").split(" ")

        invalid_names = [name for name in user_names if not is_valid_name(name)]
        if invalid_names:
            await message.answer("Доступны только латинские буквы, цифры и @: " + ', '.join(invalid_names))
            # await state.finish()
            # await message.answer("❌ Действие отменено")
        else:
            data['users'] = user_names
            await message.answer("Введите сообщение, которое хотите отправить.", reply_markup=keyboard)
            await Form.next()


@member_admin_state_message_check
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message'] = message.text  # Сохраняем текст сообщения

        new_day_start = get_new_day_start()

        async with async_session_maker() as session:
            query = await session.execute(
                select(Player).filter(
                    Player.update_time >= new_day_start))
            all_users = query.scalars().all()

        # print(data['users'])
        users_from_db = {user.tg_nic: user.tg_id for user in all_users if user.tg_nic in data['users']}
        # print(users_from_db)

        failed_users = []  # Список пользователей, которым не удалось отправить сообщение

        if users_from_db:
            print(users_from_db)
            # Отправляем сообщение каждому пользователю
            for user_nic, user_id in users_from_db.items():
                # print(user)
                try:
                    await bot.send_message(user_id, data['message'])
                except Exception as e:
                    failed_users.append(user_nic + " " + str(e))  # Добавляем пользователя в список неудач
                    print(f"Не удалось отправить сообщение пользователю {user_nic}: {e}")
        else:   # Это нужно на случай если введут имя неправильное
            failed_users = [i for i in data['users']]
        if failed_users:
            await message.answer(
                "❌ Не удалось отправить сообщения следующим пользователям: " + "\n" + ",\n".join(failed_users))
        else:
            await message.answer("✅ Сообщения были отправлены.")
        await state.finish()


def register_handlers_group_message(dp: Dispatcher):
    dp.register_callback_query_handler(start_group_command, text='group')
    dp.register_message_handler(process_users, state=Form.users)
    dp.register_message_handler(process_message, state=Form.message)
    dp.register_callback_query_handler(cancel_state, text="cancel",
                                       state=Form.all_states)  # Обработчик кнопки отмены
