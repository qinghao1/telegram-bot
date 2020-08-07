import os
import datetime
import logging
import telegram

from database.database import (
    get_broadcast_subscribers,
    get_raw_menu,
    get_hidden_cuisines,
    update_subscribe_setting,
)
from scheduler.scheduler_config import (
    BREAKFAST_BROADCAST_TIME,
    DINNER_BROADCAST_TIME,
    MENU_DOWNLOAD_TIME,
    NUM_DAYS_TO_DOWNLOAD,
)
from scraper.src.main import get_menu
from util.const import BREAKFAST, DINNER
from util.kb_mark_up import breakfast_opt_kb, dinner_opt_kb
from util.messages import menu_msg_opt_in
from util.util import parse_menu, localized_date_today, localized_date_tomorrow


def scheduler(job_queue):
    # get tomorrow's menu

    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_date = datetime.datetime.combine(tomorrow_date, datetime.time.min)
    job_queue.run_daily(
        callback=lambda: get_menu(tomorrow_date, NUM_DAYS_TO_DOWNLOAD),
        time=MENU_DOWNLOAD_TIME,
    )

    # schedule breakfast and dinner broadcasts
    # breakfast is broadcasted the day before, dinner the day itself

    job_queue.run_daily(
        callback=meal_broadcast(BREAKFAST, tomorrow=True), time=BREAKFAST_BROADCAST_TIME
    )
    job_queue.run_daily(
        callback=meal_broadcast(DINNER, tomorrow=False), time=DINNER_BROADCAST_TIME
    )


# meal broadcast function
def meal_broadcast(meal, tomorrow=False):

    # use localized_date_today() in this function instead of date.today()
    # as the VM provided by NUS is running in UTC time.

    def send_menu(context):
        date = localized_date_tomorrow() if tomorrow else localized_date_today
        menu = get_raw_menu(meal, date)

        if menu is None:
            return

        # get the subscribers before the broadcast
        subscribers = get_broadcast_subscribers(meal)

        logging.info(
            f"meal broadcast in progress... number of subscribers: {len(subscribers)}"
        )

        for user_id in subscribers:
            # extracts chat_id from nested [] from database
            chat_id = user_id[0]
            hidden_cuisines = get_hidden_cuisines(chat_id)
            reply_markup = breakfast_opt_kb if meal is BREAKFAST else dinner_opt_kb
            try:
                context.bot.send_message(
                    chat_id=chat_id,
                    text=menu_msg_opt_in(date, meal, parse_menu(menu, hidden_cuisines)),
                    reply_markup=reply_markup(hidden_cuisines, date),
                    parse_mode=telegram.ParseMode.HTML,
                )
            except Exception:
                logging.warning(
                    f"{chat_id}: exception occurs, reverting user's subscription status"
                )
                update_subscribe_setting(chat_id, meal)
                continue
            logging.info(f"{chat_id}: {meal} menu broadcast")

        logging.info("meal broadcast finished")

    return send_menu
