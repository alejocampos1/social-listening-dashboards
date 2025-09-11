import streamlit as st
from datetime import datetime
from .filters import FilterManager
from .tables import DataTableManager
from .visualizations import VisualizationManager

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
    
    # Área de visualizaciones
    # Renderizar visualizaciones
    viz_manager = VisualizationManager()
    viz_manager.render_visualizations(filters)
    
    # Tabla de registros
    st.subheader("📋 Registros Recientes (Top 100)")

    # Renderizar tabla de datos
    table_manager = DataTableManager()
    df_resultado = table_manager.render_data_table(filters)

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