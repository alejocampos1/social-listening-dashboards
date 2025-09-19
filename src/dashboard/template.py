import streamlit as st
import time

from datetime import datetime
from .filters import FilterManager
from .tables import DataTableManager
from .visualizations import VisualizationManager
from src.utils.data_cache import DataCacheManager, get_cached_social_data, cache_social_data

def render_dashboard_header(dashboard_info, last_update_str="No disponible"):
    """Renderiza el header del dashboard con styling profesional"""
    
    # Header con styling personalizado
    header_html = f"""
    <div class="main-header fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 2.5rem; color: white;">
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
                    <div style="color: #00D4FF; margin: 0; font-size: 0.9rem; font-weight: 600;">Última Actualización</div>
                    <p style="color: white; margin: 0.25rem 0 0 0; font-weight: 600;">{last_update_str}</p>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def render_main_content(filter_manager, user_info, db_connection, header_placeholder):
    """Renderiza el contenido principal del dashboard"""
    filters = st.session_state.filters
    
    # Obtener alerta_id
    alerta_id = user_info['dashboard']['alert_ids'][0]
    
    # LOADING SCREEN
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
        time.sleep(0.5)
        
        # QUERY REAL DURANTE EL LOADING
        status_text.text("Obteniendo datos...")
        progress_bar.progress(50)
        
        # Preparar parámetros de query
        sentiment_code = None
        if filters['polaridad'] != 'Todos':
            sentiment_mapping = {'Positivo': 'POS', 'Neutro': 'NEU', 'Negativo': 'NEG'}
            sentiment_code = sentiment_mapping.get(filters['polaridad'])
        
        # Query principal sin límite
        # Intentar obtener datos del caché primero
        cache_manager = DataCacheManager()
        df_completo = get_cached_social_data(
            alerta_id=alerta_id,
            origins=filters['origen'],
            start_date=filters['fecha_inicio'],
            end_date=filters['fecha_fin'],
            sentiment=sentiment_code,
            cache_manager=cache_manager
        )

        # Si no hay caché válido, ejecutar query y cachear resultado
        if df_completo is None:
            df_completo = db_connection.get_social_listening_data(
                alerta_id=alerta_id,
                origins=filters['origen'],
                start_date=filters['fecha_inicio'],
                end_date=filters['fecha_fin'],
                sentiment=sentiment_code,
                limit=None
            )
            
            # Cachear los datos obtenidos
            cache_social_data(
                data=df_completo,
                alerta_id=alerta_id,
                origins=filters['origen'],
                start_date=filters['fecha_inicio'],
                end_date=filters['fecha_fin'],
                sentiment=sentiment_code,
                cache_manager=cache_manager
            )
        
        # Obtener timestamp de última actualización
        last_update = db_connection.get_last_update_timestamp(alerta_id)
        last_update_str = last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else "No disponible"
        
        # ACTUALIZAR HEADER CON DATOS REALES
        with header_placeholder.container():
            render_dashboard_header(user_info['dashboard'], last_update_str)
                    
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
    viz_manager.render_visualizations(filters, df_completo, filter_manager)
    
    st.divider()
    
    # Tabla de registros - usar datos compartidos
    st.subheader("📋 Tabla de Registros")
    table_manager = DataTableManager()
    df_resultado = table_manager.render_data_table(filters, df_completo)
    
    # Resumen de filtros al final
    st.divider()
    current_year = datetime.now().year
    st.markdown(f"""
    <div style='text-align: center; color: rgba(255,255,255,0.4); margin-top: 2rem;'>
        Copyright ©{current_year} - Proyecto OCD - Todos los derechos reservados.<br>
        Los datos de este tablero y sus fuentes de origen están protegidos por acuerdos de confidencialidad y no pueden ser divulgados.
    </div>
    """, unsafe_allow_html=True)

def render_dashboard(user_info, db_connection, super_editor_mode=False):
    """Función principal que renderiza todo el dashboard"""
    # Inicializar el filter manager
    filter_manager = FilterManager()
    
    # Crear placeholder para header que se actualizará después
    header_placeholder = st.empty()
    
    # Renderizar header inicial con valor temporal
    with header_placeholder.container():
        render_dashboard_header(user_info['dashboard'], "Actualizando...")
    
    # Renderizar filtros en sidebar
    filters = filter_manager.render_filters()
    
    # Renderizar contenido principal (que actualizará el header)
    render_main_content(filter_manager, user_info, db_connection, header_placeholder)
    
    # Super Editor si está activado
    if super_editor_mode:
        st.markdown("---")
        
        from src.editor.super_editor import SuperEditor
        filters = st.session_state.filters
        if filters['applied']:
            alerta_id = user_info['dashboard']['alert_ids'][0]
            sentiment_code = None
            if filters['polaridad'] != 'Todos':
                sentiment_mapping = {'Positivo': 'POS', 'Neutro': 'NEU', 'Negativo': 'NEG'}
                sentiment_code = sentiment_mapping.get(filters['polaridad'])
            
            # Usar datos cacheados en lugar de nueva query
            df_completo = get_cached_social_data(
                alerta_id=alerta_id,
                origins=filters['origen'],
                start_date=filters['fecha_inicio'],
                end_date=filters['fecha_fin'],
                sentiment=sentiment_code
            )

            # Si por alguna razón no hay caché, hacer fallback a query directa
            if df_completo is None:
                df_completo = db_connection.get_social_listening_data(
                    alerta_id=alerta_id,
                    origins=filters['origen'],
                    start_date=filters['fecha_inicio'],
                    end_date=filters['fecha_fin'],
                    sentiment=sentiment_code,
                    limit=None
                )
            
            editor = SuperEditor()
            editor.render_super_editor(filters, df_completo, user_info, db_connection)
        else:
            st.info("🔍 Aplique los filtros para cargar datos en el editor")
    
    return filter_manager