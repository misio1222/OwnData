import sqlite3

try:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Znalezione tabele:")
        for table in tables:
            print(f"- {table[0]}")
    else:
        print("Brak tabel w bazie danych.")

    conn.close()
except Exception as e:
    print(f"Wystąpił błąd: {e}")
