import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import streamlit as st

class SessionManager:
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.session_timeout = 600  # 10 minutos en segundos
        self._ensure_sessions_directory()
    
    def _ensure_sessions_directory(self):
        """Crea el directorio de sesiones si no existe"""
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Crear .gitignore para no versionar sesiones
        gitignore_path = self.sessions_dir / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write("*.json\n")
    
    def generate_session_token(self, username):
        """Genera un token único para la sesión"""
        timestamp = str(time.time())
        return hashlib.md5(f"{username}_{timestamp}".encode()).hexdigest()
    
    def save_session(self, username, user_info):
        """Guarda la sesión en archivo"""
        token = self.generate_session_token(username)
        session_data = {
            'token': token,
            'username': username,
            'user_info': user_info,
            'created_at': time.time(),
            'last_activity': time.time()
        }
        
        session_file = self.sessions_dir / f"{token}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, default=str)
        
        # Guardar token en session_state para referencia
        st.session_state.session_token = token
        
        # Agregar token a URL para persistir entre recargas
        st.query_params['session'] = token
        
        return token
    
    def load_session(self, token):
        """Carga sesión desde archivo"""
        session_file = self.sessions_dir / f"{token}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            return session_data
        except:
            return None
    
    def is_session_valid(self, token):
        """Verifica si la sesión es válida"""
        session_data = self.load_session(token)
        
        if not session_data:
            return False
        
        # Verificar timeout
        current_time = time.time()
        last_activity = session_data.get('last_activity', 0)
        
        if current_time - last_activity > self.session_timeout:
            self.delete_session(token)
            return False
        
        return True
    
    def update_activity(self, token):
        """Actualiza timestamp de actividad"""
        session_data = self.load_session(token)
        
        if session_data:
            session_data['last_activity'] = time.time()
            session_file = self.sessions_dir / f"{token}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, default=str)
    
    def delete_session(self, token):
        """Elimina sesión"""
        session_file = self.sessions_dir / f"{token}.json"
        if session_file.exists():
            session_file.unlink()
        
        if 'session_token' in st.session_state:
            del st.session_state.session_token
    
    def restore_session_if_valid(self):
        """Intenta restaurar sesión válida al cargar la página"""
        token = st.session_state.get('session_token')
        
        # Si no hay token en session_state, buscar en query params
        if not token:
            query_params = st.query_params
            token = query_params.get('session')
            
            if not token:
                return False
                
            session_data = self.load_session(token)
        else:
            session_data = self.load_session(token)
        
        if session_data and self.is_session_valid(token):
            # Restaurar datos en session_state
            st.session_state.authenticated = True
            st.session_state.user_info = session_data['user_info']
            st.session_state.username = session_data['username']
            st.session_state.session_token = token
            
            # Agregar token a URL para persistir
            st.query_params['session'] = token
            
            # Actualizar actividad
            self.update_activity(token)
            return True
        
        return False
    
    def cleanup_expired_sessions(self):
        """Limpia sesiones expiradas (llamar ocasionalmente)"""
        current_time = time.time()
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                last_activity = session_data.get('last_activity', 0)
                if current_time - last_activity > self.session_timeout:
                    session_file.unlink()
            except:
                # Si hay error leyendo, eliminar archivo corrupto
                session_file.unlink()