from datetime import datetime

def format_date(date):
    '''Функція яка повертає дату у вигляді рядка у форматі "yyyymmdd".'''
    formatted_date = date.strftime('%Y%m%d')
    return formatted_date