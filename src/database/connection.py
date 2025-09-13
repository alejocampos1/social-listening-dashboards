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

    def get_timeline_data(self, alerta_id, origins, start_date, end_date, sentiment=None):
        """Obtiene datos para gráfico timeline agrupados por fecha"""
        query, params = self.sql_builder.get_timeline_query(
            alerta_id, origins, start_date, end_date, sentiment
        )
        
        if not query:
            return pd.DataFrame()
        
        return self.execute_query(query, params)

    def get_sentiment_distribution(self, alerta_id, origins, start_date, end_date):
        """Obtiene distribución de sentimientos"""
        query, params = self.sql_builder.get_sentiment_query(
            alerta_id, origins, start_date, end_date
        )
        
        if not query:
            return pd.DataFrame()
        
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
    
    def get_total_mentions_count(self, alerta_id, origins, start_date, end_date, sentiment=None):
        """Obtiene el conteo total real de menciones sin límite"""
        
        # Convertir polaridad de filtro a código de BD si es necesario
        sentiment_code = sentiment
        
        union_queries = []
        params = []
        
        for origin in origins:
            if origin in self.sql_builder.table_mapping:
                tables = self.sql_builder.table_mapping[origin]
                
                for table in tables:
                    select_query = f"""
                    SELECT COUNT(*) as count
                    FROM ocdul.{table}
                    WHERE alerta_id = %s
                        AND origin = %s
                        AND created_time BETWEEN %s AND %s
                    """
                    
                    # Parámetros para esta tabla
                    table_params = [alerta_id, origin, start_date, end_date]
                    
                    if sentiment_code and sentiment_code in ['POS', 'NEU', 'NEG']:
                        select_query += " AND sentiment_pred = %s"
                        table_params.append(sentiment_code)
                    
                    union_queries.append(select_query)
                    params.extend(table_params)
        
        if not union_queries:
            return 0
        
        # Sumar todos los conteos
        final_query = f"""
        SELECT SUM(count) as total_count
        FROM ({' UNION ALL '.join(union_queries)}) as combined
        """
        
        result = self.execute_query(final_query, params)
        
        if not result.empty and result.iloc[0]['total_count']:
            return int(result.iloc[0]['total_count'])
        
        return 0