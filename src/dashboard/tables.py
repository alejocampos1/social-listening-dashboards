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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Mapear valores de BD a display para las opciones
            db_to_display = {
                'Facebook': 'Facebook',
                'X': 'X (Twitter)', 
                'Instagram': 'Instagram',
                'TikTok': 'TikTok'
            }
            
            # Obtener valores únicos reales de los datos
            redes_en_data_db = df['origin'].unique().tolist()
            redes_en_data_display = [db_to_display.get(red, red) for red in redes_en_data_db]
            
            selected_red_display = st.multiselect(
                "Filtrar por Red Social",
                options=redes_en_data_display,
                default=redes_en_data_display,
                key="table_filter_red"
            )
            
            # Convertir selección de display a valor de BD
            display_to_db = {v: k for k, v in db_to_display.items()}
        
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
        
        # Filtros de fecha específicos para la tabla
        st.write("**Filtro de Fecha:**")
        col_date1, col_date2 = st.columns(2)

        with col_date1:
            # Obtener rango de fechas de los datos
            min_date = df['created_time'].min().date() if not df.empty else datetime.now().date()
            max_date = df['created_time'].max().date() if not df.empty else datetime.now().date()
            
            table_start_date = st.date_input(
                "Desde",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key="table_date_start"
            )

        with col_date2:
            table_end_date = st.date_input(
                "Hasta", 
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="table_date_end"
            )

        # Aplicar filtro de fecha
        if table_start_date and table_end_date:
            start_datetime = pd.Timestamp(table_start_date)
            end_datetime = pd.Timestamp(table_end_date) + pd.Timedelta(days=1)
            
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df['created_time']) >= start_datetime) & 
                (pd.to_datetime(filtered_df['created_time']) < end_datetime)
            ]
        
        if selected_red_display:  # Si hay selecciones
            # Convertir las selecciones de display a valores de BD
            display_to_db = {v: k for k, v in db_to_display.items()}
            selected_red_db_list = [display_to_db.get(red, red) for red in selected_red_display if red is not None]
            filtered_df = filtered_df[filtered_df['origin'].isin(selected_red_db_list)]
        
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
            
            
        # Botón de descarga - usar datos completos filtrados (sin límite de filas)
        download_df = filtered_df.copy()

        # Preparar datos para descarga
        if not download_df.empty:
            # Formatear para descarga
            download_df_formatted = download_df.copy()
            
            # Renombrar columnas para descarga
            column_rename = {
                'id': 'ID',
                'created_time': 'Fecha',
                'origin': 'Red Social',
                'text': 'Contenido Completo',
                'polaridad_display': 'Polaridad',
                'sentiment_confidence': 'Confianza'
            }
            
            # Agregar columnas numéricas si existen
            if 'likes' in download_df_formatted.columns:
                column_rename['likes'] = 'Likes'
            if 'comments' in download_df_formatted.columns:
                column_rename['comments'] = 'Comentarios'
            if 'shares' in download_df_formatted.columns:
                column_rename['shares'] = 'Shares'
            
            # Seleccionar y renombrar columnas
            available_download_columns = [col for col in column_rename.keys() if col in download_df_formatted.columns]
            download_df_final = download_df_formatted[available_download_columns]
            download_df_final = download_df_final.rename(columns=column_rename)
            
            # Convertir a CSV
            csv_data = download_df_final.to_csv(index=False)
            
            st.markdown("""
            <style>
            div[data-testid="stDownloadButton"] > button {
                background-color: #0483C3 !important;
                border-color: #0483C3 !important;
            }
            div[data-testid="stDownloadButton"] > button:hover {
                background-color: #036A9F !important;
                border-color: #036A9F !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Botón de descarga
            st.download_button(
                label=f"📥 Descargar datos filtrados ({len(download_df_final):,} registros)",
                data=csv_data,
                file_name=f"social_listening_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )
        else:
            st.warning("No hay datos para descargar con los filtros aplicados")

        st.divider()    
        
        # Opciones de visualización
        rows_to_show = st.number_input("Filas a mostrar", min_value=10, max_value=500, value=100, step=10)

        
        # Preparar DataFrame para display (limitar a muestra para performance)
        display_df = filtered_df.head(rows_to_show).copy()
        
        # Truncar contenido por defecto
        if 'text' in display_df.columns:
            display_df['text'] = display_df['text'].apply(
                lambda x: str(x)[:50] + "..." if len(str(x)) > 50 else str(x)
            )
        
        # Formatear columnas para display
        display_columns = {
            'id': 'ID',
            'created_time': 'Fecha',
            'origin': 'Red Social',
            'text': 'Contenido',
            'polaridad_display': 'Polaridad'
        }
        
        # Agregar columnas numéricas si existen
#        if 'likes' in display_df.columns:
#            display_df['likes'] = display_df['likes'].fillna(0).astype(int)
#            display_columns['likes'] = 'Likes'
#        
#        if 'comments' in display_df.columns:
#            display_df['comments'] = display_df['comments'].fillna(0).astype(int)
#            display_columns['comments'] = 'Comentarios'
#        
#        if 'shares' in display_df.columns:
#            display_df['shares'] = display_df['shares'].fillna(0).astype(int)
#            display_columns['shares'] = 'Shares'
#        
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
        
        # Control de texto
        show_full_content = st.checkbox("Mostrar texto completo", value=False)
        if show_full_content:
            st.info("💡 Para ver el texto completo, active la opción y actualice la página")
        
        # Información adicional
        st.subheader("Estadísticas de la tabla")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Distribución por Red Social:**")
            if 'origin' in filtered_df.columns:
                red_counts = filtered_df['origin'].value_counts()
                
                # Usar los mismos colores que en visualizations.py
                social_colors = {
                    'Facebook': '#1877F2',
                    'Instagram': '#E4405F', 
                    'X': '#1DA1F2',
                    'TikTok': '#000000'
                }
                
                # Crear gráfico con colores específicos
                import plotly.express as px
                
                chart_data = pd.DataFrame({
                    'Red Social': red_counts.index,
                    'Cantidad': red_counts.values
                })
                
                fig = px.bar(
                    chart_data,
                    x='Red Social', 
                    y='Cantidad',
                    color='Red Social',
                    color_discrete_map=social_colors
                )
                
                fig.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis_title="",
                    yaxis_title=""
                )
                
                st.plotly_chart(fig, use_container_width=True, key="chart_redes_sociales")
            
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
            
            st.plotly_chart(fig, use_container_width=True, key="chart_polaridad")
            
        return filtered_df