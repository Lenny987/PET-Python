from datetime import datetime


'''
Checking if a certain time has passed
'''


def check_time(time, seconds, unit="seconds"):
    if unit == "seconds":
        if (datetime.now() - time).seconds >= seconds:
            return True
    elif unit == "microseconds":
        if (datetime.now() - time).microseconds >= seconds:
            return True
    
    return False