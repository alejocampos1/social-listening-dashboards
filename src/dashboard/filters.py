import streamlit as st
from datetime import datetime, timedelta

class FilterManager:
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """Inicializa el estado de los filtros"""
        if 'filters' not in st.session_state:
            st.session_state.filters = {
                'origen': ['Facebook', 'X (Twitter)', 'Instagram', 'TikTok'],
                'fecha_inicio': datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'fecha_fin': datetime.now(),
                'polaridad': 'Todos',
                'applied': True
            }
    
    def render_filters(self):
        """Renderiza los filtros en la sidebar y maneja su estado"""
        st.sidebar.header("🔍  Filtros")
        
        # Filtro de Origen
        origen_options_display = ["Facebook", "X (Twitter)", "Instagram", "TikTok"]
        origen_options_db = ["Facebook", "X", "Instagram", "TikTok"]

        # Crear mapeo bidireccional
        display_to_db = dict(zip(origen_options_display, origen_options_db))
        db_to_display = dict(zip(origen_options_db, origen_options_display))

        selected_origen_display = st.sidebar.multiselect(
            "Origen (Redes Sociales)",
            options=origen_options_display,
            default=origen_options_display,  # Mostrar todas por defecto
            help="Selecciona las redes sociales a incluir",
            key="filter_origen",
            on_change=None
        )

        # Convertir selección de display a valores de BD
        selected_origen_db = [display_to_db[origin] for origin in selected_origen_display]
        
        # Filtro de Timeline
        st.sidebar.subheader("📅  Fecha")
        
        time_option = st.sidebar.selectbox(
            "Seleccione un rango de fechas",
            ["Rango personalizado", "Últimos 7 días", "Últimos 30 días", "Este mes", "Últimos 3 meses", "Histórico Completo"],
            key="filter_time_option",
            on_change=None
        )
        
        # Manejar fechas según opción seleccionada
        if time_option == "Rango personalizado":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                fecha_inicio = st.date_input(
                    "Desde",
                    value=st.session_state.filters['fecha_inicio'].date(),
                    key="filter_fecha_inicio",
                    on_change=None
                )
            with col2:
                fecha_fin = st.date_input(
                    "Hasta",
                    value=st.session_state.filters['fecha_fin'].date(),
                    key="filter_fecha_fin",
                    on_change=None
                )
            
            # Convertir a datetime
            fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
            fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
            
        else:
            # Calcular fechas automáticamente
            fecha_fin = datetime.now()
            if time_option == "Últimos 7 días":
                fecha_inicio = fecha_fin - timedelta(days=7)
            elif time_option == "Últimos 30 días":
                fecha_inicio = fecha_fin - timedelta(days=30)
            elif time_option == "Este mes":
                fecha_inicio = fecha_fin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif time_option == "Últimos 3 meses":
                fecha_inicio = fecha_fin - timedelta(days=90)
            elif time_option == "Histórico Completo":
                fecha_inicio = datetime(2025, 1, 1)
            
            st.sidebar.info(f"📅 {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")
        
        # Validación de fechas
        if fecha_inicio > fecha_fin:
            st.sidebar.error("❌ La fecha de inicio no puede ser mayor que la fecha final")
            return None
        
        # Filtro de Polaridad
        st.sidebar.subheader("📊  Polaridad")
        polaridad_options = ["Todos", "Positivo", "Neutro", "Negativo"]
        selected_polaridad = st.sidebar.radio(
            "Sentimiento",
            options=polaridad_options,
            index=polaridad_options.index(st.session_state.filters['polaridad']),
            key="filter_polaridad",
            on_change=None
        )
        
        # Botones de acción
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            apply_filters = st.button(
                "🔄 Aplicar",
                type="primary",
                use_container_width=True,
                key="apply_filters_btn"
            )
        
        with col2:
            reset_filters = st.button(
                "↩️ Reset",
                use_container_width=True,
                key="reset_filters_btn"
            )
        
        # Manejar acciones
        if apply_filters:
            # Validar que al menos una red social esté seleccionada
            if not selected_origen_display:
                st.sidebar.error("❌ Selecciona al menos una red social")
                return None
            
            # Actualizar filtros en session state
            st.session_state.filters = {
                'origen': selected_origen_display,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'polaridad': selected_polaridad,
                'applied': True
            }
            st.sidebar.success("✅ Filtros aplicados")
        
        if reset_filters:
            # Resetear a valores por defecto
            st.session_state.filters = {
                'origen': ['Facebook', 'X (Twitter)', 'Instagram', 'TikTok'],
                'origen_display': selected_origen_display,
                'fecha_inicio': datetime.now() - timedelta(days=30),
                'fecha_fin': datetime.now(),
                'polaridad': 'Todos',
                'applied': True
            }
            st.rerun()
        
        # Botón de logout al final de la sidebar
        st.sidebar.markdown("---")
        from src.auth.authenticator import show_logout_button
        show_logout_button()

        return st.session_state.filters
    
    def get_filter_summary(self):
        """Retorna un resumen de los filtros aplicados"""
        filters = st.session_state.filters
        
        # Contar días en el rango
        days_diff = (filters['fecha_fin'] - filters['fecha_inicio']).days
        
        summary = {
            'total_origins': len(filters['origen']),
            'date_range_days': days_diff,
            'polaridad': filters['polaridad'],
            'is_applied': filters['applied']
        }
        
        return summary
    
    def build_query_filters(self):
        """Construye los parámetros para las queries SQL (para uso futuro)"""
        filters = st.session_state.filters
        
        # Mapear nombres de redes sociales a valores de DB (ajustar según tu DB)
        origin_mapping = {
            'Facebook': 'FB',
            'X (Twitter)': 'X',
            'Instagram': 'IG',
            'TikTok': 'TIKTOK'
        }
        
        db_origins = [origin_mapping.get(origin, origin) for origin in filters['origen']]
        
        query_params = {
            'origins': db_origins,
            'start_date': filters['fecha_inicio'],
            'end_date': filters['fecha_fin'],
            'sentiment': None if filters['polaridad'] == 'Todos' else filters['polaridad'].lower()
        }
        
        return query_params