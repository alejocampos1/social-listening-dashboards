import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from typing import Dict, List, Any

class SuperEditor:
    def __init__(self):
        # Inicializar queue de cambios si no existe
        if 'edit_queue' not in st.session_state:
            st.session_state.edit_queue = []
        
        # Mapeos de sentimiento
        self.sentiment_mapping = {
            'POS': 'Positivo',
            'NEU': 'Neutro', 
            'NEG': 'Negativo'
        }
        
        self.reverse_sentiment_mapping = {v: k for k, v in self.sentiment_mapping.items()}
        
        # Colores para sentimientos
        self.sentiment_colors = {
            'Positivo': '#10B981',
            'Neutro': '#F59E0B', 
            'Negativo': '#FF006B'
        }
    
    def render_super_editor(self, filters, df_completo, user_info, db_connection):
        """Renderiza la interfaz principal del Super Editor"""
        
        st.markdown(
            """
            <h1 style='text-align: center;'>🛠️ Modo Súper Editor (Acceso Restringido)</h1>
            """, 
            unsafe_allow_html=True
        )        
        st.markdown("---")
        
        # Verificar permisos
        if not self._check_editor_permissions(user_info):
            st.error("❌ No tienes permisos para acceder al Super Editor")
            st.info("Contacta al administrador para solicitar acceso")
            return
        
        # Verificar si hay datos
        if not filters['applied'] or df_completo.empty:
            st.info("🔍 Aplique los filtros principales para cargar datos en el editor")
            return
        
        # Preparar datos
        df = self._prepare_editor_data(df_completo)
        
        # Mostrar estadísticas generales
        self._render_editor_stats(df)
        
        st.markdown("---")
        
        # Filtros específicos del editor
        filtered_df = self._render_editor_filters(df)
        
        if filtered_df.empty:
            st.warning("⚠️ No hay datos con los filtros aplicados")
            return
        
        st.markdown("---")
        
        # Tabla editable
        self._render_editable_table(filtered_df)
        
        st.markdown("---")

        # Sección unificada de cambios pendientes
        self._render_pending_changes(db_connection, user_info)
        
    
    def _check_editor_permissions(self, user_info: Dict) -> bool:
        """Verifica si el usuario tiene permisos de super editor"""
        try:
            # Obtener información del usuario actual
            user_data = user_info.get('user', {})
            
            # Verificar si tiene permisos de super editor
            has_access = user_data.get('super_editor_access', False)
            
            return has_access
            
        except Exception as e:
            # En caso de error, denegar acceso por seguridad
            st.error(f"Error verificando permisos: {str(e)}")
            return False
    
    def _prepare_editor_data(self, df_completo: pd.DataFrame) -> pd.DataFrame:
        """Prepara los datos para el editor"""
        df = df_completo.copy()
        
        # Agregar columna de sentimiento legible
        df['sentiment_display'] = df['sentiment_pred'].map(self.sentiment_mapping).fillna('Desconocido')
        
        # Agregar columna de ID único para tracking
        df['edit_id'] = df.index
        
        return df
    
    def _render_editor_stats(self, df: pd.DataFrame):
        """Renderiza estadísticas del editor"""
        
        st.metric("Total Registros", f"{len(df):,}")

    def _render_editor_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renderiza filtros específicos del editor"""
        st.subheader("🔽 Filtros del Editor")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtro por fecha - selección manual
            st.write("**Rango de Fechas:**")
            
            col_start, col_end = st.columns(2)
            
            with col_start:
                start_date = st.date_input(
                    "Desde",
                    value=df['created_time'].min().date(),
                    key="editor_date_start"
                )
            
            with col_end:
                end_date = st.date_input(
                    "Hasta",
                    value=df['created_time'].max().date(),
                    key="editor_date_end"
                )
            
            # Convertir a tuple para mantener compatibilidad con el código existente
            date_range = (start_date, end_date)
        
        with col2:
            # Filtro por red social
            available_origins = df['origin'].unique().tolist()
            selected_origins = st.multiselect(
                "Redes Sociales",
                options=available_origins,
                default=available_origins,
                key="editor_origin_filter"
            )
        
        with col3:
            # Filtro por sentimiento actual
            available_sentiments = df['sentiment_display'].unique().tolist()
            selected_sentiments = st.multiselect(
                "Sentimientos Actuales",
                options=available_sentiments,
                default=available_sentiments,
                key="editor_sentiment_filter"
            )
        
        # Aplicar filtros
        filtered_df = df.copy()
        
        # Filtro de fecha
        if len(date_range) == 2:
            start_date = pd.Timestamp(date_range[0])
            end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
            filtered_df = filtered_df[
                (filtered_df['created_time'] >= start_date) & 
                (filtered_df['created_time'] < end_date)
            ]
        
        # Filtro de origen
        if selected_origins:
            filtered_df = filtered_df[filtered_df['origin'].isin(selected_origins)]
        
        # Filtro de sentimiento
        if selected_sentiments:
            filtered_df = filtered_df[filtered_df['sentiment_display'].isin(selected_sentiments)]
        
        return pd.DataFrame(filtered_df)
    
    def _render_queue_status(self):
        """Renderiza el estado del queue de cambios"""
        st.subheader("📋 Queue de Cambios")
        
        if not st.session_state.edit_queue:
            st.info("No hay cambios pendientes")
            return
        
        # Mostrar resumen del queue
        queue_df = pd.DataFrame(st.session_state.edit_queue)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Cambios por Sentimiento:**")
            if 'new_sentiment' in queue_df.columns:
                sentiment_changes = queue_df['new_sentiment'].value_counts()
                for sentiment, count in sentiment_changes.items():
                    st.write(f"• {sentiment}: {count} cambios")
        
        with col2:
            st.write("**Acciones:**")
            col_clear, col_preview = st.columns(2)
            
            with col_clear:
                if st.button("🗑️ Limpiar Queue", type="secondary"):
                    st.session_state.edit_queue = []
                    st.rerun()
            
            with col_preview:
                if st.button("👁️ Preview Cambios", type="secondary"):
                    self._show_changes_preview()
    
    def _render_editable_table(self, df: pd.DataFrame):
        """Renderiza la tabla editable"""
        st.subheader("📝 Tabla Editable")
        
        # Limitar registros para performance
        max_records = st.number_input(
            "Máximo de registros a mostrar", 
            min_value=10, 
            max_value=500, 
            value=100, 
            step=10
        )
        
        display_df = df.head(max_records).copy()
        
        if display_df.empty:
            st.warning("No hay registros para mostrar")
            return
        
        # Preparar columnas para display
        columns_to_show = [
            'edit_id', 'created_time', 'origin',
            'text', 'sentiment_display'
        ]
        
        # Filtrar columnas que existen
        available_columns = [col for col in columns_to_show if col in display_df.columns]
        table_df = display_df[available_columns].copy()
        
        # Truncar texto para mejor visualización
        if 'text' in table_df.columns:
            table_df['text'] = table_df['text'].apply(
                lambda x: str(x)[:100] + "..." if len(str(x)) > 100 else str(x)
            )
        
        # Mostrar tabla con controles de edición
        st.write("**Instrucciones:** Selecciona registros y usa los controles de abajo para cambiar sentimientos")
        
        # Mostrar tabla editable con dropdown para sentimiento
        # Agregar columna de eliminación
        table_df['eliminar'] = False

        # Mostrar tabla editable con dropdown para sentimiento y checkbox para eliminar
        edited_df = st.data_editor(
            table_df,
            use_container_width=True,
            hide_index=True,
            height=1200,
            column_config={
                'edit_id': st.column_config.NumberColumn('ID', width="small", disabled=True),
                'created_time': st.column_config.DatetimeColumn('Fecha', width="medium", disabled=True),
                'origin': st.column_config.TextColumn('Red Social', width="small", disabled=True),
                'text': st.column_config.TextColumn('Contenido', width="large", disabled=True),
                'sentiment_display': st.column_config.SelectboxColumn(
                    'Sentimiento',
                    width="small",
                    options=['Positivo', 'Neutro', 'Negativo'],
                    required=True
                ),
                'eliminar': st.column_config.CheckboxColumn(
                    'Eliminar',
                    width="small",
                    help="Marcar para eliminar este registro"
                )
            },
            key="sentiment_editor_table"
        )

        # Detectar cambios y agregarlos al queue automáticamente
        self._detect_and_queue_changes(table_df, edited_df, df)

        # Detectar registros marcados para eliminar
        self._detect_and_queue_deletions(table_df, edited_df, df)
                  
    def _render_pending_changes(self, db_connection, user_info):
        """Renderiza la sección unificada de cambios pendientes"""
        st.subheader("📋 Cambios Pendientes")
        
        if not st.session_state.edit_queue:
            st.info("No hay cambios pendientes")
            return
        
        # Mostrar tabla de cambios
        queue_df = pd.DataFrame(st.session_state.edit_queue)
        
        display_columns = ['edit_id', 'current_sentiment', 'new_sentiment', 'text_preview']
        available_cols = [col for col in display_columns if col in queue_df.columns]
        
        st.dataframe(
            queue_df[available_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                'edit_id': st.column_config.NumberColumn('ID', width="small"),
                'current_sentiment': st.column_config.TextColumn('Actual', width="small"),
                'new_sentiment': st.column_config.TextColumn('Nuevo', width="small"),
                'text_preview': st.column_config.TextColumn('Contenido', width="large")
            }
        )
        
        # Controles
        col1, col2 = st.columns([3, 1])

        with col1:
            queue_count = len(st.session_state.edit_queue)
            st.metric("Total", queue_count)

        with col2:
            # Botones alineados a la derecha
            if st.button("🗑️ Limpiar Todo", type="secondary", use_container_width=True):
                st.session_state.edit_queue = []
                st.rerun()
            
            if st.button("✅ Aplicar Cambios", type="primary", use_container_width=True):
                self._apply_changes_to_database(db_connection, user_info)
    
    def _detect_and_queue_deletions(self, original_df, edited_df, full_df):
        """Detecta registros marcados para eliminar y los agrega/remueve del queue"""
        
        # Limpiar todas las eliminaciones existentes del queue primero
        st.session_state.edit_queue = [q for q in st.session_state.edit_queue 
                                    if q.get('action') != 'delete']
        
        # Buscar registros actualmente marcados para eliminar
        deletion_mask = edited_df['eliminar'] == True
        
        if deletion_mask.any():
            marked_for_deletion = edited_df[deletion_mask]
            deletions_detected = 0
            
            for _, row in marked_for_deletion.iterrows():
                edit_id = row['edit_id']
                record = full_df[full_df['edit_id'] == edit_id].iloc[0]
                
                queue_entry = {
                    'edit_id': edit_id,
                    'record_id': int(record.get('id', edit_id)),
                    'table_name': record.get('table_source'),
                    'action': 'delete',
                    'current_sentiment': record['sentiment_display'],
                    'new_sentiment': 'ELIMINADO',
                    'timestamp': datetime.now(),
                    'text_preview': str(record.get('text', ''))[:50] + "..."
                }
                
                if queue_entry['table_name']:
                    st.session_state.edit_queue.append(queue_entry)
                    deletions_detected += 1
    
    def _add_to_queue(self, selected_ids: List[int], new_sentiment: str, df: pd.DataFrame):
        """Agrega cambios al queue"""
        for edit_id in selected_ids:
            # Buscar el registro
            record = df[df['edit_id'] == edit_id].iloc[0]
            
            # Crear entrada del queue
            queue_entry = {
                'edit_id': edit_id,
                'record_id': int(record.get('id', edit_id)),
                'table_name': record.get('table_source'),
                'current_sentiment': record['sentiment_display'],
                'new_sentiment': new_sentiment,
                'new_sentiment_code': self.reverse_sentiment_mapping[new_sentiment],
                'timestamp': datetime.now(),
                'text_preview': str(record.get('text', ''))[:50] + "..."
            }
            
            # Validar que tenemos tabla
            if not queue_entry['table_name']:
                st.error(f"No se pudo identificar la tabla para el registro {edit_id}")
                continue
            
            # Evitar duplicados
            existing = [q for q in st.session_state.edit_queue 
                    if q['edit_id'] == edit_id]
            
            if existing:
                # Actualizar existente
                for i, q in enumerate(st.session_state.edit_queue):
                    if q['edit_id'] == edit_id:
                        st.session_state.edit_queue[i] = queue_entry
                        break
            else:
                # Agregar nuevo
                st.session_state.edit_queue.append(queue_entry)
    
    def _get_table_name(self, origin: str) -> str:
        """Obtiene el nombre de tabla basado en el origen"""
        # Mapeo de origen a tabla
        table_mapping = {
            'Facebook': 'posts_facebook',
            'Instagram': 'posts_instagram', 
            'X': 'posts_x',
            'TikTok': 'posts_tiktok'
        }
        return table_mapping.get(origin, 'unknown_table')
    
    def _show_changes_preview(self):
        """Muestra preview de los cambios pendientes"""
        if not st.session_state.edit_queue:
            st.info("No hay cambios para mostrar")
            return
        
        with st.expander("🔍 Preview de Cambios", expanded=True):
            queue_df = pd.DataFrame(st.session_state.edit_queue)
            
            # Mostrar resumen
            st.write("**Resumen de Cambios:**")
            col1, col2 = st.columns(2)
            
            with col1:
                change_summary = queue_df.groupby(['current_sentiment', 'new_sentiment']).size().reset_index(name='count')
                st.dataframe(change_summary, hide_index=True)
            
            with col2:
                table_summary = queue_df['table_name'].value_counts()
                st.write("**Por Tabla:**")
                for table, count in table_summary.items():
                    st.write(f"• {table}: {count} cambios")
            
            # Mostrar detalles
            st.write("**Detalle de Cambios:**")
            preview_columns = ['edit_id', 'current_sentiment', 'new_sentiment', 'text_preview', 'timestamp']
            available_preview_cols = [col for col in preview_columns if col in queue_df.columns]
            
            st.dataframe(
                queue_df[available_preview_cols],
                hide_index=True,
                use_container_width=True
            )
    
    def _render_action_controls(self, db_connection, user_info: Dict):
        """Renderiza controles para aplicar o cancelar cambios"""
        st.subheader("🚀 Aplicar Cambios")
        
        if not st.session_state.edit_queue:
            st.info("No hay cambios pendientes para aplicar")
            return
        
        # Mostrar resumen final
        queue_count = len(st.session_state.edit_queue)
        st.write(f"**{queue_count} cambios pendientes**")
        
        # Controles
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("❌ Cancelar Todo", type="secondary"):
                st.session_state.edit_queue = []
                st.success("✅ Queue limpiado")
                st.rerun()
        
        with col2:
            if st.button("👁️ Preview Final", type="secondary"):
                self._show_changes_preview()
        
        with col3:
            if st.button("✅ Aplicar Cambios", type="primary"):
                self._apply_changes_to_database(db_connection, user_info)
                
    def _detect_and_queue_changes(self, original_df, edited_df, full_df):
        """Detecta cambios en la tabla y los agrega automáticamente al queue"""
        # Solo procesar si realmente hay diferencias
        if original_df.equals(edited_df):
            return
        
        # Usar vectorización para detectar cambios más rápido
        mask = original_df['sentiment_display'] != edited_df['sentiment_display']
        
        if not mask.any():
            return
        
        changed_rows = edited_df[mask]
        changes_detected = 0
        
        for _, row in changed_rows.iterrows():
            edit_id = row['edit_id']
            new_sentiment = row['sentiment_display']
            
            # Evitar duplicados en el queue
            existing_ids = [q['edit_id'] for q in st.session_state.edit_queue]
            if edit_id not in existing_ids:
                # Buscar record más eficientemente
                record = full_df[full_df['edit_id'] == edit_id].iloc[0]
                self._add_to_queue([edit_id], new_sentiment, full_df)
                changes_detected += 1
        
        # Solo mostrar mensaje si hay cambios nuevos
        if changes_detected > 0:
            st.toast(f"✅ {changes_detected} cambios agregados", icon="✅")
    
    def _apply_changes_to_database(self, db_connection, user_info: Dict):
        """Aplica los cambios a la base de datos"""
        if not st.session_state.edit_queue:
            st.warning("No hay cambios para aplicar")
            return
        
        try:
            with st.spinner("Aplicando cambios a la base de datos..."):
                success_count = 0
                error_count = 0
                
                for change in st.session_state.edit_queue:
                    try:
                        # Validar tabla
                        if not change.get('table_name'):
                            error_count += 1
                            st.error(f"Error en cambio {change['edit_id']}: tabla no identificada")
                            continue
                        
                        # Verificar si es eliminación o actualización
                        if change.get('action') == 'delete':
                            # Eliminar registro
                            success, message = db_connection.delete_record(
                                table_name=change['table_name'],
                                record_id=change['record_id']
                            )
                            
                            if success:
                                # Registrar eliminación en logs
                                db_connection.log_editor_change(
                                    user_name=user_info['user']['name'],
                                    table_name=change['table_name'],
                                    record_id=change['record_id'],
                                    old_sentiment=change['current_sentiment'],
                                    new_sentiment='ELIMINADO'
                                )
                                success_count += 1
                            else:
                                error_count += 1
                                st.error(f"Error eliminando registro {change['edit_id']}: {message}")
                        
                        else:
                            # Actualizar sentimiento (código existente)
                            success, message = db_connection.update_sentiment(
                                table_name=change['table_name'],
                                record_id=change['record_id'],
                                new_sentiment=change['new_sentiment_code'],
                                confidence=1.0
                            )
                            
                            if success:
                                # Registrar en logs
                                db_connection.log_editor_change(
                                    user_name=user_info['user']['name'],
                                    table_name=change['table_name'],
                                    record_id=change['record_id'],
                                    old_sentiment=change['current_sentiment'],
                                    new_sentiment=change['new_sentiment']
                                )
                                success_count += 1
                            else:
                                error_count += 1
                                st.error(f"Error en cambio {change['edit_id']}: {message}")
                            
                    except Exception as e:
                        error_count += 1
                        st.error(f"Error en cambio {change['edit_id']}: {str(e)}")
                
                # Limpiar queue y tabla editable
                st.session_state.edit_queue = []
                if 'sentiment_editor_table' in st.session_state:
                    del st.session_state['sentiment_editor_table']
                
                # Mostrar resultados
                if success_count > 0:
                    st.success(f"✅ {success_count} cambios aplicados exitosamente")
                
                if error_count > 0:
                    st.error(f"❌ {error_count} cambios fallaron")
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error crítico al aplicar cambios: {str(e)}")
    
    def _log_changes(self, user_info: Dict, success_count: int, error_count: int):
        """Registra los cambios en el log"""
        # TODO: Implementar sistema de logging
        log_entry = {
            'user': user_info.get('name', 'Unknown'),
            'timestamp': datetime.now(),
            'success_count': success_count,
            'error_count': error_count,
            'total_changes': success_count + error_count
        }
        
        # Por ahora solo almacenar en session_state
        if 'edit_logs' not in st.session_state:
            st.session_state.edit_logs = []
        
        st.session_state.edit_logs.append(log_entry)