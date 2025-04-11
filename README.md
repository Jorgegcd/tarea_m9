# Basketball Analytics Dashboard

Dashboard interactivo desarrollado con **Dash**, **Plotly** y **Flask-Login** para el análisis de rendimiento y salud de jugadores de baloncesto.

## Estructura del proyecto

```
Basketball Analytics/
├── app.py
├── config.py
├── cache-directory/
├── assets/
│   ├── pdf_descarga
│   └── custom.css
├── data/
│   ├── db_connection.py
│   ├── lesiones_aba_2.csv
│   └── tarea_m9.db
├── utils/
│   ├── cache_config.py
│   ├── image_utils.py
│   ├── pdf_generator.py
│   └── plot_utils.py
├── layouts/
│   ├── auth_layout.py
│   ├── home.py
│   ├── performance.py
│   └── medical.py
├── components/
│   └── navbar.py
├── callbacks/
│   ├── auth_callbacks.py
│   ├── performance_callbacks.py
│   └── medical_callbacks.py
├── requirements.txt
└── README.md
```

## Cómo ejecutar la app

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/basketball-analytics.git
cd basketball-analytics
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```
