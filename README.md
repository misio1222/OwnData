# System Rejestracji Wizyt

Prosty system do rejestracji wizyt składający się z aplikacji webowej (Flask) oraz aplikacji desktopowej (Tkinter). System umożliwia dodawanie, przeglądanie i usuwanie wizyt oraz wysyła powiadomienia SMS o nowo dodanych rezerwacjach za pomocą Twilio.

## Funkcjonalności

-   **Aplikacja webowa:**
    -   Formularz do dodawania nowych wizyt.
    -   Lista wszystkich zarejestrowanych wizyt.
    -   Możliwość usuwania wizyt.
-   **Aplikacja desktopowa:**
    -   Graficzny interfejs do zarządzania wizytami.
    -   Synchronizacja z serwerem w czasie rzeczywistym.
    -   Dodawanie i usuwanie wizyt.
-   **Powiadomienia SMS:**
    -   Automatyczne wysyłanie potwierdzenia o rezerwacji na podany numer telefonu.

## Wymagania

-   Python 3.6+
-   Konto Twilio (do wysyłania powiadomień SMS)

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

3.  **Zainstaluj wymagane biblioteki:**
    ```bash
    pip install -r requirements.txt
    ```

## Konfiguracja

### 1. Baza danych

Przed pierwszym uruchomieniem aplikacji webowej, musisz zainicjować bazę danych. Uruchom poniższą komendę w terminalu, w głównym katalogu projektu:

```bash
flask initdb
```
Spowoduje to utworzenie pliku `database.db`, w którym będą przechowywane dane.

### 2. Powiadomienia SMS (Twilio)

Aby powiadomienia SMS działały, musisz skonfigurować trzy zmienne środowiskowe. Zastąp wartości przykładowe swoimi danymi z konta Twilio.

**Linux/macOS:**
```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="twoj_auth_token"
export TWILIO_PHONE_NUMBER="+1234567890" # Twój numer telefonu Twilio
```

**Windows (Command Prompt):**
```bash
set TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
set TWILIO_AUTH_TOKEN="twoj_auth_token"
set TWILIO_PHONE_NUMBER="+1234567890"
```

> **Uwaga:** Jeśli nie skonfigurujesz powyższych zmiennych, aplikacja będzie działać, ale powiadomienia SMS będą jedynie symulowane (wyświetlane w konsoli), a nie faktycznie wysyłane.

## Uruchomienie

Projekt składa się z dwóch aplikacji, które muszą być uruchomione jednocześnie, aby aplikacja desktopowa mogła komunikować się z serwerem.

### 1. Uruchomienie aplikacji webowej (serwera)

W terminalu, w głównym katalogu projektu, uruchom:
```bash
flask run
```
Serwer będzie dostępny pod adresem `http://127.0.0.1:5000`.

### 2. Uruchomienie aplikacji desktopowej

Otwórz **nowy terminal** i, upewniwszy się, że wirtualne środowisko jest aktywne, uruchom:
```bash
python desktop_app.py
```
Pojawi się okno aplikacji, w którym możesz zarządzać wizytami.
