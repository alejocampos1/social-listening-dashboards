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
    page_title="Proyecto OCDUL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
        st.title("📊 Proyecto OCDUL")
        st.write(f"**Usuario:** {user_info['user']['name']}")
        st.write(f"**Email:** {user_info['user']['email']}")
        st.divider()
            
    # Renderizar dashboard completo
    db = DatabaseConnection()
    filter_manager = render_dashboard(user_info, db)


if __name__ == "__main__":
    main()