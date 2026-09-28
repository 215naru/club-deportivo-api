ALTER DATABASE club_deportivo CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

DROP TABLE IF EXISTS canchas;
DROP TABLE IF EXISTS socios;
DROP TABLE IF EXISTS deportes;

CREATE TABLE IF NOT EXISTS deportes (
id INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO deportes (nombre)
VALUES 
('Fútbol'),
('Tenis'),
('Pádel');

CREATE TABLE IF NOT EXISTS socios (
id INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(150) NOT NULL,
email VARCHAR(150) NOT NULL UNIQUE,
activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS canchas (
id INT PRIMARY KEY AUTO_INCREMENT,
nombre VARCHAR(150) NOT NULL,
id_deporte INT NOT NULL,
precio_hora INT NOT NULL,
techada BOOLEAN NOT NULL DEFAULT FALSE,
activa BOOLEAN NOT NULL DEFAULT TRUE,
FOREIGN KEY(id_deporte) REFERENCES deportes(id)
);

CREATE TABLE IF NOT EXISTS reservas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_socio INT NOT NULL,
    id_cancha INT NOT NULL,
    fecha_hora_inicio DATETIME(6) NOT NULL,
    fecha_hora_fin DATETIME(6) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    precio_hora INT NOT NULL,
    precio_total INT NOT NULL,

    CONSTRAINT fk_reservas_socio
        FOREIGN KEY (id_socio)
        REFERENCES socios(id),

    CONSTRAINT fk_reservas_cancha
        FOREIGN KEY (id_cancha)
        REFERENCES canchas(id)
);
