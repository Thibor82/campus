CREATE TYPE public.rol_usuario AS ENUM
    ('alumno', 'profesor', 'administrador');

ALTER TYPE public.rol_usuario
    OWNER TO postgres;


CREATE TABLE usuarios ( 
    id_usuarios SERIAL PRIMARY KEY, 
    usuario VARCHAR() NOT NULL, 
    usuario_email VARCHAR() UNIQUE NOT NULL,
    password VARCHAR () NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    rol rol_usuario () NOT NULL);

-- tabla para almacenar eventos/calendario de cada alumno
CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuarios) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- tabla de asignaturas
CREATE TABLE asignaturas (
    id_asignatura SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    id_profesor INTEGER NOT NULL REFERENCES usuarios(id_usuarios) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- tabla de matriculación (relación alumno-asignatura)
CREATE TABLE matriculaciones (
    id_matriculacion SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuarios) ON DELETE CASCADE,
    id_asignatura INTEGER NOT NULL REFERENCES asignaturas(id_asignatura) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(id_usuario, id_asignatura)
);

-- tabla de eventos de asignatura (eventos públicos de la asignatura)
CREATE TABLE eventos_asignatura (
    id_evento_asign SERIAL PRIMARY KEY,
    id_asignatura INTEGER NOT NULL REFERENCES asignaturas(id_asignatura) ON DELETE CASCADE,
    id_profesor INTEGER NOT NULL REFERENCES usuarios(id_usuarios) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ========== TRIGGERS ==========

-- Función para crear evento de bienvenida al registrar usuario
CREATE OR REPLACE FUNCTION crear_evento_bienvenida()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO eventos (id_usuarios, fecha, titulo, descripcion, creado_en)
    VALUES (
        NEW.id_usuarios,
        CURRENT_DATE,
        'Bienvenido al Campus',
        'Evento automático de bienvenida. Tu cuenta ha sido creada correctamente.',
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger que se dispara después de insertar un usuario
CREATE TRIGGER trigger_evento_bienvenida
AFTER INSERT ON usuarios
FOR EACH ROW
EXECUTE FUNCTION crear_evento_bienvenida();

