import datetime
from logging import getLogger

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.utils.request import Request
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

from echo.config import load_config
from echo.utils import debug_requests


config = load_config()

logger = getLogger(__name__)

BUTTON1_RULES = "Подать обьявление"


def get_base_inline_keyboard():
    """ Получить клавиатуру для сообщения
        Эта клавиатура будет видна под каждым сообщением, где её прикрепили
    """
    # Каждый список внутри `keyboard` -- это один горизонтальный ряд кнопок
    keyboard = [
        # Каждый элемент внутри списка -- это один вертикальный столбец.
        # Сколько кнопок -- столько столбцов
        [
            InlineKeyboardButton(BUTTON1_RULES, callback_data='BUTTON1_RUL')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# def get_base_reply_keyboard():
#     keyboard = [
#         [
#             KeyboardButton(BUTTON1_RULES)
#         ]
#     ]
#
#     return ReplyKeyboardMarkup(
#         keyboard=keyboard,
#         resize_keyboard=True,
#     )


@debug_requests
def do_start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if chat_id == config.FEEDBACK_USER_ID or chat_id == config.FEEDBACK_USER_ID2:
        update.message.reply_text(
            text='Для того, чтобы ответить человеку, отвечайте ему как в обычном чате)'
        )
    else:
        update.message.reply_text(
            text='Отправьте текст объявления и загрузите фото\nВ ближайшее время мы Вам ответим',
            reply_markup=get_base_inline_keyboard()
        )


@debug_requests
def keyboard_callback_handler(update: Update, context: CallbackContext):
    """ Обработчик ВСЕХ кнопок со ВСЕХ клавиатур
    """
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == 'BUTTON1_RUL':
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        answer_text = '\n.         БОТ ПРИВЕТСТВУЕТ ВАС!         .\n\n' \
                      '                 В Н И М А Н И Е !!!\n\n' \
                      '       Ознакомление с правилами\n              подачи объявлений\n\n' \
                      '             О Б Я З А Т Е Л Ь Н О !!!\n'
        query.bot.answer_callback_query(callback_query_id=query.id, text=answer_text, show_alert=True)

        query.message.reply_text(
            text='Требования к объявлению:\n\n'
                 '1 - Краткое, но точное и, по возможности, полное описание товара.\n'
                 '2 - Не более 400 символов в описании (включая пробелы и знаки пунктуации)  '
                 'Проверить количество символов\n'
                 '3 - Фото до 4 шт включительно.\n'
                 '4 - Указана цена. БЕЗ "ОТВЕЧУ В ЛС" !!!\n'
                 '5 - Повторная публикация объявления не чаще 1 раза в неделю. (7 ДНЕЙ)\n'
                 '6 - Для тех, кто пригласит 10 друзей действует бонус - дополнительное объявление.\n\n'
                 'За нарушение правил объявление будет удалено, а участник будет забанен!!!\n\n'
                 'Категорически ЗАПРЕЩЕНО:\n\n'
                 '1. Публикация объявления не соответствующего правилам.\n'
                 '2. Повтор объявления раньше чем через 7 дней.\n'
                 '3. Публикация одного и того же объявления с разных аккаунтов.\n'
                 '4. Продажа/покупка  товаров, подпадающих под действующее законодательство Украины.\n\n'
                 'За нарушение правил Вы будете забанены.\n'
        )
        # query.message.reply_text(
        #     text='Отправьте текст объявления и загрузите фото\nВ ближайшее время мы Вам ответим'
        # )

@debug_requests
def do_echo(update: Update, context: CallbackContext):

    chat_id = update.message.chat_id

    if chat_id == config.FEEDBACK_USER_ID or chat_id == config.FEEDBACK_USER_ID2:
        error_message = None
        reply = update.message.reply_to_message
        if reply:
            forward_from = reply.forward_from
            if forward_from:
                text = update.message.text
                context.bot.send_message(
                    chat_id=forward_from.id,    # пересылка админу
                    text=text,
                )
                if chat_id == config.FEEDBACK_USER_ID:
                    update.message.forward(
                        chat_id=config.FEEDBACK_USER_ID2,
                    )
                if chat_id == config.FEEDBACK_USER_ID2:
                    update.message.forward(
                        chat_id=config.FEEDBACK_USER_ID,
                    )

                # update.message.reply_text(
                #     text='Сообщение было отправлено',
                # )
            else:
                error_message = 'Нельзя ответить самому себе'
        else:
            error_message = 'Нажмите "ответить" на сообщении выбранного человека, чтобы ответить автору сообщения'

        # Отправить сообщение об ошибке если оно есть
        if error_message is not None:
            update.message.reply_text(
                text=error_message,
            )
    else:
        # Пересылать всё как есть
        update.message.forward(
            chat_id=config.FEEDBACK_USER_ID,
        )
        update.message.forward(
            chat_id=config.FEEDBACK_USER_ID2,
        )
        # update.message.reply_text(
        #     text='Сообщение было отправлено',
        # )


def main():
    logger.info('Запускаем бота...')

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
    start_handler = CommandHandler('start', do_start)
    message_handler = MessageHandler(Filters.all, do_echo)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(buttons_handler)


    # Начать бесконечную обработку входящих сообщений
    updater.start_polling()
    updater.idle()

    logger.info('Закончили...')


if __name__ == '__main__':
    main()
