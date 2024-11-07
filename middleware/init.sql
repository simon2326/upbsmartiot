-- Tabla de temperatura
CREATE TABLE IF NOT EXISTS temperature (
    entity_id VARCHAR(50),
    temperature FLOAT,
    timestamp TIMESTAMP
);

-- Tabla de humedad
CREATE TABLE IF NOT EXISTS humidity (
    entity_id VARCHAR(50),
    humidity FLOAT,
    timestamp TIMESTAMP
);

-- Tabla de posición
CREATE TABLE IF NOT EXISTS position (
    entity_id VARCHAR(50),
    timestamp TIMESTAMP,
    lat FLOAT,
    lon FLOAT
);

-- Tabla de predicciones
CREATE TABLE IF NOT EXISTS prediction (
    timestamp TIMESTAMP PRIMARY KEY,
    temperature_prediction FLOAT,
    humidity_prediction FLOAT
);
