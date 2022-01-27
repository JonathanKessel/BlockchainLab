# BlockchainLab

Projektarbeit im Modul BlockchainLab im Wintersemester 2021/22 an der Hochschule der Medien, Stuttgart
Original-Commits und Arbeitsfortschritt wurde in [diesem](https://github.com/pxlfrk/BlockchainLab), externen Repository dokumentiert. Die Inhalte und Arbeitsdateien wurden nach Beendigung der Arbeiten zur Konsolidierung aller Arbeiten hier zusammengefasst.

## Block-Identifikation

### Ansatz

6 Farben - 6 Formen

Daraus ergeben sich - da für PREV und SELF je 12 Elemente vorgesehen sind - 12^6 Möglichkeiten. Wir vergeben also für jeden Block eine eindeutige Zahl zwischen 435356467 und 2176782335 (in dezimal), damit wir mind. eine zwölfstellige Base6-Codierung erreichen.

Diese wandeln wir in das Base6-Zahlensystem um, dass beispielweise aus `2985983` `143555555` macht. Der Vorteil hierbei ist, dass wir kein umständliches Script schreiben müssen dass uns Zahlen mit nur spezifischen Zeichen (1-6) generiert.

## Manuelles Umwandeln von SVG in PNG

Falls nötig kann auch manuell über die 'CLI' von Inkscape ein SVG konvertiert werden. Hier kann auch die Ausgabegröße parametrisiert werden.
SVG Export in PNG konvertieren:

``` shell
inkscape --export-png=asset_x2.png --export-width=6000 asset_x.svg
```

## Prepare development Environment

Use your favorite local python environment solution to create a new venv and make sure to activate it afterwards.

```shell
python3 -m venv .env
```

```shell
source .env/bin/activate
```

### Install necessary packages

```shell
pip install -r requirements.txt
```

### Update Requirements.txt to latest installed packages

```shell
pip freeze > requirements.txt
```

## Repository

Das [Repository von Jonathan](https://github.com/JonathanKessel/BlockchainLab) wurde als Submobule hinzugefügt.

```shell
git submodule add https://github.com/JonathanKessel/BlockchainLab.git
git submodule update --init --recursive # needed when you reclone your repo (submodules may not get cloned automatically)
```
