import streamlit as st
from src.utils.logger import UserLogger
from .session_manager import SessionManager


class AuthManager:
    def __init__(self):
        self.config = self._load_config()
        self.session_manager = SessionManager()
    
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
                    
                    user_info = {
                        'user': user_data,
                        'dashboard': dashboard_info,
                        'dashboard_id': dashboard_id
                    }
                    
                    # Guardar sesión persistente
                    session_token = self.session_manager.save_session(username, user_info)
                    
                    # Guardar también en session_state
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.session_state.username = username
                    
                    return True, user_info
                    
        except Exception as e:
            st.error(f"Error en autenticación: {e}")
        
        return False, None
    
    def logout(self):
        """Limpia la sesión del usuario y registra el logout"""
        username = st.session_state.get('username')
        user_info = st.session_state.get('user_info')
        
        if username and user_info:
            # Registrar logout en logs
            logger = UserLogger()
            logger.log_logout(username, user_info)
        
        # Eliminar sesión persistente
        token = st.session_state.get('session_token')
        if token:
            self.session_manager.delete_session(token)
        
        # Limpiar session_state
        keys_to_clear = ['authenticated', 'user_info', 'username', 'session_token']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]


def check_authentication():
    """Verifica si el usuario está autenticado, incluyendo restauración de sesión"""
    auth_manager = AuthManager()
    
    # Verificar sesión activa o restaurar desde archivo
    if st.session_state.get('authenticated', False):
        # Actualizar actividad de sesión existente
        token = st.session_state.get('session_token')
        if token:
            auth_manager.session_manager.update_activity(token)
        return True
    
    # Intentar restaurar sesión persistente
    if auth_manager.session_manager.restore_session_if_valid():
        return True
    
    return False


def show_login_form():
    """Muestra el formulario de login"""
    st.markdown("<h1 style='text-align: center;'>🔐 Proyecto OCDUL</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Acceso a Dashboards de Social Listening</h3>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Crear columnas para centrar el formulario
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            username = st.text_input("Usuario", max_chars=50)
            password = st.text_input("Contraseña", type="password", max_chars=50)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Centrar el botón
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
                
                if submitted:
                    auth_manager = AuthManager()
                    success, user_info = auth_manager.authenticate(username, password)
                    
                    if success:
                        # Registrar login en logs
                        logger = UserLogger()
                        logger.log_login(username, user_info)
                        
                        st.success("✅ Login exitoso")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")


def get_user_info():
    """Obtiene la información del usuario autenticado"""
    return st.session_state.get('user_info', None)


def show_logout_button():
    """Muestra el botón de logout en la sidebar"""
    if st.sidebar.button("🚪 Cerrar Sesión"):
        auth_manager = AuthManager()
        auth_manager.logout()
        st.rerun()