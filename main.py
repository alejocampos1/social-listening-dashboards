import streamlit as st
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
        show_logout_button()
    
    # Área principal del dashboard
    st.title(user_info['dashboard']['title'])
    st.write(user_info['dashboard']['description'])
    
    # TEMPORAL: Mostrar información del dashboard
    st.info("🚧 Dashboard en construcción...")
    
    # Mostrar configuración actual (temporal)
    with st.expander("ℹ️ Información de configuración (temporal)"):
        st.write("**Dashboard ID:**", user_info['dashboard_id'])
        st.write("**Alert IDs:**", user_info['dashboard']['alert_ids'])

if __name__ == "__main__":
    main()