from dash import html
import dash_bootstrap_components as dbc
from flask_login import login_required

# Generamos layout de la página de inicio
def home_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Bienvenido a Basketball Analytics", className="text-center mb-4"), # Indica el título de la página
                html.P(
                    "Esta plataforma aporta análisis de rendimiento y seguimiento medico para el baloncesto a través de diferentes dashboards", # Descripción de la app
                    className="lead text-center"
                ),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Performance Dashboard", className="text-center")), 
                    dbc.CardBody([
                        html.P("Sigue estadísticas de jugador, partidos y tendencias.", className="text-center"), # Descripción de pestaña
                        html.Div(
                           dbc.Button("Pestaña Performance", href="/performance", color="primary"),
                           className="d-flex justify-content-center" # Centramos el botón
                        )
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Dashboard Médico", className="text-center")),
                    dbc.CardBody([
                        html.P("Monitoriza la salud, lesiones y registros médicos de los jugadores" , className="text-center"),# Descripción de pestaña
                        html.Div(
                            dbc.Button("Pestaña Médico", href="/medical", color="primary"),
                            className="d-flex justify-content-center" # Centramos el botón
                        )
                    ])
                ])
            ], width=6)
        ], className="mt-4")
    ])
