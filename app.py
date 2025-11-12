import sqlite3
import os
from flask import Flask, jsonify, render_template, request, g, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = 'database.db'

# --- Połączenie z bazą danych ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Baza danych została zainicjowana.')

# --- Funkcje pomocnicze do logiki biznesowej ---
def get_setting(key):
    db = get_db()
    cursor = db.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    return row['value'] if row else None

def calculate_available_slots(date_str):
    db = get_db()

    # Pobierz długość wizyty z ustawień
    duration = int(get_setting('appointment_duration'))

    # Znajdź dzień tygodnia dla podanej daty (0=poniedziałek, ..., 6=niedziela)
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return []
    day_of_week = target_date.weekday()

    # Pobierz godziny pracy dla tego dnia
    cursor = db.execute('SELECT start_time, end_time FROM availability WHERE day_of_week = ?', (day_of_week,))
    availability = cursor.fetchall()

    if not availability:
        return [] # Brak godzin pracy w tym dniu

    # Pobierz już zarezerwowane wizyty
    cursor = db.execute('SELECT time FROM appointments WHERE date = ?', (date_str,))
    booked_slots = {row['time'] for row in cursor.fetchall()}

    # Generuj wszystkie możliwe sloty i odfiltruj zajęte
    available_slots = []
    for schedule in availability:
        start_time = datetime.strptime(schedule['start_time'], '%H:%M')
        end_time = datetime.strptime(schedule['end_time'], '%H:%M')

        current_slot = start_time
        while current_slot < end_time:
            slot_str = current_slot.strftime('%H:%M')
            if slot_str not in booked_slots:
                available_slots.append(slot_str)
            current_slot += timedelta(minutes=duration)

    return available_slots

# --- Główne trasy aplikacji webowej ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API Endpoints ---

# API: Zarządzanie wizytami
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    db = get_db()
    cursor = db.execute('SELECT * FROM appointments ORDER BY date, time')
    appointments = [dict(row) for row in cursor.fetchall()]
    return jsonify(appointments)

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    required_fields = ['name', 'phone_number', 'date', 'time']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Brakujące dane'}), 400

    db = get_db()
    db.execute(
        'INSERT INTO appointments (name, phone_number, date, time) VALUES (?, ?, ?, ?)',
        (data['name'], data['phone_number'], data['date'], data['time'])
    )
    db.commit()
    return jsonify({'message': 'Wizyta dodana pomyślnie'}), 201

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    db = get_db()
    db.execute('DELETE FROM appointments WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Wizyta usunięta pomyślnie'}), 200

# API: Ustawienia
@app.route('/api/settings/duration', methods=['GET'])
def get_duration():
    duration = get_setting('appointment_duration')
    return jsonify({'duration': int(duration) if duration else 30})

@app.route('/api/settings/duration', methods=['POST'])
def set_duration():
    data = request.json
    duration = data.get('duration')
    if not duration or not isinstance(duration, int) or duration <= 0:
        return jsonify({'error': 'Nieprawidłowa wartość czasu trwania'}), 400

    db = get_db()
    db.execute("UPDATE settings SET value = ? WHERE key = 'appointment_duration'", (str(duration),))
    db.commit()
    return jsonify({'message': 'Czas trwania wizyty zaktualizowany'}), 200

# API: Dostępność
@app.route('/api/availability', methods=['GET'])
def get_availability():
    db = get_db()
    cursor = db.execute('SELECT * FROM availability ORDER BY day_of_week, start_time')
    availability = [dict(row) for row in cursor.fetchall()]
    return jsonify(availability)

@app.route('/api/availability', methods=['POST'])
def add_availability():
    data = request.json
    required = ['day_of_week', 'start_time', 'end_time']
    if not all(field in data for field in required):
        return jsonify({'error': 'Brakujące dane'}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO availability (day_of_week, start_time, end_time) VALUES (?, ?, ?)',
            (data['day_of_week'], data['start_time'], data['end_time'])
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Taki harmonogram już istnieje'}), 409
    return jsonify({'message': 'Dodano nowy harmonogram pracy'}), 201

@app.route('/api/availability/<int:id>', methods=['DELETE'])
def delete_availability(id):
    db = get_db()
    db.execute('DELETE FROM availability WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Harmonogram usunięty'}), 200

# API: Wolne terminy
@app.route('/api/available_slots', methods=['GET'])
def get_available_slots():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Brak parametru daty'}), 400

    slots = calculate_available_slots(date_str)
    return jsonify(slots)

if __name__ == '__main__':
    app.run(debug=True)
