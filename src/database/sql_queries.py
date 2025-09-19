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
        
        # Mapeo optimizado - precalculado una sola vez
        self.column_mappings = self._build_column_mappings()
        
        # Mapeo de polaridad a valores legibles
        self.sentiment_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro',
            'NEG': 'Negativo'
        }
    
    def _build_column_mappings(self) -> Dict[str, Dict[str, str]]:
        """Precalcula mapeos de columnas para todas las tablas - OPTIMIZACIÓN"""
        mappings = {}
        
        # Definir mapeos específicos por tabla
        column_configs = {
            # Facebook
            'posts_facebook': {
                'author': 'owner_full_name',
                'likes': 'reactions_like_count',
                'comments': 'comments_count',
                'shares': 'shares_count'
            },
            'comentarios_facebook': {
                'author': 'owner_full_name',
                'likes': 'reactions_like_count',
                'comments': 'comments_count',
                'shares': '0'
            },
            
            # Instagram
            'posts_instagram': {
                'author': 'owner_username',
                'likes': 'likes_count',
                'comments': 'comments_count',
                'shares': '0'
            },
            'comentarios_instagram': {
                'author': 'owner_username',
                'likes': 'likes_count',
                'comments': '0',
                'shares': '0'
            },
            
            # X (Twitter)
            'posts_x': {
                'author': 'author_username',
                'likes': 'favorite_count',
                'comments': 'reply_count',
                'shares': 'retweet_count'
            },
            'respuestas_x': {
                'author': 'author_username',
                'likes': 'favorite_count',
                'comments': 'reply_count',
                'shares': 'retweet_count'
            },
            'quotes_x': {
                'author': 'author_username',
                'likes': 'favorite_count',
                'comments': 'reply_count',
                'shares': 'retweet_count'
            },
            
            # TikTok
            'posts_tiktok': {
                'author': 'author_username',
                'likes': 'digg_count',
                'comments': 'comment_count',
                'shares': 'share_count'
            },
            'comentarios_tiktok': {
                'author': 'author_username',
                'likes': 'digg_count',
                'comments': 'reply_count',
                'shares': '0'
            }
        }
        
        # Procesar todas las tablas
        for table_name, columns in column_configs.items():
            mappings[table_name] = {
                'author': columns.get('author', 'NULL'),
                'likes': f"COALESCE({columns.get('likes', '0')}, 0)",
                'comments': f"COALESCE({columns.get('comments', '0')}, 0)",
                'shares': f"COALESCE({columns.get('shares', '0')}, 0)"
            }
        
        return mappings
    
    def build_optimized_query(self, 
                            alerta_id: int,
                            origins: List[str],
                            start_date: datetime,
                            end_date: datetime,
                            sentiment: Optional[str] = None,
                            limit: int = 100) -> str:
        """Construye una query optimizada con filtros tempranos y menos UNIONs"""
        
        # Mapear valores de display a valores de BD
        display_to_db = {
            "Facebook": "Facebook",
            "X (Twitter)": "X", 
            "Instagram": "Instagram",
            "TikTok": "TikTok"
        }
        
        # Construir lista de tablas necesarias con sus orígenes
        table_configs = []
        for origin_display in origins:
            if origin_display in self.table_mapping:
                origin_db = display_to_db.get(origin_display, origin_display)
                tables = self.table_mapping[origin_display]
                
                for table in tables:
                    if table in self.column_mappings:
                        table_configs.append({
                            'table': table,
                            'origin_db': origin_db,
                            'mappings': self.column_mappings[table]
                        })
        
        if not table_configs:
            return ""
        
        # Construir CTE (Common Table Expression) para cada tabla - OPTIMIZACIÓN
        cte_queries = []
        for i, config in enumerate(table_configs):
            table = config['table']
            mappings = config['mappings']
            
            # Query optimizada con filtros tempranos
            cte_query = f"""
            t{i} AS (
                SELECT 
                    id,
                    alerta_id,
                    created_time,
                    origin,
                    text,
                    sentiment_pred,
                    sentiment_confidence,
                    {mappings['author']} as author,
                    {mappings['likes']} as likes,
                    {mappings['comments']} as comments,
                    {mappings['shares']} as shares,
                    '{table}' as table_source
                FROM ocdul.{table}
                WHERE alerta_id = %s
                    AND origin = %s
                    AND created_time BETWEEN %s AND %s
                    {"AND sentiment_pred = %s" if sentiment and sentiment in ['POS', 'NEU', 'NEG'] else ""}
            )"""
            
            cte_queries.append(cte_query)
        
        # Query principal con CTE - MUCHO MÁS EFICIENTE
        final_query = f"""
        WITH {', '.join(cte_queries)}
        SELECT * FROM (
            {' UNION ALL '.join([f"SELECT * FROM t{i}" for i in range(len(table_configs))])}
        ) combined
        ORDER BY created_time DESC
        {"LIMIT " + str(limit) if limit is not None else ""}
        """
        
        return final_query
    
    def get_optimized_parameters(self,
                               alerta_id: int,
                               origins: List[str],
                               start_date: datetime,
                               end_date: datetime,
                               sentiment: Optional[str] = None) -> List:
        """Genera parámetros optimizados para la query - MENOS REPETICIÓN"""
        
        display_to_db = {
            "Facebook": "Facebook",
            "X (Twitter)": "X", 
            "Instagram": "Instagram",
            "TikTok": "TikTok"
        }
        
        params = []
        
        for origin_display in origins:
            if origin_display in self.table_mapping:
                origin_db = display_to_db.get(origin_display, origin_display)
                tables = self.table_mapping[origin_display]
                
                for table in tables:
                    if table in self.column_mappings:
                        # Parámetros base para cada tabla
                        table_params = [alerta_id, origin_db, start_date, end_date]
                        
                        # Agregar parámetro de sentimiento si se especifica
                        if sentiment and sentiment in ['POS', 'NEU', 'NEG']:
                            table_params.append(sentiment)
                        
                        params.extend(table_params)
        
        return params
    
    # MÉTODOS LEGACY - Mantener compatibilidad
    def build_unified_query(self, 
                        alerta_id: int,
                        origins: List[str],
                        start_date: datetime,
                        end_date: datetime,
                        sentiment: Optional[str] = None,
                        limit: int = 100) -> str:
        """Método legacy - redirige a versión optimizada"""
        return self.build_optimized_query(alerta_id, origins, start_date, end_date, sentiment, limit)
    
    def get_query_parameters(self,
                       alerta_id: int,
                       origins: List[str],
                       start_date: datetime,
                       end_date: datetime,
                       sentiment: Optional[str] = None) -> List:
        """Método legacy - redirige a versión optimizada"""
        return self.get_optimized_parameters(alerta_id, origins, start_date, end_date, sentiment)
    
    def get_author_column(self, table_name: str) -> str:
        """Método legacy - mantener para compatibilidad"""
        if table_name in self.column_mappings:
            return self.column_mappings[table_name]['author']
        return 'NULL'
    
    def get_engagement_columns(self, table_name: str) -> Dict[str, str]:
        """Método legacy - mantener para compatibilidad"""
        if table_name in self.column_mappings:
            mappings = self.column_mappings[table_name]
            return {
                'likes': mappings['likes'],
                'comments': mappings['comments'],
                'shares': mappings['shares']
            }
        return {'likes': '0', 'comments': '0', 'shares': '0'}
    
    def get_tables_for_origins(self, origins: List[str]) -> List[str]:
        """Obtiene la lista de tablas necesarias para los orígenes especificados"""
        tables = []
        for origin in origins:
            if origin in self.table_mapping:
                tables.extend(self.table_mapping[origin])
        return list(set(tables))