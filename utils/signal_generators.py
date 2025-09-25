import numpy as np
import scipy.signal as signal
from typing import Tuple, List, Union

class SignalGenerator:
    """Generador de señales de prueba para validación de filtros"""
    
    @staticmethod
    def generate_impulse(sample_rate: float, duration: float, 
                        amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera una señal impulso (delta de Dirac)
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        amplitude : float
            Amplitud del impulso
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal impulso
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        impulse = np.zeros_like(t)
        impulse[0] = amplitude
        return t, impulse
    
    @staticmethod
    def generate_step(sample_rate: float, duration: float,
                     amplitude: float = 1.0, 
                     step_time: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera una señal escalón unitario
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        amplitude : float
            Amplitud del escalón
        step_time : float
            Tiempo en el que ocurre el escalón
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal escalón
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        step = np.zeros_like(t)
        step_index = int(step_time * sample_rate)
        step[step_index:] = amplitude
        return t, step
    
    @staticmethod
    def generate_sine(sample_rate: float, duration: float, 
                     frequency: float, amplitude: float = 1.0,
                     phase: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera una señal sinusoidal
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        frequency : float
            Frecuencia de la sinusoidal en Hz
        amplitude : float
            Amplitud de la señal
        phase : float
            Fase inicial en radianes
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal sinusoidal
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t + phase)
        return t, sine_wave
    
    @staticmethod
    def generate_chirp(sample_rate: float, duration: float,
                      freq_start: float, freq_end: float,
                      amplitude: float = 1.0,
                      method: str = 'linear') -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera una señal chirp (barrido de frecuencia)
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        freq_start : float
            Frecuencia inicial en Hz
        freq_end : float
            Frecuencia final en Hz
        amplitude : float
            Amplitud de la señal
        method : str
            Método de barrido ('linear', 'quadratic', 'logarithmic')
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal chirp
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        if method == 'linear':
            # Barrido lineal de frecuencia
            phase = 2 * np.pi * (freq_start * t + 
                                (freq_end - freq_start) * t**2 / (2 * duration))
        elif method == 'quadratic':
            # Barrido cuadrático
            phase = 2 * np.pi * (freq_start * t + 
                                (freq_end - freq_start) * t**3 / (3 * duration**2))
        elif method == 'logarithmic':
            # Barrido logarítmico
            k = (freq_end / freq_start) ** (1 / duration)
            phase = 2 * np.pi * freq_start * (k**t - 1) / np.log(k)
        else:
            raise ValueError("Método no soportado. Use 'linear', 'quadratic' o 'logarithmic'")
        
        chirp_signal = amplitude * np.sin(phase)
        return t, chirp_signal
    
    @staticmethod
    def generate_white_noise(sample_rate: float, duration: float,
                            amplitude: float = 1.0,
                            noise_type: str = 'uniform') -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera ruido blanco
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        amplitude : float
            Amplitud del ruido
        noise_type : str
            Tipo de ruido ('uniform', 'gaussian')
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal de ruido
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        n_samples = len(t)
        
        if noise_type == 'uniform':
            noise = amplitude * (2 * np.random.random(n_samples) - 1)
        elif noise_type == 'gaussian':
            noise = amplitude * np.random.randn(n_samples)
        else:
            raise ValueError("Tipo de ruido no soportado. Use 'uniform' o 'gaussian'")
        
        return t, noise
    
    @staticmethod
    def generate_multitone(sample_rate: float, duration: float,
                          frequencies: List[float],
                          amplitudes: Union[List[float], None] = None,
                          phases: Union[List[float], None] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera una señal multitono (suma de sinusoides)
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        frequencies : List[float]
            Lista de frecuencias en Hz
        amplitudes : List[float], optional
            Lista de amplitudes para cada frecuencia
        phases : List[float], optional
            Lista de fases para cada frecuencia
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Señal multitono
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        if amplitudes is None:
            amplitudes = [1.0] * len(frequencies)
        if phases is None:
            phases = [0.0] * len(frequencies)
        
        if len(frequencies) != len(amplitudes) or len(frequencies) != len(phases):
            raise ValueError("Las listas de frecuencias, amplitudes y fases deben tener la misma longitud")
        
        multitone = np.zeros_like(t)
        for freq, amp, phase in zip(frequencies, amplitudes, phases):
            multitone += amp * np.sin(2 * np.pi * freq * t + phase)
        
        return t, multitone
    
    @staticmethod
    def generate_pulse_train(sample_rate: float, duration: float,
                            pulse_frequency: float, pulse_width: float,
                            amplitude: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera un tren de pulsos
        
        Parameters:
        -----------
        sample_rate : float
            Frecuencia de muestreo en Hz
        duration : float
            Duración de la señal en segundos
        pulse_frequency : float
            Frecuencia de repetición de pulsos en Hz
        pulse_width : float
            Ancho de cada pulso en segundos
        amplitude : float
            Amplitud de los pulsos
            
        Returns:
        --------
        t : np.ndarray
            Array de tiempos
        signal : np.ndarray
            Tren de pulsos
        """
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        pulse_train = np.zeros_like(t)
        
        pulse_period = 1.0 / pulse_frequency
        samples_per_pulse = int(pulse_width * sample_rate)
        samples_per_period = int(pulse_period * sample_rate)
        
        for i in range(0, len(t), samples_per_period):
            end_idx = min(i + samples_per_pulse, len(t))
            pulse_train[i:end_idx] = amplitude
        
        return t, pulse_train

class FilterTester:
    """Utilidades para testing de filtros con señales generadas"""
    
    def __init__(self, filter_designer):
        self.designer = filter_designer
        self.generator = SignalGenerator()
    
    def test_impulse_response(self, duration: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """Prueba el filtro con una señal impulso"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay filtro diseñado para probar")
        
        sample_rate = self.designer.sample_rate
        t, impulse = self.generator.generate_impulse(sample_rate, duration)
        
        # Aplicar filtro
        response = signal.sosfilt(self.designer.sos_coeffs, impulse)
        
        return t, response
    
    def test_step_response(self, duration: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """Prueba el filtro con una señal escalón"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay filtro diseñado para probar")
        
        sample_rate = self.designer.sample_rate
        t, step = self.generator.generate_step(sample_rate, duration)
        
        # Aplicar filtro
        response = signal.sosfilt(self.designer.sos_coeffs, step)
        
        return t, response
    
    def test_frequency_response(self, frequencies: List[float], 
                              duration: float = 0.1) -> Tuple[List[float], List[float]]:
        """
        Prueba la respuesta del filtro a diferentes frecuencias
        
        Returns:
        --------
        frequencies : List[float]
            Frecuencias probadas
        gains : List[float]
            Ganancia del filtro en cada frecuencia (dB)
        """
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay filtro diseñado para probar")
        
        sample_rate = self.designer.sample_rate
        gains = []
        
        for freq in frequencies:
            # Generar sinusoidal
            t, sine = self.generator.generate_sine(sample_rate, duration, freq)
            
            # Aplicar filtro
            filtered = signal.sosfilt(self.designer.sos_coeffs, sine)
            
            # Calcular ganancia (RMS)
            input_rms = np.sqrt(np.mean(sine**2))
            output_rms = np.sqrt(np.mean(filtered**2))
            
            if input_rms > 0:
                gain_db = 20 * np.log10(output_rms / input_rms)
            else:
                gain_db = -np.inf
            
            gains.append(gain_db)
        
        return frequencies, gains
    
    def test_noise_rejection(self, duration: float = 1.0,
                           noise_frequency: float = None) -> Tuple[float, float]:
        """
        Prueba la capacidad del filtro para rechazar ruido
        
        Returns:
        --------
        input_snr : float
            SNR de la señal de entrada (dB)
        output_snr : float
            SNR de la señal filtrada (dB)
        """
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay filtro diseñado para probar")
        
        sample_rate = self.designer.sample_rate
        
        # Generar señal útil (sinusoidal a frecuencia media)
        if noise_frequency is None:
            # Usar frecuencia de corte si está disponible
            if hasattr(self.designer, 'filter_info'):
                cutoff = self.designer.filter_info.get('cutoff_freq', 100)
                if isinstance(cutoff, tuple):
                    signal_freq = np.mean(cutoff)
                else:
                    signal_freq = cutoff
            else:
                signal_freq = 50
        else:
            signal_freq = noise_frequency
        
        t, signal = self.generator.generate_sine(sample_rate, duration, signal_freq)
        
        # Generar ruido
        _, noise = self.generator.generate_white_noise(sample_rate, duration)
        
        # Mezclar señal y ruido (SNR de 0 dB para prueba)
        noisy_signal = signal + noise
        
        # Aplicar filtro
        filtered_signal = signal.sosfilt(self.designer.sos_coeffs, noisy_signal)
        
        # Calcular SNR
        def calculate_snr(signal, noise):
            signal_power = np.mean(signal**2)
            noise_power = np.mean(noise**2)
            return 10 * np.log10(signal_power / noise_power) if noise_power > 0 else np.inf
        
        input_snr = calculate_snr(signal, noisy_signal - signal)
        output_snr = calculate_snr(filtered_signal, filtered_signal - signal)
        
        return input_snr, output_snr