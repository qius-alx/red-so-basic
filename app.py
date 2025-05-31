from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# Almacenamiento en memoria para usuarios conectados y mensajes
usuarios_conectados = {}
mensajes = []

@app.route('/')
def home():
    return render_template('home.html')

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado:', request.sid)
    # Eliminar usuario de la lista de conectados
    user_id = None
    for uid, sid in usuarios_conectados.items():
        if sid == request.sid:
            user_id = uid
            break
    
    if user_id:
        del usuarios_conectados[user_id]
        emit('usuario_desconectado', {'usuario': user_id}, broadcast=True)
        emit('lista_usuarios', list(usuarios_conectados.keys()), broadcast=True)

@socketio.on('unirse_chat')
def handle_join(data):
    username = data.get('username')
    if username and username not in usuarios_conectados:
        # Guardar el usuario con su ID de sesión
        usuarios_conectados[username] = request.sid
        # Notificar a todos los usuarios sobre el nuevo usuario
        emit('usuario_conectado', {'usuario': username}, broadcast=True)
        # Enviar la lista actualizada de usuarios
        emit('lista_usuarios', list(usuarios_conectados.keys()), broadcast=True)
        # Enviar historial de mensajes al nuevo usuario
        emit('historial_mensajes', mensajes)
    else:
        # Notificar al usuario que el nombre ya está en uso
        emit('error_nombre', {'mensaje': 'Este nombre de usuario ya está en uso'})

@socketio.on('enviar_mensaje')
def handle_message(data):
    username = data.get('username')
    mensaje = data.get('mensaje')
    
    if username and mensaje and username in usuarios_conectados:
        # Crear objeto de mensaje
        msg = {
            'usuario': username,
            'mensaje': mensaje
        }
        # Guardar mensaje en el historial
        mensajes.append(msg)
        # Mantener solo los últimos 100 mensajes
        if len(mensajes) > 100:
            mensajes.pop(0)
        # Enviar mensaje a todos los usuarios
        emit('nuevo_mensaje', msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)