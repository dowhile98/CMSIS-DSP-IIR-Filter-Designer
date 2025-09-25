CMSIS-DSP IIR Filter Designer
Una herramienta profesional para el diseño, análisis y exportación de filtros IIR compatibles con CMSIS-DSP de ARM. Diseñada específicamente para desarrolladores de sistemas embebidos que trabajan con microcontroladores ARM Cortex-M.
🚀 Características Principales
🎯 Diseño de Filtros Avanzado
Tipos de Filtro: Butterworth, Chebyshev (Tipos I y II), Elíptico, Bessel
Configuraciones: Paso bajo, paso alto, paso banda, elimina banda
Parámetros Avanzados: Control de ripple, atenuación, orden del filtro
Validación en Tiempo Real: Análisis de estabilidad y respuesta en frecuencia
💻 Interfaces Múltiples
Interfaz Gráfica (GUI): Diseño visual e interactivo con PySide6
Línea de Comandos (CLI): Automatización y scripts por lotes
Integración Perfecta: Mismo motor de procesamiento para ambas interfaces
📊 Análisis y Visualización
Respuesta en Frecuencia: Magnitud y fase
Diagrama de Polos y Ceros: Análisis de estabilidad
Respuestas Temporales: Impulso y escalón
Validación Completa: Reportes detallados de calidad del filtro
🔧 Exportación CMSIS-DSP
Formatos Soportados: Direct Form I y Direct Form II Transposed
Tipos de Datos: float32, Q15, Q31
Archivos Listos para Usar: Headers .h compatibles con ARM CMSIS-DSP
Código de Ejemplo: Plantillas de inicialización y uso
📦 Instalación
Requisitos Previos
Python 3.8 o superior
pip (gestor de paquetes de Python)
Instalación de Dependencias
# Instalar dependencias básicas
pip install numpy scipy matplotlib

# Para usar la interfaz gráfica (opcional)
pip install PySide6

# O instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt


Instalación Rápida
# Clonar el repositorio
git clone [https://github.com/tu-usuario/cmsis-iir-designer.git](https://github.com/tu-usuario/cmsis-iir-designer.git)
cd cmsis-iir-designer

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la herramienta
python main.py --help


🎮 Uso Rápido
Modo Interfaz Gráfica (GUI)
# Lanzar la interfaz gráfica
python main.py --gui

# Con parámetros iniciales específicos
python main.py --gui --sample-rate 44100 --filter-type elliptic --theme dark


Modo Línea de Comandos (CLI)
# Filtro paso bajo básico
python main.py --type lowpass --freq 1000 --order 4 --sample-rate 44100

# Filtro paso banda con gráficas
python main.py --type bandpass --freq 500 2000 --order 6 --filter-type chebyshev1 --plot

# Exportación avanzada
python main.py --type highpass --freq 300 --order 5 --format both --data-type q15 --output my_filter.h


📖 Guía de Uso Detallada
Diseño de Filtros con GUI
Configuración Básica:
Establece la frecuencia de muestreo
Selecciona el tipo de filtro y banda
Define el orden del filtro
Parámetros de Frecuencia:
Lowpass/Highpass: Una frecuencia de corte
Bandpass/Bandstop: Frecuencias inferior y superior
Parámetros Avanzados:
Ripple: Para Chebyshev y Elíptico (0.1-10 dB)
Atenuación: Para Chebyshev2 y Elíptico (10-100 dB)
Validación y Exportación:
Visualiza las gráficas de respuesta
Verifica la estabilidad del filtro
Exporta coeficientes para CMSIS-DSP
Uso Avanzado con CLI
# Ejemplo completo con validación
python main.py \
    --type bandpass \
    --freq 100 1000 \
    --order 8 \
    --filter-type elliptic \
    --ripple 0.5 \
    --attenuation 60 \
    --sample-rate 48000 \
    --format both \
    --data-type float32 \
    --plot \
    --verbose


Integración con CMSIS-DSP
Los archivos exportados son compatibles con la API estándar de CMSIS-DSP:
// Ejemplo de uso en firmware ARM
#include "arm_math.h"
#include "iir_filter_coeffs.h"

// Buffer de estado
static float32_t iirState[IIR_STATE_SIZE];

// Instancia del filtro
arm_biquad_casd_df2T_instance_f32 iirFilter;

void init_filter(void) {
    arm_biquad_cascade_df2T_init_f32(
        &iirFilter, 
        IIR_NUM_SECTIONS, 
        (float32_t*)iirCoeffs_DF2T, 
        iirState
    );
}

void process_audio(float32_t *input, float32_t *output, uint32_t blockSize) {
    arm_biquad_cascade_df2T_f32(&iirFilter, input, output, blockSize);
}


🏗️ Arquitectura del Proyecto
cmsis_iir_designer/
├── core/                    # Núcleo de procesamiento
│   ├── filter_designer.py   # Diseño de filtros IIR
│   ├── validation_tools.py  # Análisis y validación
│   └── coefficient_exporter.py # Gestión de coeficientes
├── ui/                      # Interfaces de usuario
│   ├── cli_interface.py     # Línea de comandos
│   └── gui_interface.py     # Interfaz gráfica
├── exporters/               # Exportadores
│   ├── cmsis_exporter.py    # Formato CMSIS-DSP
│   └── formats.py           # Utilidades de formato
├── utils/                   # Utilidades
│   ├── plotter.py          # Visualización
│   └── signal_generators.py # Señales de prueba
├── tests/                   # Pruebas unitarias
│   └── test_filter_design.py
├── templates/               # Plantillas
│   └── cmsis_header_template.h
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias
└── README.md               # Documentación


🔬 Características Técnicas
Algoritmos Implementados
Diseño de Filtros: Usa scipy.signal.iirfilter con método de secciones de segundo orden (SOS)
Análisis de Estabilidad: Verificación de polos dentro del círculo unitario
Transformación de Coeficientes: Conversión a formatos CMSIS-DSP (DF1/DF2T)
Normalización: Manejo numérico robusto para fixed-point
Formatos de Exportación Soportados
Formato
Descripción
Uso Típico
Direct Form II Transposed
5 coeficientes por sección
Procesamiento general
Direct Form I
5 coeficientes + 4 estados
Mayor estabilidad numérica
float32
Precisión simple
Cortex-M4F/M7 con FPU
Q15
Fixed-point 16-bit
Cortex-M0/M3 sin FPU
Q31
Fixed-point 32-bit
Mayor precisión fixed-point

Validaciones Implementadas
✅ Estabilidad: Análisis de ubicación de polos
✅ Causalidad: Verificación de realizabilidad física
✅ Sensibilidad Numérica: Análisis de robustez
✅ Cumplimiento de Especificaciones: Verificación vs. diseño
🧪 Ejemplos Prácticos
Ejemplo 1: Filtro Anti-aliasing
# Filtro Butterworth para audio de 44.1 kHz
python main.py --type lowpass --freq 20000 --order 4 --sample-rate 44100 --plot


Ejemplo 2: Filtro de Banda para Instrumentación
# Filtro paso banda para medición de vibraciones
python main.py --type bandpass --freq 10 1000 --order 6 --filter-type bessel --plot


Ejemplo 3: Filtro para Procesamiento de Señales Biomédicas
# Filtro elíptico para ECG
python main.py --type bandpass --freq 0.5 40 --order 5 --filter-type elliptic --ripple 0.1 --attenuation 80


📊 Resultados y Gráficas
La herramienta genera múltiples gráficas de análisis:
Respuesta en Frecuencia: Magnitud (dB) vs Frecuencia (Hz)
Diagrama de Polos y Ceros: Análisis de estabilidad
Respuesta al Impulso: Comportamiento temporal
Respuesta al Escalón: Respuesta transitoria
🔧 Desarrollo y Contribución
Estructura del Código
El proyecto sigue una arquitectura modular:
# Ejemplo de uso programático
from core.filter_designer import IIRFilterDesigner, FilterType
from exporters.cmsis_exporter import CMSISExporter

# Diseñar filtro
designer = IIRFilterDesigner(sample_rate=1000)
designer.design_lowpass(cutoff_freq=100, order=4, filter_type=FilterType.BUTTERWORTH)

# Exportar coeficientes
exporter = CMSISExporter(designer)
exporter.export_to_cmsis_header("filter.h", "DF2T", "float32")


Ejecución de Pruebas
# Ejecutar todas las pruebas
python -m pytest tests/

# Pruebas específicas
python tests/test_filter_design.py

# Con cobertura de código
python -m pytest tests/ --cov=core --cov=exporters --cov-report=html


Guía de Contribución
Fork el proyecto
Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
Commit tus cambios (git commit -m 'Add some AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)
Abre un Pull Request
📈 Rendimiento y Optimizaciones
Optimizaciones Implementadas
Cálculo Vectorizado: Uso de NumPy para operaciones eficientes
Manejo de Memoria: Reutilización de buffers y arrays
Procesamiento por Lotes: Optimizado para diseño múltiple
Validación Incremental: Solo recalcula lo necesario
Benchmarks
Operación
Tiempo Promedio
Diseño de filtro (orden 4)
< 10 ms
Análisis de estabilidad
< 5 ms
Generación de gráficas
< 100 ms
Exportación de coeficientes
< 5 ms

🌐 Compatibilidad
Plataformas Soportadas
Windows: 10, 11 (testado)
Linux: Ubuntu 18.04+, Debian 10+, CentOS 7+
macOS: 10.15+ (Catalina y superiores)
Versiones de Python
Python 3.8 (recomendado)
Python 3.9, 3.10, 3.11 (soportados)
Python 3.7 (soporte limitado)
Dependencias Principales
Paquete
Versión
Propósito
NumPy
≥1.21.0
Cálculos numéricos
SciPy
≥1.7.0
Procesamiento de señales
Matplotlib
≥3.5.0
Visualización
PySide6
≥6.5.0
Interfaz gráfica (opcional)

🐛 Solución de Problemas
Problemas Comunes
Error: "No module named 'PySide6'"
# Solución: Instalar PySide6 o usar modo CLI
pip install PySide6
# o
python main.py --type lowpass --freq 100 --order 4  # Sin --gui


Error: "Filter is unstable"
Reduce el orden del filtro
Aumenta la frecuencia de muestreo
Considera usar filtro Bessel para fase lineal
Problemas de Rendimiento
Usa órdenes de filtro más bajos para diseños complejos
En CLI, evita --plot si solo necesitas los coeficientes
Debug Mode
# Ejecutar con información de debug
python main.py --type lowpass --freq 100 --order 4 --verbose

# Modo interactivo para desarrollo
python -i main.py --type lowpass --freq 100 --order 4


📄 Licencia
Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.
🙋‍♂️ Soporte y Contacto
Reportar Issues: GitHub Issues
Discusiones: GitHub Discussions
Email: tu-email@dominio.com
🤝 Contribuyentes
Tu Nombre - Desarrollo principal
📚 Recursos Adicionales
Documentación Relacionada
ARM CMSIS-DSP Documentation
SciPy Signal Processing
PySide6 Documentation
Tutoriales y Ejemplos
Guía de Diseño de Filtros Digitales
Integración con STM32 CubeIDE
Procesamiento en Tiempo Real
Publicaciones Técnicas
Optimización de Filtros IIR para Embedded
Comparativa de Formatos CMSIS-DSP
¿Te gusta este proyecto? ⭐ Dale una estrella en GitHub para apoyar el desarrollo!
<div align="center">
¿Necesitas ayuda personalizada? ¡Abre un issue o contáctame directamente!



Última actualización: Enero 2025
</div>
