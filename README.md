# CMSIS-DSP IIR Filter Designer

Una herramienta profesional para el diseño, análisis y exportación de filtros IIR compatibles con **CMSIS-DSP** de ARM. Diseñada específicamente para desarrolladores de sistemas embebidos que trabajan con microcontroladores ARM Cortex-M.
<img width="1408" height="938" alt="image" src="https://github.com/user-attachments/assets/959ac61b-0075-4c86-b3c7-7e9e740cdae8" />
<img width="1408" height="938" alt="image" src="https://github.com/user-attachments/assets/c9f0c6c9-14a6-4b93-a9da-16069b5a5b6f" />
<img width="1408" height="938" alt="image" src="https://github.com/user-attachments/assets/4b7ad8b9-844d-4a15-9aa4-9a922245005b" />

## CLI
<img width="510" height="293" alt="image" src="https://github.com/user-attachments/assets/29018e67-df10-4416-a874-e1092a58b63e" />

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

### Uso Avanzado con CLI

```bash
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

```

## 🏗️ Arquitectura del Proyecto

```bash
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
│   ├── plotter.py           # Visualización
│   └── signal_generators.py # Señales de prueba
├── tests/                   # Pruebas unitarias
│   └── test_filter_design.py
├── templates/               # Plantillas
│   └── cmsis_header_template.h
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias
└── README.md                # Documentación
```

## 🔬 Características Técnicas

### Algoritmos Implementados

- scipy.signal.iirfilter con SOS

- Verificación de polos en el círculo unitario

- Conversión a formatos CMSIS-DSP (DF1/DF2T)

- Manejo robusto para fixed-point

### Formatos de Exportación Soportados

| Formato                   | Descripción        | Uso Típico                  |
| ------------------------- | ------------------ | --------------------------- |
| Direct Form II Transposed | 5 coef/ sección    | Procesamiento general       |
| Direct Form I             | 5 coef + 4 estados | Mayor estabilidad           |
| float32                   | Precisión simple   | Cortex-M4F/M7 con FPU       |
| Q15                       | Fixed-point 16-bit | Cortex-M0/M3 sin FPU        |
| Q31                       | Fixed-point 32-bit | Mayor precisión fixed-point |

### Validaciones

✅ Estabilidad
✅ Causalidad
✅ Sensibilidad Numérica
✅ Cumplimiento de Especificaciones

## 🧪 Ejemplos Prácticos

#### Ejemplo 1: Filtro Anti-aliasing

```bash
python main.py --type lowpass --freq 20000 --order 4 --sample-rate 44100 --plot
```

#### Ejemplo 2: Filtro de Banda para Instrumentación

```bash
python main.py --type bandpass --freq 10 1000 --order 6 --filter-type bessel --plot
```

#### Ejemplo 3: Filtro para Señales Biomédicas

```bash
python main.py --type bandpass --freq 0.5 40 --order 5 --filter-type elliptic --ripple 0.1 --attenuation 80
```

## 📊 Resultados y Gráficas

- Respuesta en Frecuencia

- Polos y Ceros

- Respuesta al Impulso

- Respuesta al Escalón

## 🔧 Desarrollo y Contribución

### Ejemplo Programático

```bash
from core.filter_designer import IIRFilterDesigner, FilterType
from exporters.cmsis_exporter import CMSISExporter

designer = IIRFilterDesigner(sample_rate=1000)
designer.design_lowpass(cutoff_freq=100, order=4, filter_type=FilterType.BUTTERWORTH)

exporter = CMSISExporter(designer)
exporter.export_to_cmsis_header("filter.h", "DF2T", "float32")
```

### Ejecución de Pruebas

```bash
python -m pytest tests/
python tests/test_filter_design.py
python -m pytest tests/ --cov=core --cov=exporters --cov-report=html
```

### Guía de Contribución

1. Fork

2. Crea rama feature/AmazingFeature

3. Commit

4. Push

5. Pull Request

### 📈 Rendimiento y Optimizaciones

- <10 ms diseño de filtro (orden 4)

- <5 ms análisis de estabilidad

- <100 ms generación de gráficas

- <5 ms exportación

### 🌐 Compatibilidad

- Windows: 10, 11

- Linux: Ubuntu 18.04+, Debian 10+, CentOS 7+

- macOS: 10.15+

- Python: 3.8–3.11 (3.8 recomendado)

### Dependencias principales: NumPy ≥1.21, SciPy ≥1.7, Matplotlib ≥3.5, PySide6 ≥6.5

🐛 Solución de Problemas

Error: No module named 'PySide6'
👉 Instalar PySide6 o usar CLI

Error: Filter is unstable
👉 Reducir orden, aumentar frecuencia de muestreo, usar Bessel

Problemas de rendimiento:
👉 Usar órdenes más bajos, evitar --plot

### Debug Mode:

```bash
python main.py --type lowpass --freq 100 --order 4 --verbose
```

## 🙋‍♂️ Soporte y Contacto

Reportar Issues: GitHub Issues

Discusiones: GitHub Discussions

Email: jeffryquino@gmail.com

<div align="center">

⭐ ¿Te gusta este proyecto? ¡Dale una estrella en GitHub para apoyar el desarrollo!

📅 Última actualización: Enero 2025

<b>Quino B. Jeffry</b>
</div> ```

