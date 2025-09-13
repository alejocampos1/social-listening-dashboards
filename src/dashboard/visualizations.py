import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    
    def create_timeline_chart(self, filters, alerta_id, db_connection):
        """Crea el gráfico de timeline por red social usando datos reales"""
        
        # Convertir polaridad de filtro a código de BD
        sentiment_code = None
        if filters['polaridad'] != 'Todos':
            sentiment_mapping = {
                'Positivo': 'POS',
                'Neutro': 'NEU',
                'Negativo': 'NEG'
            }
            sentiment_code = sentiment_mapping.get(filters['polaridad'])
        
        # Obtener datos reales de timeline
        df = db_connection.get_timeline_data(
            alerta_id=alerta_id,
            origins=filters['origen'],
            start_date=filters['fecha_inicio'],
            end_date=filters['fecha_fin'],
            sentiment=sentiment_code
        )
        
        # Verificar si hay datos
        if df.empty:
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
        
        # Crear gráfico de líneas múltiples
        fig = go.Figure()
        
        for red_social in filters['origen']:
            # Filtrar datos para esta red social
            data_red = df[df['origin'] == red_social] if 'origin' in df.columns else pd.DataFrame()
            
            if not data_red.empty:
                fig.add_trace(go.Scatter(
                    x=data_red['fecha'],
                    y=data_red['total_count'],
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
                'x': 0.5,
                'font': {'size': 18, 'color': 'white'}
            },
            xaxis_title='Fecha',
            yaxis_title='Volumen de Menciones',
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
    
    def create_sentiment_donut(self, filters, alerta_id, db_connection):
        """Crea el gráfico donut de distribución de sentimientos usando datos reales"""
        
        # Obtener datos reales de distribución de sentimientos
        df = db_connection.get_sentiment_distribution(
            alerta_id=alerta_id,
            origins=filters['origen'],
            start_date=filters['fecha_inicio'],
            end_date=filters['fecha_fin']
        )
        
        # Verificar si hay datos
        if df.empty:
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
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            return fig
        
        # Convertir códigos de sentimiento a texto legible
        sentiment_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro',
            'NEG': 'Negativo'
        }
        
        df['sentiment_display'] = df['sentiment_pred'].map(sentiment_mapping).fillna('Desconocido')
        
        # Si hay filtro de polaridad específico, mostrar solo ese
        if filters['polaridad'] != 'Todos':
            df = df[df['sentiment_display'] == filters['polaridad']]
            
            if df.empty:
                # Crear gráfico vacío para filtro específico
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No hay datos para polaridad: {filters['polaridad']}",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    font_size=16, font_color="white",
                    showarrow=False
                )
                fig.update_layout(
                    title={
                        'text': 'Distribución de Polaridad',
                        'x': 0.5,
                        'font': {'size': 18, 'color': 'white'}
                    },
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    showlegend=False
                )
                return fig
        
        # Colores para cada sentimiento
        colors = [self.sentiment_colors.get(sentiment, self.color_palette['primary']) 
                for sentiment in df['sentiment_display']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df['sentiment_display'],
            values=df['count'],
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
        total_mentions = df['count'].sum()
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
                'font': {'size': 18, 'color': 'white'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
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
    
    def render_kpis(self, filters, alerta_id, db_connection):
        """Renderiza los KPIs principales usando datos reales"""
        
        # Convertir polaridad de filtro a código de BD
        sentiment_code = None
        if filters['polaridad'] != 'Todos':
            sentiment_mapping = {
                'Positivo': 'POS',
                'Neutro': 'NEU',
                'Negativo': 'NEG'
            }
            sentiment_code = sentiment_mapping.get(filters['polaridad'])
        
        # Obtener datos para calcular KPIs
        df = db_connection.get_social_listening_data(
            alerta_id=alerta_id,
            origins=filters['origen'],
            start_date=filters['fecha_inicio'],
            end_date=filters['fecha_fin'],
            sentiment=sentiment_code,
        )
        
        # Verificar si hay datos
        if df.empty:
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
        
        # Calcular KPIs
        total_mentions = db_connection.get_total_mentions_count(
                        alerta_id=alerta_id,
                        origins=filters['origen'],
                        start_date=filters['fecha_inicio'],
                        end_date=filters['fecha_fin'],
                        sentiment=sentiment_code
                    )
        
        # Confianza promedio
        if 'sentiment_confidence' in df.columns:
            avg_confidence = df['sentiment_confidence'].mean()
            confidence_display = f"{avg_confidence:.2f}"
            confidence_delta = None  # No tenemos datos históricos para comparar
        else:
            confidence_display = "N/A"
            confidence_delta = None
        
        # Total de likes
        if 'likes' in df.columns:
            total_likes = df['likes'].fillna(0).sum()
            likes_display = f"{int(total_likes):,}"
        else:
            total_likes = 0
            likes_display = "N/A"
        
        # Calcular sentimiento promedio
        if 'sentiment_pred' in df.columns:
            sentiment_counts = df['sentiment_pred'].value_counts()
            
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
                delta=None,  # Sin datos históricos para comparar
                help="Número total de menciones en el período seleccionado"
            )
        
        with col2:
            st.metric(
                label="🎯 Confianza Promedio",
                value=confidence_display,
                delta=confidence_delta,
                help="Confianza promedio del análisis de sentimiento"
            )
        
        with col3:
            st.metric(
                label="👥 Total Likes", 
                value=likes_display,
                delta=None,  # Sin datos históricos para comparar
                help="Suma total de likes/reacciones"
            )
        
        with col4:
            st.metric(
                label="😊 Sentimiento",
                value=sentiment_display,
                delta=None,  # Sin datos históricos para comparar
                delta_color=sentiment_delta_color,
                help="Puntuación de sentimiento promedio (-100 a +100)"
            )
    
    def render_visualizations(self, filters, alerta_id, db_connection):
        """Renderiza todas las visualizaciones usando datos reales"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver las visualizaciones")
            return
        
        # KPIs principales
        st.subheader("📊 Métricas Principales")
        self.render_kpis(filters, alerta_id, db_connection)
        
        st.divider()
        
        # Gráficos principales
        st.subheader("📈 Visualizaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico Timeline
            with st.spinner("Generando gráfico de timeline..."):
                timeline_fig = self.create_timeline_chart(filters, alerta_id, db_connection)
                st.plotly_chart(timeline_fig, use_container_width=True)
        
        with col2:
            # Gráfico Donut de Sentimientos
            with st.spinner("Generando gráfico de sentimientos..."):
                sentiment_fig = self.create_sentiment_donut(filters, alerta_id, db_connection)
                st.plotly_chart(sentiment_fig, use_container_width=True)
        
        return True