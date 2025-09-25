import argparse
import sys
from pathlib import Path
from core.filter_designer import IIRFilterDesigner, FilterType
from exporters.cmsis_exporter import CMSISExporter
from utils.plotter import FilterPlotter

class CLIInterface:
    def __init__(self):
        self.parser = self._setup_parser()
    
    def _setup_parser(self):
        parser = argparse.ArgumentParser(
            description='Herramienta de diseño de filtros IIR para CMSIS-DSP',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  # Filtro paso bajo Butterworth de 4to orden, 100 Hz de corte
  python main.py --type lowpass --freq 100 --order 4 --format DF2T --sample-rate 1000
  
  # Filtro paso banda Chebyshev Tipo I con ripple de 1 dB
  python main.py --type bandpass --freq 50 150 --order 6 --filter-type chebyshev1 --ripple 1.0
  
  # Exportar ambos formatos y generar gráficas
  python main.py --type highpass --freq 200 --order 4 --format both --plot
            """
        )
        
        # Parámetros básicos del filtro
        parser.add_argument('--type', required=True, choices=['lowpass', 'highpass', 'bandpass', 'bandstop'],
                          help='Tipo de filtro')
        parser.add_argument('--freq', required=True, nargs='+', type=float,
                          help='Frecuencia(s) de corte (1 para low/high, 2 para band)')
        parser.add_argument('--order', required=True, type=int, help='Orden del filtro')
        parser.add_argument('--sample-rate', type=float, default=1000.0, help='Frecuencia de muestreo (Hz)')
        
        # Parámetros avanzados del filtro
        parser.add_argument('--filter-type', choices=['butterworth', 'chebyshev1', 'chebyshev2', 'elliptic', 'bessel'],
                          default='butterworth', help='Tipo de aproximación del filtro')
        parser.add_argument('--ripple', type=float, default=1.0, help='Ripple en banda pasante (dB) para Chebyshev/Elliptic')
        parser.add_argument('--attenuation', type=float, default=40.0, help='Atenuación en banda stop (dB) para Chebyshev2/Elliptic')
        
        # Opciones de exportación
        parser.add_argument('--format', choices=['DF1', 'DF2T', 'both'], default='DF2T',
                          help='Formato de exportación para CMSIS-DSP')
        parser.add_argument('--output', '-o', type=str, default='iir_filter_coeffs.h',
                          help='Nombre del archivo de salida')
        parser.add_argument('--data-type', choices=['float32', 'q31', 'q15'], default='float32',
                          help='Tipo de datos para CMSIS-DSP')
        
        # Opciones de visualización
        parser.add_argument('--plot', action='store_true', help='Generar gráficas de validación')
        parser.add_argument('--plot-file', type=str, default='filter_validation.png',
                          help='Nombre del archivo para las gráficas')
        
        return parser
    
    def run(self):
        """Ejecuta la interfaz de línea de comandos"""
        args = self.parser.parse_args()
        
        try:
            # Validar parámetros
            self._validate_args(args)
            
            # Crear diseñador de filtros
            designer = IIRFilterDesigner(args.sample_rate)
            filter_type = FilterType(args.filter_type)
            
            # Diseñar filtro según el tipo
            if args.type == 'lowpass':
                designer.design_lowpass(args.freq[0], args.order, filter_type, 
                                      args.ripple, args.attenuation)
            elif args.type == 'highpass':
                designer.design_highpass(args.freq[0], args.order, filter_type,
                                       args.ripple, args.attenuation)
            elif args.type == 'bandpass':
                if len(args.freq) != 2:
                    raise ValueError("Bandpass requiere dos frecuencias (low, high)")
                designer.design_bandpass(args.freq[0], args.freq[1], args.order, filter_type,
                                       args.ripple, args.attenuation)
            elif args.type == 'bandstop':
                if len(args.freq) != 2:
                    raise ValueError("Bandstop requiere dos frecuencias (low, high)")
                designer.design_bandstop(args.freq[0], args.freq[1], args.order, filter_type,
                                       args.ripple, args.attenuation)
            
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
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def _validate_args(self, args):
        """Valida los argumentos de la línea de comandos"""
        if args.type in ['lowpass', 'highpass'] and len(args.freq) != 1:
            raise ValueError(f"{args.type} requiere exactamente una frecuencia")
        
        if args.type in ['bandpass', 'bandstop'] and len(args.freq) != 2:
            raise ValueError(f"{args.type} requiere dos frecuencias")
        
        if args.order <= 0:
            raise ValueError("El orden debe ser un número positivo")
        
        if args.sample_rate <= 0:
            raise ValueError("La frecuencia de muestreo debe ser positiva")
        
        if any(freq <= 0 for freq in args.freq):
            raise ValueError("Las frecuencias deben ser positivas")
        
        if any(freq >= args.sample_rate/2 for freq in args.freq):
            raise ValueError("Las frecuencias deben ser menores que la frecuencia de Nyquist")