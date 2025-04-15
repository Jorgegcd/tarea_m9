<<<<<<< HEAD

=======
>>>>>>> 7cdfeaaa2eb802e966a7c08aebdc32409f157f75
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
<<<<<<< HEAD

### 4. Verifica que existe la carpeta `cache-directory`

Si no existe, créala:

```bash
mkdir cache-directory
```

### 5. Asegúrate de tener los datos

Debes tener el archivo de base de datos en la ruta:

```
data/tarea_m9.db
data/lesiones_aba_2.csv
```

Y en `assets/images/teams/` los logos de los equipos.

### 6. Configura Orca para exportar imágenes

Si usas funciones como `write_image` con `engine='orca'`, asegúrate de tenerlo instalado:

```bash
conda install -c plotly plotly-orca
```

O sigue las [instrucciones oficiales](https://github.com/plotly/orca) para tu sistema.

### 7. Ejecutar la app

```bash
python app.py
```

La app estará disponible en: [http://127.0.0.1:8050](http://127.0.0.1:8050)

## Credenciales de acceso

Usuario por defecto:

```
Username: admin
Password: admin
```

## Funcionalidades

- **Login seguro con Flask-Login**
- **Dashboards por pestañas**:
  - Seguimiento médico (lesiones)
  - Rendimiento de equipos (eficiencias, radar, donuts, PDF)
- **Exportación a PDF personalizada**
- **Sistema de caché por funciones pesadas**

## Tecnologías

- Dash
- Flask
- Flask-Login
- Plotly
- Pandas
- SQLite
- FPDF
- Flask-Caching
=======
>>>>>>> 7cdfeaaa2eb802e966a7c08aebdc32409f157f75
