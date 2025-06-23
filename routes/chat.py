from flask import Blueprint, render_template, request, session, current_app
from flask_socketio import emit, join_room, leave_room
from utils.decorators import login_required
from models.message import Message # Asumiendo que este modelo ya existe y funciona
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def index():
    return render_template('chat.html', username=session.get('username'))

# --- Definiciones de Manejadores de Eventos SocketIO ---
# Estas funciones serán llamadas por la instancia de SocketIO principal.
# El decorador @socketio.on se aplicará en la función de registro o directamente en app.py.

def on_chat_connect():
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id:
        current_app.logger.warn(f"Conexión a /chat rechazada para SID {request.sid}: Sin user_id en sesión.")
        emit('error', {'message': 'Autenticación requerida.'}, room=request.sid)
        return False # Prevenir la conexión

    current_app.logger.info(f"Usuario {username} (ID: {user_id}, SID: {request.sid}) conectado a namespace /chat.")
    join_room('global_chat_room')
    emit('status', {'message': f'¡Bienvenido al chat, {username}!'}, room=request.sid)

    try:
        # Corregido: Límite cambiado de 50 a 30.
        messages = Message.get_latest_global_messages(limit=30)
        # Asumimos que Message.get_latest_global_messages ya formatea los timestamps si es necesario,
        # o devuelve objetos datetime que SocketIO puede serializar (a menudo a ISO 8601).
        # El cliente (chat.html) es responsable de mostrar el timestamp en formato legible.
        emit('load_old_messages', {'messages': messages}, room=request.sid)
        current_app.logger.info(f"Enviados {len(messages)} mensajes antiguos a {username}.")
    except Exception as e:
        current_app.logger.error(f"Error al cargar historial para {username}: {e}")
        emit('error', {'message': 'Error al cargar historial de mensajes.'}, room=request.sid)

    emit('user_joined', {'username': username, 'sid': request.sid}, room='global_chat_room', include_self=False)

def on_chat_disconnect():
    username = session.get('username', 'Un usuario')
    user_id = session.get('user_id')
    current_app.logger.info(f"Usuario {username} (ID: {user_id}, SID: {request.sid}) desconectado de /chat.")
    leave_room('global_chat_room')
    emit('user_left', {'username': username, 'sid': request.sid}, room='global_chat_room')

def on_send_global_message(data):
    user_id = session.get('user_id')
    username = session.get('username')
    message_content = data.get('message', '').strip()

    if not user_id: # Chequeo de seguridad
        emit('error', {'message': 'No estás autenticado.'}, room=request.sid)
        return

    if not message_content:
        emit('error', {'message': 'El mensaje no puede estar vacío.'}, room=request.sid)
        return

    try:
        message_id = Message.create_global_message(user_id, message_content)
        if message_id:
            current_app.logger.info(f"Mensaje (ID: {message_id}) de {username} guardado.")
            new_message_data = {
                'id': message_id,
                'username': username,
                'message': message_content,
                'user_id': user_id, # Para que el cliente pueda identificar sus propios mensajes
                'timestamp': datetime.utcnow().isoformat() + "Z" # Formato ISO 8601 con Z para UTC
            }
            emit('new_global_message', new_message_data, room='global_chat_room')
        else:
            emit('error', {'message': 'Error al guardar el mensaje en el servidor.'}, room=request.sid)
    except Exception as e:
        current_app.logger.error(f"Error en on_send_global_message por {username}: {e}")
        emit('error', {'message': 'Error interno al enviar mensaje.'}, room=request.sid)

# (Los manejadores de mensajes privados se omiten aquí, se abordarán en su propio paso)

# Función que será llamada desde app.py para registrar estos manejadores
def register_chat_event_handlers(socketio_instance):
    socketio_instance.on_event('connect', on_chat_connect, namespace='/chat')
    socketio_instance.on_event('disconnect', on_chat_disconnect, namespace='/chat')
    socketio_instance.on_event('send_global_message', on_send_global_message, namespace='/chat')
    # No se necesita un evento 'request_history' si se carga al conectar.
    current_app.logger.info("Manejadores de eventos SocketIO del chat registrados para el namespace /chat.")
