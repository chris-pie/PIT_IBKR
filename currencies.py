import datetime
import sqlite3
import decimal
import requests
from typing import *


def convert_decimal(dec: bytes) -> decimal.Decimal:
    return decimal.Decimal(dec.decode("ASCII"))


def adapt_decimal(dec: decimal.Decimal) -> str:
    return str(dec)


sqlite3.register_adapter(decimal.Decimal, adapt_decimal)
sqlite3.register_converter("MYDEC", convert_decimal)


class Currencies:
    def __init__(self):
        self.connection = sqlite3.connect("currencies.db", isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS currencies
            (exchange_date DATE, currency TEXT, rate MYDEC)
            '''
        )
        self.connection.commit()

    def _get_currency_from_NBP(self, day: datetime.date, currency: str) -> Optional[decimal.Decimal]:
        r = requests.get(f"http://api.nbp.pl/api/exchangerates/rates/A/{currency}/{day.strftime('%Y-%m-%d')}")
        if r.status_code == 200:
            return decimal.Decimal(r.json(parse_float=decimal.Decimal)["rates"][0]["mid"])
        else:
            r = requests.get(f"http://api.nbp.pl/api/exchangerates/rates/B/{currency}/{day.strftime('%Y-%m-%d')}")
            if r.status_code == 200:
                return decimal.Decimal(r.json(parse_float=decimal.Decimal)["rates"][0]["mid"])
            else:
                return None

    def get_currency_for_day(self, day: datetime.date, currency: str) -> decimal.Decimal:
        cursor = self.connection.cursor()
        curr_day = day
        days = []
        while True:
            days.append(curr_day)
            cursor.execute('SELECT rate FROM currencies WHERE exchange_date = ? AND currency = ?', [curr_day, currency])
            res = cursor.fetchone()
            if res is None:
                res = self._get_currency_from_NBP(curr_day, currency)
                if res:
                    cursor.executemany('INSERT INTO currencies (rate, exchange_date, currency) VALUES (?, ?, ?)',
                                       [(res, a, currency) for a in days])
            else:
                res = res[0]
            if res is not None:
                cursor.close()
                return res

            curr_day = curr_day - datetime.timedelta(days=1)


currencies = Currencies()
