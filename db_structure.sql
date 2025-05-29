-- Estructura de la tabla de usuarios para SQL Server

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL
);

-- Nueva tabla para almacenar las puntuaciones

CREATE TABLE scores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category NVARCHAR(100) NOT NULL,
    score INT NOT NULL,
    CONSTRAINT FK_scores_users FOREIGN KEY (user_id) REFERENCES users(id)
);
