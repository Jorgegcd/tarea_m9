import os

# Generamos función para guardar en imagen las gráficas del formato
def guardar_graficas_pdf(fig_donut=None,  fig_radar = None, fig_donut_rivales = None, fig_temporal = None, carpeta="temp"):
    rutas = {}

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    # Guardamos en imagen la gráfica de donut de las posesiones de equipo
    if fig_donut:
        try:
            ruta_donut = os.path.join(carpeta, "grafica_donut.png")
            fig_donut.write_image(ruta_donut, engine = "orca")
            rutas["donut"] = ruta_donut
        except Exception as e:
            print("Error al guardar fig_donut:", e)

    # Guardamos en imagen la gráfica de donut de las posesiones del rival
    if fig_donut_rivales:
        try:
            ruta_donut_rivales = os.path.join(carpeta, "grafica_donut_rivales.png")
            fig_donut_rivales.write_image(ruta_donut_rivales, engine = "orca")
            rutas["donut_rivales"] = ruta_donut_rivales
        except Exception as e:
            print("Error al guardar fig_donut_rivales:", e)
    
    # Guardamos en imagen la gráfica del radar comparativo entre los datos del equipo y los datos de los rivales que se enfrentan a ellos
    if fig_radar:
        try:
            ruta_radar = os.path.join(carpeta, "grafica_radar.png")
            fig_radar.write_image(ruta_radar, engine = "orca")
            rutas["radar"] = ruta_radar
        except Exception as e:
            print("Error al guardar fig_radar:", e)
    
    # Guardamos en imagen la gráfica de evolución temporal del equipo
    if fig_temporal:
        try:
            ruta_temporal = os.path.join(carpeta, "grafica_temporal.png")
            fig_temporal.write_image(ruta_temporal, engine = "orca")
            rutas["temporal"] = ruta_temporal
        except Exception as e:
            print("Error al guardar fig_temporal:", e)

    return rutas
