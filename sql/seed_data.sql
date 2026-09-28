-- Ejecutar después de sql/init_db.sql para insertar datos de prueba.

INSERT INTO socios (nombre, email, activo) VALUES
('Juan Pérez', 'juan.perez@example.com', TRUE),
('Ana Gómez', 'ana.gomez@example.com', TRUE),
('Carlos Ruiz', 'carlos.ruiz@example.com', FALSE);

INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
('Cancha 1 - Fútbol 5', 1, 1000000, FALSE, TRUE),
('Cancha 2 - Tenis', 2, 800000, TRUE, TRUE),
('Cancha 3 - Pádel', 3, 900000, TRUE, TRUE);

INSERT INTO reservas (id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin, estado, precio_hora, precio_total) VALUES
(1, 1, '2026-10-15 18:00:00', '2026-10-15 20:00:00', 'confirmada', 1000000, 2000000),
(2, 2, '2026-10-16 10:00:00', '2026-10-16 11:00:00', 'confirmada', 800000, 800000),
(1, 3, '2026-09-01 09:00:00', '2026-09-01 10:00:00', 'finalizada', 900000, 900000);
