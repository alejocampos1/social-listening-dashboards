import json
import logging
from datetime import datetime
from pathlib import Path
import streamlit as st

from src.database.connection import DatabaseConnection

class UserLogger:
    def __init__(self):
        self.log_file = Path("logs/user_activity.log")
        self.json_log_file = Path("logs/user_activity.json")
        self._ensure_log_directory()
        self._setup_logging()
        self.db_connection = DatabaseConnection()
    
    def _ensure_log_directory(self):
        """Crea el directorio de logs si no existe"""
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Crear archivo JSON si no existe
        if not self.json_log_file.exists():
            with open(self.json_log_file, 'w') as f:
                json.dump([], f)
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        # Crear logger específico para evitar conflictos
        self.logger = logging.getLogger(f"UserLogger_{id(self)}")
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            # Handler para archivo
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.INFO)
            
            # Formato
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
    
    def log_login(self, username, user_info):
        """Registra login en BD"""
        self.db_connection.log_user_access(
            username=username,
            user_name=user_info['user']['name'],
            email=user_info['user']['email'],
            action="LOGIN",
            dashboard_id=user_info['dashboard_id'],
            dashboard_title=user_info['dashboard']['title']
        )
    
    def log_logout(self, username, user_info=None):
        """Registra logout en BD"""
        if user_info:
            self.db_connection.log_user_access(
                username=username,
                user_name=user_info['user']['name'],
                email=user_info['user']['email'],
                action="LOGOUT",
                dashboard_id=user_info['dashboard_id'],
                dashboard_title=user_info['dashboard'].get('title', '')
            )
    
    def _append_json_log(self, log_entry):
        """Agrega una entrada al log JSON"""
        try:
            # Leer logs existentes
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
            
            # Agregar nueva entrada
            logs.append(log_entry)
            
            # Mantener solo los últimos 1000 logs
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # Escribir de vuelta
            with open(self.json_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error escribiendo log JSON: {e}")
    
    def get_recent_logs(self, limit=50):
        """Obtiene los logs más recientes"""
        try:
            with open(self.json_log_file, 'r') as f:
                logs = json.load(f)
            return logs[-limit:] if logs else []
        except Exception as e:
            self.logger.error(f"Error leyendo logs: {e}")
            return []