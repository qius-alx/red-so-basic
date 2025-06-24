import json
from utils.database import get_db
from datetime import datetime

class ActivityLog:
    @staticmethod
    def create_log(user_id, action, details=None, ip_address=None):
        """
        Registra una nueva actividad en la base de datos.
        - user_id: ID del usuario que realiza la acción (puede ser None para acciones del sistema).
        - action: Descripción de la acción (ej: 'login', 'create_user', 'send_message').
        - details: Un diccionario con detalles adicionales, se guardará como JSON.
        - ip_address: Dirección IP desde donde se realizó la acción.
        """
        db = get_db()
        cursor = db.cursor()

        # Convertir el diccionario de detalles a una cadena JSON
        details_json = json.dumps(details) if details is not None else None

        try:
            cursor.execute(
                """
                INSERT INTO activity_logs (user_id, action, details, ip_address, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, action, details_json, ip_address, datetime.utcnow())
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            # En un sistema real, aquí se debería loggear el error de forma más robusta.
            # print(f"Error al crear log de actividad: {e}")
            # Considerar usar current_app.logger.error() si está disponible en el contexto.
            # No relanzar el error para no interrumpir la acción principal que se está loggeando.
            return None

    @staticmethod
    def get_logs(page=1, per_page=20, user_id_filter=None, action_filter=None, start_date=None, end_date=None):
        """
        Obtiene logs de actividad con filtros y paginación.
        - user_id_filter: Filtra por ID de usuario.
        - action_filter: Filtra por tipo de acción (puede usar LIKE %action%).
        - start_date, end_date: Filtran por rango de fechas (objetos datetime).
        """
        db = get_db()
        cursor = db.cursor()

        base_query = """
            SELECT al.id, al.user_id, u.user AS username, al.action,
                   al.details, al.ip_address, al.created_at
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
        """
        count_query = "SELECT COUNT(*) as total_logs FROM activity_logs"

        conditions = []
        params = []

        if user_id_filter is not None:
            conditions.append("al.user_id = %s")
            params.append(user_id_filter)
        if action_filter:
            conditions.append("al.action LIKE %s")
            params.append(f"%{action_filter}%")
        if start_date:
            conditions.append("al.created_at >= %s")
            params.append(start_date)
        if end_date:
            # Para que end_date sea inclusivo, se podría ajustar a fin del día si solo se pasa fecha.
            conditions.append("al.created_at <= %s")
            params.append(end_date)

        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause

        base_query += " ORDER BY al.created_at DESC"

        offset = (page - 1) * per_page
        base_query += " LIMIT %s OFFSET %s"
        query_params_paginated = tuple(params) + (per_page, offset)
        query_params_count = tuple(params)

        try:
            cursor.execute(base_query, query_params_paginated)
            logs_data = cursor.fetchall()

            # Parsear la cadena JSON de 'details' de nuevo a un diccionario
            logs = []
            for log_row in logs_data:
                log_dict = dict(log_row) # Convertir Row object a dict si es necesario (depende del cursor)
                if log_dict.get('details'):
                    try:
                        log_dict['details'] = json.loads(log_dict['details'])
                    except json.JSONDecodeError:
                        # Si hay error, dejar 'details' como la cadena original o un mensaje de error
                        log_dict['details'] = {"error": "No se pudo parsear JSON", "original": log_dict['details']}
                logs.append(log_dict)

            cursor.execute(count_query, query_params_count)
            total_logs = cursor.fetchone()['total_logs']

            return logs, total_logs
        except Exception as e:
            # print(f"Error al obtener logs de actividad: {e}")
            # Considerar usar current_app.logger.error()
            return [], 0

    # Ejemplo de una acción específica de logueo
    @staticmethod
    def log_user_login(user_id, ip_address):
        return ActivityLog.create_log(user_id, 'user_login', ip_address=ip_address)

    @staticmethod
    def log_user_logout(user_id, ip_address=None): # ip_address puede ser None si no se puede obtener al logout
        return ActivityLog.create_log(user_id, 'user_logout', ip_address=ip_address)

    @staticmethod
    def log_message_sent(user_id, message_type, message_id, receiver_id=None, ip_address=None):
        details = {'message_type': message_type, 'message_id': message_id}
        if receiver_id:
            details['receiver_id'] = receiver_id
        action = 'send_private_message' if message_type == 'private' else 'send_global_message'
        return ActivityLog.create_log(user_id, action, details=details, ip_address=ip_address)

    @staticmethod
    def log_forum_activity(user_id, action_type, item_id, ip_address=None):
        # action_type: 'create_question', 'create_answer'
        # item_id: ID de la pregunta o respuesta creada
        details = {'item_id': item_id}
        return ActivityLog.create_log(user_id, action_type, details=details, ip_address=ip_address)

    @staticmethod
    def log_admin_action(admin_user_id, action, target_user_id=None, details=None, ip_address=None):
        log_details = details if details is not None else {}
        if target_user_id:
            log_details['target_user_id'] = target_user_id

        # Prepend 'admin_' to action to differentiate from user actions if needed
        admin_action_name = f"admin_{action}"
        return ActivityLog.create_log(admin_user_id, admin_action_name, details=log_details, ip_address=ip_address)
