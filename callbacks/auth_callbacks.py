from dash import callback, Output, Input, State, no_update
from flask_login import login_user, logout_user
from config import VALID_USERNAME_PASSWORD, User
from datetime import timedelta
from flask import session

# Callback para manejar el login
@callback(
    Output("url", "pathname"),
    Output("login-error", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if not username and not password:
        return no_update

    if username in VALID_USERNAME_PASSWORD and VALID_USERNAME_PASSWORD[username] == password:
        user = User(username)
        login_user(user, remember=True, duration=timedelta(days=30))
        session.permanent = True
        return "/home", ""  # Redirige correctamente al dashboard
    else:
        return no_update, "Usuario o contraseña incorrectos"
    
# Callback para manejar el logout
@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if not n_clicks:
        return no_update
    session.clear()
    logout_user()
    return "/logout"
