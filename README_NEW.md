# campus

<a href="https://github.com/Thibor82/campus">Campus_Konectia</a> © 2026 by 
<a href="https://spaceham.es/">Rubén Caballero</a> is licensed under 
<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>
<img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">
<img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">
<img src="https://mirrors.creativecommons.org/presskit/icons/sa.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">

## Nuevas características
- Calendario personal para alumnos
  - Visualización mensual
  - Selección de días para ver eventos y añadir nuevos
  - Almacenamiento de eventos en la base de datos (tabla `eventos`)

## Migración de base de datos
Se agregó una nueva tabla `eventos` en `InfoDataBase/Schema.sql`:

```sql
CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);
```

Aplica esta modificación recreando el esquema o ejecutando la sentencia en tu base de datos existente.
