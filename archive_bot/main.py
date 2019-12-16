from logging import getLogger

from telegram import Bot
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request

from archive_bot.db import init_db
from archive_bot.db import add_message
from archive_bot.db import count_messages
from archive_bot.db import list_messages
from echo.config import load_config
from echo.utils import debug_requests


config = load_config()

logger = getLogger(__name__)


COMMAND_COUNT = 'count'
COMMAND_LIST = 'list'


def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Кол-во сообщений', callback_data=COMMAND_COUNT),
            ],
            [
                InlineKeyboardButton(text='Мои сообщения', callback_data=COMMAND_LIST),
            ],
        ],
    )


@debug_requests
def message_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'аноним'

    text = update.effective_message.text
    reply_text = f'Привет, {name}!\n\n{text}'

    # Ответить пользователю
    update.message.reply_text(
        text=reply_text,
        reply_markup=get_keyboard(),
    )

    # Записать сообщение в БД
    if text:
        add_message(
            user_id=user.id,
            text=text,
        )


@debug_requests
def callback_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    callback_data = update.callback_query.data

    if callback_data == COMMAND_COUNT:
        count = count_messages(user_id=user.id)
        text = f'У вас {count} сообщений!'
    elif callback_data == COMMAND_LIST:
        messages = list_messages(user_id=user.id, limit=5)
        text = '\n\n'.join([f'#{message_id} - {message_text}' for message_id, message_text in messages])
    else:
        text = 'Произошла ошибка'

    update.effective_message.reply_text(
        text=text,
    )


def main():
    logger.info('Start ArchiveBot')

    req = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
    )
    bot = Bot(
        token='855883347:AAHxvaX7DSchTqeXA59q3yqbQw74ZHixVM4',
        request=req,
        base_url='https://telegg.ru/orig/bot',
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    # Проверить что бот корректно подключился к Telegram API
    info = bot.get_me()
    logger.info(f'Bot info: {info}')

    # Подключиться к СУБД
    init_db()

    # Навесить обработчики команд
    updater.dispatcher.add_handler(MessageHandler(Filters.all, message_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    # Начать бесконечную обработку входящих сообщений
    updater.start_polling()
    updater.idle()
    logger.info('Stop ArchiveBot')


if __name__ == '__main__':
    main()
