import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
from src.utils.logger import UserLogger


class AuthManager:
    def __init__(self):
        self.config = self._load_config()
        self.SESSION_TIMEOUT_MINUTES = 10
    
    def _load_config(self):
        """Carga la configuración desde Streamlit secrets"""
        try:
            return st.secrets
        except Exception as e:
            st.error(f"Error cargando configuración: {e}")
            return None
    
    def generate_session_token(self, username):
        """Genera un token único para la sesión"""
        timestamp = str(time.time())
        return hashlib.md5(f"{username}_{timestamp}".encode()).hexdigest()
    
    def save_session_cookie(self, username, user_info):
        """Guarda la sesión en el session state de manera persistente"""
        token = self.generate_session_token(username)
        session_data = {
            'token': token,
            'username': username,
            'user_info': user_info,
            'last_activity': time.time(),
            'login_time': time.time()
        }
        
        # Guardar en session_state de manera persistente
        st.session_state.persistent_session = session_data
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.username = username
    
    def check_session_validity(self):
        """Verifica si la sesión es válida y no ha expirado"""
        if 'persistent_session' not in st.session_state:
            return False
        
        session_data = st.session_state.persistent_session
        last_activity = session_data.get('last_activity', 0)
        current_time = time.time()
        
        # Verificar timeout de 10 minutos (600 segundos)
        timeout_seconds = self.SESSION_TIMEOUT_MINUTES * 60
        if current_time - last_activity > timeout_seconds:
            self.clear_session()
            return False
        
        # Actualizar timestamp de actividad
        session_data['last_activity'] = current_time
        st.session_state.persistent_session = session_data
        
        return True
    
    def restore_session_from_cookie(self):
        """Restaura la sesión desde session_state si es válida"""
        if self.check_session_validity():
            session_data = st.session_state.persistent_session
            st.session_state.authenticated = True
            st.session_state.user_info = session_data['user_info']
            st.session_state.username = session_data['username']
            return True
        return False
    
    def clear_session(self):
        """Limpia completamente la sesión"""
        keys_to_clear = ['authenticated', 'user_info', 'username', 'persistent_session']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_session_info(self):
        """Obtiene información sobre la sesión actual"""
        if 'persistent_session' not in st.session_state:
            return None
        
        session_data = st.session_state.persistent_session
        current_time = time.time()
        last_activity = session_data.get('last_activity', current_time)
        login_time = session_data.get('login_time', current_time)
        
        # Calcular tiempo restante
        timeout_seconds = self.SESSION_TIMEOUT_MINUTES * 60
        time_since_activity = current_time - last_activity
        time_remaining = max(0, timeout_seconds - time_since_activity)
        
        return {
            'username': session_data.get('username'),
            'login_time': datetime.fromtimestamp(login_time),
            'last_activity': datetime.fromtimestamp(last_activity),
            'time_remaining_minutes': int(time_remaining / 60),
            'time_remaining_seconds': int(time_remaining % 60)
        }
    
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
                    self.save_session_cookie(username, user_info)
                    
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
        
        # Limpiar sesión
        self.clear_session()

def check_authentication():
    """Verifica si el usuario está autenticado, incluyendo restauración de sesión"""
    auth_manager = AuthManager()
    
    # Primero verificar si ya hay autenticación activa
    if st.session_state.get('authenticated', False):
        # Verificar que la sesión no haya expirado
        if auth_manager.check_session_validity():
            return True
        else:
            # Sesión expirada
            st.warning("Sesión expirada por inactividad. Por favor, inicie sesión nuevamente.")
            return False
    
    # Intentar restaurar sesión desde cookies/session_state
    if auth_manager.restore_session_from_cookie():
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