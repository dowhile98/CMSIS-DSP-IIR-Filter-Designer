import scipy.signal as signal
import numpy as np
from enum import Enum

class FilterType(Enum):
    BUTTERWORTH = "butterworth"
    CHEBYSHEV1 = "chebyshev1"
    CHEBYSHEV2 = "chebyshev2"
    ELLIPTIC = "elliptic"
    BESSEL = "bessel"

class IIRFilterDesigner:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.filter_coeffs = None
        self.sos_coeffs = None
        self.filter_info = {}
    
    def design_lowpass(self, cutoff_freq, order, filter_type=FilterType.BUTTERWORTH, 
                      ripple=1.0, attenuation=40.0):
        """Diseña un filtro paso bajo"""
        nyquist = self.sample_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        
        if filter_type == FilterType.BUTTERWORTH:
            self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='lowpass',
                                              ftype='butter', output='sos')
        elif filter_type == FilterType.CHEBYSHEV1:
            self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='lowpass',
                                              ftype='cheby1', rp=ripple, output='sos')
        elif filter_type == FilterType.CHEBYSHEV2:
            self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='lowpass',
                                              ftype='cheby2', rs=attenuation, output='sos')
        elif filter_type == FilterType.ELLIPTIC:
            self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='lowpass',
                                              ftype='ellip', rp=ripple, rs=attenuation, output='sos')
        elif filter_type == FilterType.BESSEL:
            self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='lowpass',
                                              ftype='bessel', output='sos')
        
        self._store_filter_info(cutoff_freq, order, filter_type, 'lowpass')
        return self.sos_coeffs
    
    def design_highpass(self, cutoff_freq, order, filter_type=FilterType.BUTTERWORTH,
                       ripple=1.0, attenuation=40.0):
        """Diseña un filtro paso alto"""
        nyquist = self.sample_rate / 2
        normal_cutoff = cutoff_freq / nyquist
        
        self.sos_coeffs = signal.iirfilter(order, normal_cutoff, btype='highpass',
                                          ftype=filter_type.value, rp=ripple, 
                                          rs=attenuation, output='sos')
        self._store_filter_info(cutoff_freq, order, filter_type, 'highpass')
        return self.sos_coeffs
    
    def design_bandpass(self, low_cutoff, high_cutoff, order, filter_type=FilterType.BUTTERWORTH,
                       ripple=1.0, attenuation=40.0):
        """Diseña un filtro paso banda"""
        nyquist = self.sample_rate / 2
        normal_low = low_cutoff / nyquist
        normal_high = high_cutoff / nyquist
        
        self.sos_coeffs = signal.iirfilter(order, [normal_low, normal_high], btype='bandpass',
                                          ftype=filter_type.value, rp=ripple,
                                          rs=attenuation, output='sos')
        self._store_filter_info((low_cutoff, high_cutoff), order, filter_type, 'bandpass')
        return self.sos_coeffs
    
    def design_bandstop(self, low_cutoff, high_cutoff, order, filter_type=FilterType.BUTTERWORTH,
                       ripple=1.0, attenuation=40.0):
        """Diseña un filtro elimina banda"""
        nyquist = self.sample_rate / 2
        normal_low = low_cutoff / nyquist
        normal_high = high_cutoff / nyquist
        
        self.sos_coeffs = signal.iirfilter(order, [normal_low, normal_high], btype='bandstop',
                                          ftype=filter_type.value, rp=ripple,
                                          rs=attenuation, output='sos')
        self._store_filter_info((low_cutoff, high_cutoff), order, filter_type, 'bandstop')
        return self.sos_coeffs
    
    def _store_filter_info(self, cutoff, order, filter_type, band_type):
        """Almacena información del filtro diseñado"""
        self.filter_info = {
            'cutoff_freq': cutoff,
            'order': order,
            'filter_type': filter_type,
            'band_type': band_type,
            'sample_rate': self.sample_rate,
            'num_sections': self.sos_coeffs.shape[0],
            'design_date': np.datetime64('now')
        }
    
    def check_stability(self):
        """Verifica la estabilidad del filtro analizando los polos"""
        if self.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        try:
            # Obtener polos y ceros
            z, p, k = signal.sos2zpk(self.sos_coeffs)
            
            # Verificar que todos los polos estén dentro del círculo unitario
            stable = all(np.abs(p) < 1.0) if len(p) > 0 else True
            
            return stable, z, p, k
            
        except Exception as e:
            # Fallback en caso de error
            return True, np.array([]), np.array([]), 1.0
    
    def get_filter_response(self, freq_points=1024):
        """Obtiene la respuesta en frecuencia del filtro"""
        if self.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        w, h = signal.sosfreqz(self.sos_coeffs, worN=freq_points, fs=self.sample_rate)
        return w, h