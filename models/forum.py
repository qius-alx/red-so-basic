from utils.database import get_db
from datetime import datetime

class Question:
    @staticmethod
    def create(user_id, title, content):
        """Crea una nueva pregunta en el foro."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO questions (user_id, title, content) VALUES (%s, %s, %s)",
                (user_id, title, content)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            # Considerar loggear el error: current_app.logger.error(f"Error al crear pregunta: {e}")
            raise # Re-lanzar para que la ruta lo maneje o se muestre un error genérico

    @staticmethod
    def get_all(page=1, per_page=10):
        """
        Obtiene todas las preguntas del foro, paginadas.
        Incluye el nombre de usuario del autor.
        Ordena por fecha de creación descendente (más nuevas primero).
        """
        db = get_db()
        cursor = db.cursor()
        offset = (page - 1) * per_page
        try:
            cursor.execute(
                """
                SELECT q.id, q.user_id, q.title, q.content, q.created_at, u.user AS username
                FROM questions q
                JOIN users u ON q.user_id = u.id
                ORDER BY q.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (per_page, offset)
            )
            questions = cursor.fetchall() # Lista de diccionarios

            # Obtener el total de preguntas para la paginación
            cursor.execute("SELECT COUNT(*) as total_questions FROM questions")
            total_questions = cursor.fetchone()['total_questions']

            return questions, total_questions
        except Exception as e:
            # Considerar loggear el error
            # current_app.logger.error(f"Error al obtener todas las preguntas: {e}")
            return [], 0

    @staticmethod
    def find_by_id(question_id):
        """
        Encuentra una pregunta por su ID.
        Incluye el nombre de usuario del autor.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                SELECT q.id, q.user_id, q.title, q.content, q.created_at, u.user AS username
                FROM questions q
                JOIN users u ON q.user_id = u.id
                WHERE q.id = %s
                """,
                (question_id,)
            )
            return cursor.fetchone() # Un solo diccionario o None
        except Exception as e:
            # Considerar loggear el error
            # current_app.logger.error(f"Error al buscar pregunta por ID {question_id}: {e}")
            return None

    @staticmethod
    def get_answers(question_id):
        """
        Obtiene todas las respuestas para una pregunta dada, ordenadas por fecha.
        Incluye el nombre de usuario del autor de la respuesta.
        """
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                SELECT a.id, a.user_id, a.content, a.created_at, u.user AS username
                FROM answers a
                JOIN users u ON a.user_id = u.id
                WHERE a.question_id = %s
                ORDER BY a.created_at ASC
                """,
                (question_id,)
            )
            return cursor.fetchall() # Lista de diccionarios
        except Exception as e:
            # Considerar loggear el error
            # current_app.logger.error(f"Error al obtener respuestas para pregunta {question_id}: {e}")
            return []

class Answer:
    @staticmethod
    def create(question_id, user_id, content):
        """Crea una nueva respuesta a una pregunta."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO answers (question_id, user_id, content) VALUES (%s, %s, %s)",
                (question_id, user_id, content)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            # Considerar loggear el error
            # current_app.logger.error(f"Error al crear respuesta: {e}")
            raise # Re-lanzar para que la ruta lo maneje

    # No se necesita un 'get_all' para Answers independiente de Questions usualmente.
    # Se obtienen a través de Question.get_answers(question_id).
    # Podría haber un find_by_id si se necesitara editar/borrar respuestas directamente.
    @staticmethod
    def find_by_id(answer_id):
        """Encuentra una respuesta por su ID (si fuera necesario para editar/borrar)."""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                SELECT a.id, a.question_id, a.user_id, a.content, a.created_at, u.user AS username
                FROM answers a
                JOIN users u ON a.user_id = u.id
                WHERE a.id = %s
                """,
                (answer_id,)
            )
            return cursor.fetchone()
        except Exception as e:
            # current_app.logger.error(f"Error al buscar respuesta por ID {answer_id}: {e}")
            return None
