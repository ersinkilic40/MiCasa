import psycopg2
import matplotlib.pyplot as plt


# DATABASE-CONNECTIE

conn = psycopg2.connect(
    host="20.74.85.78",
    port=5432,
    database="micasadatabase",
    user="jay",
    password="Micasatiel0344"
)

cur = conn.cursor()
cur.execute("SELECT temper, verbruik FROM verbruik ORDER BY datum;")
rows = cur.fetchall()
cur.close()
conn.close()


# DATA SCHEIDEN

temperatures = [float(r[0]) for r in rows]  # feature X
energy = [float(r[1]) for r in rows]  # target y

# Print de eerste 10 rijen om te controleren
print("Eerste 10 datapunten (temperatuur, verbruik):")
for i in range(10):
    print(temperatures[i], energy[i])



# CORRELATIES

def cor(x, y):
    n = len(x)
    mid_x = sum(x) / n
    mid_y = sum(y) / n
    teller = sum((x[i] - mid_x) * (y[i] - mid_y) for i in range(n))
    sx = sum((xi - mid_x) ** 2 for xi in x)
    sy = sum((yi - mid_y) ** 2 for yi in y)
    noemer = (sx * sy) ** 0.5
    return teller / noemer if noemer != 0 else 0.0


dagen = list(range(1, len(energy) + 1))
print("Correlatie temperatuur-verbruik:", cor(temperatures, energy))
print("Correlatie dag-verbruik:", cor(dagen, energy))



# spreidingsdiagram temperatuur vs energieverbruik
plt.figure(figsize=(6, 4))                      # handzaam formaat voor Word
plt.scatter(temperatures, energy, color='steelblue', label='Meetdata')
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Energieverbruik (kWh)")
plt.title("Figuur 1 – Verkennend spreidingsdiagram temperatuur vs verbruik")
plt.legend()
plt.show()