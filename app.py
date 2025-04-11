import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from utils.cache_config import cache
import os
from config import User, VALID_USERNAME_PASSWORD
from layouts.auth_layout import login_layout, logout_layout
import callbacks.auth_callbacks
from layouts.home import home_layout
from layouts.performance import performance_layout
from layouts.medical import medical_layout
from components.navbar import create_navbar
from datetime import timedelta
from flask import session
import callbacks.performance_callbacks
import callbacks.medical_callbacks

# Inicializamos la app de Dash con estilos Bootstrap
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"],
                suppress_callback_exceptions=True,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Iniciamos el Flask server
server = app.server

# Configuramos las secret key de Flask and el tiempo de vida de la sesión
server.config.update(
    SECRET_KEY='your-super-secret-key-123',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=10),
    REMEMBER_COOKIE_DURATION=timedelta(minutes=30),
    SESSION_COOKIE_SECURE=False, 
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_REFRESH_EACH_REQUEST=False
)

# Configuramos el Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

@login_manager.user_loader
def load_user(user_id):
    if user_id not in VALID_USERNAME_PASSWORD:
        return None
    return User(user_id)

# Layout principal de la página
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@callback(
    Output('navbar-collapse', 'is_open'),
    Input('navbar-toggler', 'n_clicks'),
    State('navbar-collapse', 'is_open'),
    prevent_initial_call=True
)

# Generamos función de colapso del navbar
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

def display_page(pathname):
    if pathname == '/logout':
        return logout_layout()
    
    if pathname == '/login' or pathname == '/':
        if current_user.is_authenticated:
            return html.Div([create_navbar(), home_layout()])
        return login_layout()
    
    if not current_user.is_authenticated:
        return login_layout()
    
    page_content = html.Div([create_navbar()])
    
    if pathname == '/home':
        page_content.children.append(home_layout())
    elif pathname == '/performance':
        page_content.children.append(performance_layout())
    elif pathname == '/medical':
        page_content.children.append(medical_layout())
    else:
        page_content.children.append(home_layout())
    
    return page_content

# Generamos el login en base al número de clicks, usuario y password
def login(n_clicks, username, password):
    if not n_clicks:
        return no_update, no_update
        
    if not username or not password:
        return no_update, "Please enter both username and password"
    
    if VALID_USERNAME_PASSWORD.get(username) == password:
        user = User(username)
        login_user(user, remember=True, duration=timedelta(minutes=30))
        session.permanent = True
        return "/home", ""
    
    return no_update, "Invalid username or password"

# Generamos la función logout en base al número de clicks
def logout(n_clicks):
    if not n_clicks:
        return no_update
    session.clear()
    logout_user()
    return "/login"

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def render_page(pathname):
    # Si intenta acceder a una página privada sin estar logueado
    if pathname in ["/home", "/performance", "/medical"]:
        if not current_user.is_authenticated:
            return login_layout(session_expired=True)

    # Si está en login o raíz, mostrar la pestaña login
    if pathname in ["/", "/login"]:
        if current_user.is_authenticated:
            return display_page("/home")  # Redirigimos al home directamente
        return login_layout()

    try:
        return display_page(pathname)
    except Exception as e:
        print (f"Error mostrando {pathname}:", e)
        return html.Div("Ha ocurrido un error al mostrar la página.", style={"color": "red"})

if __name__ == '__main__':
    if not os.path.exists('cache-directory'):
        os.makedirs('cache-directory')
    
    # Inicializamos la caché con el server
    cache.init_app(server)
    
    app.run_server(debug=True, dev_tools_hot_reload=False)