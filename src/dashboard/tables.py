import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

class DataTableManager:
    def __init__(self):
        pass
    
    def render_data_table(self, filters, df_completo):
        """Renderiza la tabla de datos con los filtros aplicados usando datos compartidos"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver los datos en la tabla")
            return
        
        # Verificar si hay datos
        if df_completo.empty:
            st.warning("⚠️ No se encontraron datos para los filtros aplicados")
            return pd.DataFrame()
        
        # Convertir sentiment_pred a texto legible
        df = df_completo.copy()
        sentiment_display_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro', 
            'NEG': 'Negativo'
        }
        df['polaridad_display'] = df['sentiment_pred'].map(sentiment_display_mapping).fillna('Desconocido')
        
        # Calcular métricas de la tabla (sobre todos los datos)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Registros", len(df))
        with col2:
            if 'sentiment_confidence' in df.columns:
                confidence_avg = df['sentiment_confidence'].mean()
                st.metric("Confianza Promedio", f"{confidence_avg:.2f}")
            else:
                st.metric("Confianza Promedio", "N/A")
        with col3:
            if 'likes' in df.columns:
                total_likes = df['likes'].sum()
                st.metric("Total Likes", f"{total_likes:,}")
            else:
                st.metric("Total Likes", "N/A")
        
        # Filtros adicionales de la tabla
        st.subheader("🔧 Filtros de Tabla")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por red social específica - usar todas las opciones disponibles
            redes_en_data = filters['origen']  # Usar las mismas opciones del filtro principal
            selected_red = st.selectbox(
                "Filtrar por Red Social",
                options=['Todas'] + redes_en_data,
                key="table_filter_red"
            )
        
        with col2:
            # Filtro por polaridad específica - usar todas las opciones disponibles
            polaridades_en_data = ['Positivo', 'Neutro', 'Negativo']  # Opciones fijas completas
            selected_pol = st.selectbox(
                "Filtrar por Polaridad",
                options=['Todas'] + polaridades_en_data,
                key="table_filter_pol"
            )
        
        with col3:
            # Ordenar por
            sort_options = ['Fecha (Reciente)', 'Fecha (Antigua)', 'Confianza (Alta)', 'Confianza (Baja)']
            if 'likes' in df.columns:
                sort_options.extend(['Likes (Alto)', 'Likes (Bajo)'])
            sort_by = st.selectbox(
                "Ordenar por",
                options=sort_options,
                key="table_sort"
            )
        
        # Aplicar filtros adicionales
        filtered_df = df.copy()
        
        if selected_red != 'Todas':
            filtered_df = filtered_df[filtered_df['origin'] == selected_red]
        
        if selected_pol != 'Todas':
            filtered_df = filtered_df[filtered_df['polaridad_display'] == selected_pol]
        
        # Aplicar ordenamiento
        if sort_by == 'Fecha (Reciente)':
            filtered_df = filtered_df.sort_values('created_time', ascending=False)
        elif sort_by == 'Fecha (Antigua)':
            filtered_df = filtered_df.sort_values('created_time', ascending=True)
        elif sort_by == 'Confianza (Alta)' and 'sentiment_confidence' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('sentiment_confidence', ascending=False)
        elif sort_by == 'Confianza (Baja)' and 'sentiment_confidence' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('sentiment_confidence', ascending=True)
        elif sort_by == 'Likes (Alto)' and 'likes' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('likes', ascending=False)
        elif sort_by == 'Likes (Bajo)' and 'likes' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('likes', ascending=True)
        
        # Mostrar información de registros filtrados
        if len(filtered_df) != len(df):
            st.info(f"Mostrando {len(filtered_df)} de {len(df)} registros")
        
        # Configurar display de la tabla
        st.subheader("📋 Tabla de Datos")
        
        # Opciones de visualización
        col1, col2 = st.columns(2)
        with col1:
            show_full_content = st.checkbox("Mostrar contenido completo", value=False)
        with col2:
            rows_to_show = st.number_input("Filas a mostrar", min_value=10, max_value=500, value=100, step=10)
        
        # Preparar DataFrame para display (limitar a muestra para performance)
        display_df = filtered_df.head(rows_to_show).copy()
        
        # Truncar contenido si es necesario
        if not show_full_content and 'text' in display_df.columns:
            display_df['text'] = display_df['text'].apply(
                lambda x: str(x)[:50] + "..." if len(str(x)) > 50 else str(x)
            )
        
        # Formatear columnas para display
        display_columns = {
            'id': 'ID',
            'created_time': 'Fecha',
            'origin': 'Red Social',
            'author': 'Usuario',
            'text': 'Contenido',
            'polaridad_display': 'Polaridad'
        }
        
        # Agregar columnas numéricas si existen
        if 'likes' in display_df.columns:
            display_df['likes'] = display_df['likes'].fillna(0).astype(int)
            display_columns['likes'] = 'Likes'
        
        if 'comments' in display_df.columns:
            display_df['comments'] = display_df['comments'].fillna(0).astype(int)
            display_columns['comments'] = 'Comentarios'
        
        if 'shares' in display_df.columns:
            display_df['shares'] = display_df['shares'].fillna(0).astype(int)
            display_columns['shares'] = 'Shares'
        
        if 'sentiment_confidence' in display_df.columns:
            display_df['confidence_formatted'] = display_df['sentiment_confidence'].apply(
                lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
            )
            display_columns['confidence_formatted'] = 'Confianza'
        
        # Seleccionar solo las columnas que existen
        available_columns = [col for col in display_columns.keys() if col in display_df.columns]
        display_df_final = display_df[available_columns]
        
        # Renombrar columnas
        column_config = {}
        for old_name, new_name in display_columns.items():
            if old_name in available_columns:
                if old_name == 'created_time':
                    column_config[old_name] = st.column_config.DatetimeColumn(new_name, width="medium")
                elif old_name in ['likes', 'comments', 'shares']:
                    column_config[old_name] = st.column_config.NumberColumn(new_name, width="small")
                elif old_name == 'text':
                    column_config[old_name] = st.column_config.TextColumn(new_name, width="large")
                else:
                    column_config[old_name] = st.column_config.TextColumn(new_name, width="small")
        
        # Mostrar tabla
        st.dataframe(
            display_df_final,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )
        
        # Información adicional
        with st.expander("📊 Estadísticas de la tabla"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Distribución por Red Social:**")
                if 'origin' in filtered_df.columns:
                    red_counts = filtered_df['origin'].value_counts()
                    st.bar_chart(red_counts)
            
            with col2:
                st.write("**Distribución por Polaridad:**")
                pol_counts = filtered_df['polaridad_display'].value_counts()
                
                # Usar los mismos colores que en visualizations.py
                sentiment_colors = {
                    'Positivo': '#10B981',    # Verde
                    'Neutro': '#F59E0B',      # Amarillo
                    'Negativo': '#FF006B'     # Magenta
                }
                
                # Crear DataFrame para plotly
                import plotly.express as px
                
                chart_data = pd.DataFrame({
                    'Polaridad': pol_counts.index,
                    'Cantidad': pol_counts.values
                })
                
                fig = px.bar(
                    chart_data,
                    x='Polaridad', 
                    y='Cantidad',
                    color='Polaridad',
                    color_discrete_map=sentiment_colors
                )
                
                fig.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis_title="",
                    yaxis_title=""
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        return filtered_df