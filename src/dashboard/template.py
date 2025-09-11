import streamlit as st
from datetime import datetime
from .filters import FilterManager

def render_dashboard_header(dashboard_info):
    """Renderiza el header del dashboard"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(dashboard_info['title'])
        st.caption(dashboard_info['description'])
    
    with col2:
        # Placeholder para timestamp de última actualización
        st.metric(
            label="Última Actualización",
            value="Pendiente",
            help="Timestamp del registro más reciente"
        )

def render_filters_summary(filter_manager):
    """Renderiza un resumen de los filtros aplicados"""
    summary = filter_manager.get_filter_summary()
    filters = st.session_state.filters
    
    if not summary['is_applied']:
        st.info("🔍 Configure y aplique filtros para ver los datos")
        return
    
    with st.expander("📋 Resumen de Filtros Aplicados", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Redes Sociales",
                value=summary['total_origins'],
                help="Número de plataformas seleccionadas"
            )
        
        with col2:
            st.metric(
                label="Período (días)",
                value=summary['date_range_days'],
                help="Rango de fechas seleccionado"
            )
        
        with col3:
            st.metric(
                label="Polaridad",
                value=summary['polaridad'],
                help="Filtro de sentimiento aplicado"
            )
        
        with col4:
            st.metric(
                label="Estado",
                value="✅ Aplicado",
                help="Los filtros están activos"
            )
        
        # Detalles de los filtros
        st.write("**Plataformas seleccionadas:**", ", ".join(filters['origen']))
        st.write(f"**Rango de fechas:** {filters['fecha_inicio'].strftime('%Y-%m-%d')} a {filters['fecha_fin'].strftime('%Y-%m-%d')}")

def render_main_content(filter_manager):
    """Renderiza el contenido principal del dashboard"""
    filters = st.session_state.filters
    
    # Mostrar resumen de filtros
    render_filters_summary(filter_manager)
    
    # Solo mostrar contenido si los filtros están aplicados
    if not filters['applied']:
        st.warning("⚠️ Por favor aplique los filtros para visualizar los datos")
        return
    
    # KPIs principales
    st.subheader("📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Menciones",
            value="---",
            delta="---",
            help="Número total de menciones en el período seleccionado"
        )
    
    with col2:
        st.metric(
            label="Engagement",
            value="---",
            delta="---",
            help="Engagement promedio de las menciones"
        )
    
    with col3:
        st.metric(
            label="Alcance",
            value="---",
            delta="---",
            help="Alcance total de las menciones"
        )
    
    with col4:
        st.metric(
            label="Sentimiento Promedio",
            value="---",
            delta="---",
            help="Distribución de sentimientos"
        )
    
    # Área de visualizaciones
    st.subheader("📈 Visualizaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🚧 **Gráfico Timeline por Red Social**\n\nMostrará el volumen de menciones a lo largo del tiempo, separado por plataforma.")
        
        # Placeholder para parámetros del gráfico
        with st.expander("Configuración del gráfico (futuro)"):
            st.write("**Filtros aplicados:**")
            query_params = filter_manager.build_query_filters()
            st.json(query_params)
    
    with col2:
        st.info("🚧 **Gráfico de Distribución de Polaridad**\n\nMostrará la distribución de sentimientos en formato donut chart.")
        
        # Mostrar configuración de polaridad
        with st.expander("Configuración de polaridad (futuro)"):
            if filters['polaridad'] == 'Todos':
                st.write("Mostrando todas las polaridades")
            else:
                st.write(f"Filtrado por: {filters['polaridad']}")
    
    # Tabla de registros
    st.subheader("📋 Registros Recientes (Top 100)")
    
    # Información sobre la tabla futura
    st.info("🚧 **Tabla de Datos**\n\nMostrará los 100 registros más recientes que coincidan con los filtros aplicados.")
    
    with st.expander("Vista previa de estructura de tabla"):
        import pandas as pd
        
        # DataFrame de ejemplo para mostrar estructura
        sample_data = {
            'Fecha': ['2024-01-15', '2024-01-14', '2024-01-13'],
            'Red Social': ['Facebook', 'Instagram', 'X (Twitter)'],
            'Usuario': ['@usuario1', '@usuario2', '@usuario3'],
            'Contenido': ['Texto de ejemplo...', 'Otro texto...', 'Más contenido...'],
            'Polaridad': ['Positivo', 'Neutro', 'Negativo'],
            'Engagement': [150, 89, 234]
        }
        
        df_sample = pd.DataFrame(sample_data)
        st.dataframe(df_sample, use_container_width=True)
        st.caption("Vista previa de la estructura de datos (datos de ejemplo)")

def render_dashboard(user_info):
    """Función principal que renderiza todo el dashboard"""
    # Inicializar el filter manager
    filter_manager = FilterManager()
    
    # Renderizar header
    render_dashboard_header(user_info['dashboard'])
    
    # Renderizar filtros en sidebar
    filters = filter_manager.render_filters()
    
    # Renderizar contenido principal
    render_main_content(filter_manager)
    
    return filter_manager