from utils.database import get_db
# El hashing y la verificación de contraseñas se manejan en auth_helpers.py
# y en las rutas o comandos CLI directamente.

class User:
    @staticmethod
    def find_by_username(username_form):
        """Encuentra un usuario por su nombre de usuario."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user = %s", (username_form,))
        return cursor.fetchone() # Devuelve un diccionario o None

    @staticmethod
    def find_by_id(user_id_session):
        """Encuentra un usuario por su ID."""
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id_session,))
        return cursor.fetchone() # Devuelve un diccionario o None

    @staticmethod
    def create_user(username_form, hashed_password_string, user_role='user'):
        """Crea un nuevo usuario."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (user, password, role) VALUES (%s, %s, %s)",
                (username_form, hashed_password_string, user_role)
            )
            db.commit()
            return cursor.lastrowid # Devuelve el ID del nuevo usuario
        except Exception as e:
            db.rollback()
            if hasattr(e, 'args') and e.args[0] == 1062: # Error MySQL para 'Duplicate entry'
                 raise ValueError(f"El nombre de usuario '{username_form}' ya existe.")
            # Considerar loggear el error: current_app.logger.error(f"Error al crear usuario: {e}")
            raise # Re-lanzar para manejo en la capa superior

    @staticmethod
    def get_all_users(page=1, per_page=15):
        """Obtiene todos los usuarios con paginación."""
        db = get_db()
        cursor = db.cursor()
        offset = (page - 1) * per_page
        try:
            cursor.execute(
                "SELECT id, user, role, created_at, last_login FROM users ORDER BY id ASC LIMIT %s OFFSET %s",
                (per_page, offset)
            )
            users = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']

            return users, total_users
        except Exception as e:
            # current_app.logger.error(f"Error al obtener todos los usuarios: {e}")
            return [], 0

    @staticmethod
    def update_user_details(user_id, new_username=None, new_hashed_password=None, new_role=None):
        """
        Actualiza los detalles de un usuario existente.
        Solo actualiza los campos que se proporcionan (no son None).
        """
        db = get_db()
        cursor = db.cursor()

        fields_to_update = []
        values = []

        if new_username:
            fields_to_update.append("user = %s")
            values.append(new_username)
        if new_hashed_password:
            fields_to_update.append("password = %s")
            values.append(new_hashed_password)
        if new_role:
            fields_to_update.append("role = %s")
            values.append(new_role)

        if not fields_to_update:
            return 0 # No hay nada que actualizar

        values.append(user_id) # Para la cláusula WHERE

        query = f"UPDATE users SET {', '.join(fields_to_update)} WHERE id = %s"

        try:
            cursor.execute(query, tuple(values))
            db.commit()
            return cursor.rowcount # Número de filas afectadas
        except Exception as e:
            db.rollback()
            if hasattr(e, 'args') and e.args[0] == 1062: # Duplicate entry for username
                raise ValueError(f"El nuevo nombre de usuario '{new_username}' ya está en uso.")
            # current_app.logger.error(f"Error al actualizar usuario {user_id}: {e}")
            raise

    @staticmethod
    def delete_user_by_id(user_id):
        """Elimina un usuario por su ID."""
        db = get_db()
        cursor = db.cursor()
        try:
            # Considerar qué sucede con el contenido del usuario (mensajes, preguntas).
            # schema.sql usa ON DELETE CASCADE o ON DELETE SET NULL para algunas tablas.
            # Si un admin se borra a sí mismo, la sesión debe ser invalidada en la ruta.
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            db.commit()
            return cursor.rowcount # Número de filas eliminadas
        except Exception as e:
            db.rollback()
            # current_app.logger.error(f"Error al eliminar usuario {user_id}: {e}")
            raise
