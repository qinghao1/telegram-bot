from util.util import utc_time

# broadcast timings
BREAKFAST_BROADCAST_TIME = utc_time(hour=0,
                                    minute=0,
                                    second=1)
DINNER_BROADCAST_TIME = utc_time(hour=15,
                                 minute=0,
                                 second=0)

# menu download timing (for tomorrow's menu)
MENU_DOWNLOAD_TIME = utc_time(hour=18,
                             minute=0,
                             second=0)

NUM_DAYS_TO_DOWNLOAD = 10
