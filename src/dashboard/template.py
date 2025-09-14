import streamlit as st
import time

from datetime import datetime
from .filters import FilterManager
from .tables import DataTableManager
from .visualizations import VisualizationManager

def render_dashboard_header(dashboard_info):
    """Renderiza el header del dashboard con styling profesional"""
    
    # Header con styling personalizado
    header_html = f"""
    <div class="main-header fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="gradient-title" style="margin: 0; font-size: 2.5rem;">
                    {dashboard_info['title']}
                </h1>
                <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
                    {dashboard_info['description']}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="
                    background: linear-gradient(135deg, #1E293B 0%, #262730 100%);
                    padding: 1rem;
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.1);
                ">
                    <h4 style="color: #00D4FF; margin: 0; font-size: 0.9rem;">Última Actualización</h4>
                    <p style="color: white; margin: 0.25rem 0 0 0; font-weight: 600;">Pendiente</p>
                    <small style="color: rgba(255,255,255,0.6);">Timestamp del registro más reciente</small>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def render_filters_summary(filter_manager):
    """Renderiza un resumen de los filtros aplicados"""
    summary = filter_manager.get_filter_summary()
    filters = st.session_state.filters
    
    if not summary['is_applied']:
        st.info("🔍 Configure y aplique filtros para ver los datos")
        return
    
    with st.expander("📋 Resumen de Filtros Aplicados", expanded=False):
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

def render_main_content(filter_manager, user_info, db_connection):
    """Renderiza el contenido principal del dashboard"""
    filters = st.session_state.filters
    
    # LOADING SCREEN - Solo si los filtros están aplicados
    loading_container = st.empty()
    
    with loading_container.container():
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>🔄 Cargando Dashboard...</h2>
            <p>Obteniendo datos de social listening</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Conectando a base de datos...")
        progress_bar.progress(25)
        time.sleep(0.5)  # Simular tiempo de conexión
        
        # QUERY REAL DURANTE EL LOADING
        status_text.text("Obteniendo datos...")
        progress_bar.progress(50)
        
        # Preparar parámetros de query
        alerta_id = user_info['dashboard']['alert_ids'][0]
        sentiment_code = None
        if filters['polaridad'] != 'Todos':
            sentiment_mapping = {'Positivo': 'POS', 'Neutro': 'NEU', 'Negativo': 'NEG'}
            sentiment_code = sentiment_mapping.get(filters['polaridad'])
        
        # Query principal sin límite
        df_completo = db_connection.get_social_listening_data(
            alerta_id=alerta_id,
            origins=filters['origen'],
            start_date=filters['fecha_inicio'],
            end_date=filters['fecha_fin'],
            sentiment=sentiment_code,
            limit=None
        )
        
        status_text.text("Procesando visualizaciones...")
        progress_bar.progress(75)
        time.sleep(0.3)
        
        status_text.text("Finalizando...")
        progress_bar.progress(100)
        time.sleep(0.2)
    
    # Limpiar loading y mostrar dashboard real
    loading_container.empty()
    
    # Área de visualizaciones - usar datos compartidos
    viz_manager = VisualizationManager()
    viz_manager.render_visualizations(filters, df_completo)
    
    # Tabla de registros - usar datos compartidos
    st.subheader("📋 Registros Recientes (Top 500)")
    table_manager = DataTableManager()
    df_resultado = table_manager.render_data_table(filters, df_completo)
    
    # Resumen de filtros al final como pie de página
    st.divider()
    with st.expander("📋 Resumen de Filtros Aplicados", expanded=False):
        summary = filter_manager.get_filter_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Redes Sociales", summary['total_origins'])
        with col2:
            st.metric("Período (días)", summary['date_range_days'])
        with col3:
            st.metric("Polaridad", summary['polaridad'])
        with col4:
            st.metric("Estado", "✅ Aplicado")
        
        st.write("**Plataformas:** ", ", ".join(filters['origen']))
        st.write(f"**Fechas:** {filters['fecha_inicio'].strftime('%Y-%m-%d')} a {filters['fecha_fin'].strftime('%Y-%m-%d')}")

def render_dashboard(user_info, db_connection):
    """Función principal que renderiza todo el dashboard"""
    # Inicializar el filter manager
    filter_manager = FilterManager()
    
    # Renderizar header
    render_dashboard_header(user_info['dashboard'])
    
    # Renderizar filtros en sidebar
    filters = filter_manager.render_filters()
    
    # Renderizar contenido principal
    render_main_content(filter_manager, user_info, db_connection)
    
    return filter_manager