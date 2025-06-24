from flask import (
    Flask, session, redirect, url_for, render_template, request, flash
)
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
import click # For CLI commands

from config import Config
from utils import database
from utils.decorators import login_required # Decorator for login
from utils.auth_helpers import hash_password # For hashing password in CLI
from models.user import User # For User model in CLI

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
database.init_app(app) # Configura el teardown de la BD y puede inicializar MySQL
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Blueprints ---
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from routes.chat import chat_bp, register_chat_event_handlers # Importar la función de registro
app.register_blueprint(chat_bp, url_prefix='/chat') # Registrarlo

from routes.forum import forum_bp # Importar el blueprint del foro
app.register_blueprint(forum_bp, url_prefix='/forum') # Registrarlo

from routes.admin import admin_bp # Importar el blueprint de administración
app.register_blueprint(admin_bp, url_prefix='/admin') # Registrarlo

# Registrar manejadores de eventos SocketIO del chat
register_chat_event_handlers(socketio)

# --- Main Routes ---
@app.route('/')
def index():
    if 'user_id' in session:
        # Si el usuario está en sesión, redirige a la página principal del chat blueprint
        return redirect(url_for('chat.index'))
    # Si no, redirige a la página de login del blueprint de autenticación
    return redirect(url_for('auth.login'))

# La ruta '/main_chat_placeholder' ha sido eliminada ya que su funcionalidad
# es ahora manejada por la ruta '/' del chat_bp.

# --- CLI Commands ---
@app.cli.command("create-admin")
@click.argument("username", default="62528438")
@click.argument("password", default="2023107007")
def create_admin_command(username, password):
    """Crea o actualiza un usuario administrador."""
    with app.app_context():
        try:
            hashed_pwd = hash_password(password)

            # Usar el método estático de la clase User para obtener la conexión a la BD
            # Esto asume que get_db() y las operaciones del cursor están manejadas dentro de los métodos de User
            # o que necesitamos obtener la db y cursor aquí si User.update no existe.

            db = database.get_db() # Obtener la conexión a la BD
            cursor = db.cursor()

            user = User.find_by_username(username)

            if user:
                # Si el usuario existe, actualizar contraseña y rol
                # Asumiendo que 'user' es un diccionario (DictCursor)
                cursor.execute(
                    "UPDATE users SET password = %s, role = %s WHERE id = %s",
                    (hashed_pwd, 'admin', user['id'])
                )
                db.commit()
                click.echo(f"Usuario '{username}' actualizado a rol 'admin' y contraseña actualizada.")
            else:
                # Si el usuario no existe, crearlo
                User.create_user(username, hashed_pwd, 'admin')
                # User.create_user ya hace commit, así que no es necesario aquí.
                click.echo(f"Usuario administrador '{username}' creado exitosamente.")

        except ValueError as ve: # Capturar error de usuario duplicado de User.create_user
             click.echo(f"Error: {ve}")
        except Exception as e:
            # database.get_db().rollback() # Asegurar rollback en caso de otros errores
            click.echo(f"Error al crear/actualizar administrador: {e}")
            # Considerar loggear el error completo para depuración
            # current_app.logger.error(f"Error en create-admin: {e}")


if __name__ == '__main__':
    # Para desarrollo, debug=True es útil.
    # use_reloader=True es el default y ayuda con el desarrollo.
    # allow_unsafe_werkzeug=True puede ser necesario para algunos entornos de desarrollo,
    # especialmente si se usa el reloader con ciertos tipos de errores.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True, allow_unsafe_werkzeug=True)