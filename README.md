NIE JESTEM DORADZĄ PODATKOWYM, TO NARZĘDZIE MA TYLKO CHARAKTER POMOCNICZY I NIE JEST TO OPINIA PODATKOWA.
Skrypt obliczający wartości do PIT-38 z platformy Interactive Brokers (IBKR), w Polsce też znanych jako Lynx.
Dla poprawnego działania należy z platformy IBKR wygenerować raporty (Statements) zawierające przynajmniej sekcję Trades. Raporty MUSZĄ pokrywać CAŁĄ HISTORIĘ KONTA (Ostatni rok to za mało).
Raporty mogą na siebie nachodzić datami, zostaną poprawnie policzone tylko raz.
Powłoka graficzna w trakcie tworzenia, skrypt simplePrint pozwala na uruchomienie narzędzia w trybie tekstowym. Jako kolejne argumenty należy podać ścieżki do wygenerowanych raportów.
Np.  
py simplePrint.py "D:\dev\PIT_IBKR\pit\pit\MULTI_20191106_20201105.csv" "D:\dev\PIT_IBKR\pit\pit\MULTI_20201106_20211105.csv" "D:\dev\PIT_IBKR\pit\pit\MULTI_20211108_20220215.csv"

Jako wynik zostaną wypisane:
Przychody i Koszta za kolejne lata (pozycje 21 i 22 w PIT-38)
Dochody z innych krajów (pozycja 32 w PIT/ZG)
Jeśli jako kraj jest podana nazwa giełdy lub inny symbol (np BVME, EUDARK) oznacza to że w skrypcie ta giełda nie ma przypisanego kraju. W takim wypadku należy skonsultować się z listą giełd na stronie IBKR: https://www.interactivebrokers.com/en/index.php?f=1562
