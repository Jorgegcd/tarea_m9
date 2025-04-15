from dash import callback, Output, Input, State,  no_update
from data.db_connection import get_matches_data, get_teams_data
import pandas as pd
import plotly.graph_objects as go
from utils.cache_config import cache
import os
import plotly.express as px
from utils.pdf_generator import generar_pdf
from utils.plot_utils import generar_donut_equipo_figure, generar_donut_rivales_figure, generar_radar_figure, grafica_temporal
import traceback
import plotly.io as pio
pio.kaleido.scope.mathjax = None
from dash.exceptions import PreventUpdate
from utils.image_utils import guardar_graficas_pdf
from utils.cache_config import cache

@callback(
    Output("team-selector", "options"),
    Input("season-selector", "value")
)

# Generamos función para seleccionar equipos
@cache.memoize(timeout=600)
def update_team_selector(season):
    print("Callback ejecutado con temporada:", season)

    if not season:
        return []

    # Obtenemos datos de equipos y partidos
    try:
        df_matches = get_matches_data()
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"  
    
    df_teams = get_teams_data()

    # Filtramos por temporada
    df_season = df_matches[df_matches["season"] == season]

    # Mostramos IDs únicos de equipos en esa temporada
    team_ids = df_season["team_id"].unique()

    # Filtramos equipos por esos IDs
    df_filtered_teams = df_teams[df_teams["team_id"].isin(team_ids)]

    # Ordenamos por nombre y construimos opciones
    df_filtered_teams = df_filtered_teams.sort_values("team_name")
    options = [
        {"label": row["team_name"], "value": row["team_id"]}
        for _, row in df_filtered_teams.iterrows()
    ]

    return options

@callback(
    Output("offensive-rating", "children"),
    Output("defensive-rating", "children"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Generamos la función para el cálculo de eficiencia ofensiva y defensiva
@cache.memoize(timeout=600)
def calcular_ratings(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return "–", "–"

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"

    # Aseguramosse de que la columna 'date' es datetime
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
        return "–", "–"

    # Realizamos las sumas necesarias para calcular los ratings
    total_pts = df_filtered["pts"].sum()
    total_pts_opp = df_filtered["pts_opp"].sum()
    total_fga = df_filtered["fga"].sum()
    total_fta = df_filtered["fta"].sum()
    total_or = df_filtered["or"].sum()
    total_to = df_filtered["to"].sum()

    # Calculamos las posesiones estimadas
    possessions = total_fga + 0.44 * total_fta - total_or + total_to

    # Calculamos los ratings
    off_rating = round((total_pts * 100 / possessions), 2) if possessions else 0
    def_rating = round((total_pts_opp * 100 / possessions), 2) if possessions else 0

    return f"{off_rating}", f"{def_rating}"

@callback(
    Output("efg", "children"),
    Output("off_reb", "children"),
    Output("turnovers", "children"),
    Output("ft_rate", "children"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Generamos la función de cálculo de los cuatro factores
@cache.memoize(timeout=600)
def calcular_cuatro_factores(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return "–", "–", "–", "–"

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"
    
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
        return "–", "–", "–", "–"

    # Se extraen y calculan las métricas necesarias
    fgm = df_filtered["fgm"].sum()
    fg3m = df_filtered["fg3m"].sum()
    fga = df_filtered["fga"].sum()
    off_reb = df_filtered["or"].sum()
    def_reb_opp = df_filtered["dr_opp"].sum()
    to = df_filtered["to"].sum()
    fta = df_filtered["fta"].sum()
    ftm = df_filtered["ftm"].sum()

    # Tiro de campo efectivo (eFG%)
    efg = (fgm + 0.5 * fg3m) / fga * 100 if fga else 0

    # % Rebote Ofensivo
    total_rebs = off_reb + def_reb_opp
    off_reb_pct = off_reb / total_rebs * 100 if total_rebs else 0

    # % Pérdidas
    to_pct = to / (fga + 0.44 * fta + to) * 100 if (fga + 0.44 * fta + to) else 0

    # FT Rate
    ft_rate = ftm / fga * 100 if fga else 0

    return (
        f"{efg:.2f}",
        f"{off_reb_pct:.2f}",
        f"{to_pct:.2f}",
        f"{ft_rate:.2f}"
    )

@callback(
    Output("diferencia-puntos", "figure"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Creamos la gráfica de evolución de resultados
@cache.memoize(timeout=600)
def actualizar_grafica_diferencia(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"
    
    teams = get_teams_data() # Cargamos la función para obtener los datos de los equipos
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

@callback(
    Output("grafica-donut", "figure"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Realizamos la gráfica de donut con los datos de posesiones que se actualicen según filtros
@cache.memoize(timeout=600)
def actualizar_donut_posesiones(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"
    
    df["date"] = pd.to_datetime(df["date"])

    # Indicamos los filtros de temporada, equipo y victorias/derrotas
    df_filtered = df[
        (df["season"] == season) &
        (df["team_id"] == team_id) &
        (df["w/l"].isin(wl_filter))
    ]

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

@callback(
    Output("grafica-donut-rivales", "figure"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Realizamos la gráfica de donut con los datos de posesiones de los rivales que se actualicen según filtros
@cache.memoize(timeout=600)
def actualizar_donut_rivales(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"
    
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
        marker=dict(colors=["tomato", "darkred", "lightcoral", "red"])  # gama de rojos suaves
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

@callback(
    Output("grafica-radar", "figure"),
    Input("season-selector", "value"),
    Input("team-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("wl-selector", "value")
)

# Realizamos la gráfica de radar con los datos de estadísticas avanzadas que se actualicen según filtros
@cache.memoize(timeout=600)
def actualizar_radar_avanzado(season, team_id, start_date, end_date, wl_filter):
    if not all([season, team_id, wl_filter]):
        return go.Figure()

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"
    
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

    teams = get_teams_data() # Cargamos la función que otorga los datos de los equipos
    nombre_equipo_row = teams[teams["team_id"] == team_id] # Sacamos el id del equipo
    nombre_equipo_str = nombre_equipo_row["team_name"].values[0] if not nombre_equipo_row.empty else f"Equipo {team_id}" # Sacamos el nombre en base del id

    # Generamos radar del equipo
    fig.add_trace(go.Scatterpolar(
        r=team_normalized,
        theta=list(equipo.keys()),
        fill='toself',
        name='Equipo',
        line=dict(color='steelblue'),
        mode='lines+markers',
        text=[f"{equipo[k]:.1f}%" for k in equipo],  # Muestra sobre el punto
        textposition='top center',
        hovertemplate=f"<b>{nombre_equipo_str}</b><br>Métrica: %{{theta}}<br>Valor: %{{text}}<extra></extra>"
    ))

    # Generamos radar de los rivales
    fig.add_trace(go.Scatterpolar(
        r=rival_normalized,
        theta=list(rival.keys()),
        fill='toself',
        name='Rival',
        line=dict(color='tomato'),
        mode='lines+markers',
        text=[f"{rival[k]:.1f}%" for k in rival],
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

@callback(
    Output("pdf-download-link", "href"),
    Output("pdf-download-link", "style"),
    Input("export-pdf-button", "n_clicks"),
    State("season-selector", "value"),
    State("team-selector", "value"),
    State("wl-selector", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date")
)

# Generamos la función para exportar el PDF
def exportar_pdf(n_clicks, temporada, team_id, wl_filter, start_date, end_date):

    if not n_clicks:
        raise PreventUpdate

    try:
        df = get_matches_data() # Cargamos la función para obtener los datos de los partidos
    except Exception as e:
        print("Error al cargar datos de partidos:", e)
        return "–", "–"

    # Aseguramos que la columna 'date' es datetime
    df["date"] = pd.to_datetime(df["date"])

    # Filtramos por equipo seleccionado y rivales
    df_filtered = df[
        (df["season"] == temporada) &
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
        return "–", "–"

    # Calculamos los valores totales
    total_pts = df_filtered["pts"].sum()
    total_pts_opp = df_filtered["pts_opp"].sum()
    total_fga = df_filtered["fga"].sum()
    total_fta = df_filtered["fta"].sum()
    total_or = df_filtered["or"].sum()
    total_to = df_filtered["to"].sum()

    # Realizamos las sumas necesarias para calcular los ratings
    fgm = df_filtered["fgm"].sum()
    fg3m = df_filtered["fg3m"].sum()
    fga = df_filtered["fga"].sum()
    off_reb = df_filtered["or"].sum()
    def_reb_opp = df_filtered["dr_opp"].sum()
    to = df_filtered["to"].sum()
    fta = df_filtered["fta"].sum()
    ftm = df_filtered["ftm"].sum()

    # Tiro de campo efectivo (eFG%)
    efg = round((fgm + 0.5 * fg3m) / fga * 100,2) if fga else 0
    # % Rebote Ofensivo
    total_rebs = off_reb + def_reb_opp
    off_reb_pct = round(off_reb / total_rebs * 100, 2) if total_rebs else 0
    # % Pérdidas
    to_pct = round(to / (fga + 0.44 * fta + to) * 100, 2) if (fga + 0.44 * fta + to) else 0
    # FT Rate
    ft_rate = round(ftm / fga * 100, 2) if fga else 0
    
    # Calculamos las posesiones estimadas
    possessions = total_fga + 0.44 * total_fta - total_or + total_to

    # Cálculamos los ratings
    off_rating = round((total_pts * 100 / possessions), 2) if possessions else 0
    def_rating = round((total_pts_opp * 100 / possessions), 2) if possessions else 0

    teams = get_teams_data() # Cargamos la función que otorga los datos de los equipos

    nombre_equipo_row = teams[teams["team_id"] == team_id]
    nombre_equipo_str = nombre_equipo_row["team_name"].values[0] if not nombre_equipo_row.empty else f"Equipo {team_id}"
    page_title = f"Informe de {nombre_equipo_str} en la temporada {temporada}"

    # Indicamos los nombres de las columnas y los datos
    tabla_headers_rating = ["Off Rating", "Def Rating"]
    tabla_headers_cuatro_factores = ["eFG%", "% Rebote Ofensivo", "% Perdidas", "FT Rate"]
    tabla_data_cuatro_factores = [[efg, off_reb_pct, to_pct, ft_rate]]
    tabla_data_rating = [[off_rating, def_rating]]

    # Se generan imágenes de donut, donut de rivales y radar
    fig_temporal = grafica_temporal(temporada, team_id, start_date, end_date, wl_filter)
    fig_donut = generar_donut_equipo_figure(temporada, team_id, start_date, end_date, wl_filter)
    fig_radar = generar_radar_figure(temporada, team_id, start_date, end_date, wl_filter)
    fig_donut_rivales = generar_donut_rivales_figure(temporada, team_id, start_date, end_date, wl_filter)
    
    # Guardamos las figuras
    rutas_imagenes = guardar_graficas_pdf(fig_donut=fig_donut, fig_donut_rivales=fig_donut_rivales, fig_radar=fig_radar, fig_temporal=fig_temporal)
    for k, ruta in rutas_imagenes.items():
        print(f"✅ Ruta imagen {k}: {ruta} - Existe: {os.path.exists(ruta)}")
    
    # Generamos texto de contexto según filtros seleccionados
    descripcion_contexto = "Informe de Performance"

    # Añadimos el texto para la condición de victoria o derrota
    if wl_filter == ["W"]:
        descripcion_contexto += " en las victorias"
    elif wl_filter == ["L"]:
        descripcion_contexto += " en las derrotas"
    else:
        descripcion_contexto += " en todos los partidos"

    # Añadimos el texto para la condición de fechas si ambas están seleccionadas
    if start_date and end_date:
        descripcion_contexto += f" entre {start_date} y {end_date}"
    else:
        descripcion_contexto += " de la temporada"

    # Se genera pdf
    try:
        generar_pdf(page_title, nombre_equipo_str, team_id, tabla_headers_rating, tabla_data_rating, tabla_headers_cuatro_factores,
                    tabla_data_cuatro_factores, rutas_imagenes=rutas_imagenes, descripcion_contexto=descripcion_contexto)
    except Exception as e:
        print("Error al generar el PDF:", e)
        return "-", {"display": "none"}
    
    href_pdf = f"/assets/performance_report_test.pdf"
    return href_pdf, {"display": "inline-block"}