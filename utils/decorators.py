from functools import wraps
from flask import session, redirect, url_for, flash # Eliminado current_app por ahora

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'admin':
            flash('No tienes permisos de administrador para acceder.', 'danger')
            return redirect(url_for('index')) # Redirige a la ruta raíz de la app
        return f(*args, **kwargs)
    return decorated_function
