import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Reporting Obligataire",
    layout="wide"
)

st.title("📈 Reporting Portefeuille Obligataire")

uploaded_file = st.file_uploader(
    "Charger le fichier Excel",
    type=["xlsx"]
)

if uploaded_file:

    perf = pd.read_excel(
        uploaded_file,
        sheet_name="Performance"
    )

    portefeuille = pd.read_excel(
        uploaded_file,
        sheet_name="Portefeuille"
    )

    perf["Date"] = pd.to_datetime(perf["Date"])

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
    ) - 1

    annual_return_bm = (
        perf["VL_Benchmark"].iloc[-1]
        /
        perf["VL_Benchmark"].iloc[0]
    ) - 1

    excess_return = (
        annual_return_pf
        -
        annual_return_bm
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
        annual_return_pf
        /
        volatility_pf
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
        annual_return_pf
        /
        downside_std
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
        /
        tracking_error
        if tracking_error > 0
        else 0
    )

    cumulative = (
        1 + perf["Return_PF"]
    ).cumprod()

    running_max = cumulative.cummax()

    drawdown = (
        cumulative
        /
        running_max
        - 1
    )

    max_drawdown = drawdown.min()

    duration = portefeuille[
        "Duration"
    ].mean()

    ytm = portefeuille[
        "YTM"
    ].mean()

    # SCORE

    score = 0

    if excess_return > 0:
        score += 20

    if sharpe > 1:
        score += 15

    if sortino > 1:
        score += 15

    if volatility_pf < volatility_bm:
        score += 15

    if max_drawdown > -0.05:
        score += 20

    if information_ratio > 0.5:
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

    col1,col2,col3,col4,col5 = st.columns(5)

    col1.metric(
        "Performance PF",
        f"{annual_return_pf:.2%}"
    )

    col2.metric(
        "Performance Indice",
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

    st.subheader(
        "Score Obligataire"
    )

    st.metric(
        rating,
        f"{score}/100"
    )

    fig = px.line(
        perf,
        x="Date",
        y=[
            "VL_Portefeuille",
            "VL_Benchmark"
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Répartition des Notations"
    )

    fig2 = px.pie(
        portefeuille,
        names="Notation",
        values="Poids"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.subheader(
        "Répartition des Maturités"
    )

    fig3 = px.histogram(
        portefeuille,
        x="Maturite",
        y="Poids"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    commentaire = f"""
Le portefeuille affiche une performance de
{annual_return_pf:.2%}
contre
{annual_return_bm:.2%}
pour son indice de référence.

La surperformance ressort à
{excess_return:.2%}.

La duration moyenne du portefeuille est de
{duration:.2f} années et son rendement
actuariel moyen atteint
{ytm:.2f}%.

Le ratio de Sharpe ressort à
{sharpe:.2f}
et le ratio de Sortino à
{sortino:.2f}.

Le drawdown maximal observé est de
{max_drawdown:.2%}.

L'analyse globale conduit à une notation
{rating}.
"""

    st.subheader(
        "Commentaire Automatique"
    )

    st.write(commentaire)
