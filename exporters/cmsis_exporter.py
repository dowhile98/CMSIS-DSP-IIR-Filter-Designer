import numpy as np
from pathlib import Path

class CMSISExporter:
    def __init__(self, filter_designer):
        self.designer = filter_designer
        self.export_formats = ['DF1', 'DF2T']
    
    def export_to_cmsis_header(self, filename, form_type="DF2T", data_type="float32"):
        """Exporta los coeficientes a un archivo .h compatible con CMSIS-DSP"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay coeficientes de filtro para exportar")
        
        sos_coeffs = self.designer.sos_coeffs
        num_sections = sos_coeffs.shape[0]
        
        if form_type == "DF2T":
            coeffs_array = self._prepare_df2t_coeffs(sos_coeffs)
            state_size = num_sections * 2  # 2 estados por sección para DF2T
        elif form_type == "DF1":
            coeffs_array = self._prepare_df1_coeffs(sos_coeffs)
            state_size = num_sections * 4  # 4 estados por sección para DF1
        else:
            raise ValueError(f"Formato no soportado: {form_type}")
        
        header_content = self._generate_header_file(coeffs_array, num_sections, 
                                                  state_size, form_type, data_type)
        
        with open(filename, 'w') as f:
            f.write(header_content)
        
        return header_content
    
    def _prepare_df2t_coeffs(self, sos_coeffs):
        """Prepara coeficientes para Direct Form II Transposed"""
        cmsis_coeffs = []
        
        for i in range(sos_coeffs.shape[0]):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            # Normalizar por a0 (asumiendo a0 != 0)
            b0_norm, b1_norm, b2_norm = b0/a0, b1/a0, b2/a0
            a1_norm, a2_norm = a1/a0, a2/a0
            
            # Formato CMSIS-DSP: { b0, b1, b2, a1, a2 }
            cmsis_coeffs.extend([b0_norm, b1_norm, b2_norm, a1_norm, a2_norm])
        
        return np.array(cmsis_coeffs, dtype=np.float32)
    
    def _prepare_df1_coeffs(self, sos_coeffs):
        """Prepara coeficientes para Direct Form I"""
        cmsis_coeffs = []
        
        for i in range(sos_coeffs.shape[0]):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            # Normalizar por a0
            b0_norm, b1_norm, b2_norm = b0/a0, b1/a0, b2/a0
            a1_norm, a2_norm = a1/a0, a2/a0
            
            # Formato CMSIS-DSP DF1: { b0, b1, b2, a0, a1, a2 }
            # Nota: CMSIS-DSP espera a0 normalizado a 1, pero incluimos los coeficientes completos
            cmsis_coeffs.extend([b0_norm, b1_norm, b2_norm, 1.0, a1_norm, a2_norm])
        
        return np.array(cmsis_coeffs, dtype=np.float32)
    
    def _generate_header_file(self, coeffs_array, num_sections, state_size, form_type, data_type):
        """Genera el contenido del archivo .h"""
        
        # Formatear array de coeficientes para C
        coeffs_str = ",\n    ".join([f"{coeff:.10f}f" for coeff in coeffs_array])
        
        if data_type == "float32":
            c_type = "float32_t"
        elif data_type == "q31":
            c_type = "q31_t"
        elif data_type == "q15":
            c_type = "q15_t"
        else:
            c_type = "float32_t"
        
        header_template = f"""
#ifndef IIR_FILTER_COEFFS_H
#define IIR_FILTER_COEFFS_H

#include "arm_math.h"

#define IIR_NUM_SECTIONS    {num_sections}
#define IIR_STATE_SIZE      {state_size}
#define IIR_FORM_TYPE       {form_type}

// Coeficientes del filtro IIR para CMSIS-DSP ({form_type})
// Diseñado el: {np.datetime64('now')}
// Secciones: {num_sections}
// Tipo de datos: {data_type}

static const {c_type} iirCoeffs_{form_type}[IIR_NUM_SECTIONS * {5 if form_type == 'DF2T' else 6}] = {{
    {coeffs_str}
}};

// Ejemplo de inicialización para CMSIS-DSP:

/*
#include "arm_math.h"
#include "iir_coeffs.h"

// Buffer de estado
static {c_type} iirState[IIR_STATE_SIZE];

// Instancia del filtro
arm_biquad_casd_{form_type.lower()}_inst_{data_type} iirFilter;

// Función de inicialización
void init_iir_filter(void) {{
    arm_biquad_cascade_{form_type.lower()}_init_{data_type}(
        &iirFilter, 
        IIR_NUM_SECTIONS, 
        ({c_type}*)iirCoeffs_{form_type}, 
        iirState
    );
}}

// Función de procesamiento (ejecutar por bloques)
void process_iir_filter({c_type} *input, {c_type} *output, uint32_t blockSize) {{
    arm_biquad_cascade_{form_type.lower()}_{data_type}(
        &iirFilter, input, output, blockSize
    );
}}
*/

#endif /* IIR_FILTER_COEFFS_H */
"""
        return header_template
    
    def export_coefficients_text(self, form_type="DF2T"):
        """Exporta coeficientes en formato texto para verificación"""
        if self.designer.sos_coeffs is None:
            raise ValueError("No hay coeficientes de filtro para exportar")
        
        sos_coeffs = self.designer.sos_coeffs
        output = f"Coeficientes del filtro IIR ({form_type})\n"
        output += "=" * 50 + "\n"
        
        for i in range(sos_coeffs.shape[0]):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            output += f"Sección {i+1}:\n"
            output += f"  Numerador: [{b0:.6f}, {b1:.6f}, {b2:.6f}]\n"
            output += f"  Denominador: [{a0:.6f}, {a1:.6f}, {a2:.6f}]\n"
            
            if form_type == "DF2T":
                b0_norm, b1_norm, b2_norm = b0/a0, b1/a0, b2/a0
                a1_norm, a2_norm = a1/a0, a2/a0
                output += f"  DF2T: [{b0_norm:.6f}, {b1_norm:.6f}, {b2_norm:.6f}, {a1_norm:.6f}, {a2_norm:.6f}]\n"
            
            output += "\n"
        
        return output