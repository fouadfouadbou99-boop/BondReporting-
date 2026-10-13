def build_commentary(metrics):

    commentaire = f"""
Le portefeuille a réalisé une performance annualisée
de {metrics['performance']:.2%}
contre {metrics['benchmark']:.2%}
pour son indice de référence.

L'écart de performance ressort à
{metrics['excess_return']:.2%}.

Le rendement actuariel moyen du portefeuille
s'établit à {metrics['ytm']:.2f}%.

La duration modifiée est de
{metrics['duration_mod']:.2f}.

Le ratio de Sharpe atteint
{metrics['sharpe']:.2f}
et le ratio de Sortino
{metrics['sortino']:.2f}.

La VaR 95% ressort à
{metrics['var95']:.2%}
contre une CVaR de
{metrics['cvar95']:.2%}.

L'appréciation globale est
{metrics['rating']}
avec un score de
{metrics['score']}/100.
"""

    return commentaire
