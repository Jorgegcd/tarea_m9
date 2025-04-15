from dash import callback, Output, Input, State,  no_update
from data.db_connection import get_matches_data, get_teams_data
import pandas as pd
import plotly.graph_objects as go
from utils.cache_config import cache
import os
import plotly.express as px

# Copiamos la función de generar el donut de equipo para insertarlo en el pdf
@cache.memoize(timeout=600)
def generar_donut_equipo_figure(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try: # manejo de errores
        df = get_matches_data() # Cargamos la función que otorga los datos de los partidos
    except Exception as e:
        return go.Figure()
    
    df["date"] = pd.to_datetime(df["date"])

    # Indicamos los filtros de temporada, equipo y victorias/derrotas
    df_filtered = df[
        (df["season"] == season) &
        (df["team_id"] == team_id) &
        (df["w/l"].isin(wl_filter))
    ]

    # Indicamos los filtros de fecha
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered["date"] >= pd.to_datetime(start_date)) &
            (df_filtered["date"] <= pd.to_datetime(end_date))
        ]

    if df_filtered.empty:
        return go.Figure()

    # Hacemos el cálculo de posesiones
    fg2a = df_filtered["fg2a"].sum()
    fg3a = df_filtered["fg3a"].sum()
    fta = df_filtered["fta"].sum()
    to = df_filtered["to"].sum()
    ft_ponderados = 0.44 * fta

    total = fg2a + fg3a + ft_ponderados + to
    
    if total == 0:
        return go.Figure()

    # Indicamos los valores y etiquetas del donut
    labels = ["Tiros 2", "Tiros 3", "T. Libres", "Pérdidas"]
    values = [fg2a, fg3a, ft_ponderados, to]

    # Generamos el donut
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        textinfo="percent+label",
        marker=dict(colors=["steelblue", "cyan", "navy", "lightskyblue"]) # Introducimos gama de colores azul
    )])

    fig.update_layout(
        title=None,
        height=500,
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
        uirevision="static"
    )

    return fig

# Copiamos la función de generar el donut de las posesiones de los rivales para insertarlo en el pdf
@cache.memoize(timeout=600)
def generar_donut_rivales_figure(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try: # manejo de errores
        df = get_matches_data() # Cargamos la función que otorga los datos de los partidos
    except Exception as e:
        return go.Figure()
    
    df["date"] = pd.to_datetime(df["date"])

    # Indicamos los filtros de temporada, equipo y victorias/derrotas
    df_filtered = df[
        (df["season"] == season) &
        (df["team_id"] == team_id) &
        (df["w/l"].isin(wl_filter))
    ]

    # Indicamos los filtros de fecha
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered["date"] >= pd.to_datetime(start_date)) &
            (df_filtered["date"] <= pd.to_datetime(end_date))
        ]

    if df_filtered.empty:
        return go.Figure()

    # Hacemos el cálculo de posesiones de los rivales
    fg2a_opp = df_filtered["fg2a_opp"].sum()
    fg3a_opp = df_filtered["fg3a_opp"].sum()
    fta_opp = df_filtered["fta_opp"].sum()
    to_opp = df_filtered["to_opp"].sum()
    ft_ponderados = 0.44 * fta_opp

    total = fg2a_opp + fg3a_opp + ft_ponderados + to_opp
    if total == 0:
        return go.Figure()

    # Indicamos los valores y etiquetas del donut
    labels = ["Tiros 2", "Tiros 3", "T. Libres", "Pérdidas"]
    values = [fg2a_opp, fg3a_opp, ft_ponderados, to_opp]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        textinfo="percent+label",
        marker=dict(colors=["tomato", "darkred", "lightcoral", "red"]) # Introducimos gama de colores azul
    )])

    fig.update_layout(
        title=None,
        height= 500,
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40), 
        showlegend=False,
        uirevision="static"
    )

    return fig

# Copiamos la función de generar el radar de estadísticas avanzadas para insertarlo en el pdf
@cache.memoize(timeout=600)
def generar_radar_figure(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try: # manejo de errores
        df = get_matches_data() # Cargamos la función que otorga los datos de los partidos
    except Exception as e:
        return go.Figure()
    
    df["date"] = pd.to_datetime(df["date"])

    # Filtramos por temporada
    df_season = df[df["season"] == season]

    # Filtramos por equipo seleccionado y rivales
    df_filtered = df_season[
        (df_season["team_id"] == team_id) &
        (df_season["w/l"].isin(wl_filter))
    ]

    # Indicamos los filtros de fecha
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered["date"] >= pd.to_datetime(start_date)) &
            (df_filtered["date"] <= pd.to_datetime(end_date))
        ]

    if df_filtered.empty:
        return go.Figure()

    # Generamos función de las métricas que vamos a calcular
    def calcular_metricas(df, is_opp=False):
        prefix = "_opp" if is_opp else ""
        return {
            "eFG%": ((df[f"fgm{prefix}"].sum() + 0.5 * df[f"fg3m{prefix}"].sum()) / df[f"fga{prefix}"].sum()) * 100,
            "TS%": (df[f"pts{prefix}"].sum() / (2 * (df[f"fga{prefix}"].sum() + 0.44 * df[f"fta{prefix}"].sum()))) * 100,
            "%R.Of": (df[f"or{prefix}"].sum() / (df[f"or{prefix}"].sum() + df[f"dr{'' if is_opp else '_opp'}"].sum())) * 100,
            "%R.Def": (df[f"dr{prefix}"].sum() / (df[f"dr{prefix}"].sum() + df[f"or{'' if is_opp else '_opp'}"].sum())) * 100,
            "%Robo": (df[f"st{prefix}"].sum() / (df[f"fga{prefix}"].sum() + 0.44 * df[f"fta{prefix}"].sum() + df[f"to{prefix}"].sum())) * 100,
            "%Pérd": (df[f"to{prefix}"].sum() / (df[f"fga{prefix}"].sum() + 0.44 * df[f"fta{prefix}"].sum() + df[f"to{prefix}"].sum())) * 100,
            "%Tap": (df[f"blk{prefix}"].sum() / df[f"fga{'' if is_opp else '_opp'}"].sum()) * 100
        }
    
    # Indicamos las métricas a mostrar en el radar por equipo y rival
    equipo = calcular_metricas(df_filtered, is_opp=False)
    rival = calcular_metricas(df_filtered, is_opp=True)

    # Hacemos normalización por métrica usando toda la temporada
    equipos_totales = df_season["team_id"].unique()
    normalizadores = {k: [] for k in equipo.keys()}

    for eq in equipos_totales:
        df_eq = df_season[df_season["team_id"] == eq]
        valores = calcular_metricas(df_eq)
        for k in valores:
            normalizadores[k].append(valores[k])

    team_normalized = []
    rival_normalized = []

    # Hacemos función de normalización
    def normaliza(val, lista, invertir=False):
        min_v, max_v = min(lista), max(lista)
        if max_v - min_v == 0:
            return 0.5
        norm = (val - min_v) / (max_v - min_v)
        return 1 - norm if invertir else norm

    for key in equipo:
        invertir = key == "%Pérd"
        team_normalized.append(normaliza(equipo[key], normalizadores[key], invertir))
        rival_normalized.append(normaliza(rival[key], normalizadores[key], invertir))

    # Generamos el Radar chart
    fig = go.Figure()

    teams = get_teams_data() # Cargamos la función que otorga los datos de los partidos
    nombre_equipo_row = teams[teams["team_id"] == team_id] # Sacamos el id del equipo
    nombre_equipo_str = nombre_equipo_row["team_name"].values[0] if not nombre_equipo_row.empty else f"Equipo {team_id}" # Sacamos el nombre en base del id

    metricas = list(equipo.keys())

    # Generamos radar del equipo
    fig.add_trace(go.Scatterpolar(
        r=team_normalized + [team_normalized[0]],
        theta=metricas + [metricas[0]],
        fill='toself',
        name='Equipo',
        line=dict(color='steelblue'),
        mode='lines+markers',
        text=[f"{equipo[k]:.1f}%" for k in equipo] + [f"{equipo[metricas[0]]:.1f}%"],
        textposition='top center',
        hovertemplate=f"<b>{nombre_equipo_str}</b><br>Métrica: %{{theta}}<br>Valor: %{{text}}<extra></extra>"
    ))

    # Generamos radar de los rivales
    fig.add_trace(go.Scatterpolar(
        r=rival_normalized + [rival_normalized[0]],
        theta=metricas + [metricas[0]],
        fill='toself',
        name='Rival',
        line=dict(color='tomato'),
        mode='lines+markers',
        text=[f"{rival[k]:.1f}%" for k in rival] + [f"{rival[metricas[0]]:.1f}%"],
        textposition='top center',
        hovertemplate=f"<b>Rivales de: {nombre_equipo_str}</b><br>Métrica: %{{theta}}<br>Valor: %{{text}}<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False)),
        showlegend=True,
        height=500,
        margin=dict(t=40, b=0, l=0, r=0),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.2)
    )

    return fig

# Copiamos la función de la evolución temporal del equipo a lo largo de la temporada
@cache.memoize(timeout=600)
def grafica_temporal(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try: # manejo de errores
        df = get_matches_data() # Cargamos la función que otorga los datos de los partidos
    except Exception as e:
        return go.Figure()
    
    try: # manejo de errores
        teams = get_teams_data() # Cargamos la función para obtener los datos de los equipos
    except Exception as e:
        return go.Figure()

    df["date"] = pd.to_datetime(df["date"])

    # Indicamos los filtros de temporada, equipo y victorias/derrotas
    df_filtered = df[
        (df["season"] == season) &
        (df["team_id"] == team_id) &
        (df["w/l"].isin(wl_filter))
    ]

    # Indicamos los filtros de fecha
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered["date"] >= pd.to_datetime(start_date)) &
            (df_filtered["date"] <= pd.to_datetime(end_date))
        ]

    if df_filtered.empty:
        return go.Figure()

    # Calculamos diferencia de puntos
    df_filtered = df_filtered.sort_values("date")
    df_filtered["diff"] = df_filtered["pts"] - df_filtered["pts_opp"]

    # Se hace un merge con tabla de equipos para obtener nombre del rival
    df_filtered = df_filtered.merge(
        teams,
        how="left",
        left_on="team_id_opp",
        right_on="team_id",
        suffixes=("", "_rival")
    )
    
    # Añadimos marcador y resultado
    df_filtered["resultado"] = df_filtered["w/l"]
    df_filtered["marcador"] = df_filtered["pts"].astype(str) + "–" + df_filtered["pts_opp"].astype(str)
    df_filtered['texto_marker'] = df_filtered.apply(
        lambda row: f"{row['team_name']}<br>{row['pts']} - {row['pts_opp']}", axis=1
    )

    # Creamos texto para hover
    df_filtered["hover"] = df_filtered.apply(
        lambda row: f"{row['date'].date()}<br>vs {row['team_name']}<br>{row['pts']} - {row['pts_opp']}", axis=1
    )

    # Indicamos los colores por resultado
    colores = ["green" if d > 0 else "red" for d in df_filtered["diff"]]

    # Añadimos los logos
    df_filtered["logo_path"] = df_filtered["team_id_opp"].apply(
        lambda tid: f"images/teams/{tid}.png"
    )

    # Creamos el gráfico
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_filtered["date"],
        y=df_filtered["diff"],
        mode="markers+lines+text",
        marker=dict(size=10,color=colores),
        text=df_filtered["texto_marker"],
        textposition="middle right",
        hovertext=df_filtered["hover"],
        hoverinfo="text",
        line=dict(color="blue", width=2),
        name="Diferencia"
    ))

    fig.update_layout(
        title= None,
        xaxis_title="",
        yaxis_title="Diferencia de puntos",
        height=500,
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        uirevision="static"
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey', zeroline=True, zerolinecolor='darkslategrey', zerolinewidth=1.5)

    return fig