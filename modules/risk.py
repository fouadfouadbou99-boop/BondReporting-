import numpy as np

def volatility(returns):

    return (
        returns.std()
        * np.sqrt(12)
    )

def sharpe(
        return_pf,
        vol,
        rf=0.02):

    if vol == 0:
        return 0

    return (
        return_pf - rf
    ) / vol

def sortino(
        return_pf,
        returns,
        rf=0.02):

    downside = returns[
        returns < 0
    ]

    if len(downside) == 0:
        return 0

    downside_vol = (
        downside.std()
        * np.sqrt(12)
    )

    return (
        return_pf - rf
    ) / downside_vol

def max_drawdown(returns):

    cumulative = (
        1 + returns
    ).cumprod()

    running_max = (
        cumulative.cummax()
    )

    dd = (
        cumulative
        /
        running_max
        - 1
    )

    return dd.min()

def var_95(returns):

    return np.percentile(
        returns,
        5
    )

def cvar_95(returns):

    var = np.percentile(
        returns,
        5
    )

    return returns[
        returns <= var
    ].mean()

def dv01(df):

    return (
        df["Valeur_Marchande"]
        * df["Duration"]
        * 0.0001
    ).sum()
