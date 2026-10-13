def attribution_summary(df):

    return {

        "Portage":
        df["Effet_Portage"].sum(),

        "Taux":
        df["Effet_Taux"].sum(),

        "Credit":
        df["Effet_Credit"].sum()

    }
