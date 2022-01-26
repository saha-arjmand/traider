import datetime

# now utc time
current_utc_time = datetime.datetime.utcnow()
current_uts_time_to_seconds = int((current_utc_time - datetime.datetime(1970,1,1)).total_seconds())

# minute timframe
# time must be from 1 min ago to 2 minutes past
lastTime  = current_uts_time_to_seconds - current_utc_time.second
firstTime = lastTime - 60