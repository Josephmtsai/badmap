from datetime import datetime, timedelta
def convertToInt(input):
    try:
        result = int(input)
    except ValueError:
        result = 0
    return result

def convertToSTRDateTime(input,weekday):
    try:
        timeArray = input.split(":")
        minuteValue = '0'
        if len( timeArray) > 1:
            minuteValue =timeArray[1]
        
        result = datetime(datetime.today().year, datetime.today().month ,datetime.today().day, int(timeArray[0]), int(minuteValue),0,0) + timedelta(days=weekday)
    except ValueError:
        result = datetime(1970,1,1,0, 0,0,0)    
    return result.strftime("%Y-%m-%d %H:%M")

def getTodayWeekDay():
    return datetime.today().weekday()    

def unix_time_millis(dt):
	epoch = datetime.utcfromtimestamp(0)
	return (dt - epoch).total_seconds() * 1000.0	

def convertToDateTime(input,weekday):
    try:
        timeArray = input.split(":")
        minuteValue = '0'
        if len( timeArray) > 1:
            minuteValue =timeArray[1]
        result = datetime(datetime.today().year, datetime.today().month ,datetime.today().day, int(timeArray[0]), int(minuteValue),0,0) + timedelta(days=weekday)
    except ValueError:
        result = datetime(1970,1,1,0, 0,0,0)    
    return result
    