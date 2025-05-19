import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from io import StringIO

# Criar diretório de saída
img_dir = Path("imgs")
img_dir.mkdir(exist_ok=True)

# URL do dataset do Painel COVID BR
url = "https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv"

# Realizar download com headers
headers = {
    "User-Agent": "Mozilla/5.0 (GitHub Actions - COVID Bot)"
}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(f"Erro ao baixar dados: {response.status_code}")

df = pd.read_csv(StringIO(response.text))
df["date"] = pd.to_datetime(df["date"])
df = df[["date", "state", "newCases", "newDeaths"]].dropna()

# Casos e mortes semanais - Brasil
br = df.groupby("date")[["newCases", "newDeaths"]].sum().resample("W").sum()

plt.figure(figsize=(10, 5))
br["newCases"].plot()
plt.title("Casos semanais de COVID-19 no Brasil")
plt.ylabel("Casos por semana")
plt.grid(True)
plt.tight_layout()
plt.savefig(img_dir / "brasil_casos_semanais.png")
plt.close()

plt.figure(figsize=(10, 5))
br["newDeaths"].plot(color="red")
plt.title("Mortes semanais de COVID-19 no Brasil")
plt.ylabel("Mortes por semana")
plt.grid(True)
plt.tight_layout()
plt.savefig(img_dir / "brasil_mortes_semanais.png")
plt.close()

# Gráficos por estado
estados = ["SP", "RJ", "RS", "BA", "MG"]
df_est = df[df["state"].isin(estados)].copy()
df_est = df_est.groupby(["date", "state"]).sum().reset_index()
df_est.set_index("date", inplace=True)
df_est = df_est.groupby("state")[["newCases", "newDeaths"]].resample("W").sum().reset_index()

plt.figure(figsize=(10, 5))
for estado in estados:
    subset = df_est[df_est["state"] == estado]
    plt.plot(subset["date"], subset["newCases"], label=estado)
plt.title("Casos semanais por estado")
plt.ylabel("Casos por semana")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(img_dir / "estados_casos.png")
plt.close()

plt.figure(figsize=(10, 5))
for estado in estados:
    subset = df_est[df_est["state"] == estado]
    plt.plot(subset["date"], subset["newDeaths"], label=estado)
plt.title("Mortes semanais por estado")
plt.ylabel("Mortes por semana")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(img_dir / "estados_mortes.png")
plt.close()
