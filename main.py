#!/usr/bin/env python3
"""
Herramienta de Diseño de Filtros IIR para CMSIS-DSP
Autor: Tu Nombre
Fecha: 2024
"""

import sys
import os
import argparse

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_arg_parser():
    """Configura el parser de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Herramienta de Diseño de Filtros IIR para CMSIS-DSP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo CLI - Filtro paso bajo Butterworth
  python main.py --type lowpass --freq 100 --order 4 --format DF2T --sample-rate 1000 --plot

  # Modo GUI - Interfaz gráfica
  python main.py --gui

Modos de operación:
  --gui    Usar interfaz gráfica (GUI)
  Sin --gui: Usar interfaz de línea de comandos (CLI)

Para ayuda detallada:
  python main.py --help
        """
    )
    
    # Parámetros básicos del filtro
    filter_group = parser.add_argument_group('Parámetros del Filtro')
    filter_group.add_argument('--type', 
                            choices=['lowpass', 'highpass', 'bandpass', 'bandstop'],
                            help='Tipo de filtro: lowpass, highpass, bandpass, bandstop')
    
    filter_group.add_argument('--freq', nargs='+', type=float,
                            help='Frecuencia(s) de corte (1 para low/high, 2 para band)')
    
    filter_group.add_argument('--order', type=int,
                            help='Orden del filtro (entero positivo)')
    
    # Parámetros opcionales del filtro
    filter_group.add_argument('--sample-rate', type=float, default=1000.0,
                            help='Frecuencia de muestreo en Hz (por defecto: 1000)')
    
    filter_group.add_argument('--filter-type', 
                            choices=['butterworth', 'chebyshev1', 'chebyshev2', 'elliptic', 'bessel'],
                            default='butterworth',
                            help='Tipo de aproximación del filtro (por defecto: butterworth)')
    
    filter_group.add_argument('--ripple', type=float, default=1.0,
                            help='Ripple en banda pasante (dB) para Chebyshev/Elliptic (por defecto: 1.0)')
    
    filter_group.add_argument('--attenuation', type=float, default=40.0,
                            help='Atenuación en banda stop (dB) para Chebyshev2/Elliptic (por defecto: 40.0)')
    
    # Opciones de exportación
    export_group = parser.add_argument_group('Opciones de Exportación')
    export_group.add_argument('--format', 
                            choices=['DF1', 'DF2T', 'both'], default='DF2T',
                            help='Formato de exportación CMSIS-DSP (por defecto: DF2T)')
    
    export_group.add_argument('--output', '-o', type=str, default='iir_filter_coeffs.h',
                            help='Nombre del archivo de salida (por defecto: iir_filter_coeffs.h)')
    
    export_group.add_argument('--data-type', 
                            choices=['float32', 'q31', 'q15'], default='float32',
                            help='Tipo de datos para CMSIS-DSP (por defecto: float32)')
    
    # Opciones de visualización
    viz_group = parser.add_argument_group('Opciones de Visualización')
    viz_group.add_argument('--plot', action='store_true',
                          help='Generar gráficas de validación')
    
    viz_group.add_argument('--plot-file', type=str, default='filter_validation.png',
                          help='Nombre del archivo para las gráficas (por defecto: filter_validation.png)')
    
    # Modo de operación
    mode_group = parser.add_argument_group('Modo de Operación')
    mode_group.add_argument('--gui', action='store_true',
                          help='Usar interfaz gráfica (GUI) en lugar de línea de comandos (CLI)')
    
    mode_group.add_argument('--verbose', '-v', action='store_true',
                          help='Mostrar información detallada del proceso')
    
    # Parámetros específicos de GUI
    gui_group = parser.add_argument_group('Parámetros de GUI (solo con --gui)')
    gui_group.add_argument('--theme', choices=['light', 'dark', 'system'], default='system',
                          help='Tema de la interfaz (por defecto: system)')
    
    gui_group.add_argument('--window-size', type=str, default='1400x900',
                          help='Tamaño de ventana inicial (ancho x alto) (por defecto: 1400x900)')
    
    gui_group.add_argument('--fullscreen', action='store_true',
                          help='Iniciar en modo pantalla completa')
    
    return parser

def validate_cli_args(args):
    """Valida los argumentos para el modo CLI"""
    if args.gui:
        return True, "Modo GUI seleccionado"
    
    # Validaciones para modo CLI
    if not args.type:
        return False, "El parámetro --type es obligatorio en modo CLI"
    
    if not args.freq:
        return False, "El parámetro --freq es obligatorio en modo CLI"
    
    if not args.order:
        return False, "El parámetro --order es obligatorio en modo CLI"
    
    try:
        # Validar tipo de filtro y número de frecuencias
        if args.type in ['lowpass', 'highpass'] and len(args.freq) != 1:
            raise ValueError(f"{args.type} requiere exactamente una frecuencia")
        
        if args.type in ['bandpass', 'bandstop'] and len(args.freq) != 2:
            raise ValueError(f"{args.type} requiere dos frecuencias")
        
        # Validar orden
        if args.order <= 0:
            raise ValueError("El orden debe ser un número positivo")
        
        # Validar frecuencia de muestreo
        if args.sample_rate <= 0:
            raise ValueError("La frecuencia de muestreo debe ser positiva")
        
        # Validar frecuencias de corte
        if any(freq <= 0 for freq in args.freq):
            raise ValueError("Las frecuencias deben ser positivas")
        
        # Validar que las frecuencias sean menores que Nyquist
        nyquist = args.sample_rate / 2
        if any(freq >= nyquist for freq in args.freq):
            raise ValueError(f"Las frecuencias deben ser menores que la frecuencia de Nyquist ({nyquist} Hz)")
        
        # Para bandpass/bandstop, validar que low < high
        if args.type in ['bandpass', 'bandstop']:
            if args.freq[0] >= args.freq[1]:
                raise ValueError("La frecuencia inferior debe ser menor que la superior")
        
        return True, "Argumentos válidos para CLI"
    
    except Exception as e:
        return False, str(e)

def run_cli_mode(args):
    """Ejecuta el modo línea de comandos"""
    try:
        from core.filter_designer import IIRFilterDesigner, FilterType
        from exporters.cmsis_exporter import CMSISExporter
        from utils.plotter import FilterPlotter

        if args.verbose:
            print("="*60)
            print("    HERRAMIENTA CLI DE DISEÑO DE FILTROS IIR")
            print("="*60)
            print(f"Parámetros de diseño:")
            print(f"  Tipo: {args.filter_type} {args.type}")
            print(f"  Orden: {args.order}")
            print(f"  Frecuencias: {args.freq} Hz")
            print(f"  Sample Rate: {args.sample_rate} Hz")
            print(f"  Formato: {args.format}")
            print("="*60)

        # Crear diseñador de filtros
        designer = IIRFilterDesigner(args.sample_rate)
        filter_type = FilterType(args.filter_type)

        # Diseñar el filtro según el tipo
        if args.type == 'lowpass':
            designer.design_lowpass(args.freq[0], args.order, filter_type, args.ripple, args.attenuation)
        elif args.type == 'highpass':
            designer.design_highpass(args.freq[0], args.order, filter_type, args.ripple, args.attenuation)
        elif args.type == 'bandpass':
            if len(args.freq) != 2:
                raise ValueError("Bandpass requiere dos frecuencias")
            designer.design_bandpass(args.freq[0], args.freq[1], args.order, filter_type, args.ripple, args.attenuation)
        elif args.type == 'bandstop':
            if len(args.freq) != 2:
                raise ValueError("Bandstop requiere dos frecuencias")
            designer.design_bandstop(args.freq[0], args.freq[1], args.order, filter_type, args.ripple, args.attenuation)

        # Verificar estabilidad
        stable, z, p, k = designer.check_stability()
        print(f"✓ Filtro diseñado exitosamente")
        print(f"  - Tipo: {args.filter_type} {args.type}")
        print(f"  - Orden: {args.order}, Secciones: {designer.sos_coeffs.shape[0]}")
        print(f"  - Estabilidad: {'ESTABLE' if stable else 'INESTABLE'}")

        if not stable:
            print("  ⚠️  Advertencia: El filtro es inestable!")

        # Exportar coeficientes
        exporter = CMSISExporter(designer)

        if args.format in ['DF2T', 'both']:
            header_file = args.output.replace('.h', '_df2t.h') if args.format == 'both' else args.output
            exporter.export_to_cmsis_header(header_file, 'DF2T', args.data_type)
            print(f"✓ Coeficientes exportados (DF2T): {header_file}")

        if args.format in ['DF1', 'both']:
            header_file = args.output.replace('.h', '_df1.h') if args.format == 'both' else args.output
            exporter.export_to_cmsis_header(header_file, 'DF1', args.data_type)
            print(f"✓ Coeficientes exportados (DF1): {header_file}")

        # Generar gráficas si se solicita
        if args.plot:
            plotter = FilterPlotter(designer)
            plotter.generate_comprehensive_report(args.plot_file)
            print(f"✓ Gráficas generadas: {args.plot_file}")

        # Mostrar resumen de coeficientes
        print("\n" + "="*50)
        print("RESUMEN DE COEFICIENTES:")
        print("="*50)
        print(exporter.export_coefficients_text())

        return True, "Proceso CLI completado exitosamente"

    except Exception as e:
        return False, f"Error en modo CLI: {str(e)}"

def run_gui_mode(args):
    """Ejecuta el modo interfaz gráfica"""
    try:
        # Verificar dependencias de GUI
        try:
            from PySide6 import QtWidgets
        except ImportError:
            return False, "PySide6 no está instalado. Instale con: pip install PySide6"

        from ui.gui_interface import FilterDesignerGUI
        from PySide6.QtWidgets import QApplication
        
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        
        # Configurar tema si se especificó
        if args.theme != 'system':
            app.setStyle('Fusion')
            
            if args.theme == 'dark':
                # Configurar tema oscuro
                from PySide6.QtGui import QPalette, QColor
                from PySide6.QtCore import Qt
                
                palette = QPalette()
                palette.setColor(QPalette.Window, QColor(53, 53, 53))
                palette.setColor(QPalette.WindowText, Qt.white)
                palette.setColor(QPalette.Base, QColor(25, 25, 25))
                palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
                palette.setColor(QPalette.ToolTipBase, Qt.white)
                palette.setColor(QPalette.ToolTipText, Qt.white)
                palette.setColor(QPalette.Text, Qt.white)
                palette.setColor(QPalette.Button, QColor(53, 53, 53))
                palette.setColor(QPalette.ButtonText, Qt.white)
                palette.setColor(QPalette.BrightText, Qt.red)
                palette.setColor(QPalette.Link, QColor(42, 130, 218))
                palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
                palette.setColor(QPalette.HighlightedText, Qt.black)
                app.setPalette(palette)
        
        # Crear ventana principal
        window = FilterDesignerGUI()
        
        # Configurar tamaño de ventana
        if args.window_size:
            try:
                width, height = map(int, args.window_size.split('x'))
                window.resize(width, height)
            except ValueError:
                print(f"Advertencia: Tamaño de ventana inválido '{args.window_size}'. Usando tamaño por defecto.")
        
        # Configurar pantalla completa
        if args.fullscreen:
            window.showFullScreen()
        else:
            window.show()
        
        # Ejecutar aplicación
        return_code = app.exec()
        
        return True, f"Aplicación GUI finalizada con código: {return_code}"
    
    except Exception as e:
        return False, f"Error en modo GUI: {str(e)}"

def main():
    """Función principal de la herramienta"""
    print("="*70)
    print("    HERRAMIENTA DE DISEÑO DE FILTROS IIR PARA CMSIS-DSP")
    print("="*70)
    
    # Configurar parser de argumentos
    parser = setup_arg_parser()
    
    # Si no hay argumentos, mostrar ayuda
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Validar argumentos según el modo
    is_valid, validation_msg = validate_cli_args(args)
    if not is_valid and not args.gui:
        print(f"Error: {validation_msg}")
        print("\nUse --help para más información.")
        sys.exit(1)
    
    try:
        # Ejecutar según el modo seleccionado
        if args.gui:
            success, message = run_gui_mode(args)
        else:
            success, message = run_cli_mode(args)
        
        if success:
            if args.verbose:
                print(f"✓ {message}")
            sys.exit(0)
        else:
            print(f"✗ {message}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()