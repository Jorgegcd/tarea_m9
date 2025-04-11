import sqlite3
import pandas as pd
from utils.cache_config import cache

# Indicamos la base de datos a usar
DB_PATH = "data/tarea_m9.db"

# Generamos la función para extraer datos de la tabla de los partidos
@cache.memoize(timeout=300)  # 5 minutos de caché
def get_matches_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM matches", conn)
    except Exception as e:
        print("Error leer tabla matches:", e)
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# Generamos la función para extraer datos de la tabla de los equipos
@cache.memoize(timeout=300)  # 5 minutos de caché
def get_teams_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM teams", conn)
    conn.close()
    return df