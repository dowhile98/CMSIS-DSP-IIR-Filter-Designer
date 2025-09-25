import sys
import os
import numpy as np
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGroupBox, QLabel, QComboBox, 
                               QLineEdit, QPushButton, QSlider, QTabWidget,
                               QTextEdit, QFileDialog, QMessageBox, QDoubleSpinBox,
                               QSpinBox, QCheckBox, QProgressBar, QSplitter,
                               QFormLayout, QGridLayout, QStackedWidget)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QPalette, QColor, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.signal as signal

from core.filter_designer import IIRFilterDesigner, FilterType
from core.validation_tools import FilterValidator
from exporters.cmsis_exporter import CMSISExporter
from utils.plotter import FilterPlotter
from utils.signal_generators import SignalGenerator, FilterTester

class MatplotlibCanvas(FigureCanvas):
    """Widget de Matplotlib integrado en Qt"""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)
        self.fig.tight_layout()

class WorkerThread(QThread):
    """Hilo de trabajo para operaciones que no deben bloquear la GUI"""
    progress_updated = Signal(int)
    task_completed = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.task_func(*self.args, **self.kwargs)
            self.task_completed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

class FilterDesignerGUI(QMainWindow):
    """Ventana principal de la herramienta de diseño de filtros IIR"""
    
    def __init__(self):
        super().__init__()
        self.filter_designer = None
        self.validator = None
        self.exporter = None
        self.plotter = None
        self.current_filter_params = {}
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("CMSIS-DSP IIR Filter Designer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter para paneles redimensionables
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Diseño de filtros
        left_panel = self.create_design_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho - Visualización y resultados
        right_panel = self.create_visualization_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 1000])
        main_layout.addWidget(splitter)
        
        # Barra de estado
        self.statusBar().showMessage("Listo para diseñar filtros IIR")
        
    def create_design_panel(self):
        """Crea el panel de diseño de filtros"""
        design_panel = QWidget()
        layout = QVBoxLayout(design_panel)
        
        # Grupo de configuración básica
        basic_group = QGroupBox("Configuración Básica")
        basic_layout = QFormLayout(basic_group)
        
        self.sample_rate_input = QDoubleSpinBox()
        self.sample_rate_input.setRange(100, 1000000)
        self.sample_rate_input.setValue(1000)
        self.sample_rate_input.setSuffix(" Hz")
        self.sample_rate_input.setDecimals(0)
        basic_layout.addRow("Frecuencia de Muestreo:", self.sample_rate_input)
        
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["butterworth", "chebyshev1", "chebyshev2", "elliptic", "bessel"])
        basic_layout.addRow("Tipo de Filtro:", self.filter_type_combo)
        
        self.band_type_combo = QComboBox()
        self.band_type_combo.addItems(["lowpass", "highpass", "bandpass", "bandstop"])
        basic_layout.addRow("Tipo de Banda:", self.band_type_combo)
        
        self.order_input = QSpinBox()
        self.order_input.setRange(1, 20)
        self.order_input.setValue(4)
        basic_layout.addRow("Orden del Filtro:", self.order_input)
        
        layout.addWidget(basic_group)
        
        # Widget apilado para parámetros de frecuencia
        self.freq_stacked_widget = QStackedWidget()
        
        # Widget para filtros lowpass/highpass (una frecuencia)
        self.single_freq_widget = QWidget()
        single_freq_layout = QFormLayout(self.single_freq_widget)
        self.cutoff_input = QDoubleSpinBox()
        self.cutoff_input.setRange(1, 100000)
        self.cutoff_input.setValue(100)
        self.cutoff_input.setSuffix(" Hz")
        self.cutoff_input.setDecimals(0)
        single_freq_layout.addRow("Frecuencia de Corte:", self.cutoff_input)
        self.freq_stacked_widget.addWidget(self.single_freq_widget)
        
        # Widget para filtros bandpass/bandstop (dos frecuencias)
        self.double_freq_widget = QWidget()
        double_freq_layout = QFormLayout(self.double_freq_widget)
        self.low_cutoff_input = QDoubleSpinBox()
        self.low_cutoff_input.setRange(1, 100000)
        self.low_cutoff_input.setValue(50)
        self.low_cutoff_input.setSuffix(" Hz")
        self.low_cutoff_input.setDecimals(0)
        double_freq_layout.addRow("Frecuencia Inferior:", self.low_cutoff_input)
        
        self.high_cutoff_input = QDoubleSpinBox()
        self.high_cutoff_input.setRange(1, 100000)
        self.high_cutoff_input.setValue(150)
        self.high_cutoff_input.setSuffix(" Hz")
        self.high_cutoff_input.setDecimals(0)
        double_freq_layout.addRow("Frecuencia Superior:", self.high_cutoff_input)
        self.freq_stacked_widget.addWidget(self.double_freq_widget)
        
        layout.addWidget(self.freq_stacked_widget)
        
        # Grupo de parámetros avanzados
        self.advanced_group = QGroupBox("Parámetros Avanzados")
        advanced_layout = QFormLayout(self.advanced_group)
        
        self.ripple_input = QDoubleSpinBox()
        self.ripple_input.setRange(0.1, 10.0)
        self.ripple_input.setValue(1.0)
        self.ripple_input.setSuffix(" dB")
        self.ripple_input.setDecimals(2)
        advanced_layout.addRow("Ripple en Banda Pasante:", self.ripple_input)
        
        self.attenuation_input = QDoubleSpinBox()
        self.attenuation_input.setRange(10, 100)
        self.attenuation_input.setValue(40.0)
        self.attenuation_input.setSuffix(" dB")
        self.attenuation_input.setDecimals(1)
        advanced_layout.addRow("Atenuación en Banda Stop:", self.attenuation_input)
        
        # Inicialmente ocultar parámetros avanzados
        self.advanced_group.setVisible(False)
        layout.addWidget(self.advanced_group)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.design_button = QPushButton("Diseñar Filtro")
        self.design_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(self.design_button)
        
        self.export_button = QPushButton("Exportar Coeficientes")
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)
        
        self.validate_button = QPushButton("Validar Filtro")
        self.validate_button.setEnabled(False)
        button_layout.addWidget(self.validate_button)
        
        layout.addLayout(button_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Información del filtro
        info_group = QGroupBox("Información del Filtro")
        info_layout = QVBoxLayout(info_group)
        
        self.filter_info_text = QTextEdit()
        self.filter_info_text.setMaximumHeight(150)
        self.filter_info_text.setReadOnly(True)
        info_layout.addWidget(self.filter_info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        return design_panel
    
    def create_visualization_panel(self):
        """Crea el panel de visualización"""
        viz_panel = QWidget()
        layout = QVBoxLayout(viz_panel)
        
        # Pestañas para diferentes visualizaciones
        self.tabs = QTabWidget()
        
        # Pestaña de respuesta en frecuencia
        freq_tab = QWidget()
        freq_layout = QVBoxLayout(freq_tab)
        self.freq_canvas = MatplotlibCanvas(self, width=8, height=6)
        freq_layout.addWidget(self.freq_canvas)
        self.tabs.addTab(freq_tab, "Respuesta en Frecuencia")
        
        # Pestaña de polos y ceros
        pole_zero_tab = QWidget()
        pole_zero_layout = QVBoxLayout(pole_zero_tab)
        self.pole_zero_canvas = MatplotlibCanvas(self, width=6, height=6)
        pole_zero_layout.addWidget(self.pole_zero_canvas)
        self.tabs.addTab(pole_zero_tab, "Polos y Ceros")
        
        # Pestaña de respuestas temporales
        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)
        self.time_canvas = MatplotlibCanvas(self, width=8, height=6)
        time_layout.addWidget(self.time_canvas)
        self.tabs.addTab(time_tab, "Respuestas Temporales")
        
        # Pestaña de validación
        validation_tab = QWidget()
        validation_layout = QVBoxLayout(validation_tab)
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        validation_layout.addWidget(self.validation_text)
        self.tabs.addTab(validation_tab, "Reporte de Validación")
        
        layout.addWidget(self.tabs)
        
        # Controles de visualización
        controls_layout = QHBoxLayout()
        
        self.refresh_plots_button = QPushButton("Actualizar Gráficas")
        self.refresh_plots_button.setEnabled(False)
        controls_layout.addWidget(self.refresh_plots_button)
        
        self.save_plots_button = QPushButton("Guardar Gráficas")
        self.save_plots_button.setEnabled(False)
        controls_layout.addWidget(self.save_plots_button)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        return viz_panel
    
    def update_band_parameters(self, band_type):
        """Actualiza los parámetros de frecuencia según el tipo de banda"""
        # Mostrar el widget apropiado
        if band_type in ['bandpass', 'bandstop']:
            self.freq_stacked_widget.setCurrentWidget(self.double_freq_widget)
        else:
            self.freq_stacked_widget.setCurrentWidget(self.single_freq_widget)
        
        # Actualizar parámetros avanzados según el tipo de filtro
        filter_type = self.filter_type_combo.currentText()
        self.update_advanced_parameters(filter_type)
    
    def update_advanced_parameters(self, filter_type):
        """Actualiza la visibilidad de parámetros avanzados"""
        show_advanced = filter_type in ['chebyshev1', 'chebyshev2', 'elliptic']
        self.advanced_group.setVisible(show_advanced)
        
        # Mostrar/ocultar parámetros específicos
        if filter_type in ['chebyshev2', 'elliptic']:
            self.attenuation_input.setVisible(True)
        else:
            self.attenuation_input.setVisible(False)
    
    def setup_connections(self):
        """Configura las conexiones de señales y slots"""
        # Conexiones de cambios de parámetros
        self.filter_type_combo.currentTextChanged.connect(self.update_advanced_parameters)
        self.band_type_combo.currentTextChanged.connect(self.update_band_parameters)
        
        # Conexiones de botones
        self.design_button.clicked.connect(self.design_filter)
        self.export_button.clicked.connect(self.export_coefficients)
        self.validate_button.clicked.connect(self.validate_filter)
        self.refresh_plots_button.clicked.connect(self.update_plots)
        self.save_plots_button.clicked.connect(self.save_plots)
        
        # Conectar señal de cambio de pestaña
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Inicializar visibilidad
        self.update_band_parameters(self.band_type_combo.currentText())
        self.update_advanced_parameters(self.filter_type_combo.currentText())
    
    def design_filter(self):
        """Diseña el filtro con los parámetros especificados"""
        try:
            # Recoger parámetros
            sample_rate = self.sample_rate_input.value()
            filter_type_str = self.filter_type_combo.currentText()
            band_type = self.band_type_combo.currentText()
            order = self.order_input.value()
            
            # Mapear tipo de filtro
            filter_type_map = {
                "butterworth": FilterType.BUTTERWORTH,
                "chebyshev1": FilterType.CHEBYSHEV1,
                "chebyshev2": FilterType.CHEBYSHEV2,
                "elliptic": FilterType.ELLIPTIC,
                "bessel": FilterType.BESSEL
            }
            filter_type = filter_type_map[filter_type_str]
            
            # Crear diseñador de filtros
            self.filter_designer = IIRFilterDesigner(sample_rate)
            
            # Diseñar según el tipo de banda
            if band_type in ['bandpass', 'bandstop']:
                low_cutoff = self.low_cutoff_input.value()
                high_cutoff = self.high_cutoff_input.value()
                
                if band_type == 'bandpass':
                    self.filter_designer.design_bandpass(
                        low_cutoff, high_cutoff, order, filter_type,
                        self.ripple_input.value(), self.attenuation_input.value()
                    )
                else:  # bandstop
                    self.filter_designer.design_bandstop(
                        low_cutoff, high_cutoff, order, filter_type,
                        self.ripple_input.value(), self.attenuation_input.value()
                    )
            else:
                cutoff = self.cutoff_input.value()
                
                if band_type == 'lowpass':
                    self.filter_designer.design_lowpass(
                        cutoff, order, filter_type,
                        self.ripple_input.value(), self.attenuation_input.value()
                    )
                else:  # highpass
                    self.filter_designer.design_highpass(
                        cutoff, order, filter_type,
                        self.ripple_input.value(), self.attenuation_input.value()
                    )
            
            # Actualizar interfaz
            self.export_button.setEnabled(True)
            self.validate_button.setEnabled(True)
            self.refresh_plots_button.setEnabled(True)
            self.save_plots_button.setEnabled(True)
            
            # Mostrar información del filtro
            self.update_filter_info()
            
            # Actualizar gráficas
            self.update_plots()
            
            self.statusBar().showMessage("Filtro diseñado exitosamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al diseñar el filtro: {str(e)}")
            self.statusBar().showMessage("Error en el diseño del filtro")
    
    def update_filter_info(self):
        """Actualiza la información del filtro diseñado"""
        if not self.filter_designer or not hasattr(self.filter_designer, 'filter_info'):
            return
        
        info = self.filter_designer.filter_info
        info_text = f"""INFORMACIÓN DEL FILTRO DISEÑADO:

Tipo: {info['filter_type'].value} {info['band_type']}
Orden: {info['order']}
Secciones: {info['num_sections']}
Frecuencia de Muestreo: {info['sample_rate']} Hz
Frecuencia(s) de Corte: {info['cutoff_freq']}
Fecha de Diseño: {info['design_date']}

"""
        
        # Verificar estabilidad
        stable, _, _, _ = self.filter_designer.check_stability()
        stability_status = "ESTABLE" if stable else "INESTABLE - REVISAR DISEÑO"
        info_text += f"Estabilidad: {stability_status}"
        
        self.filter_info_text.setPlainText(info_text)
    
    def update_plots(self):
        """Actualiza todas las gráficas"""
        if not self.filter_designer or self.filter_designer.sos_coeffs is None:
            return
        
        try:
            # Crear plotter si no existe
            if not self.plotter:
                self.plotter = FilterPlotter(self.filter_designer)
            
            # Actualizar gráfica según la pestaña activa
            current_tab = self.tabs.currentIndex()
            
            if current_tab == 0:  # Respuesta en frecuencia
                self.plot_frequency_response()
            elif current_tab == 1:  # Polos y ceros
                self.plot_pole_zero()
            elif current_tab == 2:  # Respuestas temporales
                self.plot_time_responses()
                
        except Exception as e:
            QMessageBox.warning(self, "Advertencia", f"Error al actualizar gráficas: {str(e)}")
    
    def plot_frequency_response(self):
        """Grafica la respuesta en frecuencia"""
        self.freq_canvas.axes.clear()
        
        w, h = self.filter_designer.get_filter_response()
        magnitude = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
        
        self.freq_canvas.axes.semilogx(w, magnitude)
        self.freq_canvas.axes.set_title('Respuesta en Frecuencia del Filtro')
        self.freq_canvas.axes.set_ylabel('Magnitud [dB]')
        self.freq_canvas.axes.set_xlabel('Frecuencia [Hz]')
        self.freq_canvas.axes.grid(True)
        self.freq_canvas.axes.set_xlim([w[1], w[-1]])
        
        self.freq_canvas.draw()
    
    def plot_pole_zero(self):
        """Grafica el diagrama de polos y ceros"""
        self.pole_zero_canvas.axes.clear()
        
        try:
            # Usar el método que devuelve tupla para compatibilidad
            if hasattr(self.filter_designer, 'check_stability'):
                stable, z, p, k = self.filter_designer.check_stability()
            else:
                # Fallback: usar el validador
                if not self.validator:
                    self.validator = FilterValidator(self.filter_designer)
                stable, z, p, k = self.validator.check_stability_tuple()
            
            # Dibujar círculo unitario
            unit_circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
            self.pole_zero_canvas.axes.add_patch(unit_circle)
            
            # Plot polos y ceros
            if len(z) > 0:
                self.pole_zero_canvas.axes.scatter(np.real(z), np.imag(z), marker='o', 
                                                facecolors='none', edgecolors='b', s=80, label='Ceros')
            if len(p) > 0:
                self.pole_zero_canvas.axes.scatter(np.real(p), np.imag(p), marker='x', 
                                                color='r', s=80, label='Polos')
            
            self.pole_zero_canvas.axes.set_title('Diagrama de Polos y Ceros')
            self.pole_zero_canvas.axes.set_xlabel('Parte Real')
            self.pole_zero_canvas.axes.set_ylabel('Parte Imaginaria')
            if len(z) > 0 or len(p) > 0:
                self.pole_zero_canvas.axes.legend()
            self.pole_zero_canvas.axes.grid(True)
            self.pole_zero_canvas.axes.axis('equal')
            self.pole_zero_canvas.axes.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            self.pole_zero_canvas.axes.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Verificar estabilidad
            stability_text = "Estable" if stable else "Inestable"
            color = "green" if stable else "red"
            self.pole_zero_canvas.axes.text(0.05, 0.95, f'Filtro: {stability_text}', 
                                        transform=self.pole_zero_canvas.axes.transAxes,
                                        bbox=dict(boxstyle="round", facecolor=color, alpha=0.7))
            
            self.pole_zero_canvas.draw()
            
        except Exception as e:
            self.pole_zero_canvas.axes.text(0.5, 0.5, f'Error al graficar polos/ceros:\n{str(e)}', 
                                        ha='center', va='center', transform=self.pole_zero_canvas.axes.transAxes,
                                        fontsize=10, color='red')
            self.pole_zero_canvas.draw()

    def plot_time_responses(self):
        """Grafica las respuestas al impulso y al escalón"""
        self.time_canvas.axes.clear()
        
        try:
            # Respuesta al impulso
            t_impulse = np.arange(100)
            impulse = np.zeros(100)
            impulse[0] = 1.0
            impulse_response = signal.sosfilt(self.filter_designer.sos_coeffs, impulse)
            
            # Respuesta al escalón
            t_step = np.arange(100)
            step = np.ones(100)
            step_response = signal.sosfilt(self.filter_designer.sos_coeffs, step)
            
            # Graficar ambas respuestas
            self.time_canvas.axes.plot(t_impulse, impulse_response, 'b-', label='Respuesta al Impulso')
            self.time_canvas.axes.plot(t_step, step_response, 'r-', label='Respuesta al Escalón')
            self.time_canvas.axes.set_title('Respuestas Temporales')
            self.time_canvas.axes.set_xlabel('Muestras')
            self.time_canvas.axes.set_ylabel('Amplitud')
            self.time_canvas.axes.legend()
            self.time_canvas.axes.grid(True)
            
            self.time_canvas.draw()
        except Exception as e:
            self.time_canvas.axes.text(0.5, 0.5, 'Error al calcular respuestas temporales', 
                                     ha='center', va='center', transform=self.time_canvas.axes.transAxes)
            self.time_canvas.draw()
    
    def validate_filter(self):
        """Ejecuta la validación completa del filtro"""
        if not self.filter_designer:
            return
        
        try:
            if not self.validator:
                self.validator = FilterValidator(self.filter_designer)
            
            # Ejecutar validación en hilo separado
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Progress bar indeterminada
            
            self.worker = WorkerThread(self.validator.generate_validation_report)
            self.worker.task_completed.connect(self.on_validation_complete)
            self.worker.error_occurred.connect(self.on_validation_error)
            self.worker.start()
            
            self.statusBar().showMessage("Validando filtro...")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en validación: {str(e)}")
    
    def on_validation_complete(self, report):
        """Maneja la finalización de la validación"""
        self.progress_bar.setVisible(False)
        self.validation_text.setPlainText(report)
        self.tabs.setCurrentIndex(3)  # Mostrar pestaña de validación
        self.statusBar().showMessage("Validación completada")
    
    def on_validation_error(self, error_msg):
        """Maneja errores en la validación"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error de Validación", error_msg)
        self.statusBar().showMessage("Error en validación")
    
    def export_coefficients(self):
        """Exporta los coeficientes a archivo .h"""
        if not self.filter_designer:
            return
        
        try:
            # Diálogo para seleccionar archivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Coeficientes CMSIS-DSP", 
                "iir_filter_coeffs.h", "Header Files (*.h)"
            )
            
            if file_path:
                if not self.exporter:
                    self.exporter = CMSISExporter(self.filter_designer)
                
                # Exportar en formato DF2T (por defecto)
                self.exporter.export_to_cmsis_header(file_path, "DF2T", "float32")
                
                QMessageBox.information(self, "Éxito", 
                                      f"Coeficientes exportados a:\n{file_path}")
                self.statusBar().showMessage("Coeficientes exportados exitosamente")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
    
    def save_plots(self):
        """Guarda todas las gráficas a archivo"""
        if not self.plotter:
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Gráficas de Validación", 
                "filter_validation.png", "Image Files (*.png *.jpg *.pdf)"
            )
            
            if file_path:
                self.plotter.generate_comprehensive_report(file_path)
                QMessageBox.information(self, "Éxito", f"Gráficas guardadas en:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar gráficas: {str(e)}")
    
    def on_tab_changed(self, index):
        """Maneja el cambio de pestaña"""
        if self.filter_designer and self.filter_designer.sos_coeffs is not None:
            self.update_plots()

def main():
    """Función principal para ejecutar la GUI"""
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = FilterDesignerGUI()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()