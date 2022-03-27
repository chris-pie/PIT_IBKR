import IBKR_Calc
import sys

calc = IBKR_Calc.IBKRCalc()
for arg in sys.argv[1:]:
    with open(arg, "r", encoding="utf-8-sig") as statement_file:
        calc.add_statement(statement_file)
result = calc.process_transactions()
for year in result:
    print(f"{year}:")
    revenue, cost = 0, 0
    for country in result[year]:
        print(f"Dochód w {country}: {str(result[year][country][0] - result[year][country][1])}")
        revenue += result[year][country][0]
        cost += result[year][country][1]
    print(f"\tPrzychód: {revenue}")
    print(f"\tKoszty: {cost}")
