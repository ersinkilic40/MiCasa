import tkinter as tk
from tkinter import ttk, messagebox
import requests
import psycopg2
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


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
        messagebox.showerror("database fout", str(e))
        return None


def save_user_to_db(username, password):
    conn= get_db_connection()
    if not conn:
        return

    cur= conn.cursor()

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users
                (
                    id
                    SERIAL
                    PRIMARY
                    KEY,
                    username
                    VARCHAR
                (
                    255
                ) UNIQUE NOT NULL,
                    password VARCHAR
                (
                    255
                ) NOT NULL
                    )
                """)

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        messagebox.showinfo("Succes", "account succesvol aangemaakt!")
    except:
        messagebox.showerror("Fout", "Gebruikersnaam bestaat al.")
    finally:
        cur.close()
        conn.close()


def check_user_in_db(username, password):
    conn= get_db_connection()
    if not conn:
        return False

    cur= conn.cursor()
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
    if not data:
        return [], []

    temperatures = [float(row[2]) for row in data]
    energy = [float(row[1]) for row in data]
    return temperatures, energy


kamers_status = {
    "Woonkamer": {
        "lamp": False,
        "raam": False,
        "deur": False,
        "verwarming": True
    },
    "Slaapkamer 1": {
        "lamp": False,
        "raam": False,
        "deur": True,
        "verwarming": False
    },
    "Slaapkamer 2": {
        "lamp": False,
        "raam": False,
        "deur": True,
        "verwarming": False
    },
    "Keuken": {
        "lamp": False,
        "raam": False,
        "deur": False,
        "verwarming": True
    }
}

LAMP_VERBRUIK = 0.06
VERWARMING_VERBRUIK = 1.5
PRIJS_PER_KWH = 0.30


def get_verbruik_per_kamer():
    data = get_verbruik_data()[-1:]
    kamers = {"Woonkamer": 0, "Slaapkamer 1": 0, "Slaapkamer 2": 0, "Keuken": 0}

    if data:
        for dag, verbruik, temp in data:
            kamers["Woonkamer"] += verbruik * 0.4
            kamers["Slaapkamer 1"] += verbruik * 0.2
            kamers["Slaapkamer 2"] += verbruik * 0.2
            kamers["Keuken"] += verbruik * 0.2

    for kamer, apparaten in kamers_status.items():
        if apparaten["lamp"]:
            kamers[kamer] += LAMP_VERBRUIK
        if apparaten["verwarming"]:
            kamers[kamer] += VERWARMING_VERBRUIK

    return kamers


def get_totaal_verbruik():
    return round(sum(get_verbruik_per_kamer().values()), 2)


def get_totaal_kosten():
    return round(get_totaal_verbruik() * PRIJS_PER_KWH, 2)


def get_current_temperature():
    try:
        response= requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=52.09&longitude=5.12&current_weather=true",
            timeout=5
        )
        data= response.json()
        return f"{data['current_weather']['temperature']} °C"
    except:
        return "Niet beschikbaar"


def genereer_energie_advies(kamers):
    advies= []
    totaal= sum(kamers.values())

    if totaal > 11.45:
        advies.append("Het totale energieverbruik is hoog. Overweeg apparaten uit te schakelen.")

    if kamers["Woonkamer"] > 4.60:
        advies.append("De woonkamer verbruikt veel energie. Check lampen en verwarming.")

    if kamers["Keuken"] > 2.30:
        advies.append("De keuken gebruikt veel energie. Controleer apparaten.")

    for kamer, status in kamers_status.items():
        if status["raam"] and status["verwarming"]:
            advies.append(f"🪟 {kamer}: Raam staat open terwijl verwarming aan is!")

    open_deuren = [k for k, v in kamers_status.items() if v["deur"]]
    if open_deuren:
        advies.append(f"Let op: Deuren staan open in {', '.join(open_deuren)}")

    if not advies:
        advies.append("Je energieverbruik is efficiënt, Goedzo")

    return advies


class MiCasaDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("MiCasa - Smart Home Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f2f5")

        temperatures, energy = get_ai_data()
        self.m, self.b = 0, 0
        if temperatures:
            self.m, self.b = gradient_descent(temperatures, energy, 0, 0, 0.001, 10000)

        self.setup_ui()
        self.show_page("dashboard")

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#1e3a8a", height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="🏠 MiCasa Dashboard", font=("Arial", 28, "bold"),
                 bg="#1e3a8a", fg="white").pack(side="left", padx=30, pady=20)
        tk.Label(header, text=f"Verhuurder: {self.username} | {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                 font=("Arial", 11), bg="#1e3a8a", fg="#94a3b8").pack(side="right", padx=30)

        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True)

        self.create_sidebar(main_container)

        self.content_area = tk.Frame(main_container, bg="#f0f2f5")
        self.content_area.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    def create_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#1e293b", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MENU", font=("Arial", 14, "bold"),
                 bg="#1e293b", fg="#94a3b8", pady=20).pack()

        buttons = [
            ("📊 Dashboard", "dashboard"),
            ("💡 Kamers", "kamers"),
            ("📈 Statistieken", "stats"),
            ("🤖 AI Voorspelling", "ai"),
            ("⚙️ Instellingen", "settings")
        ]

        for text, page in buttons:
            btn = tk.Button(sidebar, text=text, font=("Arial", 12),
                            bg="#334155", fg="white", relief="flat",
                            anchor="w", padx=20, pady=15,
                            command=lambda p=page: self.show_page(p))
            btn.pack(fill="x", padx=10, pady=5)

    def show_page(self, page_name):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        if page_name == "dashboard":
            self.show_dashboard_page()
        elif page_name == "kamers":
            self.show_kamers_page()
        elif page_name == "stats":
            self.show_stats_page()
        elif page_name == "ai":
            self.show_ai_page()
        elif page_name == "settings":
            self.show_settings_page()

    def show_dashboard_page(self):
        tk.Label(self.content_area, text="Dashboard Overzicht", font=("Arial", 24, "bold"),
                 bg="#f0f2f5", fg="#1e293b").pack(anchor="w", pady=(0, 20))

        kpi_frame = tk.Frame(self.content_area, bg="#f0f2f5")
        kpi_frame.pack(fill="x", pady=(0, 20))

        def create_kpi(parent, title, value, icon, color):
            card = tk.Frame(parent, bg=color, relief="flat")
            card.pack(side="left", padx=10, fill="both", expand=True)
            tk.Label(card, text=icon, font=("Arial", 32), bg=color, fg="white").pack(pady=(15, 5))
            tk.Label(card, text=title, font=("Arial", 11), bg=color, fg="#e0e7ff").pack()
            lbl = tk.Label(card, text=value, font=("Arial", 24, "bold"), bg=color, fg="white")
            lbl.pack(pady=(5, 15))
            return lbl

        self.temp_lbl = create_kpi(kpi_frame, "Temperatuur", get_current_temperature(), "🌡️", "#3b82f6")
        self.verbruik_lbl = create_kpi(kpi_frame, "Verbruik", f"{get_totaal_verbruik()} kWh", "⚡", "#10b981")
        self.kosten_lbl = create_kpi(kpi_frame, "Kosten Vandaag", f"€{get_totaal_kosten()}", "💰", "#f59e0b")

        actief = sum(1 for k in kamers_status.values() for app, status in k.items() if status)
        self.actief_lbl = create_kpi(kpi_frame, "Actieve Apps", str(actief), "🔌", "#8b5cf6")

        stats_frame = tk.LabelFrame(self.content_area, text="  📊 Snelle Statistieken  ",
                                    font=("Arial", 14, "bold"), bg="white", fg="#1e293b")
        stats_frame.pack(fill="both", expand=True, pady=(0, 20))

        info_text = tk.Text(stats_frame, font=("Arial", 11), bg="white",
                            relief="flat", padx=20, pady=20, height=10)
        info_text.pack(fill="both", expand=True)

        kamers = get_verbruik_per_kamer()
        info_text.insert("1.0", f"""
        🏠 VERBRUIK PER KAMER

        Woonkamer:     {round(kamers['Woonkamer'], 2)} kWh  (€{round(kamers['Woonkamer'] * PRIJS_PER_KWH, 2)})
        Slaapkamer 1:  {round(kamers['Slaapkamer 1'], 2)} kWh  (€{round(kamers['Slaapkamer 1'] * PRIJS_PER_KWH, 2)})
        Slaapkamer 2:  {round(kamers['Slaapkamer 2'], 2)} kWh  (€{round(kamers['Slaapkamer 2'] * PRIJS_PER_KWH, 2)})
        Keuken:        {round(kamers['Keuken'], 2)} kWh  (€{round(kamers['Keuken'] * PRIJS_PER_KWH, 2)})

        ────────────────────────────
        TOTAAL:        {get_totaal_verbruik()} kWh  (€{get_totaal_kosten()})
        """)
        info_text.config(state="disabled")

    def show_kamers_page(self):
        tk.Label(self.content_area, text="Kamers Beheer", font=("Arial", 24, "bold"),
                 bg="#f0f2f5", fg="#1e293b").pack(anchor="w", pady=(0, 20))

        self.kamer_widgets = {}

        for kamer in kamers_status.keys():
            kamer_card = tk.LabelFrame(self.content_area, text=f"  📍 {kamer}  ",
                                       font=("Arial", 14, "bold"), bg="white", fg="#1e293b")
            kamer_card.pack(fill="x", pady=10)

            verbruik_lbl = tk.Label(kamer_card, text="", font=("Arial", 11, "bold"),
                                    bg="white", fg="#059669")
            verbruik_lbl.pack(pady=10)

            controls = tk.Frame(kamer_card, bg="white")
            controls.pack(fill="x", padx=20, pady=(0, 15))

            apparaat_labels = {}

            for app in ["lamp", "verwarming", "raam", "deur"]:
                frame = tk.Frame(controls, bg="white")
                frame.pack(side="left", padx=10)

                icons = {"lamp": "💡", "verwarming": "🔥", "raam": "🪟", "deur": "🚪"}

                status_lbl = tk.Label(frame, text=f"{icons[app]} Uit", font=("Arial", 10),
                                      bg="#fee2e2", fg="#991b1b", padx=10, pady=5)
                status_lbl.pack()

                btn = tk.Button(frame, text="Aan/Uit", font=("Arial", 9), bg="#e2e8f0",
                                command=lambda k=kamer, a=app: self.toggle_apparaat(k, a))
                btn.pack(pady=5)

                apparaat_labels[app] = status_lbl

            self.kamer_widgets[kamer] = {
                "verbruik": verbruik_lbl,
                "apparaten": apparaat_labels
            }

        self.update_kamer_display()

    def show_stats_page(self):
        tk.Label(self.content_area, text="Statistieken & Grafieken", font=("Arial", 24, "bold"),
                 bg="#f0f2f5", fg="#1e293b").pack(anchor="w", pady=(0, 20))

        info_frame = tk.Frame(self.content_area, bg="#eff6ff")
        info_frame.pack(fill="x", pady=(0, 20))

        tk.Label(info_frame, text="📊 het energieverbruik over de laatste 10 dagen",
                 font=("Arial", 12), bg="#eff6ff", fg="#1e3a8a").pack(pady=15)

        graph_frame = tk.LabelFrame(self.content_area, text="  📈 Energieverbruik Over Tijd  ",
                                    font=("Arial", 14, "bold"), bg="white")
        graph_frame.pack(fill="both", expand=True)

        data = get_verbruik_data()
        if data:
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            laatste_data = data[-10:]
            dates = [str(row[0]) for row in laatste_data]
            verbruik = [float(row[1]) for row in laatste_data]

            x_pos = list(range(len(verbruik)))

            ax.plot(x_pos, verbruik, marker='o', linewidth=3, markersize=8, color='#3b82f6')
            ax.fill_between(x_pos, verbruik, alpha=0.3, color='#3b82f6')

            ax.set_title('Energieverbruik Laatste 10 Dagen', fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Verbruik (kWh)', fontsize=12, fontweight='bold')
            ax.set_xlabel('Datum', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')

            ax.set_xticks(x_pos)
            ax.set_xticklabels(dates, rotation=45, ha='right')

            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        else:
            tk.Label(graph_frame, text="Geen data beschikbaar om te visualiseren",
                     font=("Arial", 14), bg="white", fg="#64748b").pack(pady=50)

    def show_ai_page(self):
        tk.Label(self.content_area, text="🤖 AI Verbruiksvoorspelling", font=("Arial", 24, "bold"),
                 bg="#f0f2f5", fg="#1e293b").pack(anchor="w", pady=(0, 20))

        info_frame = tk.LabelFrame(self.content_area, text="  Over Dit Model  ",
                                   font=("Arial", 12, "bold"), bg="#eff6ff")
        info_frame.pack(fill="x", pady=(0, 20))

        tk.Label(info_frame, text="het model gebruikt lineaire regressie met gradient descent\n"
                                  "om energieverbruik te voorspellen gebaseerd op buiten temperatuur",
                 font=("Arial", 11), bg="#eff6ff", justify="left").pack(padx=20, pady=15)

        voorspel_frame = tk.LabelFrame(self.content_area, text="  🔮 Doe Een Voorspelling  ",
                                       font=("Arial", 14, "bold"), bg="white")
        voorspel_frame.pack(fill="both", expand=True)

        input_frame = tk.Frame(voorspel_frame, bg="white")
        input_frame.pack(pady=30)

        tk.Label(input_frame, text="Verwachte temperatuur (°C):",
                 font=("Arial", 13), bg="white").grid(row=0, column=0, padx=10, pady=10)

        temp_entry = tk.Entry(input_frame, font=("Arial", 13), width=15)
        temp_entry.grid(row=0, column=1, padx=10, pady=10)

        result_label = tk.Label(voorspel_frame, text="", font=("Arial", 16, "bold"),
                                bg="white", fg="#059669")
        result_label.pack(pady=20)

        def doe_voorspelling():
            try:
                temp = float(temp_entry.get())
                verbruik = voorspel_verbruik(temp, self.m, self.b)
                kosten = round(verbruik * PRIJS_PER_KWH, 2)
                result_label.config(
                    text=f"📊 Verwacht verbruik: {verbruik} kWh\n💰 Verwachte kosten: €{kosten}"
                )
            except:
                messagebox.showerror("Fout", "Voer een geldig getal in")

        tk.Button(input_frame, text="🔮 Voorspel", command=doe_voorspelling,
                  font=("Arial", 12, "bold"), bg="#3b82f6", fg="white",
                  padx=20, pady=10).grid(row=0, column=2, padx=10)

        advies_frame = tk.LabelFrame(self.content_area, text="  💡 Energieadvies  ",
                                     font=("Arial", 14, "bold"), bg="#fffbeb")
        advies_frame.pack(fill="x", pady=(20, 0))

        advies_text = tk.Text(advies_frame, font=("Arial", 11), bg="#fffbeb",
                              fg="#78350f", relief="flat", padx=20, pady=15, height=8)
        advies_text.pack(fill="x")

        kamers = get_verbruik_per_kamer()
        for tip in genereer_energie_advies(kamers):
            advies_text.insert("end", f"{tip}\n\n")
        advies_text.config(state="disabled")

    def show_settings_page(self):
        tk.Label(self.content_area, text="⚙️ Instellingen", font=("Arial", 24, "bold"),
                 bg="#f0f2f5", fg="#1e293b").pack(anchor="w", pady=(0, 20))

        prijs_frame = tk.LabelFrame(self.content_area, text="  💶 Energie Prijs  ",
                                    font=("Arial", 14, "bold"), bg="white")
        prijs_frame.pack(fill="x", pady=(0, 20))

        content = tk.Frame(prijs_frame, bg="white")
        content.pack(padx=30, pady=20)

        tk.Label(content, text=f"Huidige prijs per kWh: €{PRIJS_PER_KWH}",
                 font=("Arial", 12), bg="white").pack(anchor="w", pady=10)
        tk.Label(content, text="(op dit moment)",
                 font=("Arial", 10), bg="white", fg="#64748b").pack(anchor="w")

        account_frame = tk.LabelFrame(self.content_area, text="  👤 Account Informatie  ",
                                      font=("Arial", 14, "bold"), bg="white")
        account_frame.pack(fill="x", pady=(0, 20))

        tk.Label(account_frame, text=f"Ingelogd als: {self.username}",
                 font=("Arial", 12), bg="white").pack(anchor="w", padx=30, pady=20)

        over_frame = tk.LabelFrame(self.content_area, text="  Over MiCasa  ",
                                   font=("Arial", 14, "bold"), bg="white")
        over_frame.pack(fill="both", expand=True)

        tk.Label(over_frame, text="MiCasa Smart Home Dashboard\n\n"
                                  "Versie: 1.0\n"
                                  "Project: Smart Home HBO-ICT\n"
                                  "Team: MiCasa\n\n"
                                  "© 2025 - Alle rechten voorbehouden",
                 font=("Arial", 11), bg="white", justify="left").pack(padx=30, pady=30)

    def toggle_apparaat(self, kamer, apparaat):
        kamers_status[kamer][apparaat] = not kamers_status[kamer][apparaat]
        self.update_kamer_display()
        self.update_dashboard_kpis()

    def update_kamer_display(self):
        kamers = get_verbruik_per_kamer()

        for kamer, widgets in self.kamer_widgets.items():
            verbruik = kamers[kamer]
            widgets["verbruik"].config(
                text=f"Verbruik: {round(verbruik, 2)} kWh (€{round(verbruik * PRIJS_PER_KWH, 2)})")

            for app, lbl in widgets["apparaten"].items():
                status = kamers_status[kamer][app]
                icons = {"lamp": "💡", "verwarming": "🔥", "raam": "🪟", "deur": "🚪"}

                if status:
                    lbl.config(text=f"{icons[app]} Aan", bg="#dcfce7", fg="#166534")
                else:
                    lbl.config(text=f"{icons[app]} Uit", bg="#fee2e2", fg="#991b1b")

    def update_dashboard_kpis(self):
        if hasattr(self, 'verbruik_lbl'):
            self.verbruik_lbl.config(text=f"{get_totaal_verbruik()} kWh")
            self.kosten_lbl.config(text=f"€{get_totaal_kosten()}")

            actief = sum(1 for k in kamers_status.values() for app, status in k.items() if status)
            self.actief_lbl.config(text=str(actief))


def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showerror("Fout", "Vul alle velden in")
        return

    if check_user_in_db(username, password):
        root.withdraw()
        dashboard_window = tk.Toplevel()
        MiCasaDashboard(dashboard_window, username)
    else:
        messagebox.showerror("Fout", "Onjuiste gebruikersnaam of wachtwoord")


def register():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showerror("Fout", "Vul alle velden in")
        return

    if len(password) < 6:
        messagebox.showerror("Fout", "Wachtwoord moet minimaal 6 tekens zijn")
        return

    save_user_to_db(username, password)


root = tk.Tk()
root.title("MiCasa - Login")
root.geometry("450x550")
root.configure(bg="#1e3a8a")

login_container = tk.Frame(root, bg="white", relief="flat")
login_container.place(relx=0.5, rely=0.5, anchor="center", width=380, height=450)

tk.Label(login_container, text="🏠", font=("Arial", 48), bg="white").pack(pady=(30, 10))
tk.Label(login_container, text="MiCasa", font=("Arial", 32, "bold"), bg="white", fg="#1e3a8a").pack()
tk.Label(login_container, text="Smart Home Dashboard voor Verhuurders",
         font=("Arial", 10), bg="white", fg="#64748b").pack(pady=(0, 30))

tk.Label(login_container, text="Gebruikersnaam", font=("Arial", 10),
         bg="white", fg="#475569", anchor="w").pack(padx=40, anchor="w")
entry_username = tk.Entry(login_container, font=("Arial", 12), relief="solid", bd=1)
entry_username.pack(padx=40, pady=(5, 15), fill="x")

tk.Label(login_container, text="Wachtwoord", font=("Arial", 10),
         bg="white", fg="#475569", anchor="w").pack(padx=40, anchor="w")
entry_password = tk.Entry(login_container, font=("Arial", 12), show="●", relief="solid", bd=1)
entry_password.pack(padx=40, pady=(5, 20), fill="x")

tk.Button(login_container, text="Inloggen", command=login, font=("Arial", 12, "bold"),
          bg="#3b82f6", fg="white", relief="flat", padx=20, pady=10).pack(fill="x", padx=40, pady=(10, 10))

tk.Button(login_container, text="Account Aanmaken", command=register, font=("Arial", 10),
          bg="#e2e8f0", fg="#1e293b", relief="flat", padx=20, pady=8).pack(fill="x", padx=40)

tk.Label(login_container, text="© 2025 MiCasa - HBO-ICT Project",
         font=("Arial", 8), bg="white", fg="#94a3b8").pack(side="bottom", pady=20)

root.mainloop()