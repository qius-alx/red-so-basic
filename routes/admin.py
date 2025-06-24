from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash, current_app
)
from utils.decorators import admin_required # Asegura que solo los admins accedan
from models.user import User # Para interactuar con los datos de usuario
from utils.auth_helpers import hash_password # Para hashear contraseñas si se cambian
from models.activity_log import ActivityLog # Para registrar actividad
from math import ceil # Para la paginación

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@admin_required # Aplica a todas las rutas en este blueprint
def ensure_admin():
    # Esta función se ejecuta antes de cada request a una ruta de este blueprint.
    # El decorador @admin_required ya maneja la lógica de redirección si no es admin.
    pass

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Página principal del panel de administración."""
    # Podría mostrar estadísticas generales, etc.
    # Por ahora, solo una bienvenida.
    return render_template('admin/dashboard.html')

@admin_bp.route('/users')
def list_users():
    """Muestra una lista paginada de todos los usuarios."""
    page = request.args.get('page', 1, type=int)
    per_page = 15 # O current_app.config.get('ADMIN_USERS_PER_PAGE', 15)

    try:
        users, total_users = User.get_all_users(page=page, per_page=per_page)
    except Exception as e:
        current_app.logger.error(f"Error al obtener la lista de usuarios para admin: {e}")
        flash("Error al cargar la lista de usuarios.", "danger")
        users = []
        total_users = 0

    total_pages = ceil(total_users / per_page)

    return render_template(
        'admin/users_list.html',
        users=users,
        current_page=page,
        total_pages=total_pages
    )

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Permite editar los detalles de un usuario."""
    user = User.find_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "warning")
        return redirect(url_for('admin.list_users'))

    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '').strip() # Contraseña en texto plano
        new_role = request.form.get('role', '').strip()

        if not new_username:
            flash("El nombre de usuario no puede estar vacío.", "danger")
            return render_template('admin/user_edit.html', user=user) # Re-render con error

        # Validar rol
        if new_role not in ['user', 'admin']:
            flash("Rol inválido. Debe ser 'user' o 'admin'.", "danger")
            return render_template('admin/user_edit.html', user=user)

        new_hashed_password = None
        if new_password: # Solo hashear y actualizar si se proveyó una nueva contraseña
            new_hashed_password = hash_password(new_password)

        try:
            # Solo pasar el nuevo username si es diferente al actual para evitar error de duplicado innecesario
            username_to_update = new_username if new_username != user['user'] else None

            User.update_user_details(
                user_id=user_id,
                new_username=username_to_update,
                new_hashed_password=new_hashed_password,
                new_role=new_role
            )
            ActivityLog.log_admin_action(admin_user_id=session.get('user_id'), action='edit_user',
                                         target_user_id=user_id, ip_address=request.remote_addr,
                                         details={'username': new_username, 'role': new_role, 'password_changed': bool(new_password)})
            current_app.logger.info(f"Admin (ID: {session.get('user_id')}) editó usuario (ID: {user_id}). Logged.")
            flash(f"Usuario '{new_username}' actualizado correctamente.", "success")
            return redirect(url_for('admin.list_users'))
        except ValueError as ve: # Capturar error de nombre de usuario duplicado
            flash(str(ve), "danger")
        except Exception as e:
            current_app.logger.error(f"Error al actualizar usuario {user_id}: {e}")
            flash("Error interno al actualizar el usuario.", "danger")

        # Si hay error, volver a cargar los datos del usuario para el formulario
        # pero con los valores que el admin intentó enviar (excepto password)
        user_form_data = dict(user) # Copia para no modificar el original directamente
        user_form_data['user'] = new_username
        user_form_data['role'] = new_role
        return render_template('admin/user_edit.html', user=user_form_data)

    # Método GET: mostrar el formulario con los datos actuales del usuario
    return render_template('admin/user_edit.html', user=user)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Elimina un usuario."""
    # Prevenir que un admin se elimine a sí mismo
    if 'user_id' in session and session['user_id'] == user_id:
        flash("No puedes eliminar tu propia cuenta de administrador desde aquí.", "danger")
        return redirect(url_for('admin.list_users'))

    user_to_delete = User.find_by_id(user_id)
    if not user_to_delete:
        flash("Usuario no encontrado para eliminar.", "warning")
        return redirect(url_for('admin.list_users'))

    try:
        rows_affected = User.delete_user_by_id(user_id)
        if rows_affected > 0:
            ActivityLog.log_admin_action(admin_user_id=session.get('user_id'), action='delete_user',
                                         target_user_id=user_id, ip_address=request.remote_addr,
                                         details={'deleted_username': user_to_delete['user']})
            current_app.logger.info(f"Admin (ID: {session.get('user_id')}) eliminó usuario (ID: {user_id}, Username: {user_to_delete['user']}). Logged.")
            flash(f"Usuario '{user_to_delete['user']}' eliminado correctamente.", "success")
        else:
            # Esto podría ocurrir si el usuario fue eliminado por otro proceso entre find_by_id y delete
            flash(f"No se pudo eliminar el usuario '{user_to_delete['user']}'. Puede que ya haya sido eliminado.", "warning")
    except Exception as e:
        current_app.logger.error(f"Error al eliminar usuario {user_id}: {e}")
        flash(f"Error interno al intentar eliminar el usuario '{user_to_delete['user']}'.", "danger")

    return redirect(url_for('admin.list_users'))

@admin_bp.route('/activity-logs')
def view_activity_logs():
    """Muestra los logs de actividad con paginación y filtros."""
    page = request.args.get('page', 1, type=int)
    per_page = 25 # O current_app.config.get('ADMIN_LOGS_PER_PAGE', 25)

    # Filtros (ejemplos básicos, se pueden expandir)
    user_id_filter = request.args.get('user_id', None, type=int)
    action_filter = request.args.get('action', None, type=str)
    # start_date_filter = request.args.get('start_date', None, type=str) # Necesitaría parsing a datetime
    # end_date_filter = request.args.get('end_date', None, type=str)   # Necesitaría parsing a datetime

    try:
        logs, total_logs = ActivityLog.get_logs(
            page=page,
            per_page=per_page,
            user_id_filter=user_id_filter,
            action_filter=action_filter
            # start_date=parsed_start_date, # Si se implementa parsing
            # end_date=parsed_end_date    # Si se implementa parsing
        )
    except Exception as e:
        current_app.logger.error(f"Error al obtener logs de actividad para admin: {e}")
        flash("Error al cargar los logs de actividad.", "danger")
        logs = []
        total_logs = 0

    total_pages = ceil(total_logs / per_page)

    return render_template(
        'admin/activity_logs.html',
        logs=logs,
        current_page=page,
        total_pages=total_pages,
        user_id_filter=user_id_filter, # Para mantener filtros en paginación
        action_filter=action_filter   # Para mantener filtros en paginación
    )
