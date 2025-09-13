import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

class DataTableManager:
    def __init__(self):
        pass
    
    def render_data_table(self, filters, alerta_id, db_connection):
        """Renderiza la tabla de datos con los filtros aplicados usando datos reales"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver los datos en la tabla")
            return
        
        # Convertir polaridad de filtro a código de BD
        sentiment_code = None
        if filters['polaridad'] != 'Todos':
            sentiment_mapping = {
                'Positivo': 'POS',
                'Neutro': 'NEU',
                'Negativo': 'NEG'
            }
            sentiment_code = sentiment_mapping.get(filters['polaridad'])
        
        # Obtener datos reales de la base de datos
        with st.spinner("Cargando datos..."):
            df = db_connection.get_social_listening_data(
                alerta_id=alerta_id,
                origins=filters['origen'],
                start_date=filters['fecha_inicio'],
                end_date=filters['fecha_fin'],
                sentiment=sentiment_code,
                limit=100
            )
        
        # Verificar si hay datos
        if df.empty:
            st.warning("⚠️ No se encontraron datos para los filtros aplicados")
            return pd.DataFrame()
        
        # Convertir sentiment_pred a texto legible
        sentiment_display_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro', 
            'NEG': 'Negativo'
        }
        df['polaridad_display'] = df['sentiment_pred'].map(sentiment_display_mapping).fillna('Desconocido')
        
        # Calcular métricas de la tabla
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
            # Filtro por red social específica
            redes_en_data = df['origin'].unique().tolist() if 'origin' in df.columns else []
            selected_red = st.selectbox(
                "Filtrar por Red Social",
                options=['Todas'] + redes_en_data,
                key="table_filter_red"
            )
        
        with col2:
            # Filtro por polaridad específica
            polaridades_en_data = df['polaridad_display'].unique().tolist()
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
            rows_to_show = st.number_input("Filas a mostrar", min_value=10, max_value=100, value=50, step=10)
        
        # Preparar DataFrame para display
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
                st.bar_chart(pol_counts)
        
        return filtered_df