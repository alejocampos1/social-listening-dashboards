import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

class DataCacheManager:
    def __init__(self, cache_duration_minutes=5):
        """
        Gestor de caché para datos de social listening
        
        Args:
            cache_duration_minutes: Duración del caché en minutos
        """
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache_key_prefix = "social_listening_cache"
        
        # Inicializar caché en session_state si no existe
        if 'data_cache' not in st.session_state:
            st.session_state.data_cache = {}
    
    def generate_cache_key(self, alerta_id: int, origins: List[str], 
                      start_date: datetime, end_date: datetime, 
                      sentiment: Optional[str] = None) -> str:
        """
        Genera una clave única para el caché basada en los parámetros de consulta
        
        Args:
            alerta_id: ID de la alerta
            origins: Lista de orígenes (redes sociales)
            start_date: Fecha de inicio
            end_date: Fecha de fin
            sentiment: Sentimiento filtrado (opcional)
            
        Returns:
            Clave hash única para estos parámetros
        """
        # Agregar username para hacer caché único por usuario
        username = st.session_state.get('username', 'anonymous')
        
        # Crear string con todos los parámetros
        cache_params = {
            'username': username,  # NUEVO - separa caché por usuario
            'alerta_id': alerta_id,
            'origins': sorted(origins),  # Ordenar para consistencia
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'sentiment': sentiment
        }
        
        # Convertir a JSON string ordenado para consistencia
        params_string = json.dumps(cache_params, sort_keys=True)
        
        # Generar hash MD5
        cache_key = hashlib.md5(params_string.encode()).hexdigest()
        
        return f"{self.cache_key_prefix}_{cache_key}"
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """
        Verifica si el caché para una clave específica sigue siendo válido
        
        Args:
            cache_key: Clave del caché a verificar
            
        Returns:
            True si el caché existe y no ha expirado
        """
        if cache_key not in st.session_state.data_cache:
            return False
        
        cache_entry = st.session_state.data_cache[cache_key]
        cache_time = cache_entry.get('timestamp')
        
        if not cache_time:
            return False
        
        # Verificar si ha expirado
        time_elapsed = datetime.now() - cache_time
        return time_elapsed < self.cache_duration
    
    def get_cached_data(self, alerta_id: int, origins: List[str], 
                       start_date: datetime, end_date: datetime, 
                       sentiment: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Obtiene datos cacheados si están disponibles y son válidos
        
        Args:
            alerta_id: ID de la alerta
            origins: Lista de orígenes
            start_date: Fecha de inicio
            end_date: Fecha de fin
            sentiment: Sentimiento filtrado
            
        Returns:
            DataFrame cacheado o None si no hay caché válido
        """
        cache_key = self.generate_cache_key(alerta_id, origins, start_date, end_date, sentiment)
        
        if self.is_cache_valid(cache_key):
            cache_entry = st.session_state.data_cache[cache_key]
            return cache_entry['data'].copy()  # Devolver copia para evitar modificaciones
        
        return None
    
    def cache_data(self, data: pd.DataFrame, alerta_id: int, origins: List[str], 
                   start_date: datetime, end_date: datetime, 
                   sentiment: Optional[str] = None) -> str:
        """
        Almacena datos en el caché
        
        Args:
            data: DataFrame a cachear
            alerta_id: ID de la alerta
            origins: Lista de orígenes
            start_date: Fecha de inicio
            end_date: Fecha de fin
            sentiment: Sentimiento filtrado
            
        Returns:
            Clave del caché donde se almacenaron los datos
        """
        cache_key = self.generate_cache_key(alerta_id, origins, start_date, end_date, sentiment)
        
        cache_entry = {
            'data': data.copy(),  # Almacenar copia para evitar modificaciones
            'timestamp': datetime.now(),
            'params': {
                'alerta_id': alerta_id,
                'origins': origins,
                'start_date': start_date,
                'end_date': end_date,
                'sentiment': sentiment
            },
            'size': len(data)
        }
        
        st.session_state.data_cache[cache_key] = cache_entry
        
        # Limpiar caché antiguo para evitar acumulación de memoria
        self._cleanup_expired_cache()
        
        return cache_key
    
    def invalidate_cache(self, alerta_id: Optional[int] = None):
        """
        Invalida caché específico o todo el caché
        
        Args:
            alerta_id: Si se especifica, solo invalida caché de esa alerta.
                      Si es None, invalida todo el caché.
        """
        if alerta_id is None:
            # Limpiar todo el caché
            st.session_state.data_cache = {}
        else:
            # Limpiar solo caché de la alerta específica
            keys_to_remove = []
            for cache_key, cache_entry in st.session_state.data_cache.items():
                if cache_entry.get('params', {}).get('alerta_id') == alerta_id:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                del st.session_state.data_cache[key]
    
    def _cleanup_expired_cache(self):
        """Limpia entradas de caché expiradas para liberar memoria"""
        current_time = datetime.now()
        keys_to_remove = []
        
        for cache_key, cache_entry in st.session_state.data_cache.items():
            cache_time = cache_entry.get('timestamp')
            if cache_time and (current_time - cache_time) > self.cache_duration:
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del st.session_state.data_cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché para debugging
        
        Returns:
            Diccionario con estadísticas del caché
        """
        cache = st.session_state.data_cache
        total_entries = len(cache)
        valid_entries = sum(1 for key in cache.keys() if self.is_cache_valid(key))
        
        total_size = sum(
            entry['size'] for entry in cache.values() 
            if 'size' in entry
        )
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'total_cached_records': total_size,
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60
        }
    
    def clear_all_cache(self):
        """Limpia completamente todo el caché"""
        st.session_state.data_cache = {}


# Funciones de conveniencia para uso directo
def get_cached_social_data(alerta_id: int, origins: List[str], 
                          start_date: datetime, end_date: datetime, 
                          sentiment: Optional[str] = None, 
                          cache_manager: Optional[DataCacheManager] = None) -> Optional[pd.DataFrame]:
    """
    Función de conveniencia para obtener datos cacheados
    
    Args:
        alerta_id: ID de la alerta
        origins: Lista de orígenes
        start_date: Fecha de inicio
        end_date: Fecha de fin
        sentiment: Sentimiento filtrado
        cache_manager: Instancia del gestor de caché (opcional)
        
    Returns:
        DataFrame cacheado o None
    """
    if cache_manager is None:
        cache_manager = DataCacheManager()
    
    return cache_manager.get_cached_data(alerta_id, origins, start_date, end_date, sentiment)


def cache_social_data(data: pd.DataFrame, alerta_id: int, origins: List[str], 
                     start_date: datetime, end_date: datetime, 
                     sentiment: Optional[str] = None,
                     cache_manager: Optional[DataCacheManager] = None) -> str:
    """
    Función de conveniencia para cachear datos
    
    Args:
        data: DataFrame a cachear
        alerta_id: ID de la alerta
        origins: Lista de orígenes
        start_date: Fecha de inicio
        end_date: Fecha de fin
        sentiment: Sentimiento filtrado
        cache_manager: Instancia del gestor de caché (opcional)
        
    Returns:
        Clave del caché
    """
    if cache_manager is None:
        cache_manager = DataCacheManager()
    
    return cache_manager.cache_data(data, alerta_id, origins, start_date, end_date, sentiment)


def invalidate_social_cache(alerta_id: Optional[int] = None,
                           cache_manager: Optional[DataCacheManager] = None):
    """
    Función de conveniencia para invalidar caché
    
    Args:
        alerta_id: ID de la alerta (opcional)
        cache_manager: Instancia del gestor de caché (opcional)
    """
    if cache_manager is None:
        cache_manager = DataCacheManager()
    
    cache_manager.invalidate_cache(alerta_id)