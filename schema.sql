-- Base de datos: chat_unaj (Ejemplo, el usuario puede cambiarla)
-- CREATE DATABASE IF NOT EXISTS chat_unaj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE chat_unaj;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Tabla de Preguntas (Foro)
CREATE TABLE IF NOT EXISTS questions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de Respuestas (Foro)
CREATE TABLE IF NOT EXISTS answers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de Mensajes Globales
CREATE TABLE IF NOT EXISTS global_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- TRIGGER para mantener solo 30 mensajes globales
DELIMITER //
CREATE TRIGGER IF NOT EXISTS limit_global_messages
AFTER INSERT ON global_messages
FOR EACH ROW
BEGIN
    DELETE FROM global_messages
    WHERE id NOT IN (
        SELECT id FROM (
            SELECT id FROM global_messages
            ORDER BY created_at DESC
            LIMIT 30
        ) tmp
    );
END //
DELIMITER ;

-- Tabla de Mensajes Privados
CREATE TABLE IF NOT EXISTS private_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversation (sender_id, receiver_id, created_at)
);

-- TRIGGER para mantener solo 30 mensajes por conversación privada
DELIMITER //
CREATE TRIGGER IF NOT EXISTS limit_private_messages
AFTER INSERT ON private_messages
FOR EACH ROW
BEGIN
    DELETE FROM private_messages
    WHERE ((sender_id = NEW.sender_id AND receiver_id = NEW.receiver_id)
           OR (sender_id = NEW.receiver_id AND receiver_id = NEW.sender_id))
    AND id NOT IN (
        SELECT id FROM (
            SELECT id FROM private_messages
            WHERE ((sender_id = NEW.sender_id AND receiver_id = NEW.receiver_id)
                   OR (sender_id = NEW.receiver_id AND receiver_id = NEW.sender_id))
            ORDER BY created_at DESC
            LIMIT 30
        ) tmp
    );
END //
DELIMITER ;

-- Tabla de Logs de Actividad
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    details JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
