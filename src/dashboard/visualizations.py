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
    
    def generate_timeline_data(self, filters):
        """Genera datos para el gráfico timeline"""
        start_date = filters['fecha_inicio']
        end_date = filters['fecha_fin']
        days = (end_date - start_date).days
        
        # Crear fechas
        dates = [start_date + timedelta(days=i) for i in range(days + 1)]
        
        data = []
        for date in dates:
            for red_social in filters['origen']:
                # Generar volumen aleatorio con tendencias realistas
                base_volume = random.randint(10, 100)
                
                # Agregar variación por día de la semana
                if date.weekday() in [5, 6]:  # Fin de semana
                    volume_modifier = 0.7
                else:
                    volume_modifier = 1.0
                
                # Agregar variación por red social
                if red_social == 'Facebook':
                    social_modifier = 1.2
                elif red_social == 'Instagram':
                    social_modifier = 1.0
                elif red_social == 'X (Twitter)':
                    social_modifier = 0.8
                else:  # TikTok
                    social_modifier = 1.1
                
                final_volume = int(base_volume * volume_modifier * social_modifier)
                
                data.append({
                    'Fecha': date,
                    'Red Social': red_social,
                    'Volumen': final_volume
                })
        
        return pd.DataFrame(data)
    
    def generate_sentiment_data(self, filters):
        """Genera datos para distribución de sentimientos"""
        if filters['polaridad'] != 'Todos':
            # Si hay filtro específico, mostrar solo ese
            return pd.DataFrame({
                'Polaridad': [filters['polaridad']],
                'Count': [random.randint(80, 120)],
                'Percentage': [100.0]
            })
        
        # Distribución realista de sentimientos
        data = {
            'Positivo': random.randint(30, 50),
            'Neutro': random.randint(40, 60), 
            'Negativo': random.randint(20, 40)
        }
        
        total = sum(data.values())
        
        result = []
        for sentiment, count in data.items():
            result.append({
                'Polaridad': sentiment,
                'Count': count,
                'Percentage': round((count / total) * 100, 1)
            })
        
        return pd.DataFrame(result)
    
    def create_timeline_chart(self, filters):
        """Crea el gráfico de timeline por red social"""
        df = self.generate_timeline_data(filters)
        
        # Crear gráfico de líneas múltiples
        fig = go.Figure()
        
        for red_social in filters['origen']:
            data_red = df[df['Red Social'] == red_social]
            
            fig.add_trace(go.Scatter(
                x=data_red['Fecha'],
                y=data_red['Volumen'],
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
                showgrid=True
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
    
    def create_sentiment_donut(self, filters):
        """Crea el gráfico donut de distribución de sentimientos"""
        df = self.generate_sentiment_data(filters)
        
        # Colores para cada sentimiento
        colors = [self.sentiment_colors[sentiment] for sentiment in df['Polaridad']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df['Polaridad'],
            values=df['Count'],
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
        
        # Agregar texto central
        total_mentions = df['Count'].sum()
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
    
    def calculate_kpis(self, filters, df_data=None):
        """Calcula los KPIs principales"""
        # Simular datos de KPIs basados en filtros
        days = (filters['fecha_fin'] - filters['fecha_inicio']).days
        networks_count = len(filters['origen'])
        
        # Simular métricas realistas
        total_mentions = random.randint(500, 2000) * networks_count
        avg_engagement = round(random.uniform(2.5, 6.5), 2)
        total_reach = random.randint(50000, 200000) * networks_count
        
        # Calcular sentimiento promedio
        sentiment_data = self.generate_sentiment_data(filters)
        if filters['polaridad'] == 'Todos':
            # Calcular weighted average
            positive_weight = sentiment_data[sentiment_data['Polaridad'] == 'Positivo']['Count'].iloc[0] * 1
            neutral_weight = sentiment_data[sentiment_data['Polaridad'] == 'Neutro']['Count'].iloc[0] * 0
            negative_weight = sentiment_data[sentiment_data['Polaridad'] == 'Negativo']['Count'].iloc[0] * -1
            
            total_weighted = positive_weight + neutral_weight + negative_weight
            total_count = sentiment_data['Count'].sum()
            
            sentiment_score = round((total_weighted / total_count) * 100, 1)
        else:
            # Si está filtrado por sentimiento específico
            if filters['polaridad'] == 'Positivo':
                sentiment_score = 85.0
            elif filters['polaridad'] == 'Negativo':
                sentiment_score = -60.0
            else:
                sentiment_score = 0.0
        
        return {
            'total_mentions': total_mentions,
            'avg_engagement': avg_engagement,
            'total_reach': total_reach,
            'sentiment_score': sentiment_score
        }
    
    def render_kpis(self, filters):
        """Renderiza los KPIs principales"""
        kpis = self.calculate_kpis(filters)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 Total Menciones",
                value=f"{kpis['total_mentions']:,}",
                delta=f"+{random.randint(5, 25)}%",
                help="Número total de menciones en el período seleccionado"
            )
        
        with col2:
            st.metric(
                label="💝 Engagement Promedio",
                value=f"{kpis['avg_engagement']}%",
                delta=f"+{round(random.uniform(0.1, 1.5), 1)}%",
                help="Tasa de engagement promedio de las menciones"
            )
        
        with col3:
            st.metric(
                label="👥 Alcance Total", 
                value=f"{kpis['total_reach']:,}",
                delta=f"+{random.randint(10, 30)}%",
                help="Alcance total estimado de las menciones"
            )
        
        with col4:
            delta_color = "normal" if kpis['sentiment_score'] >= 0 else "inverse"
            st.metric(
                label="😊 Sentimiento",
                value=f"{kpis['sentiment_score']:+.1f}",
                delta=f"{random.uniform(-5, 15):+.1f}",
                delta_color=delta_color,
                help="Puntuación de sentimiento promedio (-100 a +100)"
            )
    
    def render_visualizations(self, filters):
        """Renderiza todas las visualizaciones"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver las visualizaciones")
            return
        
        # KPIs principales
        st.subheader("📊 Métricas Principales")
        self.render_kpis(filters)
        
        st.divider()
        
        # Gráficos principales
        st.subheader("📈 Visualizaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico Timeline
            timeline_fig = self.create_timeline_chart(filters)
            st.plotly_chart(timeline_fig, use_container_width=True)
        
        with col2:
            # Gráfico Donut de Sentimientos
            sentiment_fig = self.create_sentiment_donut(filters)
            st.plotly_chart(sentiment_fig, use_container_width=True)
        
        return True