from fpdf import FPDF
import os
import datetime
import textwrap

def generar_pdf(page_title, selected_teams, team_id, tabla_headers_eficiencia, tabla_data_eficiencia, tabla_headers_cuatro_factores,
                tabla_data_eficiencia_cuatro_factores, rutas_imagenes=None, descripcion_contexto="Informe de Performance"):
    
    # Generamos el PDF vertical
    class PDF(FPDF):
        def __init__(self):
            super().__init__(unit='mm', format='A4')
            self.set_auto_page_break(auto=True, margin=20)
            # Obtenemos la ruta de la fuente
            font_path = os.path.join(os.path.dirname(__file__), "..", "fonts")
            if os.path.exists(font_path):
                # Agregamos la fuente DejaVu
                self.add_font("DejaVu", "", os.path.join(font_path, "DejaVuSans.ttf"), uni=True)
                self.add_font("DejaVu", "B", os.path.join(font_path, "DejaVuSans-Bold.ttf"), uni=True)
                self.add_font("DejaVu", "I", os.path.join(font_path, "DejaVuSans-Oblique.ttf"), uni=True)
                self.add_font("DejaVu", "BI", os.path.join(font_path, "DejaVuSans-BoldOblique.ttf"), uni=True)
                self.myfont = "DejaVu"
            else:
                self.myfont = "Arial"  # Usamos Arial por defecto si la fuente no se encuentra.

        # Generamos el encabezado
        def header(self):
            current_dir = os.getcwd()
            header_path_down = os.path.join(current_dir, "images", "lineaV2_horizontal.png")
            header_path_right = os.path.join(current_dir, "images", "SDC_Hor_250.png")
            if os.path.exists(header_path_down):
                self.image(header_path_down, 5, 15, 200) # Línea horizontal azul claro que ocupe el ancho
            if os.path.exists(header_path_right):
                self.image(header_path_right, 180, 5, 20, 10) # Logo Sports Data Campus a la derecha
            
            # Designamos la fuente que queremos y que ya hemos elegido previamente al tamaño 16
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(self.myfont, "", 16) # Tipo de fuente
            
            self.set_y(10)  # Posición vertical del texto
            self.set_x((self.w - self.get_string_width("Tarea Módulo 9")) / 2)  # Centramos horizontalmente el título en el encabezado
            self.cell(55,3, "Tarea Módulo 9", border=0, align="C")

            # Designamos la fuente que queremos: Arial 8
            self.set_text_color(67, 142, 189) # Color de la fuente
            self.set_font(self.myfont, "", 8) # Tipo de fuente
                
            self.set_y(10)  # Posición vertical del texto
            self.cell(55,3, "Jorge Gómez-Cornejo Díaz", border=0, align="L") # Situamos el texto a la izquierda
            # Realizamos un salto de línea
            self.ln(20)

        # Generamos el pie de página
        def footer(self):
            current_dir = os.getcwd()
            footer_path = os.path.join(current_dir, "images", "footer_tarea.png") # Introducimos una imagen del footer que queremos
            if os.path.exists(footer_path):
                self.image(footer_path, 0, 285, 210) # Imagen del footer
            self.set_y(-20) # Posición al pie
            # Designamos la fuente que queremos, en este caso Times con tamaño 8
            self.set_font("Times","", 8)
            # Imprimimos el número de página
            self.cell(0, 28, f"Página {self.page_no()}", align="C")

        # Generamos la función para mostrar las tablas en el pdf
        def create_table(self, headers, data, col_width=None, line_height=6, margin_left=8):
            # Si existe 'team_id' en headers, eliminamos la columna correspondiente de cada fila
            if "team_id" in headers:
                idx = headers.index("team_id")
                headers = headers[:idx] + headers[idx+1:]
                data = [row[:idx] + row[idx+1:] for row in data]
            
            n = len(headers)

            # Calculamos la base del ancho de las columnas de una tabla
            if col_width:
                # Si se proporciona un ancho, lo usamos para todas las columnas
                widths = [col_width] * n
            else:
                base_width = (self.w - 2 * self.l_margin) / (n + 0.5)
                widths = [2 * base_width] + [base_width] * (n - 1)
            
            # Los encabezados son con la fuente seleccionada, en negrita y tamaño 7
            self.set_font(self.myfont, 'B', 7)
            self.set_x(margin_left)

            # Envolvemos el texto de cada encabezado
            header_lines = []  # Cada elemento es una lista de líneas para el header de esa columna
            max_lines = 0
            # Usamos "M" para estimar el ancho promedio de un caracter
            avg_char_width = self.get_string_width("M")
            for i, header in enumerate(headers):
                max_chars = max(1, int(widths[i] / avg_char_width))
                lines = textwrap.wrap(header, width=max_chars)
                header_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)
            header_height = max_lines * line_height
            y_start = self.get_y()
            
            # Mostramos cada celda de encabezado
            for i, lines in enumerate(header_lines):
                x_cell = margin_left + sum(widths[:i])
                for j in range(max_lines):
                    self.set_xy(x_cell, y_start + j * line_height)
                    # Si la celda tiene menos líneas, se imprime vacío en las restantes
                    cell_text = lines[j] if j < len(lines) else ""
                    self.cell(widths[i], line_height, cell_text, border=0, align='C')
            # Dibujamos los bordes para cada celda de encabezado
            for i in range(n):
                self.rect(margin_left + sum(widths[:i]), y_start, widths[i], header_height)
            # Posicionamos el cursor justo al final de la cabecera, sin espacio extra
            self.set_xy(margin_left, y_start + header_height)
            
            # Mostramos los datos con fuente normal y tamaño 7
            self.set_font(self.myfont, '', 7)
            for row in data:
                # Para cada celda de la fila, obtenemos las líneas
                cell_lines = []
                max_lines = 0
                for i in range(n):
                    try:
                        # Intentamos darle formato a los valores numéricos de la tabla
                        num = float(row[i])
                        if len(headers) < 18:
                            cell_text = f"{num:.2f}"
                        else:
                            cell_text = f"{num:.1f}"
                    except (ValueError, TypeError):
                        cell_text = str(row[i])
                    # Centramos los valores en cada celda
                    lines = self.multi_cell(widths[i], line_height, cell_text, border=0, align='C', split_only=True)
                    cell_lines.append(lines)
                    if len(lines) > max_lines:
                        max_lines = len(lines)
                
                # Seleccionamos la altura de las filas
                row_height = max_lines * line_height
                y_start = self.get_y()
                for i in range(n):
                    x = margin_left + sum(widths[:i])
                    for j in range(max_lines):
                        self.set_xy(x, y_start + j * line_height)
                        text_to_print = cell_lines[i][j] if j < len(cell_lines[i]) else ""
                        self.cell(widths[i], line_height, text_to_print, border=0, align='C')
                
                # Dibujamos el borde de cada celda de la fila
                for i in range(n):
                    self.rect(margin_left + sum(widths[:i]), y_start, widths[i], row_height)
                self.set_xy(margin_left, y_start + row_height)

    # Instanciamos la clase
    pdf = PDF()
    pdf.add_page()
    
    # Título de la página
    pdf.set_fill_color(255, 255, 255)  # Fondo de texto blanco
    pdf.set_text_color(67, 142, 189)  # Letra de texto Azul para títulos de encabezados
    pdf.set_font(pdf.myfont, "B", size=12) # Texto en Arial 12 en negrita
    title = page_title # Mostramos el título de la página
    pdf.cell(0, 10, title, 0, 1, 'C')  # Mostramos el texto en el centro
    pdf.ln(5)
    
    # Insertamos logo del equipo
    logo_path = os.path.join("images", "teams", f"{team_id}.png")
    if os.path.exists(logo_path):
        logo_width = 30
        x_logo = (pdf.w - logo_width) / 2
        pdf.image(logo_path, x=x_logo, w=logo_width)
        pdf.ln(5)

    # Obtenemos ancho de la página considerando márgenes
    page_width = pdf.w - 2 * pdf.l_margin
    current_y = pdf.get_y()
    # Calculamos el punto x para centrar e indicamos el tamaño de la imagen
    image_width = 120
    x_centrado = (pdf.w - image_width) / 2

    # Mostramos el texto de lo que trata el pdf
    pdf.set_font(pdf.myfont, "", 12)
    pdf.cell(0, 10, descripcion_contexto, border = str(0), align = "C")
    pdf.ln(15)

    # Introducimos la tabla de las eficiencias
    pdf.set_text_color(0, 0, 0)  # Letra de texto negro para textos
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, "Eficiencia ofensiva y defensiva", border = str(0), align = "C")
    pdf.ln(10)
    # Ajustamos el ancho de cada columna de la tabla en función del número de columnas
    col_width_eficiencia = page_width / len(tabla_headers_eficiencia)
    pdf.create_table(tabla_headers_eficiencia, tabla_data_eficiencia, col_width = col_width_eficiencia)
    pdf.ln(15)
    
    # Introducimos la tabla de los cuatro factores
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, "Cuatro factores equipo", border = str(0), align = "C")
    pdf.ln(10)
    col_width_cuatro_factores = page_width / len(tabla_headers_cuatro_factores)
    pdf.create_table(tabla_headers_cuatro_factores, tabla_data_eficiencia_cuatro_factores, col_width = col_width_cuatro_factores)
    pdf.ln(15)

    # Introducimos la gráfica de evolución temporal del equipo en la temporada
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, f"Evolución temporal {selected_teams}", border = str(0), align = "C")
    pdf.ln(10)
    pdf.set_x(x_centrado)
    pdf.image(rutas_imagenes["temporal"],w=1.1*image_width)
    pdf.ln(15)

    # Introducimos la gráfica de donut de posesiones del equipo
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, f"Distribución de posesiones de {selected_teams}", border = str(0), align = "C")
    pdf.ln(10)
    pdf.set_x(x_centrado)
    pdf.image(rutas_imagenes["donut"], w=image_width)
    pdf.ln(20)

    # Introducimos la gráfica radar de estadísticas avanzadas en la temporada
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, f"Comparativa estadísticas avanzadas de equipo con rivales", border = str(0), align = "C")
    pdf.ln(15)
    pdf.set_x(x_centrado)
    pdf.image(rutas_imagenes["radar"], w=image_width)
    pdf.ln(35)

    # Introducimos la gráfica de donut de posesiones de los rivales
    pdf.set_font(pdf.myfont, "B", 12)
    pdf.cell(page_width, 2, f"Distribución de posesiones de rivales de {selected_teams}", border = str(0), align = "C")
    pdf.ln(10)
    pdf.set_x(x_centrado)
    pdf.image(rutas_imagenes["donut_rivales"], w=image_width)
    pdf.ln(15)

    # Obtenemos ancho de la página considerando márgenes
    page_width = pdf.w - 2 * pdf.l_margin
    current_y = pdf.get_y()

    # Guarda el PDF generado en la carpeta 'assets'
    filename = "performance_report_test.pdf"
    filepath = os.path.join("assets", filename)
    pdf.output(filepath)

    print("Guardando PDF en:", filepath)
    
    return filepath