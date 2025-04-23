import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_time_distribution(times, athlete_time=None):
    """ Affiche une distribution KDE des temps de course avec une séparation rouge/bleue uniquement si un athlète est sélectionné."""
    if times.empty:
        return None

    times_in_seconds = times.dropna().to_numpy()
    
    if len(times_in_seconds) < 2:
        # Pas assez de données pour une vraie densité, on retourne None
        return None

    kde = stats.gaussian_kde(times_in_seconds, bw_method=0.2)
    x_vals = np.linspace(times_in_seconds.min(), times_in_seconds.max(), 200)
    y_vals = kde(x_vals)

    fig = go.Figure()
    
    if athlete_time is not None:
        # On coupe le graphique en deux
        split_idx = np.searchsorted(x_vals, athlete_time)
        fig.add_trace(go.Scatter(x=x_vals[:split_idx], y=y_vals[:split_idx], fill='tozeroy', mode='lines', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=x_vals[split_idx:], y=y_vals[split_idx:], fill='tozeroy', mode='lines', line=dict(color='blue')))
    else:
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, fill='tozeroy', mode='lines', line=dict(color='blue'), name='Densité'))

    fig.update_layout(
        showlegend=False, 
        title="Densité des temps de course",
        xaxis_title="Temps (secondes)",
        yaxis_title="Densité",
        xaxis=dict(
            tickmode='array',
            tickvals=list(np.linspace(times_in_seconds.min(), times_in_seconds.max(), 10)),
            ticktext=[str(pd.to_timedelta(int(t), unit='s'))[-8:] for t in np.linspace(times_in_seconds.min(), times_in_seconds.max(), 10)]
        ),
        yaxis=dict(showticklabels=False),
        template="plotly_white"
    )
    return fig

def donut_categorie_chart(data):
    ''' Affiche un donut chart avec la répartition des catégories réprésentées au sein de la course'''
    counts = data['cat'].value_counts()

    # On affiche que le top 5 des catégories les plus représentées
    top5 = counts.nlargest(5)
    others = pd.Series(counts.iloc[5:].sum(), index=["Autres"])

    counts_filtered = pd.concat([top5, others])

    colors = [
        "rgba(8, 9, 139, 1)",
        "rgba(18, 24, 170, 0.9)",
        "rgba(28, 40, 190, 0.8)",
        "rgba(48, 60, 210, 0.7)",
        "rgba(68, 80, 230, 0.6)",
        "rgba(8, 9, 200, 0.5)"
    ]

    fig = go.Figure(go.Pie(
        labels=counts_filtered.index,
        values=counts_filtered,
        hole=0.6,
        marker=dict(colors=colors[:len(counts_filtered)]),
        textinfo='label',
        hoverinfo='label+percent',
        insidetextorientation='radial',
        showlegend=False,
        textfont=dict(color="white")
    ))

    fig.update_layout(
        template="plotly_dark",
        margin=dict(t=0, b=0, l=0, r=0),
        height=250
    )

    return fig