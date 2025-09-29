import streamlit as st
from src.utils.styling import StyleManager
from src.database.connection import DatabaseConnection
from src.dashboard.template import render_dashboard
from src.auth.authenticator import (
    show_login_form, 
    check_authentication, 
    get_user_info, 
    show_logout_button
)

# Configuración de la página
st.set_page_config(
    page_title="Proyecto OCD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    """Función principal de la aplicación"""
    
    # Aplicar styling personalizado
    style_manager = StyleManager()
    style_manager.apply_custom_css()
    
    # Verificar autenticación
    if not check_authentication():
        show_login_form()
        return
    
    # Usuario autenticado - mostrar dashboard
    user_info = get_user_info()
    
    # Sidebar con info del usuario y logout
    with st.sidebar:
        st.title("Proyecto OCD")
        st.write(f"**Usuario:** {user_info['user']['name']}")
        st.write(f"**Email:** {user_info['user']['email']}")
        
        # Selector de dashboard para super usuarios
        if user_info['user'].get('super_user_access', False):
            st.divider()
            st.write("**🔑 Acceso Super Usuario**")
            
            available_dashboards = user_info.get('available_dashboards', [])
            all_dashboards = user_info.get('all_dashboards', {})
            
            # Obtener dashboard actual o usar el por defecto
            current_dashboard = st.session_state.get('current_dashboard', user_info['dashboard_id'])
            
            selected_dashboard = st.selectbox(
                "📊 Seleccionar Dashboard",
                options=available_dashboards,
                index=available_dashboards.index(current_dashboard) if current_dashboard in available_dashboards else 0
            )
            
            # Si cambió el dashboard, actualizar
            if selected_dashboard != current_dashboard:
                st.session_state.current_dashboard = selected_dashboard
                user_info['dashboard_id'] = selected_dashboard
                user_info['dashboard'] = dict(all_dashboards[selected_dashboard])
                
                # Invalidar caché para recargar datos
                from src.utils.data_cache import invalidate_social_cache
                invalidate_social_cache()
                
                st.rerun()
        
        st.divider()
        
        # Control del Super Editor - solo mostrar si tiene permisos
        super_editor_mode = False 
        
        if user_info['user'].get('super_editor_access', False):
            super_editor_mode = st.checkbox("🛠️ Modo Super Editor", value=False)
            
            if super_editor_mode:
                st.info("Modo Super Editor activado")
        
        st.divider()
            
    # Renderizar dashboard completo
    db = DatabaseConnection()
    filter_manager = render_dashboard(user_info, db, super_editor_mode)


if __name__ == "__main__":
    main()