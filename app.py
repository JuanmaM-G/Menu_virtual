from flask import Flask, flash, redirect, url_for, render_template, request, session, jsonify
import mysql.connector
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = 'clave_secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'carmentea',
    'password': 'password',
    'database': 'arepas'
}

def conectar_db():
    return mysql.connector.connect(**db_config)


db_connection = mysql.connector.connect(**db_config)
cursor = db_connection.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(**db_config)




app = Flask(__name__)

@app.route('/')
def index():
    return render_template ('index.html')

@app.route('/navbar')
def navbar():
    return render_template ('navbar.html')

@app.route('/footer')
def footer():
    return render_template ('footer.html')


# ====================================================================
#            <<------------------- MENU ------------------->>
# ====================================================================

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# = = = > SUBIR MENU < = = =
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/menu', methods=['GET', 'POST'])
def agregar_menu():
    if request.method == 'POST':
        # Obtener campos del formulario
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        precio = request.form['precio']

        # Validar imagen principal
        if 'imagen' not in request.files:
            return "Error: No se encontró la imagen"

        file = request.files['imagen']
        if file.filename == '' or not allowed_file(file.filename):
            return "Error: Imagen inválida"

        # Conexión a base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()

        # Insertar ítem del menú con imagen temporalmente vacía
        sql_item = """
            INSERT INTO menu (titulo, descripcion, precio, imagen, categoria)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores_item = (titulo, descripcion, precio, '', categoria)
        cursor.execute(sql_item, valores_item)
        menu_id = cursor.lastrowid

        # Guardar imagen con nombre único
        filename = secure_filename(f"menu_{menu_id}_" + file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Actualizar la ruta de la imagen en la BD
        cursor.execute(
            "UPDATE menu SET imagen = %s WHERE id = %s",
            (filename, menu_id)
        )

        # Finalizar
        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('mostrar_menu'))  
    return render_template('menu.html')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# = = = > ELIMINAR MENU < = = =
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/eliminar_menu/<int:menu_id>', methods=['POST'])
def eliminar_menu(menu_id):
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        # Obtener nombre de la imagen principal
        cursor.execute("SELECT imagen FROM menu WHERE id = %s", (menu_id,))
        resultado = cursor.fetchone()
        if resultado and resultado[0]:
            imagen = resultado[0]
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], imagen)
            try:
                if os.path.exists(ruta_imagen):
                    os.remove(ruta_imagen)
            except Exception as e:
                print(f"No se pudo eliminar la imagen: {e}")

        # Eliminar ítem del menú de la base de datos
        cursor.execute("DELETE FROM menu WHERE id = %s", (menu_id,))
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar el menú: {e}")
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for('obtener_menu')) 


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# = = = > ACTUALIZAR MENU < = = =
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def convertir_a_float(valor):
    return float(valor) if valor and valor.strip() else None

@app.route('/actualizar_menu/<int:menu_id>', methods=['GET', 'POST'])
def actualizar_menu(menu_id):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        # 1. Obtener datos del formulario
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        categoria = request.form.get('categoria')
        precio = convertir_a_float(request.form.get('precio'))

        # 2. Actualizar datos básicos
        cursor.execute("""
            UPDATE menu
            SET titulo = %s, descripcion = %s, categoria = %s, precio = %s
            WHERE id = %s
        """, (titulo, descripcion, categoria, precio, menu_id))

        # 3. Actualizar imagen principal (si hay nueva)
        if 'imagen' in request.files:
            nueva_imagen = request.files['imagen']
            if nueva_imagen and nueva_imagen.filename != '':
                # Eliminar imagen anterior
                cursor.execute("SELECT imagen FROM menu WHERE id = %s", (menu_id,))
                anterior = cursor.fetchone()
                if anterior and anterior['imagen']:
                    ruta_ant = os.path.join(app.config['UPLOAD_FOLDER'], anterior['imagen'])
                    if os.path.exists(ruta_ant):
                        os.remove(ruta_ant)

                # Guardar nueva imagen
                filename = secure_filename(nueva_imagen.filename)
                nueva_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute("UPDATE menu SET imagen = %s WHERE id = %s", (filename, menu_id))

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for('obtener_menu'))

    # Si es GET, renderiza el formulario con los datos actuales
    cursor.execute("SELECT * FROM menu WHERE id = %s", (menu_id,))
    item = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template("actualizar_menu.html", item=item)



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)