from datetime import timedelta

ALIVE_DURATION = timedelta(minutes=10)

ALIVE_MINUTES = int(ALIVE_DURATION.total_seconds()) // 60
