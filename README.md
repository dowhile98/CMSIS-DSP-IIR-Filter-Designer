# CMSIS-DSP IIR Filter Designer

Una herramienta profesional para el diseño, análisis y exportación de filtros IIR compatibles con **CMSIS-DSP** de ARM. Diseñada específicamente para desarrolladores de sistemas embebidos que trabajan con microcontroladores ARM Cortex-M.

---

## 🚀 Características Principales

### 🎯 Diseño de Filtros Avanzado
- **Tipos de Filtro:** Butterworth, Chebyshev (Tipos I y II), Elíptico, Bessel  
- **Configuraciones:** Paso bajo, paso alto, paso banda, elimina banda  
- **Parámetros Avanzados:** Control de ripple, atenuación, orden del filtro  
- **Validación en Tiempo Real:** Análisis de estabilidad y respuesta en frecuencia  

### 💻 Interfaces Múltiples
- **Interfaz Gráfica (GUI):** Diseño visual e interactivo con PySide6  
- **Línea de Comandos (CLI):** Automatización y scripts por lotes  
- **Integración Perfecta:** Mismo motor de procesamiento para ambas interfaces  

### 📊 Análisis y Visualización
- Respuesta en Frecuencia: Magnitud y fase  
- Diagrama de Polos y Ceros: Análisis de estabilidad  
- Respuestas Temporales: Impulso y escalón  
- Validación Completa: Reportes detallados de calidad del filtro  

### 🔧 Exportación CMSIS-DSP
- **Formatos Soportados:** Direct Form I y Direct Form II Transposed  
- **Tipos de Datos:** float32, Q15, Q31  
- **Archivos Listos para Usar:** Headers `.h` compatibles con ARM CMSIS-DSP  
- **Código de Ejemplo:** Plantillas de inicialización y uso  

---

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior  
- pip (gestor de paquetes de Python)  

### Instalación de Dependencias
```bash
# Instalar dependencias básicas
pip install numpy scipy matplotlib

# Para usar la interfaz gráfica (opcional)
pip install PySide6

# O instalar todas las dependencias desde requirements.txt
pip install -r requirements.txt

# Clonar el repositorio
git clone https://github.com/tu-usuario/cmsis-iir-designer.git
cd cmsis-iir-designer

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la herramienta
python main.py --help

```
## 🎮 Uso Rápido
### Modo Interfaz Gráfica (GUI)

```bash
# Lanzar la interfaz gráfica
python main.py --gui

# Con parámetros iniciales específicos
python main.py --gui --sample-rate 44100 --filter-type elliptic --theme dark

```
### Modo Línea de Comandos (CLI)
```bash
# Filtro paso bajo básico
python main.py --type lowpass --freq 1000 --order 4 --sample-rate 44100

# Filtro paso banda con gráficas
python main.py --type bandpass --freq 500 2000 --order 6 --filter-type chebyshev1 --plot

# Exportación avanzada
python main.py --type highpass --freq 300 --order 5 --format both --data-type q15 --output my_filter.h


```

## 📖 Guía de Uso Detallada

### Diseño de Filtros con GUI

- Configuración Básica: frecuencia de muestreo, tipo de filtro y orden

- Parámetros de Frecuencia:

    - Lowpass/Highpass: una frecuencia de corte

    - Bandpass/Bandstop: frecuencias inferior y superior

- Parámetros Avanzados: ripple y atenuación

- Validación y Exportación: gráficas, estabilidad y headers listos
