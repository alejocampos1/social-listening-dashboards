import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

class DataTableManager:
    def __init__(self):
        pass
    
    def generate_sample_data(self, filters, limit=100):
        """Genera datos de ejemplo basados en los filtros aplicados"""
        
        # Configurar generador de datos aleatorios
        random.seed(42)  # Para resultados consistentes
        
        data = []
        start_date = filters['fecha_inicio']
        end_date = filters['fecha_fin']
        
        # Generar fechas aleatorias en el rango
        date_range = (end_date - start_date).days
        
        for i in range(limit):
            # Fecha aleatoria en el rango
            random_days = random.randint(0, date_range)
            fecha = start_date + timedelta(days=random_days)
            
            # Red social aleatoria de las seleccionadas
            red_social = random.choice(filters['origen'])
            
            # Polaridad según filtro
            if filters['polaridad'] == 'Todos':
                polaridad = random.choice(['Positivo', 'Neutro', 'Negativo'])
            else:
                polaridad = filters['polaridad']
            
            # Datos simulados
            registro = {
                'ID': f"POST_{i+1:04d}",
                'Fecha': fecha.strftime('%Y-%m-%d %H:%M'),
                'Red Social': red_social,
                'Usuario': f"@usuario{random.randint(1, 1000)}",
                'Contenido': self._generate_sample_content(red_social, polaridad),
                'Polaridad': polaridad,
                'Likes': random.randint(0, 500),
                'Shares': random.randint(0, 100),
                'Comentarios': random.randint(0, 50),
                'Alcance': random.randint(100, 10000),
                'Engagement': round(random.uniform(0.5, 8.5), 2)
            }
            
            data.append(registro)
        
        # Crear DataFrame y ordenar por fecha (más reciente primero)
        df = pd.DataFrame(data)
        df['Fecha_Sort'] = pd.to_datetime(df['Fecha'])
        df = df.sort_values('Fecha_Sort', ascending=False)
        df = df.drop('Fecha_Sort', axis=1)
        
        return df
    
    def _generate_sample_content(self, red_social, polaridad):
        """Genera contenido de ejemplo según la red social y polaridad"""
        
        positive_content = [
            "¡Excelente servicio! Muy recomendado 👍",
            "Me encanta esta marca, siempre innovando",
            "Increíble experiencia, volveré sin duda",
            "Producto de alta calidad, vale la pena",
            "Atención al cliente excepcional 🌟"
        ]
        
        neutral_content = [
            "Información sobre el nuevo producto disponible",
            "Horarios de atención actualizados",
            "Evento programado para la próxima semana",
            "Más detalles en el sitio web oficial",
            "Consulta disponibilidad en tiendas"
        ]
        
        negative_content = [
            "Servicio muy lento, necesita mejorar",
            "Producto defectuoso, solicito reembolso",
            "Experiencia decepcionante esta vez",
            "Atención al cliente poco profesional",
            "No cumplió con mis expectativas"
        ]
        
        if polaridad == 'Positivo':
            content_list = positive_content
        elif polaridad == 'Negativo':
            content_list = negative_content
        else:
            content_list = neutral_content
        
        base_content = random.choice(content_list)
        
        # Agregar elementos específicos de cada red social
        if red_social == 'X (Twitter)':
            hashtags = ["#brand", "#review", "#experience"]
            base_content += f" {random.choice(hashtags)}"
        elif red_social == 'Instagram':
            base_content += " 📸✨"
        elif red_social == 'Facebook':
            base_content += " [Publicación completa en Facebook]"
        elif red_social == 'TikTok':
            base_content += " 🎵 #viral"
        
        return base_content
    
    def render_data_table(self, filters):
        """Renderiza la tabla de datos con los filtros aplicados"""
        
        if not filters['applied']:
            st.info("🔍 Aplique los filtros para ver los datos en la tabla")
            return
        
        # Generar datos de ejemplo
        with st.spinner("Cargando datos..."):
            df = self.generate_sample_data(filters, limit=100)
        
        # Métricas de la tabla
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Registros", len(df))
        with col2:
            engagement_avg = df['Engagement'].mean()
            st.metric("Engagement Promedio", f"{engagement_avg:.2f}%")
        with col3:
            total_alcance = df['Alcance'].sum()
            st.metric("Alcance Total", f"{total_alcance:,}")
        
        # Filtros adicionales de la tabla
        st.subheader("🔧 Filtros de Tabla")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por red social específica
            redes_en_data = df['Red Social'].unique().tolist()
            selected_red = st.selectbox(
                "Filtrar por Red Social",
                options=['Todas'] + redes_en_data,
                key="table_filter_red"
            )
        
        with col2:
            # Filtro por polaridad específica
            polaridades_en_data = df['Polaridad'].unique().tolist()
            selected_pol = st.selectbox(
                "Filtrar por Polaridad",
                options=['Todas'] + polaridades_en_data,
                key="table_filter_pol"
            )
        
        with col3:
            # Ordenar por
            sort_options = ['Fecha (Reciente)', 'Fecha (Antigua)', 'Engagement (Alto)', 'Engagement (Bajo)', 'Alcance (Alto)', 'Alcance (Bajo)']
            sort_by = st.selectbox(
                "Ordenar por",
                options=sort_options,
                key="table_sort"
            )
        
        # Aplicar filtros adicionales
        filtered_df = df.copy()
        
        if selected_red != 'Todas':
            filtered_df = filtered_df[filtered_df['Red Social'] == selected_red]
        
        if selected_pol != 'Todas':
            filtered_df = filtered_df[filtered_df['Polaridad'] == selected_pol]
        
        # Aplicar ordenamiento
        if sort_by == 'Fecha (Reciente)':
            filtered_df = filtered_df.sort_values('Fecha', ascending=False)
        elif sort_by == 'Fecha (Antigua)':
            filtered_df = filtered_df.sort_values('Fecha', ascending=True)
        elif sort_by == 'Engagement (Alto)':
            filtered_df = filtered_df.sort_values('Engagement', ascending=False)
        elif sort_by == 'Engagement (Bajo)':
            filtered_df = filtered_df.sort_values('Engagement', ascending=True)
        elif sort_by == 'Alcance (Alto)':
            filtered_df = filtered_df.sort_values('Alcance', ascending=False)
        elif sort_by == 'Alcance (Bajo)':
            filtered_df = filtered_df.sort_values('Alcance', ascending=True)
        
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
        if not show_full_content:
            display_df['Contenido'] = display_df['Contenido'].apply(
                lambda x: x[:50] + "..." if len(x) > 50 else x
            )
        
        # Formatear números
        display_df['Engagement'] = display_df['Engagement'].apply(lambda x: f"{x}%")
        display_df['Alcance'] = display_df['Alcance'].apply(lambda x: f"{x:,}")
        
        # Mostrar tabla
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Fecha": st.column_config.DatetimeColumn("Fecha", width="medium"),
                "Red Social": st.column_config.TextColumn("Red Social", width="small"),
                "Usuario": st.column_config.TextColumn("Usuario", width="small"),
                "Contenido": st.column_config.TextColumn("Contenido", width="large"),
                "Polaridad": st.column_config.TextColumn("Polaridad", width="small"),
                "Engagement": st.column_config.TextColumn("Engagement", width="small"),
                "Alcance": st.column_config.TextColumn("Alcance", width="small")
            }
        )
        
        # Información adicional
        with st.expander("📊 Estadísticas de la tabla"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Distribución por Red Social:**")
                red_counts = filtered_df['Red Social'].value_counts()
                st.bar_chart(red_counts)
            
            with col2:
                st.write("**Distribución por Polaridad:**")
                pol_counts = filtered_df['Polaridad'].value_counts()
                st.bar_chart(pol_counts)
        
        return filtered_df