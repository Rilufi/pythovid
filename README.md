# COVID-19 no Brasil (2025)

Este repositório coleta automaticamente os dados diários de COVID-19 no Brasil a partir da base de dados da **OMS (Organização Mundial da Saúde)** e gera dois gráficos atualizados:

- 📈 Casos diários em 2025  
- 💀 Mortes diárias em 2025  

Os gráficos são salvos na pasta `imgs/` e atualizados todos os dias automaticamente via [GitHub Actions](https://docs.github.com/actions).

## 🔄 Atualização automática

O workflow `update.yml` é executado todos os dias às 7h UTC para:

1. Baixar os dados mais recentes da OMS.
2. Filtrar os dados do Brasil em 2025.
3. Gerar os gráficos atualizados.

## 🗂 Estrutura

```
.
├── data/                       # Dados CSV baixados da OMS
├── imgs/                       # Gráficos gerados
├── main.py                     # Script de análise e geração de gráficos
├── .github/
│   └── workflows/
│       └── update.yml          # Workflow que roda automaticamente
├── README.md
```

## ▶️ Executando localmente

Para executar manualmente:

```bash
pip install -r requirements.txt
python main.py
```

## 📊 Fonte dos dados

[OMS COVID-19 Global Data](https://data.who.int/dashboards/covid19/who-covid-19-global-data.csv)
