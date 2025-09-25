import numpy as np
import scipy.signal as signal
from typing import Tuple, Dict, Any

class FilterValidator:
    def __init__(self, filter_designer):
        self.designer = filter_designer
    
    def comprehensive_validation(self) -> Dict[str, Any]:
        """Realiza una validación completa del filtro diseñado"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay filtro diseñado para validar")
        
        validation_results = {}
        
        # 1. Verificación de estabilidad
        stability_result = self.check_stability()
        validation_results['stability'] = stability_result
        
        # 2. Análisis de respuesta en frecuencia
        validation_results['frequency_response'] = self.analyze_frequency_response()
        
        # 3. Verificación de causalidad
        validation_results['causality'] = self.check_causality()
        
        # 4. Análisis de sensibilidad numérica
        validation_results['numerical_sensitivity'] = self.analyze_numerical_sensitivity()
        
        # 5. Validación de especificaciones
        if hasattr(self.designer, 'filter_info'):
            validation_results['specs_validation'] = self.validate_specifications()
        
        return validation_results
    
    def check_stability(self) -> Dict[str, Any]:
        """Verifica la estabilidad del filtro analizando polos y ceros"""
        sos_coeffs = self.designer.sos_coeffs
        z, p, k = signal.sos2zpk(sos_coeffs)
        
        # Verificar que todos los polos estén dentro del círculo unitario
        pole_magnitudes = np.abs(p)
        stable = all(pole_magnitudes < 1.0)
        
        # Calcular margen de estabilidad
        stability_margin = 1.0 - np.max(pole_magnitudes) if stable else 0.0
        
        return {
            'stable': stable,
            'poles': p,
            'zeros': z,
            'gain': k,
            'pole_magnitudes': pole_magnitudes,
            'stability_margin': stability_margin,
            'max_pole_magnitude': np.max(pole_magnitudes)
        }
    
    def check_stability_tuple(self) -> Tuple[bool, np.ndarray, np.ndarray, float]:
        """Versión alternativa que devuelve tupla para compatibilidad"""
        sos_coeffs = self.designer.sos_coeffs
        z, p, k = signal.sos2zpk(sos_coeffs)
        
        # Verificar que todos los polos estén dentro del círculo unitario
        stable = all(np.abs(p) < 1.0)
        
        return stable, z, p, k
    
    def analyze_frequency_response(self, freq_points: int = 1024) -> Dict[str, Any]:
        """Analiza la respuesta en frecuencia del filtro"""
        w, h = self.designer.get_filter_response(freq_points)
        magnitude = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
        phase = np.unwrap(np.angle(h))
        
        # Calcular group delay correctamente
        if len(w) > 1:
            group_delay = -np.diff(phase) / np.diff(w)
            # Asegurar misma longitud
            group_delay = np.append(group_delay, group_delay[-1])
        else:
            group_delay = np.array([0.0])
        
        # Encontrar frecuencia de corte (-3 dB)
        if len(magnitude) > 0:
            dc_magnitude = magnitude[0]
            # Buscar donde la magnitud cae 3 dB por debajo de DC
            cutoff_mask = magnitude <= (dc_magnitude - 3)
            if np.any(cutoff_mask):
                cutoff_index = np.argmax(cutoff_mask)
                cutoff_freq = w[cutoff_index] if cutoff_index > 0 else w[-1]
            else:
                cutoff_freq = w[-1]
        else:
            dc_magnitude = 0
            cutoff_freq = 0
        
        return {
            'frequencies': w,
            'magnitude_response': magnitude,
            'phase_response': phase,
            'group_delay': group_delay,
            'cutoff_frequency': cutoff_freq,
            'dc_gain': dc_magnitude
        }
    
    def check_causality(self) -> Dict[str, Any]:
        """Verifica que el filtro sea causal"""
        sos_coeffs = self.designer.sos_coeffs
        
        # Un filtro IIR es causal si todos los coeficientes del denominador
        # están presentes y el filtro es estable
        causal = True
        issues = []
        
        if sos_coeffs is not None and len(sos_coeffs) > 0:
            for i, section in enumerate(sos_coeffs):
                if len(section) >= 6:  # Asegurar que tiene 6 coeficientes
                    b0, b1, b2, a0, a1, a2 = section[:6]
                    
                    # Verificar que a0 no sea cero
                    if np.abs(a0) < 1e-10:
                        causal = False
                        issues.append(f"Sección {i+1}: a0 es cero o muy pequeño")
                    
                    # Verificar que el filtro sea realizable
                    elif np.abs(a0) < 1e-6:
                        causal = False
                        issues.append(f"Sección {i+1}: a0 es numéricamente problemático")
                else:
                    causal = False
                    issues.append(f"Sección {i+1}: número insuficiente de coeficientes")
        
        return {
            'causal': causal,
            'issues': issues,
            'sections_checked': len(sos_coeffs) if sos_coeffs is not None else 0
        }
    
    def analyze_numerical_sensitivity(self, perturbations: int = 100) -> Dict[str, Any]:
        """Analiza la sensibilidad numérica del filtro a perturbaciones"""
        sos_coeffs = self.designer.sos_coeffs
        
        if sos_coeffs is None:
            return {
                'sensitivity_score': 0,
                'stability_robustness': 0,
                'stability_changes': 0,
                'average_magnitude_change': 0,
                'max_magnitude_change': 0
            }
        
        stability_info = self.check_stability()
        original_stable = stability_info['stable']
        
        # Aplicar perturbaciones aleatorias a los coeficientes
        stability_changes = 0
        magnitude_changes = []
        
        for _ in range(min(perturbations, 100)):  # Limitar a 100 perturbaciones
            try:
                # Perturbar coeficientes (0.1% de variación)
                perturbation = 1.0 + 0.001 * np.random.randn(*sos_coeffs.shape)
                perturbed_sos = sos_coeffs * perturbation
                
                # Verificar estabilidad del filtro perturbado
                z, p, k = signal.sos2zpk(perturbed_sos)
                perturbed_stable = all(np.abs(p) < 1.0) if len(p) > 0 else True
                
                if original_stable != perturbed_stable:
                    stability_changes += 1
                
                # Calcular cambio en respuesta en frecuencia
                w, h_original = signal.sosfreqz(sos_coeffs, worN=100)
                w, h_perturbed = signal.sosfreqz(perturbed_sos, worN=100)
                
                if len(h_original) > 0 and len(h_perturbed) > 0:
                    mag_change = np.mean(np.abs(20*np.log10(np.abs(h_perturbed) + 1e-10) - 
                                             20*np.log10(np.abs(h_original) + 1e-10)))
                    magnitude_changes.append(mag_change)
                    
            except Exception as e:
                # Continuar con la siguiente perturbación si hay error
                continue
        
        sensitivity_score = np.mean(magnitude_changes) if magnitude_changes else 0
        stability_robustness = 1.0 - (stability_changes / perturbations) if perturbations > 0 else 1.0
        
        return {
            'sensitivity_score': sensitivity_score,
            'stability_robustness': stability_robustness,
            'stability_changes': stability_changes,
            'average_magnitude_change': np.mean(magnitude_changes) if magnitude_changes else 0,
            'max_magnitude_change': np.max(magnitude_changes) if magnitude_changes else 0
        }
    
    def validate_specifications(self) -> Dict[str, Any]:
        """Valida si el filtro cumple con las especificaciones de diseño"""
        if not hasattr(self.designer, 'filter_info'):
            return {'validated': False, 'reason': 'No hay información de diseño'}
        
        specs = self.designer.filter_info
        freq_response = self.analyze_frequency_response()
        
        validation_results = {
            'validated': True,
            'details': {}
        }
        
        # Verificar frecuencia de corte (para filtros lowpass/highpass)
        if 'band_type' in specs and specs['band_type'] in ['lowpass', 'highpass']:
            designed_cutoff = specs['cutoff_freq']
            actual_cutoff = freq_response['cutoff_frequency']
            if designed_cutoff > 0:
                cutoff_error = abs(actual_cutoff - designed_cutoff) / designed_cutoff
            else:
                cutoff_error = 0
            
            validation_results['details']['cutoff_accuracy'] = {
                'designed': designed_cutoff,
                'actual': actual_cutoff,
                'error_percent': cutoff_error * 100,
                'within_tolerance': cutoff_error < 0.1  # 10% de tolerancia
            }
        
        # Verificar estabilidad
        stability = self.check_stability()
        validation_results['details']['stability'] = {
            'stable': stability['stable'],
            'margin': stability['stability_margin']
        }
        
        # Verificar ganancia DC (para lowpass)
        if 'band_type' in specs and specs['band_type'] == 'lowpass':
            dc_gain = freq_response['dc_gain']
            validation_results['details']['dc_gain'] = {
                'value': dc_gain,
                'expected_near_0dB': abs(dc_gain) < 1.0  # Debería estar cerca de 0 dB
            }
        
        return validation_results
    
    def generate_validation_report(self) -> str:
        """Genera un reporte detallado de validación en texto"""
        try:
            validation = self.comprehensive_validation()
            
            report = "REPORTE DE VALIDACIÓN DE FILTRO IIR\n"
            report += "=" * 50 + "\n\n"
            
            # Estabilidad
            stability = validation['stability']
            report += "1. ESTABILIDAD:\n"
            report += f"   - Estado: {'ESTABLE' if stability['stable'] else 'INESTABLE'}\n"
            report += f"   - Margen de estabilidad: {stability['stability_margin']:.6f}\n"
            report += f"   - Magnitud máxima de polos: {stability['max_pole_magnitude']:.6f}\n"
            report += f"   - Número de polos: {len(stability['poles'])}\n"
            report += f"   - Número de ceros: {len(stability['zeros'])}\n\n"
            
            # Causalidad
            causality = validation['causality']
            report += "2. CAUSALIDAD:\n"
            report += f"   - Causal: {'SÍ' if causality['causal'] else 'NO'}\n"
            if causality['issues']:
                report += "   - Problemas detectados:\n"
                for issue in causality['issues']:
                    report += f"     * {issue}\n"
            report += f"   - Secciones verificadas: {causality['sections_checked']}\n\n"
            
            # Sensibilidad numérica
            sensitivity = validation['numerical_sensitivity']
            report += "3. SENSIBILIDAD NUMÉRICA:\n"
            report += f"   - Puntuación de sensibilidad: {sensitivity['sensitivity_score']:.6f}\n"
            report += f"   - Robustez de estabilidad: {sensitivity['stability_robustness']:.3f}\n"
            report += f"   - Cambios de estabilidad: {sensitivity['stability_changes']}\n"
            report += f"   - Cambio promedio en magnitud: {sensitivity['average_magnitude_change']:.6f} dB\n\n"
            
            # Validación de especificaciones
            if 'specs_validation' in validation:
                specs_val = validation['specs_validation']
                report += "4. VALIDACIÓN DE ESPECIFICACIONES:\n"
                report += f"   - Validado: {'SÍ' if specs_val['validated'] else 'NO'}\n"
                
                for key, detail in specs_val['details'].items():
                    report += f"   - {key.upper()}:\n"
                    for subkey, value in detail.items():
                        report += f"     {subkey}: {value}\n"
            
            return report
            
        except Exception as e:
            return f"Error generando reporte de validación: {str(e)}"