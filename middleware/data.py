from crate import client
import psycopg2
import pandas as pd

# Configuración de la base de datos CrateDB
crate_url = "http://10.38.32.137:8083"

# Configuración de la base de datos PostgreSQL
postgres_config = {
    'dbname': 'iot_data',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432
}

# Función para obtener datos de CrateDB
def get_data_from_crate():
    con = client.connect(crate_url)
    cur = con.cursor()
    query = "SELECT * FROM doc.etvariables;"  # Ajusta el nombre de la tabla
    cur.execute(query)
    data = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.close()
    con.close()
    return data

# Función para guardar datos en PostgreSQL
def save_data_to_postgres(data):
    conn = psycopg2.connect(**postgres_config)
    cur = conn.cursor()

    # Crear tabla si no existe
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        entity_id TEXT,
        entity_type TEXT,
        time_index TIMESTAMP,
        instanceid TEXT,
        temp FLOAT,
        humedad FLOAT,
        lat FLOAT,
        lon FLOAT
    );
    """
    cur.execute(create_table_query)
    conn.commit()

    # Insertar datos
    for index, row in data.iterrows():
        insert_query = """
        INSERT INTO sensor_data (entity_id, entity_type, time_index, instanceid, temp, humedad, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, row.values)
    conn.commit()
    cur.close()
    conn.close()

# Ejecutar funciones
data = get_data_from_crate()
save_data_to_postgres(data)
