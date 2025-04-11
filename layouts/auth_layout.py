from dash import html, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from flask_login import login_user, logout_user
from config import VALID_USERNAME_PASSWORD, User

# Generamos layout de la página de login
def login_layout(session_expired=False):
    mensaje_error = "Tu sesión ha expirado. Por favor, inicia sesión de nuevo." if session_expired else ""

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Basketball Analytics Login", className="text-center mb-4"), # Lo que indica la página cuando entramos a ella
                dbc.Card([
                    dbc.CardBody([
                        dbc.Input(
                            id="username",
                            placeholder="Username",
                            type="text",
                            className="mb-3",
                            value=""  # Valor inicial vacío
                        ),
                        dbc.Input(
                            id="password",
                            placeholder="Password",
                            type="password",
                            className="mb-3",
                            value=""  # Valor inicial vacío
                        ),
                        dbc.Button(
                            "Login",
                            id="login-button",
                            color="primary",
                            className="w-100",
                            n_clicks=0  
                        ),
                        html.Div(mensaje_error, id="login-error", className="mt-3 text-danger"),  # Añadido estilo para mensajes de error
                    ])
                ])
            ], width=500, className="offset-3")
        ])
    ], className="vh-100 d-flex align-items-center justify-content-center")

# Layout para logout
def logout_layout():
    logout_user()
    return dbc.Container([
        html.H2("Has cerrado sesión correctamente.", className="text-center text-success"), # Mensaje que se muestra
        dbc.Button("Volver al Login", href="/login", color="primary", className="d-block mx-auto mt-3") # Botón para volver al login
    ])