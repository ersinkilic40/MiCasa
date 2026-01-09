import tkinter as tk
from tkinter import ttk, messagebox
import requests
import psycopg2


def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="micasadatabase",
            user="adnan",
            password="Micasatiel0344",
            host="20.74.85.78",
            port="5432"
        )
    except Exception as e:
        messagebox.showerror("Database fout", str(e))
        return None


def save_user_to_db(username, password):
    conn = get_db_connection()
    if not conn:
        return

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )
    conn.commit()
    cur.close()
    conn.close()


def check_user_in_db(username, password):
    conn = get_db_connection()
    if not conn:
        return False

    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None


def get_verbruik_data():
    conn = get_db_connection()
    if not conn:
        return []

    cur = conn.cursor()
    cur.execute("SELECT datum, verbruik, temper FROM verbruik ORDER BY datum")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def predict(x, m, b):
    return m * x + b


def gradient_descent(X, y, m, b, lr, epochs):
    n = len(X)

    for epoch in range(epochs):
        dm = 0
        db = 0
        for i in range(n):
            y_pred = predict(X[i], m, b)
            dm += -2 * X[i] * (y[i] - y_pred)
            db += -2 * (y[i] - y_pred)

        m -= lr * (dm / n)
        b -= lr * (db / n)

    return m, b


def voorspel_verbruik(temp_celsius, m, b):
    return round(predict(temp_celsius, m, b), 2)

def get_ai_data():
    data = get_verbruik_data()
    temperatures = [float(row[2]) for row in data]
    energy = [float(row[1]) for row in data]
    return temperatures, energy

apparaten = {
    "Woonkamer": False,
    "Slaapkamer 1": False,
    "Slaapkamer 2": False,
    "Keuken": False
}

LAMP_VERBRUIK = 0.06


def get_verbruik_per_kamer():
    data = get_verbruik_data()[-1:]

    kamers = {
        "Woonkamer": 0,
        "Slaapkamer 1": 0,
        "Slaapkamer 2": 0,
        "Keuken": 0
    }

    for dag, verbruik, temp in data:
        kamers["Woonkamer"] += verbruik * 0.4
        kamers["Slaapkamer 1"] += verbruik * 0.2
        kamers["Slaapkamer 2"] += verbruik * 0.2
        kamers["Keuken"] += verbruik * 0.2

    for kamer, aan in apparaten.items():
        if aan:
            kamers[kamer] += LAMP_VERBRUIK

    return kamers


def get_verbruik_kwh(username):
    return round(sum(get_verbruik_per_kamer().values()), 2)


def get_gemiddeld_verbruik():
    data = get_verbruik_data()
    if not data:
        return 0
    return round(sum(row[1] for row in data) / len(data), 2)


def get_current_temperature():
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=52.09&longitude=5.12&current_weather=true",
            timeout=5
        )
        data = response.json()
        return f"{data['current_weather']['temperature']} °C"
    except:
        return "Niet beschikbaar"
def genereer_energie_advies(kamers):
    advies = []

    totaal = sum(kamers.values())

    if totaal > 11.45:
        advies.append("Het totale energieverbruik is hoog.")

    if kamers["Woonkamer"] > 4.60:
        advies.append("De woonkamer verbruikt veel energie, zet lampen uit als ze niet nodig zijn.")

    if kamers["Slaapkamer 1"] > 2.30:
        advies.append("Slaapkamer 1 gebruikt best veel energie.")

    if kamers["Slaapkamer 2"] > 2.30:
        advies.append("Slaapkamer 2 gebruikt best veel energie.")

    if kamers["Keuken"] > 2.30:
        advies.append("De keuken gebruikt veel energie, controleer apparaten.")

    if any(apparaten.values()) and totaal > 6:
        advies.append("Er staan lampen aan bij een hoog verbruik, overweeg ze uit te schakelen.")

    if not advies:
        advies.append("Je energieverbruik is efficiënt, ga zo door!")

    return advies



def open_dashboard(username):
    temperatures, energy = get_ai_data()

    m = 0
    b = 0
    learning_rate = 0.001
    epochs = 10000

    if temperatures:
        m, b = gradient_descent(temperatures, energy, m, b, learning_rate, epochs)

    dashboard = tk.Toplevel()
    dashboard.title("MiCasa Dashboard")
    dashboard.geometry("1000x700")

    tk.Label(dashboard, text="MiCasa Dashboard", font=("Arial", 24, "bold")).pack(pady=10)
    tk.Label(dashboard, text=f"Ingelogd als: {username}").pack()

    kpi_frame = tk.Frame(dashboard)
    kpi_frame.pack(pady=10, fill="x")

    temp_frame = tk.LabelFrame(kpi_frame, text="Temperatuur", padx=20, pady=20)
    temp_frame.pack(side="left", padx=10)
    tk.Label(temp_frame, text=get_current_temperature(), font=("Arial", 18, "bold")).pack()

    totaal_frame = tk.LabelFrame(kpi_frame, text="Totaal verbruik", padx=20, pady=20)
    totaal_frame.pack(side="left", padx=10)
    totaal_label = tk.Label(totaal_frame, font=("Arial", 18, "bold"))
    totaal_label.pack()

    kamers_lampen_frame = tk.Frame(dashboard)
    kamers_lampen_frame.pack(pady=10, fill="x")

    kamer_frame = tk.LabelFrame(kamers_lampen_frame, text="Verbruik per kamer", padx=10, pady=10)
    kamer_frame.pack(side="left", padx=10)

    lamp_frame = tk.LabelFrame(kamers_lampen_frame, text="Lampen", padx=10, pady=10)
    lamp_frame.pack(side="left", padx=10)

    kamer_labels = {}
    lamp_labels = {}

    for kamer in apparaten:
        lbl = tk.Label(kamer_frame, anchor="w", width=25)
        lbl.pack()
        kamer_labels[kamer] = lbl

        row = tk.Frame(lamp_frame)
        row.pack(anchor="w", pady=2)
        lbl_lamp = tk.Label(row, width=15)
        lbl_lamp.pack(side="left")
        lamp_labels[kamer] = lbl_lamp

        tk.Button(row, text="Aan / Uit", command=lambda k=kamer: toggle_lamp(k)).pack(side="left")

    data_frame = tk.LabelFrame(dashboard, text="Dagelijks verbruik", padx=10, pady=10)
    data_frame.pack(pady=10, fill="x")  # Gebruik fill="x" zodat het frame niet te hoog wordt

    tree = ttk.Treeview(data_frame, columns=("dag", "verbruik", "temp"), show="headings", height=1)
    tree.heading("dag", text="Dag")
    tree.heading("verbruik", text="Verbruik (kWh)")
    tree.heading("temp", text="Temperatuur (°C)")
    tree.pack(side="left", fill="x", expand=True)

    scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    for row in get_verbruik_data():
        tree.insert("", "end", values=row)

    advies_frame = tk.LabelFrame(dashboard, text="Energieadvies", padx=10, pady=10)
    advies_frame.pack(pady=10, fill="x")
    advies_text = tk.Text(advies_frame, width=70, height=5, wrap="word")
    advies_text.pack()

    ai_frame = tk.LabelFrame(dashboard, text="Verbruiksvoorspelling", padx=10, pady=10)
    ai_frame.pack(pady=10, fill="x")
    tk.Label(ai_frame, text="Verwachte buitentemperatuur (°C):").grid(row=0, column=0, sticky="w")
    temp_entry = tk.Entry(ai_frame, width=10)
    temp_entry.grid(row=0, column=1, padx=5)
    result_label = tk.Label(ai_frame, text="Geschat verbruik: - kWh")
    result_label.grid(row=1, column=0, columnspan=2, pady=5)
    tk.Button(ai_frame, text="Voorspel verbruik", command=lambda: doe_voorspelling()).grid(row=0, column=2, padx=10)

    def doe_voorspelling():
        try:
            invoer = float(temp_entry.get())
            verbruik = voorspel_verbruik(invoer, m, b)
            result_label.config(text=f"Geschat verbruik: {verbruik} kWh")
        except ValueError:
            messagebox.showerror("Fout", "Gebruik een geldig getal")

    def toggle_lamp(kamer):
        apparaten[kamer] = not apparaten[kamer]
        update_dashboard()

    def update_dashboard():
        totaal_label.config(text=f"{get_verbruik_kwh(username)} kWh")

        kamers = get_verbruik_per_kamer()
        for kamer in kamers:
            kamer_labels[kamer].config(text=f"{kamer}: {round(kamers[kamer], 2)} kWh")

        for kamer, aan in apparaten.items():
            lamp_labels[kamer].config(text=f"{kamer} lamp: {'Aan' if aan else 'Uit'}")

        advies_text.delete("1.0", tk.END)
        adviezen = genereer_energie_advies(kamers)
        for a in adviezen:
            advies_text.insert(tk.END, f"- {a}\n")

    update_dashboard()




def login():
    username = entry_username.get()
    password = entry_password.get()

    if check_user_in_db(username, password):
        open_dashboard(username)
    else:
        messagebox.showerror("Fout", "Onjuiste gebruikersnaam of wachtwoord")


def register():
    username = entry_username.get()
    password = entry_password.get()

    if username == "" or password == "":
        messagebox.showwarning("Let op", "Vul alles in")
        return

    save_user_to_db(username, password)
    messagebox.showinfo("Succes", "Account aangemaakt")


root = tk.Tk()
root.title("MiCasa Login")
root.geometry("400x300")

tk.Label(root, text="MiCasa Login", font=("Arial", 20, "bold")).pack(pady=20)

form_frame = tk.Frame(root)
form_frame.pack()

tk.Label(form_frame, text="Username").grid(row=0, column=0)
entry_username = tk.Entry(form_frame)
entry_username.grid(row=0, column=1)

tk.Label(form_frame, text="Password").grid(row=1, column=0)
entry_password = tk.Entry(form_frame, show="*")
entry_password.grid(row=1, column=1)

button_frame = tk.Frame(root)
button_frame.pack(pady=20)

tk.Button(button_frame, text="Log in", width=15, command=login).grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="Create account", width=15, command=register).grid(row=0, column=1, padx=10)

root.mainloop()









