import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from modules.performance import (
    annualized_return,
    excess_return,
    tracking_error,
    information_ratio
)

from modules.risk import (
    volatility,
    sharpe_ratio,
    sortino_ratio,
    max_drawdown,
    historical_var,
    cvar,
    parametric_var
)

from modules.scoring import (
    calculate_score,
    get_rating
)

from modules.alm import (
    build_alm_table
)

from modules.attribution import (
    attribution_summary
)

from modules.commentary import (
    build_commentary
)

from modules.exporters import (
    export_excel,
    export_word,
    export_pdf
)

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Reporting Obligataire",
    page_icon="📈",
    layout="wide"
)

# ==================================================
# HEADER
# ==================================================

st.title("📈 Reporting Obligataire")

st.markdown(
"""
Application de suivi des performances,
des risques et de l'allocation d'un
portefeuille obligataire.
"""
)

# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header("Paramètres")

rf_rate = st.sidebar.number_input(
    "Taux sans risque %",
    value=2.5
) / 100

horizon = st.sidebar.selectbox(
    "Horizon",
    [
        "Depuis origine",
        "YTD",
        "1 An",
        "3 Ans",
        "5 Ans"
    ]
)

# ==================================================
# UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "Charger le fichier Excel",
    type=["xlsx"]
)

if uploaded_file is None:

    st.info(
        """
        Le classeur doit contenir :

        - Performance
        - Portefeuille
        - Attribution
        - Courbe_Taux
        """
    )

    st.stop()

# ==================================================
# LECTURE
# ==================================================

perf = pd.read_excel(
    uploaded_file,
    sheet_name="Performance"
)

portefeuille = pd.read_excel(
    uploaded_file,
    sheet_name="Portefeuille"
)

try:

    attribution_df = pd.read_excel(
        uploaded_file,
        sheet_name="Attribution"
    )

except:

    attribution_df = None

try:

    courbe_df = pd.read_excel(
        uploaded_file,
        sheet_name="Courbe_Taux"
    )

except:

    courbe_df = None

# ==================================================
# CONTROLES
# ==================================================

required_columns = [
    "Duration",
    "Duration_Modifiee",
    "Poids",
    "YTM",
    "Valeur_Marchande",
    "Notation",
    "Emetteur",
    "Secteur",
    "Maturite"
]

missing = [
    c
    for c in required_columns
    if c not in portefeuille.columns
]

if missing:

    st.error(
        f"Colonnes manquantes : {missing}"
    )

    st.stop()

# ==================================================
# DATES
# ==================================================

perf["Date"] = pd.to_datetime(
    perf["Date"]
)

date_max = perf["Date"].max()

if horizon == "YTD":

    perf = perf[
        perf["Date"]
        >= pd.Timestamp(
            date_max.year,
            1,
            1
        )
    ]

elif horizon == "1 An":

    perf = perf[
        perf["Date"]
        >= date_max -
        pd.DateOffset(years=1)
    ]

elif horizon == "3 Ans":

    perf = perf[
        perf["Date"]
        >= date_max -
        pd.DateOffset(years=3)
    ]

elif horizon == "5 Ans":

    perf = perf[
        perf["Date"]
        >= date_max -
        pd.DateOffset(years=5)
    ]

# ==================================================
# RETURNS
# ==================================================

perf["Return_PF"] = (
    perf["VL_Portefeuille"]
    .pct_change()
)

perf["Return_BM"] = (
    perf["VL_Benchmark"]
    .pct_change()
)

perf.dropna(inplace=True)

# ==================================================
# PERFORMANCE
# ==================================================

performance_pf = annualized_return(
    perf["VL_Portefeuille"],
    perf["Date"]
)

performance_bm = annualized_return(
    perf["VL_Benchmark"],
    perf["Date"]
)

excess = excess_return(
    performance_pf,
    performance_bm
)

# ==================================================
# RISK
# ==================================================

vol_pf = volatility(
    perf["Return_PF"]
)

vol_bm = volatility(
    perf["Return_BM"]
)

sharpe = sharpe_ratio(
    performance_pf,
    vol_pf,
    rf_rate
)

sortino = sortino_ratio(
    performance_pf,
    perf["Return_PF"],
    rf_rate
)

te = tracking_error(
    perf["Return_PF"],
    perf["Return_BM"]
)

ir = information_ratio(
    excess,
    te
)

mdd = max_drawdown(
    perf["Return_PF"]
)

var95 = historical_var(
    perf["Return_PF"]
)

cvar95 = cvar(
    perf["Return_PF"]
)

param_var95 = parametric_var(
    perf["Return_PF"]
)

# ==================================================
# PORTFOLIO
# ==================================================

duration = np.average(
    portefeuille["Duration"],
    weights=portefeuille["Poids"]
)

duration_mod = np.average(
    portefeuille["Duration_Modifiee"],
    weights=portefeuille["Poids"]
)

ytm = np.average(
    portefeuille["YTM"],
    weights=portefeuille["Poids"]
)

dv01 = (
    portefeuille["Valeur_Marchande"]
    *
    portefeuille["Duration_Modifiee"]
    *
    0.0001
).sum()

issuer_concentration = (
    portefeuille
    .groupby("Emetteur")["Poids"]
    .sum()
    .max()
)

rating_diversification = (
    portefeuille["Notation"]
    .nunique()
)

# ==================================================
# SCORE
# ==================================================

metrics = {

    "excess_return": excess,
    "sharpe": sharpe,
    "sortino": sortino,
    "information_ratio": ir,
    "max_drawdown": mdd,
    "issuer_concentration": issuer_concentration,
    "duration_mod": duration_mod,
    "var95": var95,
    "rating_diversification":
        rating_diversification
}

score = calculate_score(metrics)

rating = get_rating(score)

# ==================================================
# KPI
# ==================================================

st.subheader("Tableau de Bord")

c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric(
    "Performance",
    f"{performance_pf:.2%}"
)

c2.metric(
    "Benchmark",
    f"{performance_bm:.2%}"
)

c3.metric(
    "Excess Return",
    f"{excess:.2%}"
)

c4.metric(
    "Duration",
    f"{duration:.2f}"
)

c5.metric(
    "YTM",
    f"{ytm:.2f}%"
)

c6.metric(
    "Score",
    f"{score}/100"
)

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "VaR 95%",
    f"{var95:.2%}"
)

c2.metric(
    "CVaR 95%",
    f"{cvar95:.2%}"
)

c3.metric(
    "Dur. Modifiée",
    f"{duration_mod:.2f}"
)

c4.metric(
    "DV01",
    f"{dv01:,.0f}"
)

# ==================================================
# PERFORMANCE CHART
# ==================================================

st.subheader(
    "Evolution Portefeuille vs Benchmark"
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=perf["Date"],
        y=perf["VL_Portefeuille"],
        name="Portefeuille"
    )
)

fig.add_trace(
    go.Scatter(
        x=perf["Date"],
        y=perf["VL_Benchmark"],
        name="Benchmark"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# ALLOCATION
# ==================================================

col1,col2,col3 = st.columns(3)

with col1:

    st.plotly_chart(
        px.pie(
            portefeuille,
            names="Notation",
            values="Poids",
            title="Notation"
        ),
        use_container_width=True
    )

with col2:

    st.plotly_chart(
        px.pie(
            portefeuille,
            names="Secteur",
            values="Poids",
            title="Secteurs"
        ),
        use_container_width=True
    )

with col3:

    st.plotly_chart(
        px.histogram(
            portefeuille,
            x="Maturite",
            y="Poids",
            title="Maturités"
        ),
        use_container_width=True
    )

# ==================================================
# ALM
# ==================================================

st.subheader(
    "Analyse ALM"
)

alm_table = build_alm_table(
    portefeuille
)

st.dataframe(
    alm_table,
    use_container_width=True
)

# ==================================================
# ATTRIBUTION
# ==================================================

if attribution_df is not None:

    st.subheader(
        "Attribution Performance"
    )

    attr = attribution_summary(
        attribution_df
    )

    attr_df = pd.DataFrame({

        "Source":[
            "Portage",
            "Taux",
            "Crédit"
        ],

        "Contribution":[
            attr["Portage"],
            attr["Taux"],
            attr["Credit"]
        ]
    })

    st.plotly_chart(
        px.pie(
            attr_df,
            names="Source",
            values="Contribution"
        ),
        use_container_width=True
    )

# ==================================================
# COURBE TAUX
# ==================================================

if courbe_df is not None:

    st.subheader(
        "Courbe des Taux"
    )

    st.plotly_chart(
        px.line(
            courbe_df,
            x="Maturite",
            y="Taux",
            markers=True
        ),
        use_container_width=True
    )

# ==================================================
# COMMENTAIRE
# ==================================================

comment_metrics = {

    "performance": performance_pf,
    "benchmark": performance_bm,
    "excess_return": excess,
    "ytm": ytm,
    "duration_mod": duration_mod,
    "sharpe": sharpe,
    "sortino": sortino,
    "var95": var95,
    "cvar95": cvar95,
    "score": score,
    "rating": rating
}

commentaire = build_commentary(
    comment_metrics
)

st.subheader(
    "Commentaire de Gestion"
)

st.write(commentaire)

# ==================================================
# EXPORTS
# ==================================================

synthese = pd.DataFrame({

    "Indicateur":[
        "Performance",
        "Benchmark",
        "Excess Return",
        "Sharpe",
        "Sortino",
        "VaR95",
        "CVaR95",
        "Duration",
        "Duration Modifiée",
        "DV01",
        "Score"
    ],

    "Valeur":[
        performance_pf,
        performance_bm,
        excess,
        sharpe,
        sortino,
        var95,
        cvar95,
        duration,
        duration_mod,
        dv01,
        score
    ]
})

st.subheader("Exports")

col1,col2,col3 = st.columns(3)

with col1:

    st.download_button(
        "📊 Export Excel",
        export_excel(
            synthese,
            portefeuille
        ),
        "Reporting.xlsx"
    )

with col2:

    st.download_button(
        "📝 Export Word",
        export_word(
            commentaire
        ),
        "Reporting.docx"
    )

with col3:

    st.download_button(
        "📄 Export PDF",
        export_pdf(
            commentaire
        ),
        "Reporting.pdf"
    )
