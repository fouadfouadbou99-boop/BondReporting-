def score_obligataire(metrics):

    score = 0

    if metrics["excess"] > 0:
        score += 20

    if metrics["sharpe"] > 1:
        score += 10

    if metrics["sortino"] > 1:
        score += 10

    if metrics["ir"] > 0.5:
        score += 10

    if metrics["drawdown"] > -0.05:
        score += 10

    if metrics["volatility_pf"] <
       metrics["volatility_bm"]:
        score += 10

    if metrics["duration"] < 8:
        score += 10

    if metrics["dv01"] > 0:
        score += 10

    if metrics["var95"] > -0.03:
        score += 10

    return min(score,100)

def rating(score):

    if score >= 85:
        return "🟢 Excellent"

    if score >= 70:
        return "🟢 Bon"

    if score >= 55:
        return "🟡 Correct"

    if score >= 40:
        return "🟠 Moyen"

    return "🔴 Faible"
