import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Frame, Entry, Label, Button, Scrollbar
import requests
import json

# --- Konfiguracja API ---
API_BASE_URL = "http://127.0.0.1:5000/api"

class AppointmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zarządzanie Wizytami")
        self.root.geometry("800x600")

        # --- Główne ramki interfejsu ---
        main_frame = Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)

        list_frame = Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # --- Formularz dodawania wizyty ---
        Label(form_frame, text="Imię i nazwisko:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(form_frame, text="Data (RRRR-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = Entry(form_frame, width=30)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(form_frame, text="Numer telefonu:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = Entry(form_frame, width=30)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)

        add_button = Button(form_frame, text="Dodaj wizytę", command=self.add_appointment)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Lista wizyt ---
        Label(list_frame, text="Lista wizyt:", font=("Helvetica", 12)).pack(anchor="w")

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.appointments_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.appointments_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.appointments_listbox.yview)

        # --- Przyciski akcji dla listy ---
        action_frame = Frame(main_frame)
        action_frame.pack(pady=10)

        refresh_button = Button(action_frame, text="Odśwież", command=self.fetch_appointments)
        refresh_button.pack(side=tk.LEFT, padx=5)

        delete_button = Button(action_frame, text="Usuń wybraną", command=self.delete_appointment)
        delete_button.pack(side=tk.LEFT, padx=5)

        # --- Inicjalizacja danych ---
        self.fetch_appointments()

    def fetch_appointments(self):
        try:
            response = requests.get(f"{API_BASE_URL}/appointments")
            response.raise_for_status()

            self.appointments_listbox.delete(0, tk.END)
            self.appointments_data = response.json()

            for appointment in self.appointments_data:
                display_text = f"ID: {appointment['id']} | {appointment['name']} | {appointment['date']} | {appointment['phone_number']}"
                self.appointments_listbox.insert(tk.END, display_text)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać wizyt: {e}")

    def add_appointment(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        phone = self.phone_entry.get()

        if not all([name, date, phone]):
            messagebox.showwarning("Uwaga", "Wszystkie pola muszą być wypełnione!")
            return

        payload = {
            "name": name,
            "date": date,
            "phone_number": phone
        }

        try:
            response = requests.post(f"{API_BASE_URL}/appointments", json=payload)
            response.raise_for_status()

            # Czyszczenie pól i odświeżenie listy
            self.name_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.fetch_appointments()
            messagebox.showinfo("Sukces", "Nowa wizyta została dodana.")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się dodać wizyty: {e}")

    def delete_appointment(self):
        selected_indices = self.appointments_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Uwaga", "Najpierw wybierz wizytę do usunięcia.")
            return

        # Pobierz ID wizyty z danych
        selected_index = selected_indices[0]
        appointment_id = self.appointments_data[selected_index]['id']

        if not messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tę wizytę?"):
            return

        try:
            response = requests.delete(f"{API_BASE_URL}/appointments/{appointment_id}")
            response.raise_for_status()

            self.fetch_appointments()
            messagebox.showinfo("Sukces", "Wizyta została usunięta.")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się usunąć wizyty: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppointmentApp(root)
    root.mainloop()
