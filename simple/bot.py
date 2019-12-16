from logging import getLogger

from telegram import Bot
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request

from echo.config import load_config
from echo.utils import debug_requests


config = load_config()

logger = getLogger(__name__)


@debug_requests
def message_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'аноним'

    text = update.effective_message.text
    reply_text = f'Привет, {name}!\n\n{text}'

    update.message.reply_text(
        text=reply_text,
    )


def main():
    logger.info('Start')

    req = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
    )
    bot = Bot(
        token=config.TG_TOKEN,
        request=req,
        base_url=config.TG_API_URL,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    # Проверить что бот корректно подключился к Telegram API
    info = bot.get_me()
    logger.info(f'Bot info: {info}')

    # Навесить обработчики команд
    handler = MessageHandler(Filters.all, message_handler)
    updater.dispatcher.add_handler(handler)

    # Начать бесконечную обработку входящих сообщений
    updater.start_polling()
    updater.idle()
    logger.info('Finish')


if __name__ == '__main__':
    main()
