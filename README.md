# Zaawansowany System Rejestracji Wizyt

Kompleksowy system do zarządzania rezerwacjami, zbudowany w Pythonie przy użyciu frameworka Flask. Składa się z interfejsu webowego z dynamicznym kalendarzem dla pacjentów oraz aplikacji desktopowej (Tkinter) do zaawansowanego zarządzania harmonogramem i ustawieniami.

## Główne Funkcje

-   **Dynamiczny Kalendarz (Strona WWW):**
    -   Pacjenci mogą przeglądać dostępne dni w interaktywnym kalendarzu.
    -   Po wybraniu dnia, system wyświetla listę wolnych godzin, obliczoną na podstawie harmonogramu pracy i istniejących rezerwacji.
    -   Prosty formularz pozwala na szybką rezerwację wybranego terminu.

-   **Aplikacja Desktopowa do Zarządzania:**
    -   **Zarządzanie wizytami:** Przeglądanie i usuwanie wszystkich zarezerwowanych wizyt.
    -   **Zarządzanie harmonogramem:** Definiowanie dni i godzin przyjęć. Można dodać wiele przedziałów czasowych dla jednego dnia (np. rano i po południu).
    -   **Ustawienia:** Możliwość zdefiniowania domyślnej długości jednej wizyty (w minutach), co automatycznie wpływa na generowane "sloty" w kalendarzu.

-   **Centralne API:**
    -   Wszystkie operacje (zarówno z aplikacji webowej, jak i desktopowej) są obsługiwane przez centralne API, co zapewnia spójność danych.

## Wymagania

-   Python 3.7+

## Instalacja

1.  **Sklonuj repozytorium:**
    ```bash
    git clone <adres-repozytorium>
    cd <nazwa-katalogu>
    ```

2.  **Stwórz i aktywuj wirtualne środowisko (zalecane):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Na Windows: venv\Scripts\activate
    ```

3.  **Zainstaluj wymagane zależności:**
    ```bash
    pip install Flask requests
    ```

## Konfiguracja i Uruchomienie

### 1. Inicjalizacja Bazy Danych

Przed pierwszym uruchomieniem, musisz stworzyć i zainicjować bazę danych. Użyj poniższej komendy w głównym katalogu projektu:

```bash
flask initdb
```
Ta komenda utworzy plik `database.db` z wymaganą strukturą tabel.

### 2. Uruchomienie Aplikacji Webowej (Serwera)

Serwer Flask musi działać w tle, aby zarówno strona WWW, jak i aplikacja desktopowa mogły z niego korzystać.

```bash
flask run
```
Serwer będzie dostępny pod adresem `http://127.0.0.1:5000`.

### 3. Uruchomienie Aplikacji Desktopowej

Otwórz **nowy terminal**, aktywuj wirtualne środowisko i uruchom aplikację do zarządzania:

```bash
python desktop_app.py
```
Pojawi się okno z trzema zakładkami, w których możesz zarządzać systemem.

> **Ważne:** Aplikacja webowa i desktopowa muszą działać jednocześnie. Najpierw skonfiguruj harmonogram i długość wizyt w aplikacji desktopowej, a następnie otwórz stronę `http://127.0.0.1:5000` w przeglądarce, aby zobaczyć kalendarz i dokonać rezerwacji.
