from datetime import datetime, timedelta

class Calculate_time:
    # now utc time
    current_utc_time = datetime.utcnow()
    current_uts_time_to_seconds = int((current_utc_time - datetime(1970, 1, 1)).total_seconds())

    current_utc_date0 = current_utc_time.replace(current_utc_time.year, current_utc_time.month, current_utc_time.day, 0, 0, 0, 0)

    # minute timframe
    # time must be from 1 min ago to 2 minutes past
    lastTime = current_uts_time_to_seconds - current_utc_time.second
    firstTime = lastTime - 60

    def convert_date_to_seconds(self, datetimeObj):
        seconds = int((datetimeObj - datetime(1970, 1, 1)).total_seconds())
        return seconds

    def convert_second_to_utc_time(self,seconds):
        std_time = datetime.utcfromtimestamp(seconds)
        return std_time

    def pastDay_datetime(self, daysNumber=0):
        toDay = self.current_utc_date0
        i = 0
        while i < daysNumber:
            minusDay = toDay - timedelta(days=i)
            minusSeconds = self.convert_date_to_seconds(minusDay)
            yield minusDay, minusSeconds
            i += 1


#
# timeObj = Calculate_time()
# data = timeObj.pastDay_datetime(2)
# for anyItem in data:
#     print(anyItem)

