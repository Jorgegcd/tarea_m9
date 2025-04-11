from dash import html, dcc
import dash_bootstrap_components as dbc

# Generamos función del layout de la pestaña performance
def performance_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Dashboard de Performance", className="text-center mb-4"),
            ])
        ]),
        # Generamos el filtro de temporada
        dbc.Row([
            dbc.Col([
                dbc.Label("Temporada"),
                dcc.Dropdown(
                    id="season-selector",
                    options=[
                        {"label": "2022/2023", "value": "2022/2023"},
                        {"label": "2023/2024", "value": "2023/2024"}
                    ],
                    placeholder="Selecciona una temporada"
                )
            ], width=8),
            dbc.Col([
                dbc.Row([
                    dbc.Col(
                        dbc.Button("Exportar a PDF", id="export-pdf-button", color="primary", className="mt-4"),
                        width = 6
                    ),
                    dbc.Col(
                        html.A(
                            dbc.Button([
                                html.I(className="fas fa-file-download me-2"),"Descargar PDF"
                                    ],
                                    color="info",
                                    id="boton-descargar-pdf",
                                    className="w-100"),
                                    id="pdf-download-link",
                                    href="",
                                    target="_blank",
                                    download="informe_equipo.pdf",
                                    style={"display": "none"}
                                ),
                                width = 6                    
                            )
                        ], className="g-2 mt-4")
                    ])
                ], className="mb-4"),
        
        # Generamos los filtros de equipo, fechas y resultado
        dbc.Row([
            dbc.Col([
                dbc.Label("Equipo"),
                dcc.Dropdown(id="team-selector", placeholder="Selecciona un equipo")
            ], width=4),

            dbc.Col([
                dbc.Label("Rango de Fechas", className="mb-1"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date_placeholder_text="Desde",
                    end_date_placeholder_text="Hasta",
                    display_format="YYYY-MM-DD",
                    style={"width": "100%"}
                )
            ], width=4),

            dbc.Col([
                dbc.Label("Resultado"),
                dcc.Dropdown(
                    id="wl-selector",
                    options=[
                        {"label": "Victorias", "value": "W"},
                        {"label": "Derrotas", "value": "L"}
                    ],
                    value=["W", "L"],         # Valor por defecto = ambos
                    multi=True,               # Selección múltiple
                    placeholder="Selecciona un resultado"
                )
            ], width=4),
         ], className="mb-4"),   

        # Introducimos las fichas de eficiencias ofensiva y defensiva
        dbc.Row([
            html.H5("Eficiencia ofensiva y defensiva", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "26px"}),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H4("Rating Ofensivo", className="text-center")),
                dbc.CardBody(html.H4(id="offensive-rating", className="card-title text-center", style={"color": "steelblue"}))
            ]), width=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H4("Rating Defensivo", className="text-center")),
                dbc.CardBody(html.H4(id="defensive-rating", className="card-title text-center", style={"color": "tomato"}))
            ]), width=6),
        ], className="mb-4"),

        # Introducimos fichas de los 4 factores
        dbc.Row([
            html.H5("Cuatro factores del equipo", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "24px"}),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H5("eFG%", className="text-center")),
                dbc.CardBody(html.H5(id="efg", className="card-title text-center", style={"color": "blue"}))
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H5("% Rebote Ofensivo", className="text-center")),
                dbc.CardBody(html.H5(id="off_reb", className="card-title text-center"), style={"color": "darkgoldenrod"})
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H5("% Pérdidas", className="text-center")),
                dbc.CardBody(html.H5(id="turnovers", className="card-title text-center", style={"color": "red"}))
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader(html.H5("FT Rate", className="text-center")),
                dbc.CardBody(html.H5(id="ft_rate", className="card-title text-center", style={"color": "slategrey"}))
            ]), width=3),
        ], className="mb-4"),

        # Introducimos el gráfico de evolución temporal
        dbc.Row([
            dbc.Col([
                html.H5("Evolución temporal del equipo", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "24px"}),
                dcc.Graph(id="diferencia-puntos", style={"height": "550px"})
            ])
        ], className="mb-4"),

        # Introducimos las gráficas de donut equipo, radar y donut rivales
        dbc.Row([
            dbc.Col([
                html.H5("Distribución de Posesiones Equipo", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "24px"}),
                dcc.Graph(id="grafica-donut", className="grafico-responsive", style={"height": "500px"})
            ], width=4),
            dbc.Col([
                html.H5("Comparativa de Estadísticas Avanzadas", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "24px"}),
                dcc.Graph(id="grafica-radar", style={"height": "500px"})
            ], width=4),
            dbc.Col([
                html.H5("Distribución de Posesiones de Rivales", className="text-center", style={"margin-bottom": "20px", "color": "black", "fontSize": "24px"}),
                dcc.Graph(id="grafica-donut-rivales", style={"height": "500px"})
            ], width=4)
        ])
    ], fluid=True)