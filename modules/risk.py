import numpy as np
from scipy.stats import norm


def volatility(returns):

    return (
        returns.std()
        * np.sqrt(12)
    )


def sharpe_ratio(
        performance,
        volatility_value,
        rf):

    if volatility_value <= 0:
        return 0

    return (
        performance - rf
    ) / volatility_value


def sortino_ratio(
        performance,
        returns,
        rf):

    downside = returns[
        returns < 0
    ]

    if len(downside) == 0:
        return 0

    downside_vol = (
        downside.std()
        * np.sqrt(12)
    )

    if downside_vol == 0:
        return 0

    return (
        performance - rf
    ) / downside_vol


def max_drawdown(returns):

    cumulative = (
        1 + returns
    ).cumprod()

    peak = cumulative.cummax()

    dd = (
        cumulative
        /
        peak
        - 1
    )

    return dd.min()


def historical_var(
        returns,
        confidence=95):

    percentile = (
        100 - confidence
    )

    return np.percentile(
        returns,
        percentile
    )


def cvar(
        returns,
        confidence=95):

    var = historical_var(
        returns,
        confidence
    )

    return returns[
        returns <= var
    ].mean()


def parametric_var(
        returns,
        confidence=95):

    z = norm.ppf(
        1 - confidence / 100
    )

    mu = returns.mean()

    sigma = returns.std()

    return mu + z * sigma
