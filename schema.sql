-- Usuń istniejące tabele, jeśli istnieją
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS availability;

-- Tabela do przechowywania informacji o wizytach
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
);

-- Tabela do przechowywania ustawień, np. domyślnej długości wizyty
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Tabela do przechowywania dostępności (dni i godziny pracy)
-- day_of_week: 0 = Poniedziałek, 1 = Wtorek, ..., 6 = Niedziela
CREATE TABLE availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    UNIQUE(day_of_week, start_time, end_time)
);

-- Wstawienie domyślnej wartości długości wizyty (np. 30 minut)
INSERT INTO settings (key, value) VALUES ('appointment_duration', '30');
