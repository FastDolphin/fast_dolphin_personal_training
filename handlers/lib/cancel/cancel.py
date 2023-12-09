from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from typeguard import typechecked


@typechecked
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Request creation cancelled.")
    return ConversationHandler.END
