# db_utils.py
import psycopg2
import pandas as pd
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuración de conexión a PostgreSQL usando psycopg2
def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            host="db",
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "iotplant"),
            user=os.getenv("POSTGRES_USER", "simon"),
            password=os.getenv("POSTGRES_PASSWORD", "simon123")
        )
        logger.info("Conexión exitosa a PostgreSQL")
        return connection
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        return None

# Función para obtener datos desde PostgreSQL
def get_data_from_postgres(table, limit=1000):
    connection = connect_to_postgresql()
    if connection is None:
        logger.error(f"No se pudo obtener conexión para la tabla {table}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío si falla la conexión
    
    try:
        query = f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT {limit}"
        logger.debug(f"Ejecutando query: {query}")
        data = pd.read_sql_query(query, connection)
        logger.debug(f"Datos obtenidos de {table}:")
        logger.debug(f"Columnas: {data.columns.tolist()}")
        logger.debug(f"Primeras filas: {data.head()}")
        return data
    except Exception as e:
        logger.error(f"Error al obtener datos de {table}: {e}")
        return pd.DataFrame()
    finally:
        connection.close()

# Función para obtener predicciones
def get_predictions():
    try:
        data = get_data_from_postgres("prediction", limit=24)
        logger.debug(f"Datos de predicción obtenidos: {data.shape[0]} filas")
        return data
    except Exception as e:
        logger.error(f"Error al obtener predicciones: {e}")
        return pd.DataFrame()
