import psycopg2
import matplotlib.pyplot as plt

#DATABASE-CONNECTIE

conn = psycopg2.connect(
    host="20.74.85.78",
    port=5432,
    database="micasadatabase",
    user="jay",
    password="Micasatiel0344"
)

cur = conn.cursor()


cur.execute("""
    SELECT temper, verbruik
    FROM verbruik
    ORDER BY dag;
""")

rows = cur.fetchall()

cur.close()
conn.close()

#DATA SCHEIDEN

temperatures = []
energy = []

for r in rows:
    # feature X
    temperatures.append(float(r[0]))
    # target y
    energy.append(float(r[1]))

print("Temperatuur:", temperatures)
print("Verbruik:", energy)


#correlaties

def gemiddelde(lijst):
    return sum(lijst) / len(lijst)


def cor(x, y):
    n = len(x)

    mid_x = sum(x) / n  # gemiddlede X
    mid_y = sum(y) / n  # gemiddelde Y

    teller = sum((x[i] - mid_x) * (y[i] - mid_y) for i in range(n))
    # spreiding van x en y afzonderlijk
    sx = sum((xi - mid_x) ** 2 for xi in x)
    sy = sum((yi - mid_y) ** 2 for yi in y)
    # noemer = uitkomst van spreidingen onder wortel
    noemer = (sx * sy) ** 0.5
    # als noemer 0 is return 0.0
    return teller / noemer if noemer != 0 else 0.0


dagen = list(range(1, len(energy) + 1))

print("Correlatie temperatuur-verbruik:",
      cor(temperatures, energy))
print("Correlatie dag-verbruik:",
      cor(dagen, energy))

#LINEAIRE REGRESSIE

# model: y = m*x + b

def predict(x, m, b):
    return m * x + b

def gradient_descent(X, y, m, b, lr, epochs):
    n = len(X)

    for _ in range(epochs):
        dm = 0
        db = 0

        for i in range(n):
            y_pred = predict(X[i], m, b)
            dm += -2 * X[i] * (y[i] - y_pred)
            db += -2 * (y[i] - y_pred)

        m = m - lr * (dm / n)
        b = b - lr * (db / n)

    return m, b


# startwaarden
m = 0
b = 0
learning_rate = 0.0001
epochs = 10000

m, b = gradient_descent(temperatures, energy, m, b, learning_rate, epochs)

print("Hellingshoek m:", m)
print("Intercept b:", b)

#GRAFIEK

predicted = [predict(x, m, b) for x in temperatures]


plt.scatter(temperatures, energy, label="Meetdata")
plt.plot(temperatures, predicted, label="Regressielijn", color="red")
plt.xlabel("Temperatuur (°C)")
plt.ylabel("Energieverbruik (kWh)")
plt.title("Lineaire regressie – temperatuur vs verbruik")
plt.legend()
plt.show()

