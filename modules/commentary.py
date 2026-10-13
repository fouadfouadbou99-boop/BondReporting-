def generate_commentary(metrics):

    return f"""
Le portefeuille a enregistré une
performance de
{metrics['perf_pf']:.2%}
contre
{metrics['perf_bm']:.2%}
pour l'indice.

L'écart de performance ressort à
{metrics['excess']:.2%}.

Le rendement actuariel moyen du
portefeuille atteint
{metrics['ytm']:.2f}%.

La duration moyenne ressort à
{metrics['duration']:.2f} années.

Le ratio de Sharpe atteint
{metrics['sharpe']:.2f}
et le ratio de Sortino
{metrics['sortino']:.2f}.

Le drawdown maximal observé
est de
{metrics['drawdown']:.2%}.

La VaR à 95 %
ressort à
{metrics['var95']:.2%}
et la CVaR à
{metrics['cvar95']:.2%}.

L'analyse globale conduit à une
notation
{metrics['rating']}
avec un score de
{metrics['score']}/100.
"""
