from typing import Callable, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
from utils import Config, has_access, is_admin
from typeguard import typechecked
import os


@typechecked
def send_menu_handler_factory(cfg: Config) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def send_menu(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id: int = update.effective_chat.id

        keyboard = []
        authorize_button: InlineKeyboardButton = InlineKeyboardButton(
            "🧐️️️️️️ Авторизация", callback_data="get_token"
        )
        description_button: InlineKeyboardButton = InlineKeyboardButton(
            "🔍 Как работает этот бот?", callback_data="get_description"
        )
        personal_training_button: InlineKeyboardButton = InlineKeyboardButton(
            "🦾 Получить тренировку", callback_data="get_personal_training"
        )
        send_report: InlineKeyboardButton = InlineKeyboardButton(
            "📝  Написать отчет", callback_data="send_report"
        )
        ask_for_access_button: InlineKeyboardButton = InlineKeyboardButton(
            "😫️️️️️️Запросить доступ", callback_data="ask_for_access"
        )

        api_key: str = os.getenv("X-API-Key", "")
        if has_access(cfg, api_key) or is_admin(cfg, user_chat_id=str(user_chat_id)):
            keyboard.extend(
                [[description_button], [personal_training_button], [send_report]]
            )
        else:
            keyboard.append([authorize_button])
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
