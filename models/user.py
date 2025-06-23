from utils.database import get_db
# El hashing se hará en la lógica de rutas/servicios, no en el modelo directamente.

class User:
    @staticmethod
    def find_by_username(username_form):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user = %s", (username_form,))
        return cursor.fetchone()

    @staticmethod
    def find_by_id(user_id_session):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id_session,))
        return cursor.fetchone()

    @staticmethod
    def create_user(username_form, hashed_password_string, user_role='user'):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (user, password, role) VALUES (%s, %s, %s)",
                (username_form, hashed_password_string, user_role)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            if hasattr(e, 'args') and e.args[0] == 1062: # Error MySQL para 'Duplicate entry'
                 raise ValueError(f"El nombre de usuario '{username_form}' ya existe.")
            raise
