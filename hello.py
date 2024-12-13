import datetime
import pytz

print("hello world")
new_york_timezone = pytz.timezone('America/New_York')
new_york_time = datetime.datetime.now(new_york_timezone)
print(new_york_time)
