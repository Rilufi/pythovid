import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from io import StringIO

# Diretórios para salvar os dados e imagens
data_dir = Path("data")
img_dir = Path("imgs")
data_dir.mkdir(exist_ok=True)
img_dir.mkdir(exist_ok=True)

# URL do arquivo CSV da OMS
url = "https://data.who.int/dashboards/covid19/who-covid-19-global-data.csv"

# Nome do arquivo local
filename = "who-covid-19-global-data.csv"
filepath = data_dir / filename

# Baixar o arquivo CSV
response = requests.get(url)
if response.status_code == 200:
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"Arquivo salvo em: {filepath}")
else:
    print(f"Falha ao baixar o arquivo. Status code: {response.status_code}")
    exit()

# Carregar os dados
df = pd.read_csv(filepath)
df['Date_reported'] = pd.to_datetime(df['Date_reported'])

# Filtrar Brasil e dados a partir de 2025
df_brazil = df[
    (df['Country'] == 'Brazil') &
    (df['Date_reported'] >= '2025-01-01')
]

# Gráfico de casos
plt.figure(figsize=(10, 5))
plt.plot(df_brazil['Date_reported'], df_brazil['New_cases'], marker='o')
plt.title("Casos diários de COVID-19 no Brasil em 2025")
plt.xlabel("Data")
plt.ylabel("Número de casos")
plt.xticks(rotation=45)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.tight_layout()
plt.savefig(img_dir / "brasil_casos_diarios.png")
plt.close()

# Gráfico de mortes
plt.figure(figsize=(10, 5))
plt.plot(df_brazil['Date_reported'], df_brazil['New_deaths'], color='red', marker='o')
plt.title("Mortes diárias de COVID-19 no Brasil em 2025")
plt.xlabel("Data")
plt.ylabel("Número de mortes")
plt.xticks(rotation=45)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.tight_layout()
plt.savefig(img_dir / "brasil_mortes_diarios.png")
plt.close()
