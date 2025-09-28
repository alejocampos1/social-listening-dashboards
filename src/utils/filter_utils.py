from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import pandas as pd

class FilterConstants:
    """Constantes para filtros de social listening"""
    
    # Mapeo bidireccional entre valores de display y base de datos
    SOCIAL_NETWORKS_DISPLAY_TO_DB = {
        "Facebook": "Facebook",
        "X (Twitter)": "X", 
        "Instagram": "Instagram",
        "TikTok": "TikTok"
    }
    
    SOCIAL_NETWORKS_DB_TO_DISPLAY = {v: k for k, v in SOCIAL_NETWORKS_DISPLAY_TO_DB.items()}
    
    CONTENT_TYPE_MAPPING = {
        'posts_facebook': 'Posts',
        'comentarios_facebook': 'Comentarios',
        'posts_instagram': 'Posts',
        'comentarios_instagram': 'Comentarios',
        'posts_x': 'Posts',
        'respuestas_x': 'Respuestas (X)',
        'quotes_x': 'Quotes (X)',
        'posts_tiktok': 'Posts',
        'comentarios_tiktok': 'Comentarios'
    }
    
    # Mapeo inverso para facilitar búsquedas
    CONTENT_TYPE_REVERSE_MAPPING = {v: k for k, v in CONTENT_TYPE_MAPPING.items()}
    
    # Opciones de sentimiento
    SENTIMENT_OPTIONS_DISPLAY = ["Positivo", "Neutro", "Negativo"]
    SENTIMENT_OPTIONS_DB = ["POS", "NEU", "NEG"]
    
    SENTIMENT_DISPLAY_TO_DB = {
        'Positivo': 'POS',
        'Neutro': 'NEU', 
        'Negativo': 'NEG'
    }
    
    SENTIMENT_DB_TO_DISPLAY = {v: k for k, v in SENTIMENT_DISPLAY_TO_DB.items()}
    
    # Opciones de ordenamiento para tablas
    SORT_OPTIONS = [
        'Fecha (Reciente)', 
        'Fecha (Antigua)', 
        'Confianza (Alta)', 
        'Confianza (Baja)',
        'Likes (Alto)', 
        'Likes (Bajo)'
    ]
    
    # Opciones de período de tiempo
    TIME_PERIOD_OPTIONS = [
        "Rango personalizado", 
        "Últimos 7 días", 
        "Últimos 30 días", 
        "Este mes", 
        "Últimos 3 meses", 
        "Histórico Completo"
    ]


class FilterValidator:
    """Validador para filtros de social listening"""
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
        """
        Valida que el rango de fechas sea correcto
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Tupla con (es_válido, mensaje_error)
        """
        if start_date > end_date:
            return False, "La fecha de inicio no puede ser mayor que la fecha final"
        
        # Verificar que no sea un rango excesivamente largo (más de 2 años)
        if (end_date - start_date).days > 730:
            return False, "El rango de fechas no puede ser mayor a 2 años"
        
        return True, ""
    
    @staticmethod
    def validate_social_networks(networks: List[str]) -> Tuple[bool, str]:
        """
        Valida que las redes sociales seleccionadas sean válidas
        
        Args:
            networks: Lista de redes sociales
            
        Returns:
            Tupla con (es_válido, mensaje_error)
        """
        if not networks:
            return False, "Debe seleccionar al menos una red social"
        
        valid_networks = list(FilterConstants.SOCIAL_NETWORKS_DISPLAY_TO_DB.keys())
        invalid_networks = [net for net in networks if net not in valid_networks]
        
        if invalid_networks:
            return False, f"Redes sociales no válidas: {', '.join(invalid_networks)}"
        
        return True, ""
    
    @staticmethod
    def validate_sentiment(sentiment: Optional[str]) -> Tuple[bool, str]:
        """
        Valida que el sentimiento sea válido
        
        Args:
            sentiment: Sentimiento seleccionado
            
        Returns:
            Tupla con (es_válido, mensaje_error)
        """
        if sentiment is None or sentiment == "Todos":
            return True, ""
        
        valid_sentiments = FilterConstants.SENTIMENT_OPTIONS_DISPLAY + ["Todos"]
        if sentiment not in valid_sentiments:
            return False, f"Sentimiento no válido: {sentiment}"
        
        return True, ""


class FilterMapper:
    """Mapeador para convertir entre valores de display y base de datos"""
    
    @staticmethod
    def networks_display_to_db(display_networks: List[str]) -> List[str]:
        """
        Convierte redes sociales de display a valores de BD
        
        Args:
            display_networks: Lista de redes en formato display
            
        Returns:
            Lista de redes en formato BD
        """
        return [
            FilterConstants.SOCIAL_NETWORKS_DISPLAY_TO_DB.get(network, network)
            for network in display_networks
        ]
    
    @staticmethod
    def networks_db_to_display(db_networks: List[str]) -> List[str]:
        """
        Convierte redes sociales de BD a valores de display
        
        Args:
            db_networks: Lista de redes en formato BD
            
        Returns:
            Lista de redes en formato display
        """
        return [
            FilterConstants.SOCIAL_NETWORKS_DB_TO_DISPLAY.get(network, network)
            for network in db_networks
        ]
    
    @staticmethod
    def sentiment_display_to_db(display_sentiment: Optional[str]) -> Optional[str]:
        """
        Convierte sentimiento de display a valor de BD
        
        Args:
            display_sentiment: Sentimiento en formato display
            
        Returns:
            Sentimiento en formato BD o None
        """
        if display_sentiment is None or display_sentiment == "Todos":
            return None
        
        return FilterConstants.SENTIMENT_DISPLAY_TO_DB.get(display_sentiment)
    
    @staticmethod
    def sentiment_db_to_display(db_sentiment: Optional[str]) -> str:
        """
        Convierte sentimiento de BD a valor de display
        
        Args:
            db_sentiment: Sentimiento en formato BD
            
        Returns:
            Sentimiento en formato display
        """
        if db_sentiment is None:
            return "Todos"
        
        return FilterConstants.SENTIMENT_DB_TO_DISPLAY.get(db_sentiment, db_sentiment)


class FilterProcessor:
    """Procesador para aplicar filtros en DataFrames de pandas"""
    
    @staticmethod
    def apply_network_filter(df: pd.DataFrame, selected_networks: List[str]) -> pd.DataFrame:
        """
        Aplica filtro de redes sociales a un DataFrame
        
        Args:
            df: DataFrame a filtrar
            selected_networks: Redes sociales seleccionadas (formato display)
            
        Returns:
            DataFrame filtrado
        """
        if not selected_networks or 'origin' not in df.columns:
            return df
        
        # Convertir a valores de BD para filtrar
        db_networks = FilterMapper.networks_display_to_db(selected_networks)
        return df[df['origin'].isin(db_networks)]
    
    @staticmethod
    def apply_sentiment_filter(df: pd.DataFrame, selected_sentiment: str) -> pd.DataFrame:
        """
        Aplica filtro de sentimiento a un DataFrame
        
        Args:
            df: DataFrame a filtrar
            selected_sentiment: Sentimiento seleccionado (formato display)
            
        Returns:
            DataFrame filtrado
        """
        if selected_sentiment == "Todas" or 'sentiment_pred' not in df.columns:
            return df
        
        # Convertir a valor de BD para filtrar
        db_sentiment = FilterMapper.sentiment_display_to_db(selected_sentiment)
        if db_sentiment is None:
            return df
        
        return df[df['sentiment_pred'] == db_sentiment]
    
    @staticmethod
    def apply_date_filter(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Aplica filtro de fechas a un DataFrame
        
        Args:
            df: DataFrame a filtrar
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            DataFrame filtrado
        """
        if 'created_time' not in df.columns:
            return df
        
        # Asegurar que las fechas sean timestamps de pandas
        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = pd.Timestamp(end_date) + pd.Timedelta(days=1)  # Incluir todo el día final
        
        # Convertir la columna a datetime si no lo es
        df_filtered = df.copy()
        df_filtered['created_time'] = pd.to_datetime(df_filtered['created_time'])
        
        return df_filtered[
            (df_filtered['created_time'] >= start_timestamp) & 
            (df_filtered['created_time'] < end_timestamp)
        ]
    
    @staticmethod
    def apply_sorting(df: pd.DataFrame, sort_option: str) -> pd.DataFrame:
        """
        Aplica ordenamiento a un DataFrame
        
        Args:
            df: DataFrame a ordenar
            sort_option: Opción de ordenamiento
            
        Returns:
            DataFrame ordenado
        """
        df_sorted = df.copy()
        
        if sort_option == 'Fecha (Reciente)' and 'created_time' in df_sorted.columns:
            return df_sorted.sort_values('created_time', ascending=False)
        elif sort_option == 'Fecha (Antigua)' and 'created_time' in df_sorted.columns:
            return df_sorted.sort_values('created_time', ascending=True)
        elif sort_option == 'Confianza (Alta)' and 'sentiment_confidence' in df_sorted.columns:
            return df_sorted.sort_values('sentiment_confidence', ascending=False)
        elif sort_option == 'Confianza (Baja)' and 'sentiment_confidence' in df_sorted.columns:
            return df_sorted.sort_values('sentiment_confidence', ascending=True)
        elif sort_option == 'Likes (Alto)' and 'likes' in df_sorted.columns:
            return df_sorted.sort_values('likes', ascending=False)
        elif sort_option == 'Likes (Bajo)' and 'likes' in df_sorted.columns:
            return df_sorted.sort_values('likes', ascending=True)
        
        return df_sorted
    
    @staticmethod
    def apply_content_type_filter(df: pd.DataFrame, selected_content_type: str) -> pd.DataFrame:
        """
        Aplica filtro de tipo de contenido a un DataFrame
        """
        if selected_content_type == "Todos" or 'table_source' not in df.columns:
            return df
        
        # Encontrar todas las tablas que corresponden al tipo seleccionado
        matching_tables = []
        for table_name, content_type in FilterConstants.CONTENT_TYPE_MAPPING.items():
            if content_type == selected_content_type:
                matching_tables.append(table_name)
        
        if not matching_tables:
            return df
        
        return df[df['table_source'].isin(matching_tables)]

class TimeRangeCalculator:
    """Calculador para rangos de tiempo predefinidos"""
    
    @staticmethod
    def calculate_time_range(time_option: str, reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
        """
        Calcula el rango de fechas basado en la opción seleccionada
        
        Args:
            time_option: Opción de tiempo seleccionada
            reference_date: Fecha de referencia (default: datetime.now())
            
        Returns:
            Tupla con (fecha_inicio, fecha_fin)
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        fecha_fin = reference_date
        
        if time_option == "Últimos 7 días":
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif time_option == "Últimos 30 días":
            fecha_inicio = fecha_fin - timedelta(days=30)
        elif time_option == "Este mes":
            fecha_inicio = fecha_fin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_option == "Últimos 3 meses":
            fecha_inicio = fecha_fin - timedelta(days=90)
        elif time_option == "Histórico Completo":
            fecha_inicio = datetime(2025, 8, 1)  # Fecha de inicio del sistema
        else:  # "Rango personalizado" u otra opción
            # Devolver último mes por defecto
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        return fecha_inicio, fecha_fin


# Funciones de conveniencia para uso directo
def get_available_networks_from_data(df: pd.DataFrame) -> List[str]:
    """
    Obtiene las redes sociales disponibles en un DataFrame
    
    Args:
        df: DataFrame con datos
        
    Returns:
        Lista de redes sociales en formato display
    """
    if df.empty or 'origin' not in df.columns:
        return []
    
    unique_networks_db = df['origin'].unique().tolist()
    return FilterMapper.networks_db_to_display(unique_networks_db)


def get_available_sentiments_from_data(df: pd.DataFrame) -> List[str]:
    """
    Obtiene los sentimientos disponibles en un DataFrame
    
    Args:
        df: DataFrame con datos
        
    Returns:
        Lista de sentimientos en formato display
    """
    if df.empty or 'sentiment_pred' not in df.columns:
        return FilterConstants.SENTIMENT_OPTIONS_DISPLAY
    
    unique_sentiments_db = df['sentiment_pred'].unique().tolist()
    return [
        FilterMapper.sentiment_db_to_display(sentiment) 
        for sentiment in unique_sentiments_db
        if sentiment in FilterConstants.SENTIMENT_OPTIONS_DB
    ]


def get_date_range_from_data(df: pd.DataFrame) -> Tuple[datetime, datetime]:
    """
    Obtiene el rango de fechas de un DataFrame
    
    Args:
        df: DataFrame con datos
        
    Returns:
        Tupla con (fecha_mínima, fecha_máxima)
    """
    if df.empty or 'created_time' not in df.columns:
        now = datetime.now()
        return now - timedelta(days=30), now
    
    df_dates = pd.to_datetime(df['created_time'])
    return df_dates.min().to_pydatetime(), df_dates.max().to_pydatetime()

def get_available_content_types_from_data(df: pd.DataFrame) -> List[str]:
    """
    Obtiene los tipos de contenido únicos disponibles en un DataFrame
    """
    if df.empty or 'table_source' not in df.columns:
        return []
    
    unique_table_sources = df['table_source'].unique().tolist()
    
    # Convertir nombres de tabla a tipos de contenido display
    available_types = set()  # Usar set para eliminar duplicados
    for table_source in unique_table_sources:
        content_type = FilterConstants.CONTENT_TYPE_MAPPING.get(table_source)
        if content_type:
            available_types.add(content_type)
    
    return sorted(list(available_types))


def get_content_type_counts_from_data(df: pd.DataFrame) -> Dict[str, int]:
    """
    Obtiene el conteo de registros por tipo de contenido
    
    Args:
        df: DataFrame con datos
        
    Returns:
        Diccionario con conteos por tipo de contenido
    """
    if df.empty or 'table_source' not in df.columns:
        return {}
    
    table_counts = df['table_source'].value_counts().to_dict()
    
    # Convertir nombres de tabla a tipos de contenido display
    content_type_counts = {}
    for table_source, count in table_counts.items():
        content_type = FilterConstants.CONTENT_TYPE_MAPPING.get(table_source)
        if content_type:
            content_type_counts[content_type] = count
    
    return content_type_counts