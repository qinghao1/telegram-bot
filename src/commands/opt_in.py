import telegram

from util.kb_mark_up import start_button_kb
from database.database import update_breakfast_opt_in, update_dinner_opt_in
from util.const import BREAKFAST, DINNER
from util.formatting import capitalize, normalize


def handle_opt_in(meal):
    def handle_opt_in_inner(update, context):
        chat_id = update.effective_chat.id
        chosen_option, date = update.callback_query.data.split(".")[-2:]
        if meal == BREAKFAST:
            update_breakfast_opt_in(chat_id, date, chosen_option)
        else:
            update_dinner_opt_in(chat_id, date, chosen_option)

        # Clear markup
        context.bot.edit_message_reply_markup(
            chat_id=update.effective_chat.id,
            message_id=update.callback_query.message.message_id,
        )
        # Answer callback query (clears loading symbol)
        if update.callback_query is not None:
            context.bot.answer_callback_query(update.callback_query.id)

        # Sends thank you message
        context.bot.send_message(
            chat_id=chat_id,
            text=f"You have selected {capitalize(normalize(chosen_option))}. Thank you! Your response will help to reduce food wastage.",
            reply_markup=start_button_kb(),
        )

    return handle_opt_in_inner
