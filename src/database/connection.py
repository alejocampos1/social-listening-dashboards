import psycopg2
import streamlit as st
import pandas as pd
from contextlib import contextmanager

class DatabaseConnection:
    def __init__(self):
        self.connection_string = st.secrets["database"]["connection_string"]
    
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
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                return df['table_name'].tolist()
        except Exception as e:
            st.error(f"Error obteniendo tablas: {e}")
            return []