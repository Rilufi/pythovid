import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from io import StringIO
import seaborn as sns
from datetime import datetime, timedelta

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

# Diretórios
data_dir = Path("data")
img_dir = Path("imgs/current")
data_dir.mkdir(exist_ok=True)
img_dir.mkdir(parents=True, exist_ok=True)

# URL e arquivo
url = "https://data.who.int/dashboards/covid19/who-covid-19-global-data.csv"
filename = "who-covid-19-global-data.csv"
filepath = data_dir / filename

# Download
response = requests.get(url)
if response.status_code == 200:
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"Arquivo salvo em: {filepath}")
else:
    print(f"Falha ao baixar o arquivo. Status code: {response.status_code}")
    exit()

# Processamento
df = pd.read_csv(filepath)
df['Date_reported'] = pd.to_datetime(df['Date_reported'])

# Filtrar Brasil e 2025
df_brazil = df[(df['Country'] == 'Brazil') & (df['Date_reported'] >= '2025-01-01')].copy()

# Calcular métricas
df_brazil['MM7_cases'] = df_brazil['New_cases'].rolling(7).mean()
df_brazil['MM7_deaths'] = df_brazil['New_deaths'].rolling(7).mean()
df_brazil['letalidade'] = (df_brazil['New_deaths'] / df_brazil['New_cases']) * 100

# Gráfico 1: Casos diários com média móvel
plt.figure(figsize=(14, 7))
plt.plot(df_brazil['Date_reported'], df_brazil['New_cases'], 
         color='#1f77b4', alpha=0.3, label='Casos diários')
plt.plot(df_brazil['Date_reported'], df_brazil['MM7_cases'], 
         color='#1f77b4', linewidth=3, label='Média móvel 7 dias')
plt.title("Casos Diários de COVID-19 no Brasil (2025)", pad=20, fontsize=14)
plt.ylabel("Número de casos", labelpad=10)
plt.legend()
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_casos_diarios_mm7.png", bbox_inches='tight', transparent=True)
plt.close()

# Gráfico 2: Mortes diárias com média móvel
plt.figure(figsize=(14, 7))
plt.plot(df_brazil['Date_reported'], df_brazil['New_deaths'], 
         color='#d62728', alpha=0.3, label='Óbitos diários')
plt.plot(df_brazil['Date_reported'], df_brazil['MM7_deaths'], 
         color='#d62728', linewidth=3, label='Média móvel 7 dias')
plt.title("Óbitos Diários por COVID-19 no Brasil (2025)", pad=20, fontsize=14)
plt.ylabel("Número de óbitos", labelpad=10)
plt.legend()
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_mortes_diarias_mm7.png", bbox_inches='tight', transparent=True)
plt.close()

# Gráfico 3: Taxa de letalidade
plt.figure(figsize=(14, 7))
plt.plot(df_brazil['Date_reported'], df_brazil['letalidade'], 
         color='#2ca02c', linewidth=2)
plt.title("Taxa de Letalidade Diária (%) - 2025", pad=20, fontsize=14)
plt.ylabel("Porcentagem", labelpad=10)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_letalidade_diaria.png", bbox_inches='tight', transparent=True)
plt.close()

# Comparativo com 2024
df_2024 = df[(df['Country'] == 'Brazil') & 
             (df['Date_reported'] >= '2024-01-01') & 
             (df['Date_reported'] <= '2024-12-31')].copy()
df_2024['Day_of_year'] = df_2024['Date_reported'].dt.dayofyear
df_2025 = df_brazil.copy()
df_2025['Day_of_year'] = df_2025['Date_reported'].dt.dayofyear

# Gráfico 4: Comparativo anual
plt.figure(figsize=(14, 7))
plt.plot(df_2024['Day_of_year'], df_2024['New_cases'].rolling(7).mean(), 
         label='2024', color='#7f7f7f', linestyle='--')
plt.plot(df_2025['Day_of_year'], df_2025['New_cases'].rolling(7).mean(), 
         label='2025', color='#1f77b4')
plt.title("Comparativo Anual: Casos (MM7) - 2024 vs 2025", pad=20, fontsize=14)
plt.ylabel("Casos (média móvel 7 dias)", labelpad=10)
plt.xlabel("Dia do ano", labelpad=10)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(img_dir / "comparativo_2024_2025.png", bbox_inches='tight', transparent=True)
plt.close()

# Salvar dados da última atualização
with open(img_dir / "ultima_atualizacao.txt", "w") as f:
    f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
