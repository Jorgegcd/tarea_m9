import dash_bootstrap_components as dbc
from dash import html, dcc

# Creamos la barra de navegación (menú en la parte superior)
def create_navbar():
    navbar = dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand(
                html.Span([
                    html.I(className="fas fa-basketball-ball me-2"),
                    dcc.Link("Basketball Analytics", href="/home", className="text-white text-decoration-none") # Indicamos nombres, color y dibujo
                ]),
                className="me-auto"
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dcc.Link("Inicio", href="/home", className="nav-link text-white")), # Pestaña de Inicio
                    dbc.NavItem(dcc.Link("Performance", href="/performance", className="nav-link text-white")), # Pestaña de Performance
                    dbc.NavItem(dcc.Link("Médico", href="/medical", className="nav-link text-white")), # Pestaña de Médico
                    dbc.NavItem(
                        dbc.Button("Cerrar Sesión", id="logout-button", color="light", className="ms-2") # Botón de Cerrar Sesión
                    ),
                ],
                className="ms-auto",
                navbar=True
                ),
                id="navbar-collapse",
                navbar=True,
                is_open=False,
            ),
        ]),
        color="primary",
        dark=True,
        className="mb-4",
    )
    return navbar
