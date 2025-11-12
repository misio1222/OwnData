import tkinter as tk
from tkinter import ttk, messagebox, Listbox, Frame, Entry, Label, Button, Scrollbar, Spinbox
import requests

API_BASE_URL = "http://127.0.0.1:5000/api"
DAYS_OF_WEEK = {
    "Poniedziałek": 0, "Wtorek": 1, "Środa": 2,
    "Czwartek": 3, "Piątek": 4, "Sobota": 5, "Niedziela": 6
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("System Zarządzania Wizytami")
        self.root.geometry("900x700")

        # --- Główne okno z zakładkami ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Inicjalizacja poszczególnych zakładek
        self.create_appointments_tab()
        self.create_availability_tab()
        self.create_settings_tab()

    # --- Funkcje pomocnicze do komunikacji z API ---
    def api_request(self, method, endpoint, json=None):
        try:
            url = f"{API_BASE_URL}/{endpoint}"
            response = requests.request(method, url, json=json)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd API", str(e))
            return None

    # --- Zakładka 1: Zarządzanie wizytami ---
    def create_appointments_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Wizyty')

        Label(tab, text="Zarejestrowane wizyty", font=("Helvetica", 14)).pack(pady=10)

        list_frame = Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.appointments_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.appointments_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.appointments_listbox.yview)

        btn_frame = Frame(tab)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Odśwież", command=self.load_appointments).pack(side=tk.LEFT, padx=5)
        Button(btn_frame, text="Usuń wybraną", command=self.delete_appointment).pack(side=tk.LEFT, padx=5)

        self.load_appointments()

    def load_appointments(self):
        self.appointments_listbox.delete(0, tk.END)
        data = self.api_request('get', 'appointments')
        if data:
            self.appointments_data = data
            for item in data:
                display = f"{item['id']:<4} | {item['date']} | {item['time']} | {item['name']:<25} | {item['phone_number']}"
                self.appointments_listbox.insert(tk.END, display)

    def delete_appointment(self):
        selected_idx = self.appointments_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Uwaga", "Wybierz wizytę do usunięcia.")
            return

        appointment_id = self.appointments_data[selected_idx[0]]['id']
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tę wizytę?"):
            if self.api_request('delete', f'appointments/{appointment_id}'):
                self.load_appointments()

    # --- Zakładka 2: Zarządzanie harmonogramem ---
    def create_availability_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Harmonogram')

        # Formularz do dodawania
        form_frame = ttk.LabelFrame(tab, text="Dodaj nowy termin pracy", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        Label(form_frame, text="Dzień tygodnia:").grid(row=0, column=0, sticky="w")
        self.day_var = tk.StringVar()
        day_cb = ttk.Combobox(form_frame, textvariable=self.day_var, values=list(DAYS_OF_WEEK.keys()))
        day_cb.grid(row=0, column=1, padx=5, pady=2)

        Label(form_frame, text="Godzina od:").grid(row=1, column=0, sticky="w")
        self.start_time_entry = Entry(form_frame)
        self.start_time_entry.grid(row=1, column=1, padx=5, pady=2)
        self.start_time_entry.insert(0, "HH:MM")

        Label(form_frame, text="Godzina do:").grid(row=2, column=0, sticky="w")
        self.end_time_entry = Entry(form_frame)
        self.end_time_entry.grid(row=2, column=1, padx=5, pady=2)
        self.end_time_entry.insert(0, "HH:MM")

        Button(form_frame, text="Dodaj", command=self.add_availability).grid(row=3, columnspan=2, pady=10)

        # Lista istniejących terminów
        list_frame = ttk.LabelFrame(tab, text="Aktualny harmonogram", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.availability_listbox = Listbox(list_frame)
        self.availability_listbox.pack(fill=tk.BOTH, expand=True)

        btn_frame = Frame(list_frame)
        btn_frame.pack(pady=10, fill=tk.X)
        Button(btn_frame, text="Odśwież", command=self.load_availability).pack(side=tk.LEFT)
        Button(btn_frame, text="Usuń wybrany", command=self.delete_availability).pack(side=tk.RIGHT)

        self.load_availability()

    def load_availability(self):
        self.availability_listbox.delete(0, tk.END)
        data = self.api_request('get', 'availability')
        if data:
            self.availability_data = sorted(data, key=lambda x: x['day_of_week'])
            day_names = {v: k for k, v in DAYS_OF_WEEK.items()}
            for item in self.availability_data:
                day_name = day_names.get(item['day_of_week'], 'Nieznany dzień')
                display = f"ID: {item['id']} | {day_name} | {item['start_time']} - {item['end_time']}"
                self.availability_listbox.insert(tk.END, display)

    def add_availability(self):
        day = self.day_var.get()
        start = self.start_time_entry.get()
        end = self.end_time_entry.get()

        if not all([day, start, end]) or day not in DAYS_OF_WEEK:
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola poprawnie.")
            return

        payload = {"day_of_week": DAYS_OF_WEEK[day], "start_time": start, "end_time": end}
        if self.api_request('post', 'availability', json=payload):
            self.load_availability()

    def delete_availability(self):
        selected_idx = self.availability_listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Uwaga", "Wybierz termin do usunięcia.")
            return

        avail_id = self.availability_data[selected_idx[0]]['id']
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć ten termin z harmonogramu?"):
            if self.api_request('delete', f'availability/{avail_id}'):
                self.load_availability()

    # --- Zakładka 3: Ustawienia ---
    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Ustawienia')

        settings_frame = ttk.LabelFrame(tab, text="Główne ustawienia", padding=20)
        settings_frame.pack(padx=20, pady=20)

        Label(settings_frame, text="Długość wizyty (w minutach):").grid(row=0, column=0, padx=5, pady=10)
        self.duration_spinbox = Spinbox(settings_frame, from_=5, to=120, increment=5, width=10)
        self.duration_spinbox.grid(row=0, column=1, padx=5)

        Button(settings_frame, text="Zapisz", command=self.save_settings).grid(row=1, columnspan=2, pady=20)

        self.load_settings()

    def load_settings(self):
        data = self.api_request('get', 'settings/duration')
        if data:
            self.duration_spinbox.delete(0, tk.END)
            self.duration_spinbox.insert(0, data.get('duration', 30))

    def save_settings(self):
        try:
            duration = int(self.duration_spinbox.get())
            if self.api_request('post', 'settings/duration', json={'duration': duration}):
                messagebox.showinfo("Sukces", "Ustawienia zostały zapisane.")
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawną liczbę minut.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
