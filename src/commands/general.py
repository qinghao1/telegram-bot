import telegram
from telegram.ext import run_async

from database.database import get_rc_for_user, insert_user_rc
from util.kb_mark_up import start_kb, start_button_kb, choose_rc_kb
from util.messages import welcome_msg, help_msg, welcome_msg_with_rc
import logging


@run_async
def handle_start(update, context):
    chat_id = update.effective_chat.id
    rc = get_rc_for_user(chat_id)
    if not rc:
        text = welcome_msg_with_rc(update.effective_chat.first_name)
        reply_markup = choose_rc_kb()
    else:
        text = welcome_msg(update.effective_chat.first_name)
        reply_markup = start_kb()
    if update.callback_query is not None:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.HTML,
        )
        context.bot.answer_callback_query(update.callback_query.id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=telegram.ParseMode.HTML,
        )


@run_async
def handle_help(update, context):
    if update.callback_query is not None:
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
            text=help_msg(),
            reply_markup=start_button_kb(),
            parse_mode=telegram.ParseMode.HTML,
        )
        context.bot.answer_callback_query(update.callback_query.id)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_msg(),
            reply_markup=start_button_kb(),
            parse_mode=telegram.ParseMode.HTML,
        )


def handle_error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update.update_id, context.error)
