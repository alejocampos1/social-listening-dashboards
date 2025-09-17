import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class SocialListeningQueryBuilder:
    def __init__(self):
        # Mapeo de tablas por origen
        self.table_mapping = {
            'Facebook': ['posts_facebook', 'comentarios_facebook'],
            'Instagram': ['posts_instagram', 'comentarios_instagram'],
            'X (Twitter)': ['posts_x', 'respuestas_x', 'quotes_x'],
            'TikTok': ['posts_tiktok', 'comentarios_tiktok']
        }
        
        # Mapeo de columnas comunes a nombres estándar
        self.column_mapping = {
            # Columnas base (presentes en todas las tablas)
            'id': 'id',
            'alerta_id': 'alerta_id',
            'created_time': 'created_time',
            'origin': 'origin',
            'text': 'text',
            'sentiment_pred': 'sentiment_pred',
            'sentiment_confidence': 'sentiment_confidence',
            
            # Campos de autor/usuario (varían por tabla)
            'author_facebook': {
                'posts_facebook': 'owner_full_name',
                'comentarios_facebook': 'owner_full_name'
            },
            'author_instagram': {
                'posts_instagram': 'owner_username',
                'comentarios_instagram': 'owner_username'
            },
            'author_x': {
                'posts_x': 'author_username',
                'respuestas_x': 'author_username',
                'quotes_x': 'author_username'
            },
            'author_tiktok': {
                'posts_tiktok': 'author_username',
                'comentarios_tiktok': 'author_username'
            },
            
            # Campos de engagement (varían por tabla)
            'likes_facebook': {
                'posts_facebook': 'reactions_like_count',
                'comentarios_facebook': 'reactions_like_count'
            },
            'likes_instagram': {
                'posts_instagram': 'likes_count',
                'comentarios_instagram': 'likes_count'
            },
            'likes_x': {
                'posts_x': 'favorite_count',
                'respuestas_x': 'favorite_count',
                'quotes_x': 'favorite_count'
            },
            'likes_tiktok': {
                'posts_tiktok': 'digg_count',
                'comentarios_tiktok': 'digg_count'
            },
            
            # Campos de comentarios/replies
            'comments_facebook': {
                'posts_facebook': 'comments_count',
                'comentarios_facebook': 'comments_count'
            },
            'comments_instagram': {
                'posts_instagram': 'comments_count',
                'comentarios_instagram': None  # No disponible en comentarios
            },
            'comments_x': {
                'posts_x': 'reply_count',
                'respuestas_x': 'reply_count',
                'quotes_x': 'reply_count'
            },
            'comments_tiktok': {
                'posts_tiktok': 'comment_count',
                'comentarios_tiktok': 'reply_count'
            },
            
            # Campos de shares/retweets
            'shares_facebook': {
                'posts_facebook': 'shares_count',
                'comentarios_facebook': None
            },
            'shares_x': {
                'posts_x': 'retweet_count',
                'respuestas_x': 'retweet_count',
                'quotes_x': 'retweet_count'
            },
            'shares_tiktok': {
                'posts_tiktok': 'share_count',
                'comentarios_tiktok': None
            }
        }
        
        # Mapeo de polaridad a valores legibles
        self.sentiment_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro',
            'NEG': 'Negativo'
        }
    
    def get_author_column(self, table_name: str) -> str:
        """Obtiene el nombre de la columna de autor para una tabla específica"""
        for platform, tables in self.table_mapping.items():
            if table_name in tables:
                # Mapeo específico para cada plataforma
                if platform == "X (Twitter)":
                    platform_key = "author_x"
                else:
                    platform_key = f"author_{platform.lower().replace(' ', '_')}"
                
                if platform_key in self.column_mapping:
                    result = self.column_mapping[platform_key].get(table_name, 'NULL')
                    return result
        return 'NULL'
    
    def get_engagement_columns(self, table_name: str) -> Dict[str, str]:
        """Obtiene las columnas de engagement para una tabla específica"""
        engagement = {}
        
        # Determinar plataforma
        platform = None
        for p, tables in self.table_mapping.items():
            if table_name in tables:
                platform = p.lower().replace(' (twitter)', '_x').replace(' ', '_')
                break
        
        if platform:
            # Likes
            likes_key = f"likes_{platform}"
            if likes_key in self.column_mapping:
                engagement['likes'] = self.column_mapping[likes_key].get(table_name, '0')
            
            # Comments
            comments_key = f"comments_{platform}"
            if comments_key in self.column_mapping:
                engagement['comments'] = self.column_mapping[comments_key].get(table_name, '0')
            
            # Shares
            shares_key = f"shares_{platform}"
            if shares_key in self.column_mapping:
                engagement['shares'] = self.column_mapping[shares_key].get(table_name, '0')
        
        # Valores por defecto si no se encuentran
        for metric in ['likes', 'comments', 'shares']:
            if metric not in engagement or engagement[metric] is None:
                engagement[metric] = '0'
        
        return engagement
    
    def build_unified_query(self, 
                        alerta_id: int,
                        origins: List[str],
                        start_date: datetime,
                        end_date: datetime,
                        sentiment: Optional[str] = None,
                        limit: int = 100) -> str:
        """Construye una query unificada para obtener datos de social listening"""
        
        # Mapear valores de display a valores de BD
        display_to_db = {
            "Facebook": "Facebook",
            "X (Twitter)": "X", 
            "Instagram": "Instagram",
            "TikTok": "TikTok"
        }
        
        union_queries = []
        
        for origin_display in origins:
            if origin_display in self.table_mapping:
                # Obtener valor de BD para esta red social
                origin_db = display_to_db.get(origin_display, origin_display)
                tables = self.table_mapping[origin_display]
                
                for table in tables:
                    # Obtener columnas específicas para esta tabla
                    author_col = self.get_author_column(table)
                    engagement_cols = self.get_engagement_columns(table)
                    
                    # Construir SELECT para esta tabla
                    select_query = f"""
                    SELECT 
                        id,
                        alerta_id,
                        created_time,
                        origin,
                        text,
                        sentiment_pred,
                        sentiment_confidence,
                        {author_col} as author,
                        {engagement_cols['likes']} as likes,
                        {engagement_cols['comments']} as comments,
                        {engagement_cols['shares']} as shares,
                        '{table}' as table_source
                    FROM ocdul.{table}
                    WHERE alerta_id = %s
                        AND origin = %s
                        AND created_time BETWEEN %s AND %s
                    """
                    
                    # Agregar filtro de sentimiento si se especifica
                    if sentiment and sentiment in ['POS', 'NEU', 'NEG']:
                        select_query += " AND sentiment_pred = %s"
                    
                    union_queries.append(select_query)
        
        if not union_queries:
            return ""
        
        # Unir todas las queries
        final_query = " UNION ALL ".join(union_queries)
        
        # Agregar ORDER BY y LIMIT
        final_query += """
        ORDER BY created_time DESC
        """

        if limit is not None:
            final_query += f" LIMIT {limit}"
        
        return final_query
    
    def get_query_parameters(self,
                       alerta_id: int,
                       origins: List[str],
                       start_date: datetime,
                       end_date: datetime,
                       sentiment: Optional[str] = None) -> List:
        """Genera la lista de parámetros para la query"""
        
        # Mapear valores de display a valores de BD
        display_to_db = {
            "Facebook": "Facebook",
            "X (Twitter)": "X", 
            "Instagram": "Instagram",
            "TikTok": "TikTok"
        }
        
        params = []
        
        for origin_display in origins:
            if origin_display in self.table_mapping:
                # Obtener valor de BD para esta red social
                origin_db = display_to_db.get(origin_display, origin_display)
                tables = self.table_mapping[origin_display]
                
                for table in tables:
                    # Parámetros base para cada tabla - usar valor de BD
                    table_params = [alerta_id, origin_db, start_date, end_date]
                    
                    # Agregar parámetro de sentimiento si se especifica
                    if sentiment and sentiment in ['POS', 'NEU', 'NEG']:
                        table_params.append(sentiment)
                    
                    params.extend(table_params)
        
        return params
    
    def get_tables_for_origins(self, origins: List[str]) -> List[str]:
        """Obtiene la lista de tablas necesarias para los orígenes especificados"""
        tables = []
        for origin in origins:
            if origin in self.table_mapping:
                tables.extend(self.table_mapping[origin])
        return list(set(tables))