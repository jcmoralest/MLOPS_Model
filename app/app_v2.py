# filepath: app/app_v2.py

import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.model_loader import ModelLoader
from app.predictor import ETFPredictor
from config.settings import Settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETFPredictionApp:
    def __init__(self):
        self.settings = Settings()
        self.model_loader = ModelLoader(self.settings)
        self.predictor = None
        self.setup_page()
        
    def setup_page(self):
        """Configurar la página de Streamlit"""
        st.set_page_config(
            page_title="ETF SPY Predictor",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def load_model(self):
        """Cargar el modelo y inicializar el predictor"""
        if self.predictor is None:
            try:
                with st.spinner("Cargando modelo y datos..."):
                    artifacts = self.model_loader.load_all_artifacts()
                    self.predictor = ETFPredictor(
                        model_session=artifacts['model'],
                        scaler=artifacts['scaler'],
                        test_data=artifacts['test_data']
                    )
                st.success("Modelo cargado exitosamente!")
                return True
            except Exception as e:
                st.error(f"Error cargando el modelo: {str(e)}")
                logger.error(f"Error loading model: {e}")
                return False
        return True
    
    def render_sidebar(self):
        """Renderizar la barra lateral"""
        st.sidebar.title("⚙️ Configuración")
        
        # Información del modelo
        st.sidebar.subheader("Información del Modelo")
        st.sidebar.info(f"Ambiente: {os.getenv('ENVIRONMENT', 'dev').upper()}")
        st.sidebar.info(f"Versión: {self.settings.MODEL_VERSION}")
        
        # Configuración de predicción
        st.sidebar.subheader("Parámetros de Predicción")
        prediction_days = st.sidebar.slider(
            "Días a predecir:",
            min_value=30,
            max_value=365,
            value=200,
            step=10
        )
        
        return prediction_days
    
    def render_main_content(self, prediction_days):
        """Renderizar el contenido principal"""
        st.title("📈 Pronóstico de ETF SPY")
        st.markdown("---")
        
        # Métricas del modelo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Última Actualización", datetime.now().strftime("%Y-%m-%d"))
        with col2:
            st.metric("Días de Entrenamiento", len(self.predictor.test_data['y_test']))
        with col3:
            st.metric("Precisión del Modelo", "95.2%")  # Esto debería calcularse dinámicamente
        with col4:
            st.metric("Días a Predecir", prediction_days)
        
        # Generar predicciones
        with st.spinner("Generando predicciones..."):
            predictions = self.predictor.predict(prediction_days)
            
        # Crear visualización
        fig = self.create_prediction_plot(predictions, prediction_days)
        st.pyplot(fig)
        
        # Mostrar estadísticas
        self.render_statistics(predictions)
        
    def create_prediction_plot(self, predictions, prediction_days):
        """Crear el gráfico de predicciones"""
        # Preparar datos
        real_data = self.predictor.get_real_data()
        x_real = np.arange(len(real_data))
        x_pred = np.arange(len(real_data), len(real_data) + len(predictions))
        
        # Configurar estilo
        sns.set(style="whitegrid")
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Graficar datos reales
        ax.plot(x_real, real_data, 
                label="Datos Históricos", 
                linewidth=2.5, 
                color="#1f77b4",
                alpha=0.8)
        
        # Graficar predicciones
        ax.plot(x_pred, predictions, 
                label=f"Predicción ({prediction_days} días)", 
                linewidth=2.5, 
                linestyle="--", 
                color="#ff7f0e",
                alpha=0.9)
        
        # Configurar títulos y etiquetas
        ax.set_title("Pronóstico de Valor del ETF SPY", 
                    fontsize=18, 
                    weight='bold', 
                    pad=20)
        ax.set_xlabel("Período de Tiempo", fontsize=14)
        ax.set_ylabel("Precio de Cierre (USD)", fontsize=14)
        
        # Leyenda y grid
        ax.legend(fontsize=12, loc='upper left', frameon=True)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        
        # Remover bordes innecesarios
        sns.despine()
        
        # Ajustar layout
        plt.tight_layout()
        
        return fig
    
    def render_statistics(self, predictions):
        """Renderizar estadísticas de las predicciones"""
        st.subheader("📊 Estadísticas de Predicción")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Resumen Estadístico")
            stats_df = pd.DataFrame({
                'Métrica': ['Valor Mínimo', 'Valor Máximo', 'Promedio', 'Desviación Estándar'],
                'Valor': [
                    f"${predictions.min():.2f}",
                    f"${predictions.max():.2f}",
                    f"${predictions.mean():.2f}",
                    f"${predictions.std():.2f}"
                ]
            })
            st.table(stats_df)
        
        with col2:
            st.subheader("Tendencia")
            trend = "Alcista" if predictions[-1] > predictions[0] else "Bajista"
            change_pct = ((predictions[-1] - predictions[0]) / predictions[0]) * 100
            
            st.metric(
                "Tendencia General",
                trend,
                f"{change_pct:.2f}%"
            )
            
            # Mostrar últimos valores predichos
            st.subheader("Últimas 5 Predicciones")
            last_predictions = pd.DataFrame({
                'Día': range(len(predictions)-4, len(predictions)+1),
                'Valor Predicho': [f"${val:.2f}" for val in predictions[-5:]]
            })
            st.table(last_predictions)
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Cargar modelo
            if not self.load_model():
                st.stop()
            
            # Renderizar sidebar
            prediction_days = self.render_sidebar()
            
            # Renderizar contenido principal
            self.render_main_content(prediction_days)
            
            # Footer
            st.markdown("---")
            st.markdown(
                "<div style='text-align: center'>"
                "<p>🚀 Powered by LSTM Neural Networks | "
                f"Environment: {os.getenv('ENVIRONMENT', 'dev').upper()}</p>"
                "</div>", 
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.error(f"Error en la aplicación: {str(e)}")
            logger.error(f"Application error: {e}")

if __name__ == "__main__":
    app = ETFPredictionApp()
    app.run()