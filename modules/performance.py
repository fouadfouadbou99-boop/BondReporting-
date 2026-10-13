import numpy as np


def annualized_return(values, dates):

    nb_days = (
        dates.iloc[-1]
        - dates.iloc[0]
    ).days

    if nb_days <= 0:
        return 0

    return (
        (
            values.iloc[-1]
            /
            values.iloc[0]
        ) ** (365 / nb_days)
    ) - 1


def excess_return(
        portfolio_return,
        benchmark_return):

    return (
        portfolio_return
        - benchmark_return
    )


def tracking_error(
        pf_returns,
        bm_returns):

    diff = (
        pf_returns
        - bm_returns
    )

    return (
        diff.std()
        * np.sqrt(12)
    )


def information_ratio(
        excess,
        tracking):

    if tracking == 0:
        return 0

    return excess / tracking
