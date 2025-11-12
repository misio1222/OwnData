import sqlite3
import os
from flask import Flask, jsonify, render_template, request, g, redirect, url_for
from twilio.rest import Client

app = Flask(__name__)
DATABASE = 'database.db'

# --- Twilio Configuration ---
# Upewnij się, że ustawiłeś te zmienne środowiskowe przed uruchomieniem aplikacji
# Przykład: export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxx"
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Sprawdzenie, czy konfiguracja Twilio jest obecna
if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    twilio_configured = True
else:
    twilio_configured = False
    print("OSTRZEŻENIE: Brak konfiguracji Twilio. Powiadomienia SMS nie będą wysyłane.")
    print("Ustaw zmienne środowiskowe: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")


# --- Database Helper Functions ---
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

# Command to initialize the database
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

# --- SMS Sending Function ---
def send_sms_notification(phone_number, message):
    if not twilio_configured:
        print(f"--- SYMULACJA WYSYŁKI SMS (brak konfiguracji Twilio) ---")
        print(f"Do: {phone_number}")
        print(f"Wiadomość: {message}")
        print(f"----------------------------------------------------")
        return

    try:
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"Wiadomość SMS została wysłana do {phone_number}")
    except Exception as e:
        print(f"Błąd podczas wysyłania SMS do {phone_number}: {e}")


# --- Web App Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        phone_number = request.form['phone_number']

        if name and date and phone_number:
            db.execute(
                'INSERT INTO appointments (name, date, phone_number) VALUES (?, ?, ?)',
                (name, date, phone_number)
            )
            db.commit()

            sms_message = f"Cześć {name}! Twoja wizyta została pomyślnie zarezerwowana na {date}."
            send_sms_notification(phone_number, sms_message)

            return redirect(url_for('index'))

    cursor = db.execute('SELECT * FROM appointments ORDER BY id DESC')
    appointments = cursor.fetchall()
    return render_template('index.html', appointments=appointments)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    db = get_db()
    db.execute('DELETE FROM appointments WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))


# --- API Endpoints for Desktop App ---
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    db = get_db()
    cursor = db.execute('SELECT * FROM appointments ORDER BY id DESC')
    appointments = [dict(row) for row in cursor.fetchall()]
    return jsonify(appointments)

@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    name = data.get('name')
    date = data.get('date')
    phone_number = data.get('phone_number')

    if not name or not date or not phone_number:
        return jsonify({'error': 'Missing data'}), 400

    db = get_db()
    cursor = db.execute(
        'INSERT INTO appointments (name, date, phone_number) VALUES (?, ?, ?)',
        (name, date, phone_number)
    )
    db.commit()

    sms_message = f"Cześć {name}! Twoja wizyta została pomyślnie zarezerwowana na {date}."
    send_sms_notification(phone_number, sms_message)

    return jsonify({'id': cursor.lastrowid, 'name': name, 'date': date, 'phone_number': phone_number}), 201

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    db = get_db()
    db.execute('DELETE FROM appointments WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Appointment deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
