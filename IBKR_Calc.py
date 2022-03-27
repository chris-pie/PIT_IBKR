import datetime
from typing import *
import currencies
import csv
from decimal import Decimal

exchanges = {
    "FWB": "Niemcy",
    "TGATE": "Niemcy",
    "BVME": "Włochy",
    "ISLAND": "USA",
    "DARK": "USA",
    "EUDARK": "USA",
    "BYX": "USA",
    "IBKRATS": "USA",
    "IEX": "USA",
    "IDEALFX": "USA",
    "GETTEX2": "Niemcy",
    "IBIS": "Niemcy",
    "IBIS2": "Niemcy",
    "GETTEX": "Niemcy",
}


class Transaction:
    rates = currencies.Currencies()

    def __init__(self, quantity, proceeds, fee, currency, symbol, exchange, transaction_type, date):
        self.date: datetime.date = date
        self.transaction_type = transaction_type
        self.symbol = symbol
        self.currency = currency
        self.fee = fee
        self.quantity: Decimal = quantity
        self.proceeds: Decimal = proceeds
        self.exchange = exchange
        if self.currency == "PLN":
            self.price_per_share: Decimal = -((proceeds + fee) / quantity)
        else:
            self.price_per_share: Decimal = -(
                        self.rates.get_currency_for_day(date, currency) * (proceeds + fee) / quantity)


class Instruments:
    def __init__(self):
        self.instruments: Dict[str, List[Transaction]] = {}

    def add_trade(self, trade: Transaction) -> Optional[Tuple[str, str, Decimal, Decimal]]:
        if trade.symbol not in self.instruments:
            self.instruments[trade.symbol] = [trade]
            return None
        instrument_queue = self.instruments[trade.symbol]
        if not instrument_queue:
            instrument_queue.append(trade)
        if (trade.quantity > 0) == (instrument_queue[0].quantity > 0):
            instrument_queue.append(trade)
            return None
        else:
            instrument_queue.reverse()
            year = trade.date.strftime("%Y")
            revenue_expenses = [Decimal(0), Decimal(0)]
            long_short = 0 if trade.quantity > 0 else 1
            while trade.quantity != 0:
                if not instrument_queue:
                    instrument_queue.append(trade)
                    return trade.exchange, year, revenue_expenses[0], revenue_expenses[1]
                earliest_trade = instrument_queue.pop()
                if abs(trade.quantity) - abs(earliest_trade.quantity) >= 0:
                    revenue_expenses[long_short] += abs((earliest_trade.quantity * earliest_trade.price_per_share))
                    revenue_expenses[not long_short] += abs((earliest_trade.quantity * trade.price_per_share))
                    trade.quantity = earliest_trade.quantity + trade.quantity
                else:
                    revenue_expenses[long_short] += abs(trade.quantity * earliest_trade.price_per_share)
                    revenue_expenses[not long_short] += abs(trade.quantity * trade.price_per_share)
                    earliest_trade.quantity = earliest_trade.quantity + trade.quantity
                    trade.quantity = 0
                    instrument_queue.append(earliest_trade)

            instrument_queue.reverse()
            return trade.exchange, year, revenue_expenses[0], revenue_expenses[1]


class IBKRCalc:
    def __init__(self):
        self.trades: List[Transaction] = []
        self.ranges = RangeCollection()
        self.instruments = None

    def add_statement(self, statement: Iterable[str]):
        reader = csv.reader(statement)
        start_date, end_date = None, None
        for line in reader:
            try:
                if line[0] == "Statement" and line[1] == "Data" and line[2] == "Period":
                    start_date, end_date = line[3].split("-")
                    start_date = datetime.datetime.strptime(start_date, "%B %d, %Y ")
                    end_date = datetime.datetime.strptime(end_date, " %B %d, %Y")
                if line[0] == "Trades" and line[1] == "Data" and line[2] == "Trade":
                    date = datetime.datetime.strptime(line[6], "%Y-%m-%d, %H:%M:%S").date()
                    if date not in self.ranges:
                        quantity = Decimal(line[8].replace(",", "."))
                        proceeds = Decimal(line[11])
                        fee = Decimal(line[12])
                        currency = line[4]
                        symbol = line[5]
                        exchange = line[7]
                        transaction_type = line[3]
                        self.trades.append(Transaction(quantity, proceeds, fee, currency, symbol, exchange,
                                                       transaction_type, date))
            except IndexError:
                continue
        if not start_date and end_date:
            raise ValueError
        self.ranges.add_range(start_date.date(), end_date.date())

    def process_transactions(self) -> Dict[str, Dict[str, List[Decimal]]]:
        self.instruments = Instruments()

        self.trades.sort(key=lambda x: x.date)
        years_countries: Dict[str, Dict[str, List[Decimal]]] = {}
        for trade in self.trades:
            if trade.transaction_type == "Stocks":
                ret_val = self.instruments.add_trade(trade)
                if ret_val:
                    country = exchanges.get(ret_val[0],ret_val[0])
                    if ret_val[1] not in years_countries:
                        years_countries[ret_val[1]] = {}
                    if country not in years_countries[ret_val[1]]:
                        years_countries[ret_val[1]][country] = [Decimal(0), Decimal(0)]
                    years_countries[ret_val[1]][country][0] += ret_val[2]
                    years_countries[ret_val[1]][country][1] += ret_val[3]
        return years_countries


class RangeCollection:
    def __init__(self):
        self.ranges: List[Tuple[datetime.date, datetime.date]] = []

    def add_range(self, start, end):
        self.ranges.append((start, end))

    def __contains__(self, item):
        for start, end in self.ranges:
            if start <= item <= end:
                return True
        return False
