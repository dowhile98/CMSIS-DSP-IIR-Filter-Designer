import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
from matplotlib.gridspec import GridSpec

class FilterPlotter:
    def __init__(self, filter_designer):
        self.designer = filter_designer
    
    def plot_frequency_response(self, ax=None, freq_points=1024):
        """Grafica la respuesta en frecuencia del filtro"""
        if self.designer.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        w, h = self.designer.get_filter_response(freq_points)
        
        if ax is None:
            fig, ax = plt.subplots(2, 1, figsize=(10, 8))
        else:
            fig = ax[0].figure
        
        # Magnitud
        ax[0].semilogx(w, 20 * np.log10(np.maximum(np.abs(h), 1e-10)))
        ax[0].set_title('Respuesta en Frecuencia del Filtro')
        ax[0].set_ylabel('Magnitud [dB]')
        ax[0].grid(True)
        ax[0].set_xlim([w[1], w[-1]])
        
        # Fase
        ax[1].semilogx(w, np.unwrap(np.angle(h)))
        ax[1].set_ylabel('Fase [radianes]')
        ax[1].set_xlabel('Frecuencia [Hz]')
        ax[1].grid(True)
        
        return fig
    
    def plot_impulse_response(self, ax=None, num_points=100):
        """Grafica la respuesta al impulso del filtro"""
        if self.designer.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        # Generar impulso
        impulse = np.zeros(num_points)
        impulse[0] = 1.0
        
        # Aplicar filtro
        response = signal.sosfilt(self.designer.sos_coeffs, impulse)
        
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        else:
            fig = ax.figure
        
        ax.stem(np.arange(num_points), response)
        ax.set_title('Respuesta al Impulso')
        ax.set_xlabel('Muestras')
        ax.set_ylabel('Amplitud')
        ax.grid(True)
        
        return fig
    
    def plot_step_response(self, ax=None, num_points=100):
        """Grafica la respuesta al escalón del filtro"""
        if self.designer.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        # Generar escalón
        step = np.ones(num_points)
        
        # Aplicar filtro
        response = signal.sosfilt(self.designer.sos_coeffs, step)
        
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        else:
            fig = ax.figure
        
        ax.plot(np.arange(num_points), response)
        ax.set_title('Respuesta al Escalón')
        ax.set_xlabel('Muestras')
        ax.set_ylabel('Amplitud')
        ax.grid(True)
        
        return fig
    
    def plot_pole_zero(self, ax=None):
        """Grafica el diagrama de polos y ceros"""
        if self.designer.sos_coeffs is None:
            raise ValueError("Primero debe diseñar un filtro")
        
        z, p, k = signal.sos2zpk(self.designer.sos_coeffs)
        
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        else:
            fig = ax.figure
        
        # Dibujar círculo unitario
        unit_circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
        ax.add_patch(unit_circle)
        
        # Plot polos y ceros
        ax.scatter(np.real(z), np.imag(z), marker='o', facecolors='none', 
                  edgecolors='b', s=80, label='Ceros')
        ax.scatter(np.real(p), np.imag(p), marker='x', color='r', s=80, label='Polos')
        
        ax.set_title('Diagrama de Polos y Ceros')
        ax.set_xlabel('Parte Real')
        ax.set_ylabel('Parte Imaginaria')
        ax.legend()
        ax.grid(True)
        ax.axis('equal')
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        # Verificar estabilidad
        stable, _, _, _ = self.designer.check_stability()
        stability_text = "Estable" if stable else "Inestable"
        ax.text(0.05, 0.95, f'Filtro: {stability_text}', transform=ax.transAxes,
               bbox=dict(boxstyle="round", facecolor="lightgreen" if stable else "lightcoral"))
        
        return fig
    
    def generate_comprehensive_report(self, filename=None):
        """Genera un reporte completo con todas las gráficas"""
        fig = plt.figure(figsize=(15, 12))
        gs = GridSpec(3, 2, figure=fig)
        
        ax1 = fig.add_subplot(gs[0, :])  # Respuesta frecuencia
        ax2 = fig.add_subplot(gs[1, 0])  # Impulso
        ax3 = fig.add_subplot(gs[1, 1])  # Escalón
        ax4 = fig.add_subplot(gs[2, :])  # Polos/ceros
        
        # Plot todas las respuestas
        self.plot_frequency_response(ax=[ax1, ax2])
        self.plot_impulse_response(ax=ax3)
        self.plot_pole_zero(ax=ax4)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        return fig