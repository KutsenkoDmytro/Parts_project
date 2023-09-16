from datetime import datetime

def format_date(date):
    '''Функція яка повертає дату у вигляді рядка у форматі "yyyymmdd".'''
    formatted_date = date.strftime('%Y%m%d')
    return formatted_date

def get_time_until_end_of_day():
    '''Функція яка повертає час до кінця поточної доби у секундах.'''
    current_datetime = datetime.now()
    end_of_day = current_datetime.replace(hour=23, minute=59, second=59)
    time_until_end = end_of_day - current_datetime
    return int(time_until_end.total_seconds())