from dash import callback, Output, Input
import pandas as pd
import plotly.express as px
from utils.cache_config import cache

# Cargamos los datos desde el CSV
try:
    df_lesiones = pd.read_csv("data/lesiones_aba_2.csv", parse_dates=["injury_beginning_date", "injury_recovering_date"])
except Exception as e:
    print("Error al cargar datos de lesiones:", e)

@callback(
    Output("medical-injury-type-selector", "options"),
    Input("medical-season-selector", "value")
)

# Generamos función para que se actualice la página según los tipos de lesión
def actualizar_tipos_lesion(season):
    df = df_lesiones # Cargamos los datos
    if season:
        df = df[df["season"] == season]
    tipos = df["injury_type"].dropna().unique()
    tipos_ordenados = sorted(tipos)
    return [{"label": t, "value": t} for t in tipos_ordenados]

@callback(
    Output("medical-team-selector", "options"),
    Input("medical-season-selector", "value"),
    Input("medical-injury-type-selector", "value")
)

# Generamos función del selector de equipos
@cache.memoize(timeout=600)
def actualizar_dropdown_equipos(temporada, lesiones_tipo):
    df = df_lesiones.copy() # Cargamos los datos
    if not temporada:
        return []
    
    df = df[df["season"] == temporada] # Seleccionamos temporda
    
    if lesiones_tipo:
        if isinstance(lesiones_tipo, str):  
            lesiones_tipo = [lesiones_tipo]
        df = df[df["injury_type"].isin(lesiones_tipo)]

    equipos_filtrados = (df["team_name"].dropna().sort_values().unique()) # Filtramos los equipos si se considera necesario

    return [{"label": equipo, "value": equipo} for equipo in equipos_filtrados]

@callback(
    Output("medical-season-selector", "options"),
    Input("medical-season-selector", "value")  
)

# Cargamos la temporada que nos interese (filtro)
def cargar_temporadas(_):
    temporadas = df_lesiones["season"].dropna().unique() # Cargamos las temporadas (solo 1 dato por temporada), del dataset del que proviene
    temporadas_ordenadas = sorted(temporadas)  # Orden alfabético
    return [{"label": t, "value": t} for t in temporadas_ordenadas]

@callback(
    Output("medical-player-selector", "options"),
    Input("medical-team-selector", "value"),
    Input("medical-injury-type-selector", "value"),
    Input("medical-season-selector", "value")
)

# Generamos selector de jugadores
@cache.memoize(timeout=600)
def actualizar_dropdown_jugadores(equipo, lesiones_tipo, temporada):
    df = df_lesiones.copy() # Cargamos los datos
    if not temporada:
        return []
    
    df = df[df["season"] == temporada] # Filtramos por temporada

    # Indicamos el tipo de lesión si procede
    if lesiones_tipo:
        if isinstance(lesiones_tipo, str): 
            lesiones_tipo = [lesiones_tipo]
        df = df[df["injury_type"].isin(lesiones_tipo)]

    # Indicamos el equipo si procede
    if equipo:
        df = df[df["team_name"] == equipo]

    # Filtramos jugadores
    jugadores_filtrados = (df["name"].dropna().sort_values().unique())

    return [{"label": jugador, "value": jugador} for jugador in jugadores_filtrados]

# Cargamos fehcas de inicio y fin de lesión
df_lesiones["injury_beginning_date"] = pd.to_datetime(df_lesiones["injury_beginning_date"])
df_lesiones["injury_recovering_date"] = pd.to_datetime(df_lesiones["injury_recovering_date"])

@callback(
    Output("medical-date-range", "start_date"),
    Output("medical-date-range", "end_date"),
    Input("medical-season-selector", "value"),
    Input("medical-injury-type-selector", "value"),
    Input("medical-team-selector", "value"),
    Input("medical-player-selector", "value")
)

# Generamos la función del rango de fechas
@cache.memoize(timeout=600)
def actualizar_rango_fechas(temporada, lesiones_tipo, equipo, jugadores):
    df = df_lesiones.copy() # Cargamos los datos

    if temporada:
        df = df[df["season"] == temporada] # Filtramos por temporada

    # Indicamos el tipo de lesión si procede
    if lesiones_tipo:
        if isinstance(lesiones_tipo, str):
            lesiones_tipo = [lesiones_tipo]
        df = df[df["injury_type"].isin(lesiones_tipo)]

    # Indicamos el equipo si procede
    if equipo:
        df = df[df["team_name"] == equipo]

    # Indicamos los jugadores a mostrar si procede
    if jugadores:
        if isinstance(jugadores, str):
            jugadores = [jugadores]
        df = df[df["name"].isin(jugadores)]

    if df.empty:
        return None, None

    # Filtramos por fecha de inicio de lesión (de todas las que haya) y de final
    fecha_inicio = df["injury_beginning_date"].min()
    fecha_fin = df["injury_recovering_date"].max()

    return fecha_inicio, fecha_fin

@callback(
    Output("lesion-count-graph", "figure"),
    Input("medical-season-selector", "value"),
    Input("medical-team-selector", "value"),
    Input("medical-player-selector", "value"),
    Input("medical-injury-type-selector", "value"),
    Input("medical-date-range", "start_date"),
    Input("medical-date-range", "end_date"),
)

# Generamos gráfico de cantidad de lesiones
@cache.memoize(timeout=600)
def actualizar_grafico_cantidad_lesiones(season, equipo, jugadores, tipos_lesion, start_date, end_date):
    df = df_lesiones.copy()

    if season:
        df = df[df["season"] == season] # Filtramos por temporada
    
    # Indicamos el tipo de lesión si procede
    if tipos_lesion:
        if isinstance(tipos_lesion, str):
            tipos_lesion = [tipos_lesion]
        df = df[df["injury_type"].isin(tipos_lesion)]
    
    # Indicamos el equipo si procede
    if equipo:
        df = df[df["team_name"] == equipo]
    
    # Indicamos los jugadores a mostrar si procede
    if jugadores:
        if isinstance(jugadores, str):
            jugadores = [jugadores]
        df = df[df["name"].isin(jugadores)]
    
    # Indicamos las fechas de inicio y fin si estuviesen indicadas
    if start_date and end_date:
        df = df[(df["injury_beginning_date"] >= pd.to_datetime(start_date)) & (df["injury_recovering_date"] <= pd.to_datetime(end_date))]

    if df.empty:
        return px.bar(title="Sin datos disponibles")

    # Contamos cantidad de lesiones
    conteo = df.groupby("injury_type").size().reset_index(name = "Cantidad")
    conteo = conteo.rename(columns={"injury_type": "Tipo de Lesión"})

    # Mostramos gráfica
    fig = px.bar(conteo, x="Tipo de Lesión", y="Cantidad", color="Tipo de Lesión", 
                 title=None, text="Cantidad")

    fig.update_layout(
        title_font_size=20,
        xaxis_title=None,
        yaxis_title="Cantidad",
        showlegend=False,
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
        uirevision="static"
    )

    return fig

# Cargamos los datos de las fechas de lesión
df_lesiones = pd.read_csv("data/lesiones_aba_2.csv")
df_lesiones["injury_beginning_date"] = pd.to_datetime(df_lesiones["injury_beginning_date"])
df_lesiones["injury_recovering_date"] = pd.to_datetime(df_lesiones["injury_recovering_date"])
df_lesiones["duracion_dias"] = (df_lesiones["injury_recovering_date"] - df_lesiones["injury_beginning_date"]).dt.days

@callback(
    Output("lesion-duration-graph", "figure"),
    Input("medical-season-selector", "value"),
    Input("medical-team-selector", "value"),
    Input("medical-player-selector", "value"),
    Input("medical-injury-type-selector", "value"),
    Input("medical-date-range", "start_date"),
    Input("medical-date-range", "end_date")
)

# Generamos gráfico de duración de lesiones
@cache.memoize(timeout=600)
def actualizar_grafico_duracion_lesiones(season, equipo, jugadores, lesiones_tipo, fecha_inicio, fecha_fin):
    df = df_lesiones.copy()

    if season:
        df = df[df["season"] == season] # Filtramos por temporada
    
    # Indicamos el tipo de lesión si procede
    if lesiones_tipo:
        if isinstance(lesiones_tipo, str):
            lesiones_tipo = [lesiones_tipo]
        df = df[df["injury_type"].isin(lesiones_tipo)]

    # Indicamos el equipo si procede
    if equipo:
        df = df[df["team_name"] == equipo]

    # Indicamos los jugadores a mostrar si procede
    if jugadores:
        if isinstance(jugadores, str):
            jugadores = [jugadores]
        df = df[df["name"].isin(jugadores)]

    # Indicamos las fechas de inicio y fin si estuviesen indicadas
    if fecha_inicio and fecha_fin:
        df = df[
            (df["injury_beginning_date"] >= pd.to_datetime(fecha_inicio)) &
            (df["injury_beginning_date"] <= pd.to_datetime(fecha_fin))
        ]

    if df.empty:
        return px.scatter(title="No hay datos disponibles para los filtros seleccionados.")

    # Mostramos gráfica
    fig = px.box(
        df,
        x="injury_type",
        y="duracion_dias",
        points="all",
        color="injury_type",
        title=None,
        labels={"injury_type": "Tipo de Lesión", "duracion_dias": "Días de Baja"}
    )

    fig.update_layout(
        height=500,
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        title=dict(font=dict(size=22), x=0.5),
        uirevision="static"
    )

    return fig

@callback(
    Output("lesion-table", "data"),
    Output("lesion-table", "columns"),
    Input("medical-season-selector", "value"),
    Input("medical-team-selector", "value"),
    Input("medical-player-selector", "value"),
    Input("medical-injury-type-selector", "value"),
    Input("medical-date-range", "start_date"),
    Input("medical-date-range", "end_date")
)

# Generamos tabla de lesiones
@cache.memoize(timeout=600)
def actualizar_tabla_lesiones(temporada, equipo, jugadores, lesiones_tipo, fecha_inicio, fecha_fin):
    df = df_lesiones.copy()

    if temporada:
        df = df[df["season"] == temporada] # Filtramos por temporada
    
    # Indicamos el tipo de lesión si procede
    if lesiones_tipo:
        if isinstance(lesiones_tipo, str):
            lesiones_tipo = [lesiones_tipo]
        df = df[df["injury_type"].isin(lesiones_tipo)]
    
    # Indicamos el equipo si procede
    if equipo:
        df = df[df["team_name"] == equipo]
    
    # Indicamos los jugadores a mostrar si procede
    if jugadores:
        if isinstance(jugadores, str):
            jugadores = [jugadores]
        df = df[df["name"].isin(jugadores)]
    
    # Indicamos las fechas de inicio y fin si estuviesen indicadas
    if fecha_inicio and fecha_fin:
        df = df[
            (df["injury_beginning_date"] >= pd.to_datetime(fecha_inicio)) &
            (df["injury_beginning_date"] <= pd.to_datetime(fecha_fin))
        ]

    if df.empty:
        return [], []

    # Realizmos resumen a indicar en la tabla
    resumen = df.groupby(["season", "team_name", "name", "height", "injury_type"]).agg(
        cantidad=("injury_type", "count"),
        dias_perdidos=("duracion_dias", "sum")
    ).reset_index()

    resumen = resumen.rename(columns={
        "season": "Temporada",
        "team_name": "Equipo",
        "name": "Jugador",
        "height": "Altura",
        "injury_type": "Tipo de Lesión",
        "cantidad": "Cantidad",
        "dias_perdidos": "Días de baja"
    })

    data = resumen.to_dict("records")
    columns = [{"name": col, "id": col} for col in resumen.columns]

    return data, columns