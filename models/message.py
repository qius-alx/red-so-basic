from utils.database import get_db
from datetime import datetime

class Message:
    @staticmethod
    def create_global_message(user_id, message_content):
        """
        Guarda un mensaje global en la base de datos.
        Devuelve el ID del mensaje insertado o None si falla.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO global_messages (user_id, message) VALUES (%s, %s)",
                (user_id, message_content)
            )
            db.commit()
            return cursor.lastrowid # ID del mensaje insertado
        except Exception as e:
            # print(f"Error al crear mensaje global: {e}") # Para depuración
            db.rollback()
            # Considerar loggear el error con current_app.logger.error(e) si está disponible
            return None

    @staticmethod
    def get_latest_global_messages(limit=30):
        """
        Obtiene los últimos 'limit' mensajes globales de la base de datos.
        Los mensajes se devuelven en orden cronológico (el más antiguo primero).
        """
        db = get_db()
        cursor = db.cursor()
        # Obtener los últimos 'limit' mensajes, ordenados por ID o created_at ascendentemente
        # para que al mostrarlos, el más reciente quede al final/abajo.
        # La subconsulta asegura que tomamos los N más recientes, y luego los ordenamos para visualización.
        query = """
            SELECT gm.id, gm.user_id, u.user as username, gm.message, gm.created_at
            FROM (
                SELECT * FROM global_messages ORDER BY created_at DESC LIMIT %s
            ) gm
            JOIN users u ON gm.user_id = u.id
            ORDER BY gm.created_at ASC;
        """
        try:
            cursor.execute(query, (limit,))
            messages = cursor.fetchall() # Devuelve una lista de diccionarios
            return messages
        except Exception as e:
            # print(f"Error al obtener mensajes globales: {e}") # Para depuración
            # Considerar loggear el error
            return []

    @staticmethod
    def create_private_message(sender_id, receiver_id, message_content):
        """
        Guarda un mensaje privado en la base de datos.
        Devuelve el ID del mensaje insertado o None si falla.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO private_messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                (sender_id, receiver_id, message_content)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            # print(f"Error al crear mensaje privado: {e}") # Para depuración
            db.rollback()
            # Considerar loggear el error
            return None

    @staticmethod
    def get_private_messages_between_users(user1_id, user2_id, limit=30):
        """
        Obtiene los últimos 'limit' mensajes privados entre dos usuarios.
        Los mensajes se devuelven en orden cronológico.
        """
        db = get_db()
        cursor = db.cursor()
        # Similar a global_messages, obtener los N más recientes y luego ordenarlos para visualización.
        query = """
            SELECT pm.id, pm.sender_id, su.user as sender_username,
                   pm.receiver_id, ru.user as receiver_username,
                   pm.message, pm.created_at, pm.is_read
            FROM (
                SELECT * FROM private_messages
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
                ORDER BY created_at DESC
                LIMIT %s
            ) pm
            JOIN users su ON pm.sender_id = su.id
            JOIN users ru ON pm.receiver_id = ru.id
            ORDER BY pm.created_at ASC;
        """
        try:
            cursor.execute(query, (user1_id, user2_id, user2_id, user1_id, limit))
            messages = cursor.fetchall()
            return messages
        except Exception as e:
            # print(f"Error al obtener mensajes privados: {e}") # Para depuración
            # Considerar loggear el error
            return []

    @staticmethod
    def mark_private_messages_as_read(receiver_id, sender_id):
        """
        Marca los mensajes privados de sender_id para receiver_id como leídos.
        Esto se haría, por ejemplo, cuando receiver_id abre la ventana de chat con sender_id.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            # Marcar todos los mensajes no leídos donde el receptor es receiver_id y el emisor es sender_id
            rows_affected = cursor.execute(
                "UPDATE private_messages SET is_read = TRUE "
                "WHERE receiver_id = %s AND sender_id = %s AND is_read = FALSE",
                (receiver_id, sender_id)
            )
            db.commit()
            return rows_affected # Número de mensajes actualizados
        except Exception as e:
            # print(f"Error al marcar mensajes como leídos: {e}") # Para depuración
            db.rollback()
            # Considerar loggear el error
            return 0

    @staticmethod
    def get_unread_private_messages_count(user_id):
        """
        Obtiene el número total de mensajes privados no leídos para un usuario.
        Esto podría usarse para notificaciones.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) as unread_count FROM private_messages "
                "WHERE receiver_id = %s AND is_read = FALSE",
                (user_id,)
            )
            result = cursor.fetchone()
            return result['unread_count'] if result else 0
        except Exception as e:
            # print(f"Error al contar mensajes no leídos: {e}") # Para depuración
            # Considerar loggear el error
            return 0

    # --- Métodos para el Foro (Questions y Answers) ---
    # Estos métodos se añadirían aquí si se decide que la clase Message también maneja
    # la lógica de las preguntas y respuestas del foro. Alternativamente, podrían estar
    # en models/forum.py (Question, Answer). Por simplicidad en el ejemplo, se omite
    # la implementación detallada aquí, pero se mencionan.

    # @staticmethod
    # def create_question(user_id, title, content):
    #     # Lógica para insertar en la tabla 'questions'
    #     pass

    # @staticmethod
    # def get_all_questions(limit=50, offset=0):
    #     # Lógica para obtener preguntas, posiblemente con paginación
    #     pass

    # @staticmethod
    # def get_question_by_id(question_id):
    #     # Lógica para obtener una pregunta específica y sus respuestas
    #     pass

    # @staticmethod
    # def create_answer(question_id, user_id, content):
    #     # Lógica para insertar en la tabla 'answers'
    #     pass

    # @staticmethod
    # def get_answers_for_question(question_id):
    #     # Lógica para obtener respuestas de una pregunta
    #     pass
