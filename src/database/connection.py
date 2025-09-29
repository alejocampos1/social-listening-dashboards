import psycopg2
import streamlit as st
import pandas as pd
from contextlib import contextmanager

from .sql_queries import SocialListeningQueryBuilder

class DatabaseConnection:
    def __init__(self):
        self.connection_string = st.secrets["database"]["connection_string"]
        self.sql_builder = SocialListeningQueryBuilder()

    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la DB"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Error de conexión a la base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def test_connection(self):
        """Prueba la conexión a la base de datos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return True, "Conexión exitosa"
        except Exception as e:
            return False, str(e)
    
    def execute_query(self, query, params=None):
        """Ejecuta una query y retorna un DataFrame"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            st.error(f"Error ejecutando query: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name):
        """Obtiene información sobre las columnas de una tabla"""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=[table_name])
                return df
        except Exception as e:
            st.error(f"Error obteniendo info de tabla: {e}")
            return pd.DataFrame()
    
    def get_available_tables(self):
        """Lista todas las tablas disponibles"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'ocdul'
            ORDER BY table_name
            """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                return df['table_name'].tolist()
        except Exception as e:
            st.error(f"Error obteniendo tablas: {e}")
            return []
        
    def get_social_listening_data(self, alerta_id, origins, start_date, end_date, sentiment=None, limit=100):
        """Obtiene datos unificados de social listening"""
        query = self.sql_builder.build_unified_query(
            alerta_id, origins, start_date, end_date, sentiment, limit
        )
        
        if not query:
            return pd.DataFrame()
        
        params = self.sql_builder.get_query_parameters(
            alerta_id, origins, start_date, end_date, sentiment
        )
        
        return self.execute_query(query, params)

    def get_last_update_timestamp(self, alerta_id):
        """Obtiene el timestamp del registro más reciente para una alerta"""
        tables = self.sql_builder.get_tables_for_origins([
            'Facebook', 'Instagram', 'X (Twitter)', 'TikTok'
        ])
        
        union_queries = []
        params = []
        
        for table in tables:
            union_queries.append(f"SELECT MAX(created_time) as last_update FROM ocdul.{table} WHERE alerta_id = %s")
            params.append(alerta_id)
        
        if not union_queries:
            return None
        
        query = f"""
        SELECT MAX(last_update) as latest_timestamp
        FROM ({' UNION ALL '.join(union_queries)}) as combined
        """
        
        result = self.execute_query(query, params)
        
        if not result.empty and result.iloc[0]['latest_timestamp']:
            return result.iloc[0]['latest_timestamp']
        
        return None
    
    def update_sentiment(self, table_name: str, record_id: int, new_sentiment: str, confidence: float = 1.0):
        """Actualiza el sentimiento de un registro específico"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Query para actualizar sentimiento y ajustar confianzas
                query = f"""
                UPDATE ocdul.{table_name}
                SET sentiment_pred = %s,
                    sentiment_confidence = %s
                WHERE id = %s
                """
                
                cursor.execute(query, (new_sentiment, confidence, record_id))
                conn.commit()
                
                return True, f"Registro {record_id} actualizado exitosamente"
                
        except Exception as e:
            return False, f"Error actualizando registro: {str(e)}"

    def delete_record(self, table_name: str, record_id: int):
        """Elimina un registro específico de ocdul y opcionalmente de RAW"""
        
        # Mapeo de origen a esquema RAW
        schema_mapping = {
            'facebook': 'CONSULTAS_FB_RAW',
            'instagram': 'CONSULTAS_IG_RAW',
            'x': 'CONSULTAS_X_RAW',
            'tiktok': 'CONSULTAS_TK_RAW'
        }
        
        # Mapeo de tabla a columna ID original
        id_column_mapping = {
            'posts_facebook': 'id_post_original',
            'posts_instagram': 'id_post_original',
            'posts_x': 'id_post_original',
            'posts_tiktok': 'id_post_original',
            'comentarios_facebook': 'id_comentario_original',
            'comentarios_instagram': 'id_comentario_original',
            'comentarios_tiktok': 'id_comentario_original',
            'respuestas_x': 'id_respuesta_original',
            'quotes_x': 'id_quote_original'
        }
        
        # Mapeo de tabla ocdul a tabla RAW
        raw_table_mapping = {
            'posts_facebook': 'posts',
            'posts_instagram': 'posts',
            'posts_x': 'posts',
            'posts_tiktok': 'posts',
            'comentarios_facebook': 'comentarios',
            'comentarios_instagram': 'comentarios',
            'comentarios_tiktok': 'comentarios',
            'respuestas_x': 'respuestas',
            'quotes_x': 'quotes'
        }
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 1. Obtener el ID original y origen del registro
                id_column = id_column_mapping.get(table_name)
                raw_deleted = False
                
                if id_column:
                    # Obtener ID original y origen
                    query = f"""
                    SELECT {id_column}, origin 
                    FROM ocdul.{table_name} 
                    WHERE id = %s
                    """
                    cursor.execute(query, (record_id,))
                    result = cursor.fetchone()
                    
                    if result and result[0] is not None:  # ID original existe
                        id_original = result[0]
                        origin = result[1].lower() if result[1] else None
                        
                        # 2. Intentar borrar de RAW si tenemos la info necesaria
                        if origin in schema_mapping and table_name in raw_table_mapping:
                            schema_raw = schema_mapping[origin]
                            tabla_raw = raw_table_mapping[table_name]
                            
                            # Determinar columna ID en tabla RAW
                            id_column_raw = {
                                'posts': 'id_post',
                                'comentarios': 'id_comentario',
                                'respuestas': 'id_respuesta',
                                'quotes': 'id_quote'
                            }.get(tabla_raw)
                            
                            if id_column_raw:
                                try:
                                    query_raw = f"""
                                    DELETE FROM {schema_raw}.{tabla_raw} 
                                    WHERE {id_column_raw} = %s
                                    """
                                    cursor.execute(query_raw, (id_original,))
                                    raw_deleted = cursor.rowcount > 0
                                except Exception as e:
                                    # Log pero no fallar
                                    print(f"No se pudo borrar de RAW: {e}")
                
                # 3. Borrar de ocdul
                query_ocdul = f"DELETE FROM ocdul.{table_name} WHERE id = %s"
                cursor.execute(query_ocdul, (record_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    
                    # Mensaje informativo
                    if raw_deleted:
                        return True, f"Registro {record_id} eliminado de ocdul y RAW"
                    else:
                        return True, f"Registro {record_id} eliminado de ocdul"
                else:
                    return False, f"No se encontró el registro {record_id}"
                    
        except Exception as e:
            return False, f"Error eliminando registro: {str(e)}"

    def log_editor_change(self, user_name: str, table_name: str, record_id: int, old_sentiment: str, new_sentiment: str):
        """Registra cambios del super editor en logs"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla de logs si no existe
                create_table_query = """
                CREATE TABLE IF NOT EXISTS ocdul.editor_logs (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255),
                    table_name VARCHAR(255),
                    record_id INTEGER,
                    old_sentiment VARCHAR(10),
                    new_sentiment VARCHAR(10),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_table_query)
                
                # Insertar log
                insert_query = """
                INSERT INTO ocdul.editor_logs 
                (user_name, table_name, record_id, old_sentiment, new_sentiment)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (user_name, table_name, record_id, old_sentiment, new_sentiment))
                conn.commit()
                
                return True, "Cambio registrado en logs"
                
        except Exception as e:
            return False, f"Error registrando en logs: {str(e)}"
        
    def log_user_access(self, username: str, user_name: str, email: str, 
                    action: str, dashboard_id: str, dashboard_title: str):
        """Registra accesos de usuarios en la base de datos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                INSERT INTO ocdul.user_access_logs 
                (username, user_name, email, action, dashboard_id, dashboard_title)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (username, user_name, email, action, 
                                    dashboard_id, dashboard_title))
                conn.commit()
                
                return True, "Log registrado exitosamente"
                
        except Exception as e:
            return False, f"Error registrando log: {str(e)}"