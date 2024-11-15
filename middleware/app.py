import os
import pandas as pd
import psycopg2
from crate import client
from datetime import datetime, timedelta
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from sklearn.ensemble import RandomForestRegressor

# Función para convertir de epoch en milisegundos a timestamp
def convert_epoch_ms_to_timestamp(epoch_ms):
    return datetime.fromtimestamp(epoch_ms / 1000.0)

# Conexión a PostgreSQL
def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            host="db",
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "simon"),
            password=os.getenv("POSTGRES_PASSWORD", "simon123"),
            dbname=os.getenv("POSTGRES_DB", "iotplant")
        )
        print("Conexión exitosa a PostgreSQL")
        return connection
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        return None

# Leer datos de CrateDB
def read_from_crate():
    print("Intentando conectar a CrateDB...")
    connection = client.connect('http://10.38.32.137:8083', username='crate')
    cursor = connection.cursor()
    try:
        query = """
        SELECT entity_id, temp, humedad, lat, lon, time_index
        FROM "doc"."etvariables"
        WHERE entity_id = 'Saimon'
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"Datos recuperados de CrateDB: {rows}")
        return rows
    except Exception as e:
        print(f"Error al leer datos de CrateDB: {e}")
    finally:
        cursor.close()
        connection.close()

# Insertar datos de medición en PostgreSQL
def insert_measurements(data):
    connection = connect_to_postgresql()
    if not connection:
        return
    
    cursor = connection.cursor()
    try:
        # Limpiar datos anteriores en las tablas de medición y posición
        if len(data) > 0:
            cursor.execute("DELETE FROM temperature")
            cursor.execute("DELETE FROM humidity")
            cursor.execute("DELETE FROM position")
        
        # Insertar nuevos datos
        for entity_id, temp, humidity, lat, lon, timestamp in data:
            timestamp_dt = convert_epoch_ms_to_timestamp(timestamp)
            
            if 0 < temp <= 100:
                cursor.execute("""
                INSERT INTO temperature (entity_id, temperature, timestamp)
                VALUES (%s, %s, %s)
                """, (entity_id, temp, timestamp_dt))
                
            if 0 < humidity <= 100:
                cursor.execute("""
                INSERT INTO humidity (entity_id, humidity, timestamp)
                VALUES (%s, %s, %s)
                """, (entity_id, humidity, timestamp_dt))
            
            if lat != 0 and lon != 0 and lat > -90 and lat < 90 and lon > -180 and lon < 180:
                cursor.execute("""
                INSERT INTO position (entity_id, timestamp, lat, lon)
                VALUES (%s, %s, %s, %s)
                """, (entity_id, timestamp_dt, lat, lon))
                print(f"Insertado en position: {entity_id}, {lat}, {lon}, {timestamp_dt}")
        
        connection.commit()
    except Exception as e:
        print(f"Error al insertar datos en PostgreSQL: {e}")
        connection.rollback
    finally:
        cursor.close()
        connection.close()

# Generar predicciones y almacenarlas en PostgreSQL
def predictions():
    connection = connect_to_postgresql()
    if not connection:
        return
    
    cursor = connection.cursor()
    # Obtener datos históricos para predicción
    try:
        cursor.execute("""
        SELECT temperature, timestamp 
        FROM temperature 
        ORDER BY timestamp DESC 
        LIMIT 1000
        """)
        temp_data = pd.DataFrame(cursor.fetchall(), columns=['temperature', 'timestamp'])
        
        cursor.execute("""
        SELECT humidity, timestamp 
        FROM humidity 
        ORDER BY timestamp DESC 
        LIMIT 1000
        """)
        humidity_data = pd.DataFrame(cursor.fetchall(), columns=['humidity', 'timestamp'])
        
        if len(temp_data) == 0 or len(humidity_data) == 0:
            print("No hay suficientes datos para realizar predicciones")
            return
        
        # Entrenar los modelos de predicción
        temp_forecaster = ForecasterAutoreg(
            regressor=RandomForestRegressor(n_estimators=100, random_state=123),
            lags=24
        )
        
        humidity_forecaster = ForecasterAutoreg(
            regressor=RandomForestRegressor(n_estimators=100, random_state=123),
            lags=24
        )
        
        temp_forecaster.fit(y=temp_data['temperature'])
        humidity_forecaster.fit(y=humidity_data['humidity'])
        
        # Generar predicciones
        steps = 24
        temp_predictions = temp_forecaster.predict(steps=steps).tolist()
        humidity_predictions = humidity_forecaster.predict(steps=steps).tolist()
        
        # Limpiar predicciones anteriores y guardar nuevas
        cursor.execute("SELECT COUNT(*) FROM prediction")
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute("DELETE FROM prediction")
            
        current_time = datetime.now()
        for i in range(steps):
            future_time = current_time + timedelta(hours=i)
            cursor.execute("""
            INSERT INTO prediction (timestamp, temperature_prediction, humidity_prediction)
            VALUES (%s, %s, %s)
            ON CONFLICT (timestamp) DO UPDATE 
            SET temperature_prediction = EXCLUDED.temperature_prediction,
                humidity_prediction = EXCLUDED.humidity_prediction
            """, (future_time, temp_predictions[i], humidity_predictions[i]))
        
        connection.commit()
        
    except Exception as e:
        print(f"Error al generar predicciones: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

# Ejecución principal
if __name__ == "__main__":
    print("Middleware iniciado")
    raw_data = read_from_crate()
    
    if raw_data:
        print(f"Datos recibidos de CrateDB: {raw_data}")
        insert_measurements(raw_data)
        print("Datos insertados en PostgreSQL")
        predictions()
        print("Predicciones generadas y almacenadas en PostgreSQL")
    else:
        print("No se recibieron datos de CrateDB o hubo un error en la consulta")
