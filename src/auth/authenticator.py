import streamlit as st
from src.utils.logger import UserLogger


class AuthManager:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde Streamlit secrets"""
        try:
            return st.secrets
        except Exception as e:
            st.error(f"Error cargando configuración: {e}")
            return None
    
    def authenticate(self, username, password):
        """Autentica un usuario y retorna info del dashboard"""
        if not self.config:
            return False, None
            
        try:
            users = self.config["users"]
            dashboards = self.config["dashboards"]
            
            if username in users:
                user_data = dict(users[username])
                
                if user_data['password'] == password:
                    dashboard_id = user_data['dashboard_id']
                    dashboard_info = dict(dashboards[dashboard_id])
                    
                    return True, {
                        'user': user_data,
                        'dashboard': dashboard_info,
                        'dashboard_id': dashboard_id
                    }
        except Exception as e:
            st.error(f"Error en autenticación: {e}")
        
        return False, None
    
    def logout(self):
        """Limpia la sesión del usuario"""
        keys_to_clear = ['authenticated', 'user_info', 'username']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

def show_login_form():
    """Muestra el formulario de login"""
    st.title("🔐 Proyecto OCDUL")
    st.subheader("Acceso a Dashboards de Social Listening")
    
    # Crear columnas para centrar el formulario
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")
            
            if submitted:
                auth_manager = AuthManager()
                success, user_info = auth_manager.authenticate(username, password)
                
                if success:
                    # Registrar login en logs
                    logger = UserLogger()
                    logger.log_login(username, user_info)
                    
                    # Guardar info en session state
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.session_state.username = username
                    st.success("✅ Login exitoso")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

def check_authentication():
    """Verifica si el usuario está autenticado"""
    return st.session_state.get('authenticated', False)

def get_user_info():
    """Obtiene la información del usuario autenticado"""
    return st.session_state.get('user_info', None)

def show_logout_button():
    """Muestra el botón de logout en la sidebar"""
    if st.sidebar.button("🚪 Cerrar Sesión"):
        # Registrar logout en logs
        username = st.session_state.get('username')
        user_info = st.session_state.get('user_info')
        
        logger = UserLogger()
        logger.log_logout(username, user_info)
        
        # Hacer logout
        auth_manager = AuthManager()
        auth_manager.logout()
        st.rerun()