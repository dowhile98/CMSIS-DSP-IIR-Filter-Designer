import numpy as np
from pathlib import Path
from enum import Enum

class ExportFormat(Enum):
    """Formatos de exportación disponibles"""
    CMSIS_DF1 = "cmsis_df1"
    CMSIS_DF2T = "cmsis_df2t"
    MATLAB = "matlab"
    PYTHON = "python"
    CSV = "csv"

class CoefficientExporter:
    def __init__(self, filter_designer):
        self.designer = filter_designer
        self.exporters = {
            ExportFormat.CMSIS_DF1: self._export_cmsis_df1,
            ExportFormat.CMSIS_DF2T: self._export_cmsis_df2t,
            ExportFormat.MATLAB: self._export_matlab,
            ExportFormat.PYTHON: self._export_python,
            ExportFormat.CSV: self._export_csv
        }
    
    def export_coefficients(self, filename, export_format=ExportFormat.CMSIS_DF2T, **kwargs):
        """Exporta coeficientes en el formato especificado"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay coeficientes de filtro para exportar")
        
        if export_format not in self.exporters:
            raise ValueError(f"Formato de exportación no soportado: {export_format}")
        
        return self.exporters[export_format](filename, **kwargs)
    
    def _export_cmsis_df1(self, filename, data_type="float32"):
        """Exporta coeficientes para CMSIS-DSP Direct Form I"""
        sos_coeffs = self.designer.sos_coeffs
        num_sections = sos_coeffs.shape[0]
        
        coeffs_array = []
        for i in range(num_sections):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            # Normalizar por a0
            b0_norm, b1_norm, b2_norm = b0/a0, b1/a0, b2/a0
            a1_norm, a2_norm = a1/a0, a2/a0
            
            # Formato DF1: {b0, b1, b2, a1, a2} (a0 normalizado a 1)
            coeffs_array.extend([b0_norm, b1_norm, b2_norm, a1_norm, a2_norm])
        
        return self._generate_cmsis_header(filename, coeffs_array, num_sections, 
                                         "DF1", data_type, 5)
    
    def _export_cmsis_df2t(self, filename, data_type="float32"):
        """Exporta coeficientes para CMSIS-DSP Direct Form II Transposed"""
        sos_coeffs = self.designer.sos_coeffs
        num_sections = sos_coeffs.shape[0]
        
        coeffs_array = []
        for i in range(num_sections):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            # Normalizar por a0
            b0_norm, b1_norm, b2_norm = b0/a0, b1/a0, b2/a0
            a1_norm, a2_norm = a1/a0, a2/a0
            
            # Formato DF2T: {b0, b1, b2, a1, a2}
            coeffs_array.extend([b0_norm, b1_norm, b2_norm, a1_norm, a2_norm])
        
        return self._generate_cmsis_header(filename, coeffs_array, num_sections,
                                         "DF2T", data_type, 5)
    
    def _generate_cmsis_header(self, filename, coeffs_array, num_sections, 
                             form_type, data_type, coeffs_per_section):
        """Genera archivo header para CMSIS-DSP"""
        coeffs_str = ",\n    ".join([f"{coeff:.10f}f" for coeff in coeffs_array])
        
        if data_type == "float32":
            c_type = "float32_t"
        elif data_type == "q31":
            c_type = "q31_t"
        elif data_type == "q15":
            c_type = "q15_t"
        else:
            c_type = "float32_t"
        
        state_size = num_sections * (4 if form_type == "DF1" else 2)
        
        header_content = f"""
#ifndef IIR_FILTER_COEFFS_H
#define IIR_FILTER_COEFFS_H

#include "arm_math.h"

#define IIR_NUM_SECTIONS    {num_sections}
#define IIR_STATE_SIZE      {state_size}
#define IIR_FORM_TYPE       {form_type}

// Coeficientes del filtro IIR para CMSIS-DSP
// Formato: {form_type}
// Secciones: {num_sections}
// Tipo de datos: {data_type}
// Fecha de diseño: {np.datetime64('now')}

static const {c_type} iirCoeffs_{form_type}[IIR_NUM_SECTIONS * {coeffs_per_section}] = {{
    {coeffs_str}
}};

#endif /* IIR_FILTER_COEFFS_H */
"""
        
        with open(filename, 'w') as f:
            f.write(header_content)
        
        return header_content
    
    def _export_matlab(self, filename):
        """Exporta coeficientes en formato MATLAB"""
        sos_coeffs = self.designer.sos_coeffs
        
        matlab_code = f"% Coeficientes de filtro IIR\n"
        matlab_code += f"% Diseñado el: {np.datetime64('now')}\n"
        matlab_code += f"% Secciones: {sos_coeffs.shape[0]}\n\n"
        
        matlab_code += "sos = [\n"
        for i in range(sos_coeffs.shape[0]):
            coeffs = " ".join([f"{coeff:.10f}" for coeff in sos_coeffs[i]])
            matlab_code += f"    {coeffs};\n"
        matlab_code += "];\n\n"
        
        matlab_code += "% Convertir a forma de transferencia\n"
        matlab_code += "[b, a] = sos2tf(sos);\n"
        matlab_code += "freqz(b, a);\n"
        
        with open(filename, 'w') as f:
            f.write(matlab_code)
        
        return matlab_code
    
    def _export_python(self, filename):
        """Exporta coeficientes en formato Python"""
        sos_coeffs = self.designer.sos_coeffs
        
        python_code = f"\"\"\"Coeficientes de filtro IIR\n"
        python_code += f"Diseñado el: {np.datetime64('now')}\n"
        python_code += f"Secciones: {sos_coeffs.shape[0]}\n\"\"\"\n\n"
        
        python_code += "import numpy as np\nimport scipy.signal as signal\n\n"
        python_code += "sos_coeffs = np.array([\n"
        for i in range(sos_coeffs.shape[0]):
            coeffs = ", ".join([f"{coeff:.10f}" for coeff in sos_coeffs[i]])
            python_code += f"    [{coeffs}],\n"
        python_code += "])\n\n"
        
        python_code += "# Ejemplo de uso:\n"
        python_code += "# w, h = signal.sosfreqz(sos_coeffs, fs=1000)\n"
        python_code += "# import matplotlib.pyplot as plt\n"
        python_code += "# plt.figure(); plt.semilogx(w, 20*np.log10(np.abs(h))); plt.grid(True)\n"
        
        with open(filename, 'w') as f:
            f.write(python_code)
        
        return python_code
    
    def _export_csv(self, filename):
        """Exporta coeficientes en formato CSV"""
        sos_coeffs = self.designer.sos_coeffs
        
        csv_content = "Section,b0,b1,b2,a0,a1,a2\n"
        for i in range(sos_coeffs.shape[0]):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            csv_content += f"{i+1},{b0:.10f},{b1:.10f},{b2:.10f},{a0:.10f},{a1:.10f},{a2:.10f}\n"
        
        with open(filename, 'w') as f:
            f.write(csv_content)
        
        return csv_content
    
    def get_available_formats(self):
        """Retorna lista de formatos de exportación disponibles"""
        return list(self.exporters.keys())