def calculate_score(metrics):

    score = 0

    if metrics["excess_return"] > 0:
        score += 15

    if metrics["sharpe"] > 1:
        score += 10

    if metrics["sortino"] > 1:
        score += 10

    if metrics["information_ratio"] > 0.5:
        score += 10

    if metrics["max_drawdown"] > -0.05:
        score += 10

    if metrics["issuer_concentration"] < 15:
        score += 10

    if metrics["duration_mod"] < 8:
        score += 10

    if metrics["var95"] > -0.02:
        score += 10

    if metrics["rating_diversification"] >= 4:
        score += 10

    return min(score, 100)


def get_rating(score):

    if score >= 85:
        return "🟢 Excellent"

    elif score >= 70:
        return "🟢 Bon"

    elif score >= 55:
        return "🟡 Correct"

    elif score >= 40:
        return "🟠 Moyen"

    return "🔴 Faible"
