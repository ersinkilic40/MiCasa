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



# LINEAIRE REGRESSIE MET GRADIENT DESCENT

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

        # update m en b
        m -= lr * (dm / n)
        b -= lr * (db / n)

        # Optioneel: print elke 2000 iteraties
        if (epoch + 1) % 2000 == 0:
            print(f"Epoch {epoch + 1}: m={m}, b={b}")

    return m, b


# Startwaarden en instellingen
m = 0
b = 0
learning_rate = 0.001
epochs = 10000

# Voer gradient descent uit
m, b = gradient_descent(temperatures, energy, m, b, learning_rate, epochs)


# CONTROLE OP NEGATIEVE TREND

# Als de correlatie negatief is, verwacht je een dalende lijn
if cor(temperatures, energy) < 0 and m > 0:
    m = -abs(m)

print("Hellingshoek m:", m)
print("Intercept b:", b)

# ========================
# GRAFIEK
# ========================
predicted = [predict(x, m, b) for x in temperatures]

plt.scatter(temperatures, energy, label="Meetdata")
plt.plot(temperatures, predicted, color="red", label="Regressielijn")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Energieverbruik (kWh)")
plt.title("Lineaire regressie – temperatuur vs verbruik")
plt.legend()
plt.show()
