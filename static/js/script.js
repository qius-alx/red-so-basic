document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const loginContainer = document.getElementById('login-container');
    const chatContainer = document.getElementById('chat-container');
    const usernameInput = document.getElementById('username-input');
    const loginBtn = document.getElementById('login-btn');
    const usernameDisplay = document.getElementById('username-display');
    const usuariosLista = document.getElementById('usuarios-lista');
    const mensajesContainer = document.getElementById('mensajes');
    const mensajeInput = document.getElementById('mensaje-input');
    const enviarBtn = document.getElementById('enviar-btn');
    const errorMensaje = document.getElementById('error-mensaje');
    
    // Variables globales
    let socket;
    let username = '';
    
    // Inicializar Socket.IO
    function inicializarSocketIO() {
        // Conectar al servidor
        socket = io();
        
        // Eventos de Socket.IO
        socket.on('connect', function() {
            console.log('Conectado al servidor de chat');
        });
        
        socket.on('disconnect', function() {
            console.log('Desconectado del servidor');
        });
        
        socket.on('error_nombre', function(data) {
            mostrarError(data.mensaje);
        });
        
        socket.on('usuario_conectado', function(data) {
            agregarMensajeSistema(`${data.usuario} se ha unido al chat`);
        });
        
        socket.on('usuario_desconectado', function(data) {
            agregarMensajeSistema(`${data.usuario} ha abandonado el chat`);
        });
        
        socket.on('lista_usuarios', function(usuarios) {
            actualizarListaUsuarios(usuarios);
        });
        
        socket.on('nuevo_mensaje', function(data) {
            agregarMensaje(data);
        });
        
        socket.on('historial_mensajes', function(mensajes) {
            mensajes.forEach(msg => {
                agregarMensaje(msg);
            });
        });
    }
    
    // Evento de clic para el botón de login
    loginBtn.addEventListener('click', function() {
        iniciarSesion();
    });
    
    // También permitir iniciar sesión presionando Enter
    usernameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            iniciarSesion();
        }
    });
    
    // Evento de clic para el botón de enviar mensaje
    enviarBtn.addEventListener('click', function() {
        enviarMensaje();
    });
    
    // También permitir enviar mensaje presionando Enter
    mensajeInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            enviarMensaje();
        }
    });
    
    // Función para iniciar sesión
    function iniciarSesion() {
        const inputUsername = usernameInput.value.trim();
        
        if (inputUsername.length < 3) {
            mostrarError('El nombre de usuario debe tener al menos 3 caracteres');
            return;
        }
        
        // Inicializar Socket.IO si aún no se ha hecho
        if (!socket) {
            inicializarSocketIO();
        }
        
        // Guardar el nombre de usuario
        username = inputUsername;
        
        // Enviar solicitud para unirse al chat
        socket.emit('unirse_chat', { username: username });
        
        // Mostrar el nombre de usuario en la interfaz
        usernameDisplay.textContent = username;
        
        // Cambiar a la vista de chat
        loginContainer.classList.add('oculto');
        chatContainer.classList.remove('oculto');
        
        // Dar foco al campo de mensaje
        mensajeInput.focus();
    }
    
    // Función para enviar un mensaje
    function enviarMensaje() {
        const mensaje = mensajeInput.value.trim();
        
        if (mensaje && username) {
            socket.emit('enviar_mensaje', {
                username: username,
                mensaje: mensaje
            });
            
            // Limpiar el campo de entrada
            mensajeInput.value = '';
        }
    }
    
    // Función para mostrar mensajes de error
    function mostrarError(mensaje) {
        errorMensaje.textContent = mensaje;
        
        // Ocultar el mensaje después de 3 segundos
        setTimeout(() => {
            errorMensaje.textContent = '';
        }, 3000);
    }
    
    // Función para actualizar la lista de usuarios
    function actualizarListaUsuarios(usuarios) {
        usuariosLista.innerHTML = '';
        
        usuarios.forEach(user => {
            const li = document.createElement('li');
            li.textContent = user;
            
            // Resaltar el usuario actual
            if (user === username) {
                li.textContent += ' (tú)';
                li.style.fontWeight = 'bold';
            }
            
            usuariosLista.appendChild(li);
        });
    }
    
    // Función para agregar un mensaje al chat
    function agregarMensaje(data) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = data.usuario === username ? 'mensaje mensaje-propio' : 'mensaje mensaje-otro';
        
        const usuarioDiv = document.createElement('div');
        usuarioDiv.className = 'usuario-nombre';
        usuarioDiv.textContent = data.usuario === username ? 'Tú' : data.usuario;
        
        const contenidoDiv = document.createElement('div');
        contenidoDiv.className = 'mensaje-contenido';
        contenidoDiv.textContent = data.mensaje;
        
        mensajeDiv.appendChild(usuarioDiv);
        mensajeDiv.appendChild(contenidoDiv);
        
        mensajesContainer.appendChild(mensajeDiv);
        
        // Desplazar al último mensaje
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }
    
    // Función para agregar mensajes del sistema
    function agregarMensajeSistema(mensaje) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = 'mensaje-sistema';
        mensajeDiv.textContent = mensaje;
        mensajeDiv.style.textAlign = 'center';
        mensajeDiv.style.color = '#888';
        mensajeDiv.style.margin = '10px 0';
        mensajeDiv.style.fontStyle = 'italic';
        
        mensajesContainer.appendChild(mensajeDiv);
        
        // Desplazar al último mensaje
        mensajesContainer.scrollTop = mensajesContainer.scrollHeight;
    }
});