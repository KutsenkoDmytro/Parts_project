from datetime import date
import requests
from decimal import Decimal, ROUND_HALF_UP

def get_euro_exchange_rate(date):
    '''Функция для получения курса Евро НБУ на указанную дату.'''
    url = f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json&valcode=EUR&date={date}'

    try:
        response = requests.get(url)
        data = response.json()
        if data:
            exchange_rate = Decimal(data[0]['rate']).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
            return exchange_rate
        else:
            print("Нет данных о курсе валюты на указанную дату.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении курса валюты: {e}")
        return None


def get_current_euro_exchange_rate():
    '''Функция для получения курса Евро НБУ на текущую дату.'''
    today = date.today().strftime("%Y%m%d")
    url = f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json&valcode=EUR&date={today}'

    try:
        response = requests.get(url)
        data = response.json()
        if data:
            exchange_rate = Decimal(data[0]['rate']).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
            return exchange_rate
        else:
            print("Нет данных о курсе валюты на указанную дату.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении курса валюты: {e}")
        return None
