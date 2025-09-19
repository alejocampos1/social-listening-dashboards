import streamlit as st

class StyleManager:
    def __init__(self):
        self.primary_colors = {
            'cyan': "#0483C3",
            'magenta': "#A8012D", 
            'purple': '#8B5CF6',
            'green': '#10B981',
            'yellow': '#F59E0B'
        }
        
        self.background_colors = {
            'main_bg': '#0E1117',
            'secondary_bg': '#262730',
            'card_bg': '#1E293B',
            'hover_bg': '#334155'
        }
    
    def apply_custom_css(self):
        """Aplica CSS personalizado para tema oscuro profesional"""
        
        css = f"""
        <style>
        /* Importar fuente moderna */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Variables CSS */
        :root {{
            --primary-cyan: {self.primary_colors['cyan']};
            --primary-magenta: {self.primary_colors['magenta']};
            --primary-purple: {self.primary_colors['purple']};
            --success-green: {self.primary_colors['green']};
            --warning-yellow: {self.primary_colors['yellow']};
            --bg-main: {self.background_colors['main_bg']};
            --bg-secondary: {self.background_colors['secondary_bg']};
            --bg-card: {self.background_colors['card_bg']};
            --bg-hover: {self.background_colors['hover_bg']};
        }}
        
        /* Configuración general */
        .stApp {{
            background: linear-gradient(135deg, var(--bg-main) 0%, #1a1f2e 100%);
            font-family: 'Inter', sans-serif;
        }}

        /* Aplicar Inter solo a contenido de texto, no a controles UI */
        .stMarkdown, .stText, .stWrite, 
        div[data-testid="metric-container"], 
        .streamlit-expanderHeader,
        h1, h2, h3, h4, h5, h6,
        .stSelectbox label, .stMultiSelect label {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* Aplicar Inter a gráficos y tablas */
        .js-plotly-plot, .js-plotly-plot *, 
        .stDataFrame, .stDataFrame *,
        div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        .stApp p, .stApp div, 
        .stSubheader, .stSubheader *,
        [data-testid="stHeader"],
        .main-header p, .main-header div, .main-header span,
        .element-container p, .element-container div {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background: linear-gradient(180deg, var(--bg-secondary) 0%, #1e2532 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        /* Header styling */
        .main-header {{
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        /* Cards con gradientes */
        .metric-card {{
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            border-color: var(--primary-cyan);
        }}
        
        /* Botones personalizados */
        .stButton > button {{
            background: var(--primary-cyan) !important;
            border: none !important;
            border-radius: 8px !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 16px rgba(8, 145, 178, 0.3) !important;
        }}
        
        .stButton > button:hover {{
            background: #0e7490;
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(8, 145, 178, 0.5);
        }}
        
        /* Filtros sidebar */
        .sidebar-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        /* Selectbox y multiselect styling */
        .stSelectbox > div > div {{
            background-color: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
        }}
        
        .stMultiSelect > div > div {{
            background-color: var(--bg-card);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
        }}
        
        /* Tabla styling */
        .stDataFrame {{
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}
        
        /* Métricas con gradientes */
        div[data-testid="metric-container"] {{
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1.5rem;
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}
        
        div[data-testid="metric-container"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            border-color: var(--primary-cyan);
        }}
        
        /* Expandir styling */
        .streamlit-expanderHeader {{
            background: var(--bg-card);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        /* Títulos con gradientes */
        .gradient-title {{
            background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--primary-magenta) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }}
        
        /* Animaciones suaves */
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Info boxes mejoradas */
        .stInfo {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
        }}
        
        .stSuccess {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.5);
            border-radius: 8px;
        }}
        
        .stWarning {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.1) 100%);
            border: 1px solid rgba(245, 158, 11, 0.5);
            border-radius: 8px;
        }}
        
        .stError {{
            background: linear-gradient(135deg, rgba(255, 0, 107, 0.2) 0%, rgba(255, 0, 107, 0.1) 100%);
            border: 1px solid rgba(255, 0, 107, 0.5);
            border-radius: 8px;
        }}
        
        /* Gráficos con bordes */
        .js-plotly-plot {{
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }}
        
        /* Loading states */
        .stSpinner {{
            border-color: var(--primary-cyan) !important;
        }}
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--bg-secondary);
            border-radius: 8px;
            padding: 0.25rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 6px;
            color: rgba(255, 255, 255, 0.7);
            transition: all 0.3s ease;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--primary-purple) 100%);
            color: white;
        }}
        
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--primary-purple) 100%);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, var(--primary-purple) 0%, var(--primary-magenta) 100%);
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .main-header {{
                padding: 1rem;
            }}
            
            .metric-card {{
                padding: 1rem;
            }}
        }}
        
        /* Solo cambiar el color de los tags seleccionados en multiselect */
        span[data-baseweb="tag"] {{
            background-color: var(--primary-magenta) !important;
        }}

        /* Solo el texto dentro de los tags */
        span[data-baseweb="tag"] span {{
            color: white !important;
        }}

        /* El botón X de los tags */
        span[data-baseweb="tag"] svg {{
            color: white !important;
        }}
        
        
        
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def create_gradient_title(self, text, size="h1"):
        """Crea un título con gradiente"""
        if size == "h1":
            st.markdown(f'<h1 class="gradient-title">{text}</h1>', unsafe_allow_html=True)
        elif size == "h2":
            st.markdown(f'<h2 class="gradient-title">{text}</h2>', unsafe_allow_html=True)
        elif size == "h3":
            st.markdown(f'<h3 class="gradient-title">{text}</h3>', unsafe_allow_html=True)
    
    def create_metric_card(self, title, value, delta=None, help_text=None):
        """Crea una tarjeta de métrica con styling personalizado"""
        delta_html = f'<span style="color: {self.primary_colors["green"]};">↗ {delta}</span>' if delta else ""
        help_html = f'<small style="color: rgba(255,255,255,0.6);">{help_text}</small>' if help_text else ""
        
        card_html = f"""
        <div class="metric-card fade-in">
            <h3 style="color: {self.primary_colors['cyan']}; margin: 0; font-size: 1rem;">{title}</h3>
            <h2 style="color: white; margin: 0.5rem 0; font-size: 2rem; font-weight: 700;">{value}</h2>
            {delta_html}
            {help_html}
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def add_loading_animation(self):
        """Agrega animación de carga"""
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
            <div style="
                border: 4px solid rgba(0, 212, 255, 0.1);
                border-left: 4px solid #0483C3;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
            "></div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)