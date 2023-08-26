from datetime import date
import requests
from decimal import Decimal, ROUND_HALF_UP

def get_euro_exchange_rate(date):
    '''Функція для отримання курсу Євро НБУ на вказану дату.'''
    url = f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json&valcode=EUR&date={date}'

    try:
        response = requests.get(url)
        data = response.json()
        if data:
            exchange_rate = Decimal(data[0]['rate']).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
            return exchange_rate
        else:
            print("Дані про курс валюти на вказану дату відсутні.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Помилка при отриманні курсу валюти: {e}")
        return None


def get_current_euro_exchange_rate():
    '''Функція для отримання курсу Євро НБУ на поточну дату.'''
    today = date.today().strftime("%Y%m%d")
    url = f'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json&valcode=EUR&date={today}'

    try:
        response = requests.get(url)
        data = response.json()
        if data:
            exchange_rate = Decimal(data[0]['rate']).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
            return exchange_rate
        else:
            print("Дані про курс валюти на вказану дату відсутні.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Помилка при отриманні курсу валюти: {e}")
        return None
