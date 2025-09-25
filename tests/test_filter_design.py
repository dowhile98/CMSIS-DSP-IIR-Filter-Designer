import unittest
import numpy as np
import scipy.signal as signal
import tempfile
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from core.filter_designer import IIRFilterDesigner, FilterType
from core.validation_tools import FilterValidator
from exporters.cmsis_exporter import CMSISExporter
from exporters.formats import CoefficientFormat, ExportConfig, FormatConverter
from utils.signal_generators import SignalGenerator, FilterTester

class TestFilterDesign(unittest.TestCase):
    """Pruebas unitarias para el diseño de filtros IIR"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.sample_rate = 1000.0
        self.designer = IIRFilterDesigner(self.sample_rate)
        self.validator = FilterValidator(self.designer)
        self.generator = SignalGenerator()
    
    def test_butterworth_lowpass_design(self):
        """Prueba diseño de filtro Butterworth paso bajo"""
        # Diseñar filtro
        sos_coeffs = self.designer.design_lowpass(
            cutoff_freq=100, 
            order=4, 
            filter_type=FilterType.BUTTERWORTH
        )
        
        # Verificar propiedades básicas
        self.assertEqual(sos_coeffs.shape[0], 2)  # 4to orden = 2 secciones
        self.assertEqual(sos_coeffs.shape[1], 6)  # 6 coeficientes por sección
        
        # Verificar estabilidad
        stable, _, _, _ = self.designer.check_stability()
        self.assertTrue(stable, "El filtro Butterworth debería ser estable")
    
    def test_chebyshev1_bandpass_design(self):
        """Prueba diseño de filtro Chebyshev Tipo I paso banda"""
        sos_coeffs = self.designer.design_bandpass(
            low_cutoff=50,
            high_cutoff=150,
            order=6,
            filter_type=FilterType.CHEBYSHEV1,
            ripple=1.0
        )
        
        self.assertEqual(sos_coeffs.shape[0], 3)  # 6to orden = 3 secciones
        
        # Verificar estabilidad
        stable, _, _, _ = self.designer.check_stability()
        self.assertTrue(stable, "El filtro Chebyshev debería ser estable")
    
    def test_elliptic_highpass_design(self):
        """Prueba diseño de filtro elíptico paso alto"""
        sos_coeffs = self.designer.design_highpass(
            cutoff_freq=200,
            order=5,
            filter_type=FilterType.ELLIPTIC,
            ripple=0.5,
            attenuation=60.0
        )
        
        # Orden impar puede redondear hacia arriba en secciones
        self.assertIn(sos_coeffs.shape[0], [2, 3])
        
        stable, _, _, _ = self.designer.check_stability()
        self.assertTrue(stable, "El filtro elíptico debería ser estable")
    
    def test_bessel_lowpass_design(self):
        """Prueba diseño de filtro Bessel paso bajo"""
        sos_coeffs = self.designer.design_lowpass(
            cutoff_freq=100,
            order=4,
            filter_type=FilterType.BESSEL
        )
        
        self.assertEqual(sos_coeffs.shape[0], 2)
        
        stable, _, _, _ = self.designer.check_stability()
        self.assertTrue(stable, "El filtro Bessel debería ser estable")
    
    def test_stability_validation(self):
        """Prueba validación de estabilidad"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        
        stability_info = self.validator.check_stability()
        
        self.assertTrue(stability_info['stable'])
        self.assertGreater(stability_info['stability_margin'], 0)
        self.assertLess(stability_info['max_pole_magnitude'], 1.0)
    
    def test_frequency_response_analysis(self):
        """Prueba análisis de respuesta en frecuencia"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        
        freq_response = self.validator.analyze_frequency_response()
        
        self.assertIn('frequencies', freq_response)
        self.assertIn('magnitude_response', freq_response)
        self.assertIn('phase_response', freq_response)
        self.assertIn('cutoff_frequency', freq_response)
        
        # Verificar que la frecuencia de corte esté cerca de 100 Hz
        self.assertAlmostEqual(freq_response['cutoff_frequency'], 100, delta=20)
    
    def test_causality_validation(self):
        """Prueba validación de causalidad"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        
        causality_info = self.validator.check_causality()
        
        self.assertTrue(causality_info['causal'])
        self.assertEqual(len(causality_info['issues']), 0)
    
    def test_numerical_sensitivity_analysis(self):
        """Prueba análisis de sensibilidad numérica"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        
        sensitivity_info = self.validator.analyze_numerical_sensitivity(perturbations=10)
        
        self.assertIn('sensitivity_score', sensitivity_info)
        self.assertIn('stability_robustness', sensitivity_info)
        self.assertGreaterEqual(sensitivity_info['stability_robustness'], 0)
        self.assertLessEqual(sensitivity_info['stability_robustness'], 1)
    
    def test_comprehensive_validation_report(self):
        """Prueba generación de reporte de validación completo"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        
        report = self.validator.generate_validation_report()
        
        self.assertIsInstance(report, str)
        self.assertIn("ESTABILIDAD", report)
        self.assertIn("CAUSALIDAD", report)
        self.assertIn("SENSIBILIDAD NUMÉRICA", report)
    
    def test_cmsis_export_df2t(self):
        """Prueba exportación a formato CMSIS DF2T"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        exporter = CMSISExporter(self.designer)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            temp_file = f.name
        
        try:
            header_content = exporter.export_to_cmsis_header(temp_file, "DF2T", "float32")
            
            self.assertIsInstance(header_content, str)
            self.assertIn("IIR_FILTER_COEFFS_H", header_content)
            self.assertIn("float32_t", header_content)
            self.assertIn("DF2T", header_content)
            
            # Verificar que el archivo se creó
            self.assertTrue(os.path.exists(temp_file))
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_cmsis_export_df1(self):
        """Prueba exportación a formato CMSIS DF1"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        exporter = CMSISExporter(self.designer)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            temp_file = f.name
        
        try:
            header_content = exporter.export_to_cmsis_header(temp_file, "DF1", "float32")
            
            self.assertIsInstance(header_content, str)
            self.assertIn("IIR_FILTER_COEFFS_H", header_content)
            self.assertIn("DF1", header_content)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_signal_generation(self):
        """Prueba generación de señales de prueba"""
        duration = 0.1  # 100 ms
        
        # Probar generación de impulso
        t, impulse = self.generator.generate_impulse(self.sample_rate, duration)
        self.assertEqual(len(t), len(impulse))
        self.assertEqual(impulse[0], 1.0)  # Primer sample debe ser 1
        self.assertTrue(np.all(impulse[1:] == 0))  # Resto deben ser 0
        
        # Probar generación de escalón
        t, step = self.generator.generate_step(self.sample_rate, duration)
        self.assertTrue(np.all(step == 1.0))  # Todos deben ser 1
        
        # Probar generación de sinusoidal
        t, sine = self.generator.generate_sine(self.sample_rate, duration, 50)
        self.assertEqual(len(t), len(sine))
        self.assertAlmostEqual(np.max(sine), 1.0, delta=0.1)
        self.assertAlmostEqual(np.min(sine), -1.0, delta=0.1)
    
    def test_filter_testing(self):
        """Prueba testing de filtros con señales generadas"""
        self.designer.design_lowpass(100, 4, FilterType.BUTTERWORTH)
        tester = FilterTester(self.designer)
        
        # Probar respuesta al impulso
        t, impulse_response = tester.test_impulse_response(duration=0.1)
        self.assertEqual(len(t), len(impulse_response))
        
        # Probar respuesta al escalón
        t, step_response = tester.test_step_response(duration=0.1)
        self.assertEqual(len(t), len(step_response))
        
        # Probar respuesta en frecuencia
        frequencies = [10, 50, 100, 200]  # Frecuencias de prueba
        tested_freqs, gains = tester.test_frequency_response(frequencies, duration=0.05)
        self.assertEqual(len(tested_freqs), len(gains))
        self.assertEqual(tested_freqs, frequencies)
        
        # Las ganancias deberían disminuir con la frecuencia (filtro paso bajo)
        self.assertGreater(gains[0], gains[2])  # 10 Hz > 100 Hz
        self.assertGreater(gains[1], gains[3])  # 50 Hz > 200 Hz
    
    def test_format_conversion(self):
        """Prueba conversión entre formatos de coeficientes"""
        self.designer.design_lowpass(100, 2, FilterType.BUTTERWORTH)
        sos_coeffs = self.designer.sos_coeffs
        
        # Probar conversión a DF2T
        df2t_coeffs = FormatConverter.sos_to_cmsis_df2t(sos_coeffs)
        self.assertEqual(len(df2t_coeffs), 10)  # 2 secciones × 5 coeficientes
        
        # Probar conversión a DF1
        df1_coeffs = FormatConverter.sos_to_cmsis_df1(sos_coeffs)
        self.assertEqual(len(df1_coeffs), 10)  # 2 secciones × 5 coeficientes
        
        # Probar conversión a Q15
        q15_coeffs = FormatConverter.float_to_q15(df2t_coeffs)
        self.assertEqual(len(q15_coeffs), len(df2t_coeffs))
        self.assertEqual(q15_coeffs.dtype, np.int16)
        
        # Probar conversión a Q31
        q31_coeffs = FormatConverter.float_to_q31(df2t_coeffs)
        self.assertEqual(len(q31_coeffs), len(df2t_coeffs))
        self.assertEqual(q31_coeffs.dtype, np.int32)
    
    def test_unstable_filter_detection(self):
        """Prueba detección de filtros inestables"""
        # Crear coeficientes artificialmente inestables (polos fuera del círculo unitario)
        unstable_sos = np.array([
            [1.0, 0.0, 0.0, 1.0, -1.5, 0.7]  # Polos en 0.75 ± 0.43j (magnitud ~0.86) - estable
        ])
        
        # Forzar coeficientes inestables
        unstable_sos = np.array([
            [1.0, 0.0, 0.0, 1.0, -2.0, 1.5]  # Polos en 1.0 ± 0.71j (magnitud > 1) - inestable
        ])
        
        # Verificar que se detecta la inestabilidad
        z, p, k = signal.sos2zpk(unstable_sos)
        stable = all(np.abs(p) < 1.0)
        self.assertFalse(stable, "El filtro debería ser detectado como inestable")

class TestEdgeCases(unittest.TestCase):
    """Pruebas para casos extremos y validación de errores"""
    
    def test_invalid_parameters(self):
        """Prueba manejo de parámetros inválidos"""
        designer = IIRFilterDesigner(1000)
        
        with self.assertRaises(ValueError):
            # Frecuencia de corte mayor que Nyquist
            designer.design_lowpass(600, 4, FilterType.BUTTERWORTH)
        
        with self.assertRaises(ValueError):
            # Orden negativo
            designer.design_lowpass(100, -1, FilterType.BUTTERWORTH)
    
    def test_empty_filter_validation(self):
        """Prueba validación cuando no hay filtro diseñado"""
        designer = IIRFilterDesigner(1000)
        validator = FilterValidator(designer)
        
        with self.assertRaises(ValueError):
            validator.check_stability()
        
        with self.assertRaises(ValueError):
            validator.analyze_frequency_response()
    
    def test_export_without_design(self):
        """Prueba exportación sin filtro diseñado"""
        designer = IIRFilterDesigner(1000)
        exporter = CMSISExporter(designer)
        
        with self.assertRaises(ValueError):
            exporter.export_to_cmsis_header("test.h", "DF2T", "float32")

def run_all_tests():
    """Ejecuta todas las pruebas unitarias"""
    # Crear test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFilterDesign)
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Ejecutar pruebas cuando el script se ejecuta directamente
    success = run_all_tests()
    sys.exit(0 if success else 1)