import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Reporting Obligataire",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# TITRE
# =====================================================

st.title("📈 Reporting Portefeuille Obligataire")

st.markdown("---")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Paramètres")

horizon = st.sidebar.selectbox(
    "Horizon d'analyse",
    [
        "Depuis origine",
        "YTD",
        "1 An",
        "3 Ans"
    ]
)

rf_rate = st.sidebar.number_input(
    "Taux sans risque (%)",
    value=2.5,
    step=0.1
) / 100

# =====================================================
# IMPORT
# =====================================================

uploaded_file = st.file_uploader(
    "Charger le fichier Excel",
    type=["xlsx"]
)

if uploaded_file:

    # =================================================
    # LECTURE
    # =================================================

    perf = pd.read_excel(
        uploaded_file,
        sheet_name="Performance"
    )

    portefeuille = pd.read_excel(
        uploaded_file,
        sheet_name="Portefeuille"
    )

    perf["Date"] = pd.to_datetime(perf["Date"])

    # =================================================
    # FILTRE HORIZON
    # =================================================

    date_max = perf["Date"].max()

    if horizon == "YTD":

        start_date = pd.Timestamp(
            year=date_max.year,
            month=1,
            day=1
        )

        perf = perf[
            perf["Date"] >= start_date
        ]

    elif horizon == "1 An":

        perf = perf[
            perf["Date"] >=
            date_max - pd.DateOffset(years=1)
        ]

    elif horizon == "3 Ans":

        perf = perf[
            perf["Date"] >=
            date_max - pd.DateOffset(years=3)
        ]

    # =================================================
    # CALCULS
    # =================================================

    perf["Return_PF"] = (
        perf["VL_Portefeuille"]
        .pct_change()
    )

    perf["Return_BM"] = (
        perf["VL_Benchmark"]
        .pct_change()
    )

    perf = perf.dropna()

    annual_return_pf = (
        perf["VL_Portefeuille"].iloc[-1]
        /
        perf["VL_Portefeuille"].iloc[0]
        - 1
    )

    annual_return_bm = (
        perf["VL_Benchmark"].iloc[-1]
        /
        perf["VL_Benchmark"].iloc[0]
        - 1
    )

    excess_return = (
        annual_return_pf
        - annual_return_bm
    )

    volatility_pf = (
        perf["Return_PF"].std()
        * np.sqrt(12)
    )

    volatility_bm = (
        perf["Return_BM"].std()
        * np.sqrt(12)
    )

    sharpe = (
        (annual_return_pf - rf_rate)
        / volatility_pf
        if volatility_pf > 0
        else 0
    )

    downside = perf[
        perf["Return_PF"] < 0
    ]["Return_PF"]

    downside_std = (
        downside.std()
        * np.sqrt(12)
    )

    sortino = (
        (annual_return_pf - rf_rate)
        / downside_std
        if downside_std > 0
        else 0
    )

    tracking_error = (
        (perf["Return_PF"]
         - perf["Return_BM"])
         .std()
         * np.sqrt(12)
    )

    information_ratio = (
        excess_return
        / tracking_error
        if tracking_error > 0
        else 0
    )

    cumulative = (
        1 + perf["Return_PF"]
    ).cumprod()

    rolling_max = cumulative.cummax()

    drawdown = (
        cumulative
        /
        rolling_max
        - 1
    )

    max_drawdown = drawdown.min()

    # =================================================
    # PORTFOLIO METRICS
    # =================================================

    duration = np.average(
        portefeuille["Duration"],
        weights=portefeuille["Poids"]
    )

    ytm = np.average(
        portefeuille["YTM"],
        weights=portefeuille["Poids"]
    )

    rating_diversification = (
        portefeuille["Notation"]
        .nunique()
    )

    issuer_concentration = (
        portefeuille.groupby(
            "Emetteur"
        )["Poids"]
        .sum()
        .max()
    )

    # =================================================
    # SCORE
    # =================================================

    score = 0

    if excess_return > 0:
        score += 25

    if sharpe > 1:
        score += 15

    if sortino > 1:
        score += 15

    if information_ratio > 0.50:
        score += 15

    if max_drawdown > -0.05:
        score += 15

    if issuer_concentration < 15:
        score += 15

    score = min(score,100)

    if score >= 85:
        rating = "🟢 Excellent"

    elif score >= 70:
        rating = "🟢 Bon"

    elif score >= 55:
        rating = "🟡 Correct"

    elif score >= 40:
        rating = "🟠 Moyen"

    else:
        rating = "🔴 Faible"

    # =================================================
    # KPIs
    # =================================================

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric(
        "Performance",
        f"{annual_return_pf:.2%}"
    )

    col2.metric(
        "Benchmark",
        f"{annual_return_bm:.2%}"
    )

    col3.metric(
        "Excess Return",
        f"{excess_return:.2%}"
    )

    col4.metric(
        "Duration",
        f"{duration:.2f}"
    )

    col5.metric(
        "YTM",
        f"{ytm:.2f}%"
    )

    col6.metric(
        "Score",
        f"{score}/100"
    )

    st.success(
        f"Appréciation : {rating}"
    )

    # =================================================
    # EVOLUTION DES VL
    # =================================================

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

    # =================================================
    # NOTATION
    # =================================================

    col1,col2 = st.columns(2)

    with col1:

        fig_rating = px.pie(
            portefeuille,
            names="Notation",
            values="Poids",
            title="Répartition par notation"
        )

        st.plotly_chart(
            fig_rating,
            use_container_width=True
        )

    with col2:

        fig_maturity = px.histogram(
            portefeuille,
            x="Maturite",
            y="Poids",
            title="Répartition des maturités"
        )

        st.plotly_chart(
            fig_maturity,
            use_container_width=True
        )

    # =================================================
    # TOP EMETTEURS
    # =================================================

    st.subheader(
        "Top Expositions"
    )

    top_issuers = (
        portefeuille
        .groupby("Emetteur")
        ["Poids"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_issuers
    )

    # =================================================
    # RISQUE
    # =================================================

    st.subheader(
        "Analyse Risque"
    )

    risque_df = pd.DataFrame({

        "Indicateur":[
            "Volatilité",
            "Tracking Error",
            "Sharpe",
            "Sortino",
            "Max Drawdown"
        ],

        "Valeur":[
            round(volatility_pf,4),
            round(tracking_error,4),
            round(sharpe,2),
            round(sortino,2),
            round(max_drawdown,4)
        ]
    })

    st.dataframe(
        risque_df,
        use_container_width=True
    )

    # =================================================
    # COMMENTAIRE AUTO
    # =================================================

    st.subheader(
        "Commentaire de Gestion"
    )

    commentaire = f"""
Le portefeuille affiche une performance de {annual_return_pf:.2%},
contre {annual_return_bm:.2%} pour son indice de référence,
soit un écart de performance de {excess_return:.2%}.

Le rendement actuariel moyen du portefeuille ressort à {ytm:.2f}%
pour une duration moyenne de {duration:.2f} années.

Du point de vue du risque, la volatilité annualisée atteint
{volatility_pf:.2%}, tandis que le ratio de Sharpe s'établit à
{sharpe:.2f}. Le ratio de Sortino ressort à {sortino:.2f},
témoignant du niveau de rémunération du risque baissier.

Le drawdown maximal observé sur la période atteint
{max_drawdown:.2%}.

L'analyse globale conduit à une notation {rating},
avec un score de {score}/100.
"""

    st.write(commentaire)

    # =================================================
    # EXPORT
    # =================================================

    synthese = pd.DataFrame({
        "Indicateur":[
            "Performance",
            "Benchmark",
            "Excess Return",
            "Volatilité",
            "Sharpe",
            "Sortino",
            "Duration",
            "YTM",
            "Score"
        ],
        "Valeur":[
            annual_return_pf,
            annual_return_bm,
            excess_return,
            volatility_pf,
            sharpe,
            sortino,
            duration,
            ytm,
            score
        ]
    })

    csv = synthese.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Télécharger la synthèse",
        csv,
        file_name="Reporting_Obligataire.csv",
        mime="text/csv"
    )
