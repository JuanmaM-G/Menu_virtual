from flask import Flask, flash, redirect, url_for, render_template, request, session, jsonify
import mysql.connector
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# ----------------------------
# Configuración de la app
# ----------------------------
app = Flask(__name__)
app.secret_key = 'clave_secreta'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# ----------------------------
# Configuración de uploads
# ----------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea la carpeta si no existe

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------
# Configuración de base de datos
# ----------------------------
db_config = {
    'host': 'localhost',
    'user': 'carmentea',
    'password': 'password',
    'database': 'arepas'
}

def get_db_connection():
    """Devuelve una nueva conexión a la base de datos"""
    return mysql.connector.connect(**db_config)

# =======================================================================================================

# ====================================================================
#            <<------------------- Ruta principal ------------------->>
# ====================================================================
@app.route('/')
def index():
    # Rol (0 = no registrado, 1 = usuario, 2 = admin)
    rol = session.get('rol', 0)

    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    menus = cursor.fetchall()
    cursor.close()
    conn.close()

    
    return render_template('index.html', menus=menus, rol=rol)


# ====================================================================
#            <<------------------- Rutas secundarias ------------------->>
# ====================================================================
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
    # Solo accesible para administradores
    if 'logged_in' in session and session.get('rol') == 2:
        if request.method == 'POST':
            # Obtener campos del formulario
            titulo = request.form['titulo']
            descripcion = request.form.get('descripcion', '')
            categoria = int(request.form['categoria'])
            precio = int(request.form['precio'])  # Valor entero

            # Validar imagen principal
            if 'imagen' not in request.files:
                return "Error: No se encontró la imagen"

            file = request.files['imagen']
            if file.filename == '' or not allowed_file(file.filename):
                return "Error: Imagen inválida"

            # Conexión a base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar ítem con imagen temporalmente vacía
            cursor.execute(
                "INSERT INTO menu (titulo, descripcion, precio, imagen, categoria) VALUES (%s, %s, %s, %s, %s)",
                (titulo, descripcion, precio, '', categoria)
            )
            menu_id = cursor.lastrowid

            # Guardar imagen con nombre seguro y único
            filename = secure_filename(f"menu_{menu_id}_" + file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Actualizar ruta de la imagen en la BD
            cursor.execute(
                "UPDATE menu SET imagen = %s WHERE id = %s",
                (filename, menu_id)
            )

            # Finalizar
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('index'))

        # GET: mostrar formulario
        return render_template('menu.html', rol=2)
    
    # Si no es admin o no está logueado
    return "No tienes permisos", 403



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# = = = > ELIMINAR MENU < = = =
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/eliminar_menu/<int:menu_id>', methods=['POST'])
def eliminar_menu(menu_id):
    # Solo admin puede eliminar
    if 'logged_in' in session and session.get('rol') == 2:
        conn = get_db_connection()
        cursor = conn.cursor()

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
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar el menú: {e}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    # Si no es admin o no está logueado
    return "No tienes permisos", 403



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# = = = > ACTUALIZAR MENU < = = =
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@app.route('/actualizar_menu/<int:menu_id>', methods=['GET', 'POST'])
def actualizar_menu(menu_id):
    # Solo admin puede actualizar
    if 'logged_in' in session and session.get('rol') == 2:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # 1. Obtener datos del formulario
            titulo = request.form.get('titulo')
            descripcion = request.form.get('descripcion', '')
            categoria = int(request.form.get('categoria'))
            precio = int(request.form.get('precio'))  # valor entero

            # 2. Actualizar datos básicos en la BD
            cursor.execute("""
                UPDATE menu
                SET titulo = %s, descripcion = %s, categoria = %s, precio = %s
                WHERE id = %s
            """, (titulo, descripcion, categoria, precio, menu_id))

            # 3. Actualizar imagen principal si se subió nueva
            if 'imagen_principal' in request.files:
                nueva_imagen = request.files['imagen_principal']
                if nueva_imagen and nueva_imagen.filename != '':
                    # Eliminar imagen anterior
                    cursor.execute("SELECT imagen FROM menu WHERE id = %s", (menu_id,))
                    menu = cursor.fetchone()
                    if menu and menu['imagen']:
                        ruta_ant = os.path.join(app.config['UPLOAD_FOLDER'], menu['imagen'])
                        if os.path.exists(ruta_ant):
                            os.remove(ruta_ant)

                    # Guardar nueva imagen
                    filename = secure_filename(nueva_imagen.filename)
                    nueva_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    cursor.execute("UPDATE menu SET imagen = %s WHERE id = %s", (filename, menu_id))

            # Confirmar cambios y cerrar conexión
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('index'))

        # GET: obtener datos actuales del menú
        cursor.execute("SELECT * FROM menu WHERE id = %s", (menu_id,))
        menu = cursor.fetchone()  # directamente como 'menu'
        cursor.close()
        conn.close()

        return render_template("actualizar_menu.html", menu=menu, rol=2)

    # Si no es admin o no está logueado
    return "No tienes permisos", 403




# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)