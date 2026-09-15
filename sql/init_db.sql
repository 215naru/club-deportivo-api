ALTER DATABASE club_deportivo CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

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