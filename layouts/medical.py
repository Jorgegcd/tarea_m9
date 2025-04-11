from dash import dcc, html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc

# Generamos función del layout de la pestaña médica
def medical_layout():
    return dbc.Container([
        # Introducimos los filtros de temporada y de tipo de lesión
        dbc.Row([
            dbc.Col([
                dbc.Label("Temporada"),
                dcc.Dropdown(
                    id="medical-season-selector",
                    placeholder="Selecciona una temporada"
                )
            ], width=6),
            dbc.Col([
                dbc.Label("Tipo de lesión"),
                dcc.Dropdown(
                    id="medical-injury-type-selector",
                    multi=True,
                    placeholder="Selecciona tipo(s) de lesión"
                )
            ], width=6),
        ], className="mb-4"),

        # Introducimos los filtros de Equipo, jugador(es) y rango de fechas
        dbc.Row([
            dbc.Col([
                dbc.Label("Equipo"),
                dcc.Dropdown(
                    id="medical-team-selector",
                    placeholder="Selecciona un equipo"
                )
            ], width=4),
            dbc.Col([
                dbc.Label("Jugador(es)"),
                dcc.Dropdown(
                    id="medical-player-selector",
                    multi=True,
                    placeholder="Selecciona jugador(es)"
                )
            ], width=4),
            dbc.Col([
                dbc.Label("Rango de Fechas"),
                dcc.DatePickerRange(
                    id="medical-date-range",
                    start_date_placeholder_text="Desde",
                    end_date_placeholder_text="Hasta",
                    display_format="YYYY-MM-DD",
                    style={"width": "100%"}
                )
            ], width=4)
        ], className="mb-4"),

        # Introducimos los gráficos de cantidad de lesiones y su duración
        dbc.Row([
            dbc.Col([
                html.H5("Cantidad de lesiones por tipo", className="text-center mb-3", 
                        style={"color": "black", "fontSize": "24px"}),
                dcc.Graph(id="lesion-count-graph", style={"height": "500px"})
            ], width=6),

            dbc.Col([
                html.H5("Duración de lesiones por tipo (días)", className="text-center mb-3", 
                        style={"color": "black", "fontSize": "24px"}),
                dcc.Graph(id="lesion-duration-graph", style={"height": "500px"})
            ], width=6)
        ], className="mb-4"),

        # Introducimos la tabla comparativa de lesiones
        dbc.Row([
            dbc.Col([
                html.H5("Tabla comparativa de lesiones", className="text-center mb-3", 
                        style={"color": "black", "fontSize": "24px"}),
                dcc.Loading(
                    DataTable(
                        id="lesion-table",
                        columns=[],  # Se rellenarán dinámicamente
                        data=[],     # También dinámicamente
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "center"},
                        style_header={"backgroundColor": "#f1f1f1", "fontWeight": "bold"},
                        sort_action="native",           # Habilita ordenación
                        filter_action="native",         # Habilita filtros por columna de texto
                        page_size=20,                   # Controla la paginación
                    ),
                    type="circle"
                )
            ])
        ])
    ], fluid=True)