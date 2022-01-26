import datetime

class Calculate_time:
    # now utc time
    current_utc_time = datetime.datetime.utcnow()
    current_uts_time_to_seconds = int((current_utc_time - datetime.datetime(1970, 1, 1)).total_seconds())

    # minute timframe
    # time must be from 1 min ago to 2 minutes past
    lastTime = current_uts_time_to_seconds - current_utc_time.second
    firstTime = lastTime - 60

    def convert_second_to_utc_time(self,seconds):
        std_time = datetime.datetime.utcfromtimestamp(seconds)
        return std_time
