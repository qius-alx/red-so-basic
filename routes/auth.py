from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from models.user import User # Para buscar usuarios
from utils.auth_helpers import check_password # Para verificar contraseñas
from utils.database import get_db # Para la conexión directa a BD para last_login
from datetime import datetime # Para actualizar last_login
from models.activity_log import ActivityLog # Para registrar actividad

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está en sesión, redirigirlo a la página principal (index)
    if 'user_id' in session:
        return redirect(url_for('index')) # 'index' es la ruta raíz en app.py

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Nombre de usuario y contraseña son requeridos.', 'danger')
            return render_template('login.html')

        # Buscar al usuario en la base de datos
        # User.find_by_username debería devolver un diccionario si se usa DictCursor, o None
        user_data = User.find_by_username(username)

        if user_data:
            # Verificar la contraseña hasheada
            # user_data['password'] debe ser el hash almacenado en la BD
            if check_password(user_data['password'], password):
                # Contraseña correcta, iniciar sesión
                session['user_id'] = user_data['id']
                session['username'] = user_data['user']
                session['user_role'] = user_data['role']

                # Actualizar la columna last_login para el usuario
                try:
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("UPDATE users SET last_login = %s WHERE id = %s",
                                   (datetime.utcnow(), user_data['id']))
                    db.commit()
                except Exception as e:
                    # Registrar el error es importante. Usar current_app.logger si está configurado.
                    current_app.logger.error(f"Error al actualizar last_login para el usuario {username}: {e}")
                    # Notificar al usuario puede ser opcional o un mensaje discreto
                    flash('Hubo un problema al registrar tu hora de conexión, pero estás logueado.', 'warning')

                # Registrar el login en el log de actividad
                ActivityLog.log_user_login(user_id=user_data['id'], ip_address=request.remote_addr)
                current_app.logger.info(f"Login exitoso para usuario '{username}' desde IP {request.remote_addr}. Logged.")


                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('index')) # Redirigir a la página principal
            else:
                # Contraseña incorrecta
                # Registrar intento de login fallido (opcional, podría generar muchos logs)
                # ActivityLog.create_log(user_id=None, action='login_failed', details={'username': username}, ip_address=request.remote_addr)
                # current_app.logger.warn(f"Intento de login fallido para usuario '{username}' desde IP {request.remote_addr}.")
                flash('Nombre de usuario o contraseña incorrectos.', 'danger')
        else:
            # Usuario no encontrado
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')

    # Si es GET o el login falla, mostrar el formulario de login
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    user_id_for_log = session.get('user_id') # Obtener user_id ANTES de limpiar la sesión
    username_for_log = session.get('username', 'Desconocido') # Obtener username para log

    session.clear() # Limpiar todos los datos de la sesión

    if user_id_for_log:
        ActivityLog.log_user_logout(user_id=user_id_for_log, ip_address=request.remote_addr)
        current_app.logger.info(f"Logout para usuario ID {user_id_for_log} ('{username_for_log}'). Logged.")

    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login')) # Redirigir a la página de login
