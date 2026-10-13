import numpy as np

def annual_performance(series):
    return (
        series.iloc[-1] /
        series.iloc[0]
        - 1
    )

def excess_return(
        pf_return,
        bm_return):

    return pf_return - bm_return

def tracking_error(
        pf_returns,
        bm_returns):

    diff = (
        pf_returns
        - bm_returns
    )

    return diff.std() * np.sqrt(12)

def information_ratio(
        excess,
        tracking):

    if tracking == 0:
        return 0

    return excess / tracking
