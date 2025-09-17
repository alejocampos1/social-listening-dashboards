import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .filters import FilterManager
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class VisualizationManager:
    def __init__(self):
        # Colores basados en la referencia visual (tema oscuro profesional)
        self.color_palette = {
            'primary': '#00D4FF',      # Cyan
            'secondary': '#FF006B',    # Magenta  
            'accent': '#8B5CF6',       # Púrpura
            'success': '#10B981',      # Verde
            'warning': '#F59E0B',      # Amarillo
            'background': '#0E1117',   # Fondo oscuro
            'surface': '#262730'       # Superficie
        }
        
        self.social_colors = {
            'Facebook': '#1877F2',
            'Instagram': '#E4405F', 
            'X (Twitter)': '#1DA1F2',
            'TikTok': '#000000'
        }
        
        self.sentiment_colors = {
            'Positivo': self.color_palette['success'],
            'Neutro': self.color_palette['warning'],
            'Negativo': self.color_palette['secondary']
        }
    
    def create_timeline_chart(self, filters, df_completo):
        """Crea el gráfico de timeline por red social usando datos compartidos"""
        
        # Verificar si hay datos
        if df_completo.empty:
            # Crear gráfico vacío con mensaje
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos disponibles para el período seleccionado",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={
                    'text': 'Volumen de Menciones por Red Social',
                    'xanchor': 'center',
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        # Procesar datos para timeline - agrupar por fecha y origen
        df_timeline = df_completo.copy()
        
        # Convertir created_time a fecha si es necesario
        if 'created_time' in df_timeline.columns:
            df_timeline['fecha'] = pd.to_datetime(df_timeline['created_time']).dt.date
            
            # Agrupar por fecha y origen
            timeline_data = df_timeline.groupby(['fecha', 'origin']).size().reset_index(name='total_count')
        else:
            # Si no hay datos de fecha, crear gráfico vacío
            timeline_data = pd.DataFrame()
        
        # Crear gráfico de líneas múltiples
        fig = go.Figure()

        # Mapear valores de display a BD
        display_to_db = {
            "Facebook": "Facebook",
            "X (Twitter)": "X", 
            "Instagram": "Instagram",
            "TikTok": "TikTok"
        }
        
        for red_social in filters['origen']:
            # Convertir a valor de BD para filtrar los datos
            red_social_db = display_to_db.get(red_social, red_social)
            
            # Filtrar datos para esta red social (usando valor de BD)
            data_red = timeline_data[timeline_data['origin'] == red_social_db] if not timeline_data.empty else pd.DataFrame()
            
            if not data_red.empty:
                fig.add_trace(go.Scatter(
                    x=data_red['fecha'],
                    y=data_red['total_count'],
                    mode='lines+markers',
                    name=red_social,  # Mostrar nombre de display
                    line=dict(
                        color=self.social_colors.get(red_social, self.color_palette['primary']),
                        width=3
                    ),
                    marker=dict(
                        size=6,
                        color=self.social_colors.get(red_social, self.color_palette['primary']),
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=f'<b>{red_social}</b><br>' +
                                'Fecha: %{x}<br>' +
                                'Volumen: %{y}<br>' +
                                '<extra></extra>'
                ))
            else:
                # Agregar serie vacía para mantener consistencia en la leyenda
                fig.add_trace(go.Scatter(
                    x=[],
                    y=[],
                    mode='lines+markers',
                    name=red_social,
                    line=dict(
                        color=self.social_colors.get(red_social, self.color_palette['primary']),
                        width=3
                    ),
                    marker=dict(
                        size=6,
                        color=self.social_colors.get(red_social, self.color_palette['primary']),
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=f'<b>{red_social}</b><br>Sin datos<extra></extra>'
                ))
        
        # Styling del gráfico
        fig.update_layout(
            title={
                'text': 'Volumen de Menciones por Red Social',
                'xanchor': 'center',
                'x': 0.5,
                'font': {'size': 18, 'color': 'white'}
            },
            xaxis_title='',
            yaxis_title='',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True,
                type='date'
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True
            ),
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            ),
            hovermode='x unified'
        )
        
        return fig
    
    def create_sentiment_donut(self, filters, df_completo):
        """Crea el gráfico donut de distribución de sentimientos usando datos compartidos"""
        
        # Verificar si hay datos
        if df_completo.empty:
            # Crear gráfico vacío con mensaje
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de sentimiento disponibles",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={
                    'text': 'Distribución de Polaridad',
                    'xanchor': 'center',
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            return fig
        
        # Procesar datos de sentimiento
        if 'sentiment_pred' not in df_completo.columns:
            # Sin datos de sentimiento
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de sentimiento disponibles",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={
                    'text': 'Distribución de Polaridad',
                    'xanchor': 'center',
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            return fig
        
        # Contar sentimientos
        sentiment_counts = df_completo['sentiment_pred'].value_counts()
        
        # Convertir códigos de sentimiento a texto legible
        sentiment_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro',
            'NEG': 'Negativo'
        }
        
        # Crear DataFrame para el gráfico
        chart_data = []
        for sentiment_code, count in sentiment_counts.items():
            if sentiment_code in sentiment_mapping:
                chart_data.append({
                    'sentiment_display': sentiment_mapping[sentiment_code],
                    'count': count
                })
        
        if not chart_data:
            # Sin datos válidos de sentimiento
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de sentimiento válidos",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={
                    'text': 'Distribución de Polaridad',
                    'xanchor': 'center',
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            return fig
        
        df_sentiments = pd.DataFrame(chart_data)
        
        # Colores para cada sentimiento
        colors = [self.sentiment_colors.get(sentiment, self.color_palette['primary']) 
                for sentiment in df_sentiments['sentiment_display']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df_sentiments['sentiment_display'],
            values=df_sentiments['count'],
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=14, color='white'),
            hovertemplate='<b>%{label}</b><br>' +
                        'Cantidad: %{value}<br>' +
                        'Porcentaje: %{percent}<br>' +
                        '<extra></extra>'
        )])
        
        # Agregar texto central con total
        total_mentions = df_sentiments['count'].sum()
        fig.add_annotation(
            text=f"<b>{total_mentions:,}</b><br>Total",
            x=0.5, y=0.5,
            font_size=16,
            font_color="white",
            showarrow=False
        )
        
        fig.update_layout(
            title={
                'text': 'Distribución de Polaridad',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'white'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1,
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        return fig
    
    def render_filters_summary(self, filter_manager):
        """Renderiza un resumen de los filtros aplicados"""
        summary = filter_manager.get_filter_summary()
        filters = st.session_state.filters
        
        # Crear texto descriptivo de fechas
        fecha_inicio_str = filters['fecha_inicio'].strftime('%d/%m/%Y')
        fecha_fin_str = filters['fecha_fin'].strftime('%d/%m/%Y')
        
        # Crear texto de plataformas
        if len(filters['origen']) == 4:
            plataformas_texto = "todas las plataformas"
        else:
            plataformas_texto = ", ".join(filters['origen'])
        
        # Crear texto de polaridad
        polaridad_texto = f"Sentimiento {filters['polaridad']}" if filters['polaridad'] != 'Todos' else "Todos los sentimientos"
        
        st.markdown(f"""
        <small style='color: rgba(255,255,255,0.4); text-align: center; display: block; margin-top: 2rem;'>
            Mostrando datos de {plataformas_texto} desde {fecha_inicio_str} hasta {fecha_fin_str} ({summary['date_range_days']} días) • {polaridad_texto}
        </small>
        """, unsafe_allow_html=True)
    
    def render_kpis(self, filters, df_completo):
        """Renderiza los KPIs principales usando datos compartidos"""
        
        # Verificar si hay datos
        if df_completo.empty:
            # Mostrar KPIs vacíos
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📊 Total Menciones",
                    value="0",
                    help="Número total de menciones en el período seleccionado"
                )
            
            with col2:
                st.metric(
                    label="🎯 Confianza Promedio",
                    value="N/A",
                    help="Confianza promedio del análisis de sentimiento"
                )
            
            with col3:
                st.metric(
                    label="👥 Total Likes", 
                    value="0",
                    help="Suma total de likes/reacciones"
                )
            
            with col4:
                st.metric(
                    label="😊 Sentimiento",
                    value="N/A",
                    help="Puntuación de sentimiento promedio"
                )
            return
        
        # Calcular KPIs reales
        total_mentions = len(df_completo)
        
        # Confianza promedio
        if 'sentiment_confidence' in df_completo.columns:
            avg_confidence = df_completo['sentiment_confidence'].mean()
            confidence_display = f"{avg_confidence:.2f}"
        else:
            confidence_display = "N/A"
        
        # Total de likes
        if 'likes' in df_completo.columns:
            total_likes = df_completo['likes'].fillna(0).sum()
            likes_display = f"{int(total_likes):,}"
        else:
            total_likes = 0
            likes_display = "N/A"
        
        # Calcular sentimiento promedio
        if 'sentiment_pred' in df_completo.columns:
            sentiment_counts = df_completo['sentiment_pred'].value_counts()
            
            # Calcular weighted score
            positive_count = sentiment_counts.get('POS', 0)
            neutral_count = sentiment_counts.get('NEU', 0)
            negative_count = sentiment_counts.get('NEG', 0)
            
            if total_mentions > 0:
                # Escala: Positivo=+1, Neutro=0, Negativo=-1
                weighted_score = (positive_count * 1 + neutral_count * 0 + negative_count * -1) / total_mentions
                sentiment_score = weighted_score * 100  # Convertir a escala 0-100
                sentiment_display = f"{sentiment_score:+.1f}"
                
                # Determinar color del delta
                if sentiment_score >= 0:
                    sentiment_delta_color = "normal"
                else:
                    sentiment_delta_color = "inverse"
            else:
                sentiment_display = "N/A"
                sentiment_delta_color = "normal"
        else:
            sentiment_display = "N/A"
            sentiment_delta_color = "normal"
        
        # Renderizar KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Menciones",
                value=f"{total_mentions:,}",
                help="Número total de menciones en el período seleccionado"
            )
        
        with col2:
            st.metric(
                label="🎯 Confianza Promedio",
                value=confidence_display,
                help="Confianza promedio del análisis de sentimiento"
            )
        
        with col3:
            st.metric(
                label="👥 Total Likes", 
                value=likes_display,
                help="Suma total de likes/reacciones"
            )
        
        with col4:
            st.metric(
                label="😊 Sentimiento",
                value=sentiment_display,
                delta_color=sentiment_delta_color,
                help="Puntuación de sentimiento promedio (-100 a +100)"
            )
                
    def render_visualizations(self, filters, df_completo, filter_manager):
        """Renderiza todas las visualizaciones usando datos reales"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver las visualizaciones")
            return
        
        # KPIs principales
        st.subheader("📊 Métricas Principales")
        self.render_kpis(filters, df_completo)
        self.render_filters_summary(filter_manager)
        
        st.divider()
        
        # Gráficos principales
        st.subheader("📈 Visualizaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico Timeline
            with st.spinner("Generando gráfico de timeline..."):
                timeline_fig = self.create_timeline_chart(filters, df_completo)
                st.plotly_chart(timeline_fig, use_container_width=True, key="chart_timeline")
        
        with col2:
            # Gráfico Donut de Sentimientos
            with st.spinner("Generando gráfico de sentimientos..."):
                sentiment_fig = self.create_sentiment_donut(filters, df_completo)
                st.plotly_chart(sentiment_fig, use_container_width=True, key="chart_sentiment")
        
        return True