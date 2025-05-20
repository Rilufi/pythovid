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

# Preparar dados de 2025 para comparação
df_2025['Day_of_year'] = df_2025['Date_reported'].dt.dayofyear
current_day_of_year = datetime.now().timetuple().tm_yday
df_2025_comparison = df_2025[df_2025['Day_of_year'] <= current_day_of_year].copy()

# 1. Gráfico de casos diários com média móvel (2025)
print("Gerando gráfico de casos diários...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['New_cases'], 
         color='#1f77b4', alpha=0.3, label='Casos diários')
plt.plot(df_2025['Date_reported'], df_2025['MM7_cases'], 
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

# 2. Gráfico de mortes diárias com média móvel (2025)
print("Gerando gráfico de óbitos diários...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['New_deaths'], 
         color='#d62728', alpha=0.3, label='Óbitos diários')
plt.plot(df_2025['Date_reported'], df_2025['MM7_deaths'], 
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

# 3. Gráfico de taxa de letalidade (2025)
print("Gerando gráfico de letalidade...")
plt.figure(figsize=(14, 7))
plt.plot(df_2025['Date_reported'], df_2025['letalidade'], 
         color='#2ca02c', linewidth=2)
plt.title("Taxa de Letalidade Diária (%) - 2025", pad=20, fontsize=14)
plt.ylabel("Porcentagem", labelpad=10)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(img_dir / "brasil_letalidade_diaria.png", bbox_inches='tight', transparent=True)
plt.close()

# 4. Gráfico comparativo anual (2024 vs 2025)
print("Gerando gráfico comparativo anual melhorado...")
plt.figure(figsize=(16, 8))

# Configurações gerais
plt.rcParams['font.size'] = 12
current_year = datetime.now().year

# Garantir que estamos comparando os mesmos dias do ano
min_days = min(len(df_2024), len(df_2025_comparison))
days_of_year = range(1, min_days + 1)

# Extrair os valores para comparação
mm7_2024 = df_2024['MM7_cases'].values[:min_days]
mm7_2025 = df_2025_comparison['MM7_cases'].values[:min_days]

# Criar área entre as curvas para destacar diferenças
plt.fill_between(
    days_of_year,
    mm7_2024,
    mm7_2025,
    where=(mm7_2025 > mm7_2024),
    facecolor='red', alpha=0.2, interpolate=True, label='2025 > 2024'
)

plt.fill_between(
    days_of_year,
    mm7_2024,
    mm7_2025,
    where=(mm7_2025 < mm7_2024),
    facecolor='green', alpha=0.2, interpolate=True, label='2025 < 2024'
)

# Plotar as linhas principais
line_2024, = plt.plot(
    days_of_year,
    mm7_2024,
    label='2024', color='#1f77b4', linewidth=3, alpha=0.7
)

line_2025, = plt.plot(
    days_of_year,
    mm7_2025,
    label='2025', color='#d62728', linewidth=3
)

# Adicionar marcadores mensais
months = range(1, 13)
month_names = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
month_days = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

for day, name in zip(month_days, month_names):
    plt.axvline(x=day, color='gray', linestyle=':', alpha=0.3)
    plt.text(day+2, plt.ylim()[1]*0.95, name, color='gray')

# Linha vertical para data atual
current_day = datetime.now().timetuple().tm_yday
current_line = plt.axvline(x=current_day, color='black', linestyle='--', alpha=0.7)
plt.text(current_day+2, plt.ylim()[1]*0.85, f'Hoje ({current_day}º dia)', 
         color='black', bbox=dict(facecolor='white', alpha=0.8))

# Calcular e mostrar diferenças totais
total_2024 = df_2024['New_cases'].values[:min_days].sum()  # Corrigido para usar min_days
total_2025 = df_2025_comparison['New_cases'].values[:min_days].sum()  # Corrigido para usar min_days
difference = total_2025 - total_2024
percent_diff = (difference / total_2024) * 100 if total_2024 != 0 else 0  # Adicionada verificação para divisão por zero

stats_text = (f"Comparativo até dia {current_day}:\n"
              f"2024: {total_2024/1000:.1f}k casos\n"
              f"2025: {total_2025/1000:.1f}k casos\n"
              f"Diferença: {difference/1000:+.1f}k ({percent_diff:+.1f}%)")

plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

# Configurações finais
plt.title(f"Comparativo Anual de Casos COVID-19 (Média Móvel 7 dias)\nBrasil - {current_year-1} vs {current_year}", 
          pad=20, fontsize=14, fontweight='bold')
plt.ylabel("Casos diários (MM7)", labelpad=10)
plt.xlabel("Dia do ano", labelpad=10)
plt.legend(handles=[line_2024, line_2025, current_line], loc='upper left')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(img_dir / "comparativo_2024_2025.png", 
           bbox_inches='tight', dpi=300, transparent=True)
plt.close()

# 5. Gráfico comparativo de mortes - VERSÃO CORRIGIDA
print("Gerando gráfico comparativo de óbitos melhorado...")
plt.figure(figsize=(16, 8))

# Calcular médias móveis se ainda não existirem
if 'MM7_deaths' not in df_2024.columns:
    df_2024['MM7_deaths'] = df_2024['New_deaths'].rolling(7, min_periods=1).mean()
if 'MM7_deaths' not in df_2025_comparison.columns:
    df_2025_comparison['MM7_deaths'] = df_2025_comparison['New_deaths'].rolling(7, min_periods=1).mean()

# Garantir que estamos comparando os mesmos dias do ano
min_days = min(len(df_2024), len(df_2025_comparison))
days_of_year = range(1, min_days + 1)

# Extrair os valores para comparação
mm7_deaths_2024 = df_2024['MM7_deaths'].values[:min_days]
mm7_deaths_2025 = df_2025_comparison['MM7_deaths'].values[:min_days]

# Área entre as curvas
plt.fill_between(
    days_of_year,
    mm7_deaths_2024,
    mm7_deaths_2025,
    where=(mm7_deaths_2025 > mm7_deaths_2024),
    facecolor='red', alpha=0.2, interpolate=True, label='2025 > 2024'
)

plt.fill_between(
    days_of_year,
    mm7_deaths_2024,
    mm7_deaths_2025,
    where=(mm7_deaths_2025 < mm7_deaths_2024),
    facecolor='green', alpha=0.2, interpolate=True, label='2025 < 2024'
)

# Linhas principais
line_2024_deaths, = plt.plot(
    days_of_year,
    mm7_deaths_2024,
    label='2024', color='#1f77b4', linewidth=3, alpha=0.7
)

line_2025_deaths, = plt.plot(
    days_of_year,
    mm7_deaths_2025,
    label='2025', color='#d62728', linewidth=3
)

# Marcadores mensais (reutilizando do gráfico anterior)
for day, name in zip(month_days, month_names):
    plt.axvline(x=day, color='gray', linestyle=':', alpha=0.3)
    plt.text(day+2, plt.ylim()[1]*0.95, name, color='gray')

# Linha de hoje
current_line_deaths = plt.axvline(x=current_day, color='black', linestyle='--', alpha=0.7)
plt.text(current_day+2, plt.ylim()[1]*0.85, f'Hoje ({current_day}º dia)', 
         color='black', bbox=dict(facecolor='white', alpha=0.8))

# Estatísticas
total_2024_deaths = df_2024['New_deaths'].values[:min_days].sum()  # Corrigido para usar min_days
total_2025_deaths = df_2025_comparison['New_deaths'].values[:min_days].sum()  # Corrigido para usar min_days
death_diff = total_2025_deaths - total_2024_deaths
death_pct_diff = (death_diff / total_2024_deaths) * 100 if total_2024_deaths != 0 else 0  # Adicionada verificação para divisão por zero

death_stats = (f"Comparativo até dia {current_day}:\n"
               f"2024: {total_2024_deaths:.0f} óbitos\n"
               f"2025: {total_2025_deaths:.0f} óbitos\n"
               f"Diferença: {death_diff:+.0f} ({death_pct_diff:+.1f}%)")

plt.text(0.02, 0.98, death_stats, transform=plt.gca().transAxes,
         verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

# Configurações finais
plt.title(f"Comparativo Anual de Óbitos COVID-19 (Média Móvel 7 dias)\nBrasil - {current_year-1} vs {current_year}", 
          pad=20, fontsize=14, fontweight='bold')
plt.ylabel("Óbitos diários (MM7)", labelpad=10)
plt.xlabel("Dia do ano", labelpad=10)
plt.legend(handles=[line_2024_deaths, line_2025_deaths, current_line_deaths], loc='upper left')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(img_dir / "comparativo_mortes_2024_2025.png", 
           bbox_inches='tight', dpi=300, transparent=True)
plt.close()

# Salvar dados da última atualização
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

import json
with open(img_dir / "stats.json", "w") as f:
    json.dump(stats, f)

print("Processo concluído com sucesso!")
