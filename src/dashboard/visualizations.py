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
    
    def create_total_timeline(self, filters, df_completo):
        """Crea un gráfico de línea temporal con el total de menciones combinadas"""
        
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
                    'text': 'Volumen Total de Menciones',
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
        
        # Procesar datos para timeline total
        df_timeline = df_completo.copy()
        
        if 'created_time' in df_timeline.columns:
            df_timeline['fecha'] = pd.to_datetime(df_timeline['created_time']).dt.date
            
            # Agrupar solo por fecha (suma de todas las redes)
            timeline_data = df_timeline.groupby('fecha').size().reset_index(name='total_count')
        else:
            timeline_data = pd.DataFrame()
        
        if timeline_data.empty:
            # Sin datos de fecha
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de fecha disponibles",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={
                    'text': 'Volumen Total de Menciones',
                    'xanchor': 'center',
                    'x': 0.5,
                    'font': {'size': 18, 'color': 'white'}
                },
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            return fig
        
        # Crear gráfico de línea única
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timeline_data['fecha'],
            y=timeline_data['total_count'],
            mode='lines+markers',
            name='Total Menciones',
            line=dict(
                color=self.color_palette['primary'],
                width=4
            ),
            marker=dict(
                size=8,
                color=self.color_palette['primary'],
                line=dict(width=2, color='white')
            ),
            fill='tonexty',
            fillcolor=f"rgba(0, 212, 255, 0.1)",
            hovertemplate='<b>Total Menciones</b><br>' +
                        'Fecha: %{x}<br>' +
                        'Volumen: %{y}<br>' +
                        '<extra></extra>'
        ))
        
        # Styling del gráfico
        fig.update_layout(
            title={
                'text': 'Volumen Total de Menciones',
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
            showlegend=False,
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
    
    def create_sentiment_timeline(self, filters, df_completo):
        """Crea un gráfico de línea temporal separado por sentimientos"""
        
        # Verificar si hay datos
        if df_completo.empty or 'sentiment_pred' not in df_completo.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de sentimiento disponibles",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                font_size=16, font_color="white",
                showarrow=False
            )
            fig.update_layout(
                title={'text': 'Evolución de Sentimientos', 'xanchor': 'center', 'x': 0.5, 'font': {'size': 18, 'color': 'white'}},
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white')
            )
            return fig
        
        # Procesar datos
        df_timeline = df_completo.copy()
        df_timeline['fecha'] = pd.to_datetime(df_timeline['created_time']).dt.date
        df_timeline['sentiment_display'] = df_timeline['sentiment_pred'].map({
            'POS': 'Positivo', 'NEU': 'Neutro', 'NEG': 'Negativo'
        })
        
        # Agrupar por fecha y sentimiento
        timeline_data = df_timeline.groupby(['fecha', 'sentiment_display']).size().reset_index(name='count')
        
        fig = go.Figure()
        
        for sentiment in ['Positivo', 'Neutro', 'Negativo']:
            data_sentiment = timeline_data[timeline_data['sentiment_display'] == sentiment]
            
            fig.add_trace(go.Scatter(
                x=data_sentiment['fecha'],
                y=data_sentiment['count'],
                mode='lines+markers',
                name=sentiment,
                line=dict(color=self.sentiment_colors[sentiment], width=3),
                marker=dict(size=6, color=self.sentiment_colors[sentiment]),
                hovertemplate=f'<b>{sentiment}</b><br>Fecha: %{{x}}<br>Cantidad: %{{y}}<extra></extra>'
            ))
        
        fig.update_layout(
            title={'text': 'Evolución de Sentimientos', 'xanchor': 'center', 'x': 0.5, 'font': {'size': 18, 'color': 'white'}},
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='date', title=''),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title=''),
            legend=dict(bgcolor='rgba(0,0,0,0.5)', bordercolor='rgba(255,255,255,0.2)'),
            hovermode='x unified',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig

    def create_social_bars(self, filters, df_completo):
        """Crea un gráfico de barras horizontales con porcentajes por red social"""
        
        if df_completo.empty or 'origin' not in df_completo.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos de redes sociales disponibles",
                x=0.5, y=0.5, xref="paper", yref="paper",
                font_size=16, font_color="white", showarrow=False
            )
            fig.update_layout(
                title={'text': 'Distribución por Red Social', 'xanchor': 'center', 'x': 0.5, 'font': {'size': 18, 'color': 'white'}},
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white')
            )
            return fig
        
        # Contar por red social y calcular porcentajes
        origin_counts = df_completo['origin'].value_counts()
        total_mentions = len(df_completo)
        percentages = [(count / total_mentions) * 100 for count in origin_counts.values]
        
        # Mapear a nombres de display
        display_mapping = {'Facebook': 'Facebook', 'X': 'X (Twitter)', 'Instagram': 'Instagram', 'TikTok': 'TikTok'}
        labels = [display_mapping.get(origin, origin) for origin in origin_counts.index]
        colors = [self.social_colors.get(label, self.color_palette['primary']) if label is not None else self.color_palette['primary'] for label in labels]
        
        fig = go.Figure(data=[go.Bar(
            y=labels,  # Barras horizontales
            x=percentages,
            orientation='h',
            marker_color=colors,
            text=[f'{pct:.1f}%' for pct in percentages],
            textposition='inside',
            textfont=dict(size=14, color='white', family='Arial', weight='bold'),
            hovertemplate='<b>%{y}</b><br>Porcentaje: %{x:.1f}%<br>Cantidad: %{customdata:,}<extra></extra>',
            customdata=origin_counts.values
        )])
        
        fig.update_layout(
            title={'text': 'Distribución por Red Social', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': 'white'}},
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)', 
                title='Porcentaje (%)',
                showticklabels=True,
                range=[0, max(percentages) * 1.1]  # Añadir espacio extra
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)', 
                title='',
                categoryorder='total ascending'  # Ordenar de menor a mayor
            ),
            showlegend=False,
            margin=dict(l=100, r=50, t=80, b=50)  # Más margen izquierdo para etiquetas
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
                    label="🗓️ Período de Análisis",
                    value="N/A",
                    help="Período de análisis del dashboard"
                )
            
            with col3:
                st.metric(
                    label="👥 Aporte por Red", 
                    value="0",
                    help="División de aportes por red"
                )
            
            with col4:
                st.metric(
                    label="🔊 Confianza Promedio",
                    value="N/A",
                    help="Puntuación de confianza promedio"
                )
            return
        
        # Calcular KPIs reales
        total_mentions = len(df_completo)
        
        # Período de análisis - usar fechas de los filtros
        if filters and filters.get('applied'):
            fecha_inicio = filters.get('fecha_inicio')
            fecha_fin = filters.get('fecha_fin')
            
            if fecha_inicio and fecha_fin:
                inicio_str = fecha_inicio.strftime('%d %b')
                fin_str = fecha_fin.strftime('%d %b')
                periodo_display = f"{inicio_str} - {fin_str}"
            else:
                periodo_display = "Personalizado"
        else:
            periodo_display = "N/A"
            
        
        # Sentimiento dominante y su cambio temporal
        if 'sentiment_pred' in df_completo.columns and not df_completo.empty:
            sentiment_counts = df_completo['sentiment_pred'].value_counts()
            sentiment_mapping = {
                'POS': '✅ Positivo', 
                'NEU': '⚖️ Neutro', 
                'NEG': '❌ Negativo'
            }
            
            # Sentimiento dominante
            dominant_sentiment_code = sentiment_counts.index[0]
            dominant_sentiment = sentiment_mapping.get(dominant_sentiment_code, dominant_sentiment_code)
            dominant_percentage = (sentiment_counts.iloc[0] / len(df_completo)) * 100
            
            # Calcular cambio temporal (principio vs final)
            df_temporal = df_completo.copy()
            df_temporal['created_time'] = pd.to_datetime(df_temporal['created_time'])
            df_temporal = df_temporal.sort_values('created_time')
            
            # Dividir en primera y última porción (20% de los datos)
            total_records = len(df_temporal)
            split_size = max(1, total_records // 5)
            
            df_inicio = df_temporal.head(split_size)
            df_final = df_temporal.tail(split_size)
            
            # Calcular porcentajes del sentimiento dominante en cada período
            inicio_count = len(df_inicio[df_inicio['sentiment_pred'] == dominant_sentiment_code])
            final_count = len(df_final[df_final['sentiment_pred'] == dominant_sentiment_code])
            
            inicio_percentage = (inicio_count / len(df_inicio)) * 100 if len(df_inicio) > 0 else 0
            final_percentage = (final_count / len(df_final)) * 100 if len(df_final) > 0 else 0
            
            delta_percentage = final_percentage - inicio_percentage
            
            # Extraer solo el nombre del sentimiento de forma segura
            if dominant_sentiment and ' ' in str(dominant_sentiment):
                sentiment_name = str(dominant_sentiment).split(' ')[1]
            else:
                sentiment_name = str(dominant_sentiment_code)
            
            sentimiento_display = f"{sentiment_name} ({dominant_percentage:.1f}%)"
            sentimiento_delta = f"{delta_percentage:+.1f} pp"

            # Determinar color del delta según el sentimiento
            if dominant_sentiment_code == 'POS':
                # Para positivo: deltas positivos son buenos, usar normal
                delta_color = "normal"
            elif dominant_sentiment_code == 'NEG':
                # Para negativo: deltas positivos son malos, usar inverse
                delta_color = "inverse" 
            else:
                # Neutro: sin color específico
                delta_color = "off"

        else:
            sentimiento_display = "N/A"
            sentimiento_delta = None
            delta_color = "off"
        
        # Confianza promedio
        if 'sentiment_confidence' in df_completo.columns:
            avg_confidence = df_completo['sentiment_confidence'].mean()
            confidence_display = f"{avg_confidence:.2f}"
        else:
            confidence_display = "N/A"
        
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
                label="🗓️ Período de Análisis",
                value=periodo_display,
                help="Período de análisis del dashboard"
            )
        
        with col3:
            st.metric(
                label="🎯 Sentimiento Dominante",
                value=sentimiento_display,
                delta=sentimiento_delta,
                delta_color=delta_color,
                help="Sentimiento mayoritario y cambio desde inicio del período"
            )
        
        with col4:
            st.metric(
                label="🔊 Confianza Promedio",
                value=confidence_display,
                help="Confianza promedio del análisis de sentimiento"
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
                timeline_fig = self.create_total_timeline(filters, df_completo)
                st.plotly_chart(timeline_fig, use_container_width=True, key="chart_timeline")
            
            # Gráfico Timeline por Sentimiento
            with st.spinner("Generando gráfico de sentimientos..."):
                sentiment_fig = self.create_sentiment_timeline(filters, df_completo)
                st.plotly_chart(sentiment_fig, use_container_width=True, key="chart_sentiment_timeline")
        
        with col2:
            # Gráfico Donut de Sentimientos
            with st.spinner("Generando gráfico de sentimientos..."):
                sentiment_fig = self.create_sentiment_donut(filters, df_completo)
                st.plotly_chart(sentiment_fig, use_container_width=True, key="chart_sentiment")
            
            # Gráfico Pie de Distribución por Red Social
            with st.spinner("Generando gráfico de distribución por red social..."):
                social_fig = self.create_social_bars(filters, df_completo)
                st.plotly_chart(social_fig, use_container_width=True, key="chart_social_bars")
        
        return True