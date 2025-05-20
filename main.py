import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import requests
from io import StringIO
import seaborn as sns
from datetime import datetime, timedelta
import json
from matplotlib.ticker import MaxNLocator

# Configurações
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

# Diretórios
data_dir = Path("data")
img_dir = Path("imgs")
data_dir.mkdir(exist_ok=True)
img_dir.mkdir(parents=True, exist_ok=True)

# URL e arquivo
url = "https://data.who.int/dashboards/covid19/who-covid-19-global-data.csv"
filename = "who-covid-19-global-data.csv"
filepath = data_dir / filename

# Download
print("Baixando dados atualizados da OMS...")
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    with open(filepath, 'wb') as f:
        f.write(response.content)
    print(f"Dados salvos em: {filepath}")
except Exception as e:
    print(f"Erro ao baixar dados: {str(e)}")
    exit()

# Processamento
print("Processando dados...")
df = pd.read_csv(filepath)
df['Date_reported'] = pd.to_datetime(df['Date_reported'])

# Filtrar apenas dados do Brasil
df_brazil = df[df['Country'] == 'Brazil'].copy()

# Dados de 2025 (último ano completo)
df_2025 = df_brazil[df_brazil['Date_reported'] >= '2025-01-01'].copy()

# Dados de 2024 (ano anterior para comparação)
df_2024 = df_brazil[
    (df_brazil['Date_reported'] >= '2024-01-01') & 
    (df_brazil['Date_reported'] <= '2024-12-31')
].copy()

# Verificar se há dados suficientes
if df_2025.empty or df_2024.empty:
    print("Erro: Dados insuficientes para análise. Verifique o arquivo baixado.")
    exit()

# Calcular métricas para 2025
df_2025['MM7_cases'] = df_2025['New_cases'].rolling(7, min_periods=1).mean()
df_2025['MM7_deaths'] = df_2025['New_deaths'].rolling(7, min_periods=1).mean()
df_2025['letalidade'] = (df_2025['New_deaths'] / df_2025['New_cases'].replace(0, pd.NA)) * 100

# Calcular métricas para 2024
df_2024['Day_of_year'] = df_2024['Date_reported'].dt.dayofyear
df_2024['MM7_cases'] = df_2024['New_cases'].rolling(7, min_periods=1).mean()
df_2024['MM7_deaths'] = df_2024['New_deaths'].rolling(7, min_periods=1).mean()

# Preparar dados de 2025 para comparação
df_2025['Day_of_year'] = df_2025['Date_reported'].dt.dayofyear
current_day = datetime.now().timetuple().tm_yday
current_year = datetime.now().year
df_2025_comparison = df_2025[df_2025['Day_of_year'] <= current_day].copy()

# Criar listas de valores de MM7 alinhadas por dia do ano
mm7_2024 = df_2024.set_index('Day_of_year')['MM7_cases'].reindex(range(1, current_day+1)).fillna(0).values
mm7_2025 = df_2025.set_index('Day_of_year')['MM7_cases'].reindex(range(1, current_day+1)).fillna(0).values

mm7_deaths_2024 = df_2024.set_index('Day_of_year')['MM7_deaths'].reindex(range(1, current_day+1)).fillna(0).values
mm7_deaths_2025 = df_2025.set_index('Day_of_year')['MM7_deaths'].reindex(range(1, current_day+1)).fillna(0).values

# Texto de estatísticas comparativas
delta_cases = int(df_2025['New_cases'].sum() - df_2024['New_cases'].sum())
delta_deaths = int(df_2025['New_deaths'].sum() - df_2024['New_deaths'].sum())
stats_text = (
    f"Casos: {delta_cases:+,}\n"
    f"Óbitos: {delta_deaths:+,}\n"
    f"Letalidade 2024: {(df_2024['New_deaths'].sum() / df_2024['New_cases'].sum()) * 100:.2f}%\n"
    f"Letalidade 2025: {(df_2025['New_deaths'].sum() / df_2025['New_cases'].sum()) * 100:.2f}%"
)

# 1. Gráfico de casos diários com média móvel (2025)
print("Gerando gráfico de casos diários...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['New_cases'], color='#1f77b4', alpha=0.3, label='Casos diários')
plt.plot(df_2025['Date_reported'], df_2025['MM7_cases'], color='#1f77b4', linewidth=3, label='Média móvel 7 dias')
plt.title("Casos Diários de COVID-19 no Brasil (2025)", pad=20, fontsize=14)
plt.ylabel("Número de casos", labelpad=10)
plt.legend()
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_casos_diarios_mm7.png", bbox_inches='tight', transparent=True)
plt.close()

# 2. Gráfico de mortes diárias
print("Gerando gráfico de óbitos diários...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['New_deaths'], color='#d62728', alpha=0.3, label='Óbitos diários')
plt.plot(df_2025['Date_reported'], df_2025['MM7_deaths'], color='#d62728', linewidth=3, label='Média móvel 7 dias')
plt.title("Óbitos Diários por COVID-19 no Brasil (2025)", pad=20, fontsize=14)
plt.ylabel("Número de óbitos", labelpad=10)
plt.legend()
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_mortes_diarias_mm7.png", bbox_inches='tight', transparent=True)
plt.close()

# 3. Gráfico de letalidade
print("Gerando gráfico de letalidade...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['letalidade'], color='#2ca02c', linewidth=2)
plt.title("Taxa de Letalidade Diária (%) - 2025", pad=20, fontsize=14)
plt.ylabel("Porcentagem", labelpad=10)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_letalidade_diaria.png", bbox_inches='tight', transparent=True)
plt.close()

# 4. Gráfico comparativo anual (casos)
print("Gerando gráfico comparativo anual melhorado (casos)...")
days_of_year = list(range(1, current_day+1))
plt.figure(figsize=(16, 9))
plt.plot(days_of_year, mm7_2024, label='2024', color='#1f77b4', linewidth=2.5, alpha=0.8)
plt.plot(days_of_year, mm7_2025, label='2025', color='#d62728', linewidth=2.5)
plt.fill_between(days_of_year, mm7_2024, mm7_2025, where=(mm7_2025 > mm7_2024), interpolate=True, color='red', alpha=0.15, label='2025 > 2024')
plt.fill_between(days_of_year, mm7_2024, mm7_2025, where=(mm7_2025 < mm7_2024), interpolate=True, color='green', alpha=0.15, label='2025 < 2024')
plt.axvline(current_day, color='black', linestyle='--', linewidth=1)
plt.text(current_day+1, plt.ylim()[1]*0.95, f'{current_day}º dia', ha='left', va='top', fontsize=10, color='black', bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
plt.text(0.01, 0.99, stats_text, transform=plt.gca().transAxes, fontsize=11, verticalalignment='top', bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
plt.title(f"Casos de COVID-19 no Brasil: Média Móvel (7 dias)\nComparativo {current_year-1} vs {current_year}", fontsize=16, weight='bold')
plt.xlabel("Dia do ano")
plt.ylabel("Casos diários (MM7)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
plt.tight_layout()
plt.savefig(img_dir / "comparativo_2024_2025.png", bbox_inches='tight', dpi=300, transparent=True)
plt.close()

# 5. Gráfico comparativo de óbitos
print("Gerando gráfico comparativo de óbitos melhorado...")
plt.figure(figsize=(16, 9))
plt.plot(days_of_year, mm7_deaths_2024, label='2024', color='#1f77b4', linewidth=2.5, alpha=0.8)
plt.plot(days_of_year, mm7_deaths_2025, label='2025', color='#d62728', linewidth=2.5)
plt.fill_between(days_of_year, mm7_deaths_2024, mm7_deaths_2025, where=(mm7_deaths_2025 > mm7_deaths_2024), interpolate=True, color='red', alpha=0.15, label='2025 > 2024')
plt.fill_between(days_of_year, mm7_deaths_2024, mm7_deaths_2025, where=(mm7_deaths_2025 < mm7_deaths_2024), interpolate=True, color='green', alpha=0.15, label='2025 < 2024')
plt.axvline(current_day, color='black', linestyle='--', linewidth=1)
plt.text(current_day+1, plt.ylim()[1]*0.95, f'{current_day}º dia', ha='left', va='top', fontsize=10, color='black', bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
plt.title(f"Óbitos por COVID-19 no Brasil: Média Móvel (7 dias)\nComparativo {current_year-1} vs {current_year}", fontsize=16, weight='bold')
plt.xlabel("Dia do ano")
plt.ylabel("Óbitos diários (MM7)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
plt.tight_layout()
plt.savefig(img_dir / "comparativo_obitos_2024_2025.png", bbox_inches='tight', dpi=300, transparent=True)
plt.close()

# Salvar metadados
print("Salvando metadados...")
with open(img_dir / "ultima_atualizacao.txt", "w") as f:
    f.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# Salvar estatísticas resumidas
stats = {
    "total_cases_2024": int(df_2024['New_cases'].sum()),
    "total_deaths_2024": int(df_2024['New_deaths'].sum()),
    "total_cases_2025": int(df_2025['New_cases'].sum()),
    "total_deaths_2025": int(df_2025['New_deaths'].sum()),
    "lethality_2024": round((df_2024['New_deaths'].sum() / df_2024['New_cases'].sum()) * 100, 2),
    "lethality_2025": round((df_2025['New_deaths'].sum() / df_2025['New_cases'].sum()) * 100, 2),
    "update_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
}
with open(img_dir / "stats.json", "w") as f:
    json.dump(stats, f)

print("Processo concluído com sucesso!")
