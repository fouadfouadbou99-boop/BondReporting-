import pandas as pd


def maturity_bucket(maturity):

    if maturity <= 1:
        return "0-1 an"

    elif maturity <= 3:
        return "1-3 ans"

    elif maturity <= 5:
        return "3-5 ans"

    elif maturity <= 10:
        return "5-10 ans"

    return ">10 ans"


def build_alm_table(df):

    tmp = df.copy()

    tmp["Strate"] = (
        tmp["Maturite"]
        .apply(maturity_bucket)
    )

    result = (
        tmp.groupby("Strate")
        .agg({
            "Poids": "sum",
            "Duration": "mean",
            "YTM": "mean"
        })
        .reset_index()
    )

    return result
