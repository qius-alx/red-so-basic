from flask import Blueprint, render_template, request, session, current_app
from flask_socketio import emit, join_room, leave_room
from utils.decorators import login_required
from models.message import Message
from models.user import User
from models.activity_log import ActivityLog # Para registrar actividad
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/')
@login_required
def index():
    return render_template('chat.html', username=session.get('username'))

@chat_bp.route('/users')
@login_required
def list_users_for_chat():
    current_user_id = session.get('user_id')
    all_users_data, _ = User.get_all_users(page=1, per_page=1000) # Get all users

    other_users_with_unread = []
    if all_users_data:
        for user_data_item in all_users_data: # Changed loop variable name
            if user_data_item['id'] != current_user_id:
                # Obtener el recuento de mensajes no leídos que el usuario actual (receiver)
                # ha recibido de este user_data_item['id'] (sender).
                unread_count = Message.get_unread_private_messages_count_from_sender(
                    receiver_id=current_user_id,
                    sender_id=user_data_item['id']
                )
                user_data_copy = dict(user_data_item)
                user_data_copy['unread_count'] = unread_count
                other_users_with_unread.append(user_data_copy)

    return render_template('chat/chat_users_list_panel.html', chat_users=other_users_with_unread)

# --- Manejadores de Eventos SocketIO (sin cambios en esta subtarea) ---

def on_chat_connect():
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id:
        emit('error', {'message': 'Autenticación requerida.'}, room=request.sid); return False
    join_room('global_chat_room'); join_room(str(user_id))
    current_app.logger.info(f"Usuario {username} (ID: {user_id}) unido a sala global y personal '{user_id}'.")
    emit('status', {'message': f'¡Bienvenido {username}!'}, room=request.sid)
    try:
        messages = Message.get_latest_global_messages(limit=30)
        emit('load_old_messages', {'messages': messages}, room=request.sid)
    except Exception as e:
        current_app.logger.error(f"Error cargando historial global para {username}: {e}")
    emit('user_joined', {'username': username, 'sid': request.sid}, room='global_chat_room', include_self=False)


def on_chat_disconnect():
    username = session.get('username', 'Usuario'); user_id = session.get('user_id')
    if user_id:
        leave_room('global_chat_room'); leave_room(str(user_id))
        current_app.logger.info(f"Usuario {username} (ID: {user_id}) desconectado.")
        emit('user_left', {'username': username, 'sid': request.sid}, room='global_chat_room')


def on_send_global_message(data):
    user_id = session.get('user_id'); username = session.get('username')
    message_content = data.get('message', '').strip()
    if not user_id: emit('error', {'message': 'No autenticado.'}, room=request.sid); return
    if not message_content: emit('error', {'message': 'Mensaje vacío.'}, room=request.sid); return
    try:
        msg_id = Message.create_global_message(user_id, message_content)
        if msg_id:
            emit('new_global_message', {'id': msg_id, 'username': username, 'message': message_content,
                                        'user_id': user_id, 'timestamp': datetime.utcnow().isoformat()+"Z"},
                 room='global_chat_room')
            # Registrar envío de mensaje global
            ActivityLog.log_message_sent(user_id=user_id, message_type='global',
                                         message_id=msg_id, ip_address=request.remote_addr)
            current_app.logger.info(f"Mensaje global (ID: {msg_id}) de {username} enviado y loggeado.")
        else: emit('error', {'message': 'Error guardando mensaje global.'}, room=request.sid)
    except Exception as e:
        current_app.logger.error(f"Error en send_global_message de {username}: {e}")
        emit('error', {'message': 'Error interno enviando mensaje global.'}, room=request.sid)

def on_send_private_message(data):
    sender_id = session.get('user_id'); sender_username = session.get('username')
    receiver_username = data.get('receiver_username'); message_content = data.get('message', '').strip()
    if not sender_id: emit('error', {'message': 'Autenticación requerida.'}, room=request.sid); return
    if not receiver_username: emit('error', {'message': 'Destinatario no especificado.'}, room=request.sid); return
    if not message_content: emit('error', {'message': 'Mensaje privado vacío.'}, room=request.sid); return
    receiver = User.find_by_username(receiver_username)
    if not receiver: emit('error', {'message': f'Destinatario "{receiver_username}" no encontrado.'}, room=request.sid); return
    receiver_id = receiver['id']
    if sender_id == receiver_id: emit('error', {'message': 'No puedes enviarte mensajes a ti mismo.'}, room=request.sid); return
    try:
        message_id = Message.create_private_message(sender_id, receiver_id, message_content)
        if message_id:
            private_msg_data = {
                'id': message_id, 'sender_id': sender_id, 'sender_username': sender_username,
                'receiver_id': receiver_id, 'receiver_username': receiver_username,
                'message': message_content, 'timestamp': datetime.utcnow().isoformat() + "Z", 'is_read': False
            }
            emit('new_private_message', private_msg_data, room=str(receiver_id))
            emit('new_private_message', private_msg_data, room=request.sid)
            # Registrar envío de mensaje privado
            ActivityLog.log_message_sent(user_id=sender_id, message_type='private',
                                         message_id=message_id, receiver_id=receiver_id,
                                         ip_address=request.remote_addr)
            current_app.logger.info(f"Mensaje privado (ID: {message_id}) de {sender_username} a {receiver_username} procesado y loggeado.")
        else: emit('error', {'message': 'Error al guardar mensaje privado.'}, room=request.sid)
    except Exception as e:
        current_app.logger.error(f"Error en on_send_private_message de {sender_username} a {receiver_username}: {e}")
        emit('error', {'message': 'Error interno enviando mensaje privado.'}, room=request.sid)

def on_load_private_history(data):
    user1_id = session.get('user_id'); user2_username = data.get('other_username')
    if not user1_id: emit('error', {'message': 'Autenticación requerida.'}, room=request.sid); return
    if not user2_username: emit('error', {'message': 'Usuario para historial no especificado.'}, room=request.sid); return
    user2 = User.find_by_username(user2_username)
    if not user2: emit('error', {'message': f'Usuario "{user2_username}" no encontrado.'}, room=request.sid); return
    user2_id = user2['id']
    try:
        messages = Message.get_private_messages_between_users(user1_id, user2_id, limit=30)
        Message.mark_private_messages_as_read(receiver_id=user1_id, sender_id=user2_id)

        formatted_messages = []
        for msg in messages:
            msg_copy = dict(msg)
            if isinstance(msg_copy.get('created_at'), datetime):
                msg_copy['timestamp'] = msg_copy['created_at'].isoformat() + "Z"
            formatted_messages.append(msg_copy)

        emit('loaded_private_history', {'with_username': user2_username, 'messages': formatted_messages}, room=request.sid)
    except Exception as e:
        current_app.logger.error(f"Error en on_load_private_history ({session.get('username')}, {user2_username}): {e}")
        emit('error', {'message': 'Error cargando historial privado.'}, room=request.sid)

def register_chat_event_handlers(socketio_instance):
    socketio_instance.on_event('connect', on_chat_connect, namespace='/chat')
    socketio_instance.on_event('disconnect', on_chat_disconnect, namespace='/chat')
    socketio_instance.on_event('send_global_message', on_send_global_message, namespace='/chat')
    socketio_instance.on_event('send_private_message', on_send_private_message, namespace='/chat')
    socketio_instance.on_event('load_private_history', on_load_private_history, namespace='/chat')
    current_app.logger.info("Manejadores SocketIO de Chat Global y Privado registrados para namespace /chat.")
