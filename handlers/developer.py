# handlers/developer.py
from aiogram import types, Dispatcher

from create_bot import bot
from src.utils import delete_db_player_data

COMMANDS = {
    "del_player_db <имя игрока или ник или код союзника>":
        "Удаляет все записи из базы данных об игроке.\nИспользовать "
        "только если игрок покинул гильдию и больше записи о нем не представляют "
        "ценности!\nОбратного эффекта команда не имеет!☠️☠️☠️",

    # Добавьте здесь другие команды по мере необходимости
}


async def developer_commands(message: types.Message):
    """Выводит инфо о командах разработчика"""
    is_guild_member = message.conf.get('is_guild_member', False)
    if is_guild_member:
        try:
            commands = "\n".join([f"/{command} - {description}" for command, description in COMMANDS.items()])
            await bot.send_message(message.chat.id, f"Список доступных команд администратора:\n\n{commands}")
        except Exception as e:
            await message.reply(f"Ошибка: {e}.\nОбратитесь разработчику бота в личку:\nhttps://t.me/rollbar")

async def del_db_player(message: types.Message):
    """Удаляет все записи из баз данных об игроке"""
    is_guild_member = message.conf.get('is_guild_member', False)
    if is_guild_member:
        try:
            player_name = message.get_args()  # Получаем имя игрока
            if not player_name:
                await message.reply("Пожалуйста, предоставьте имя игрока.")
                return
            mes = await delete_db_player_data(player_name)
            if mes:
                await bot.send_message(message.chat.id, f"Записи игрока {mes} безвозвратно удалены из базы данных ⚰️\n"
                                                        f"Поделом засранцу! 👹")
        except Exception as e:
            await message.reply(f"Ошибка: {e}.\nОбратитесь разработчику бота в личку:\nhttps://t.me/rollbar")

def register_handlers_developer(dp: Dispatcher):
    dp.register_message_handler(developer_commands, commands=['dev'], is_chat_admin=True)
    dp.register_message_handler(del_db_player, commands=['del_player'], is_chat_admin=True)