from typing import Callable
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
from utils import Config
from typeguard import typechecked


@typechecked
def send_menu_handler_factory(cfg: Config) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def send_menu(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id = str(update.effective_chat.id)

        keyboard = []

        description_button: InlineKeyboardButton = InlineKeyboardButton(
            "🔍 Как работает этот бот?", callback_data="get_description"
        )
        personal_training_button: InlineKeyboardButton = InlineKeyboardButton(
            "🦾 Получить тренировку", callback_data="get_personal_training"
        )
        send_report: InlineKeyboardButton = InlineKeyboardButton(
            "📝  Написать отчет", callback_data="send_report"
        )

        if user_chat_id in [cfg.ADMIN_CHAT_ID, cfg.CLIENT_CHAT_ID]:
            keyboard.extend(
                [[description_button], [personal_training_button], [send_report]]
            )
        else:  # Authorized (regular) users get only the menu button
            keyboard.append([description_button])

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите опцию:",
            reply_markup=reply_markup,
        )

    return send_menu


@typechecked
def get_send_menu_handler(cfg: Config) -> CommandHandler:
    send_menu_handler = send_menu_handler_factory(cfg)
    return CommandHandler("menu", send_menu_handler)
