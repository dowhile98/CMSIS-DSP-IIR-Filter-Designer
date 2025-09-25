from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
import numpy as np

class CoefficientFormat(Enum):
    """Formatos específicos para coeficientes"""
    CMSIS_DF1_FLOAT32 = "cmsis_df1_float32"
    CMSIS_DF2T_FLOAT32 = "cmsis_df2t_float32"
    CMSIS_DF1_Q15 = "cmsis_df1_q15"
    CMSIS_DF2T_Q15 = "cmsis_df2t_q15"
    CMSIS_DF1_Q31 = "cmsis_df1_q31"
    CMSIS_DF2T_Q31 = "cmsis_df2t_q31"
    MATLAB_SOS = "matlab_sos"
    PYTHON_SOS = "python_sos"
    CSV_TABLE = "csv_table"
    JSON_STRUCTURED = "json_structured"

class DataType(Enum):
    """Tipos de datos soportados"""
    FLOAT32 = "float32"
    Q15 = "q15"
    Q31 = "q31"

@dataclass
class CoefficientSet:
    """Conjunto completo de coeficientes de filtro"""
    sos_coefficients: np.ndarray
    filter_info: Dict[str, Any]
    sample_rate: float
    
    def __post_init__(self):
        self.num_sections = self.sos_coefficients.shape[0]
        self.section_size = self.sos_coefficients.shape[1]  # Debería ser 6

@dataclass
class ExportConfig:
    """Configuración para la exportación"""
    format_type: CoefficientFormat
    data_type: DataType = DataType.FLOAT32
    normalize_coeffs: bool = True
    include_header: bool = True
    include_comments: bool = True
    precision: int = 10
    section_delimiter: str = "\n"

class FormatConverter:
    """Conversor entre diferentes formatos de coeficientes"""
    
    @staticmethod
    def sos_to_cmsis_df1(sos_coeffs: np.ndarray, normalize: bool = True) -> np.ndarray:
        """Convierte coeficientes SOS a formato CMSIS DF1"""
        num_sections = sos_coeffs.shape[0]
        cmsis_coeffs = []
        
        for i in range(num_sections):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            if normalize and abs(a0) > 1e-10:
                b0, b1, b2 = b0/a0, b1/a0, b2/a0
                a1, a2 = a1/a0, a2/a0
                a0 = 1.0
            
            # Formato DF1: b0, b1, b2, a1, a2 (a0 implícito como 1)
            cmsis_coeffs.extend([b0, b1, b2, a1, a2])
        
        return np.array(cmsis_coeffs)
    
    @staticmethod
    def sos_to_cmsis_df2t(sos_coeffs: np.ndarray, normalize: bool = True) -> np.ndarray:
        """Convierte coeficientes SOS a formato CMSIS DF2T"""
        num_sections = sos_coeffs.shape[0]
        cmsis_coeffs = []
        
        for i in range(num_sections):
            b0, b1, b2, a0, a1, a2 = sos_coeffs[i]
            
            if normalize and abs(a0) > 1e-10:
                b0, b1, b2 = b0/a0, b1/a0, b2/a0
                a1, a2 = a1/a0, a2/a0
            
            # Formato DF2T: b0, b1, b2, a1, a2
            cmsis_coeffs.extend([b0, b1, b2, a1, a2])
        
        return np.array(cmsis_coeffs)
    
    @staticmethod
    def float_to_q15(float_array: np.ndarray) -> np.ndarray:
        """Convierte array de float a Q15 format"""
        # Q15: 1 bit signo, 15 bits fraccionarios
        q15_max = 0x7FFF  # 32767
        q15_min = -0x8000  # -32768
        
        # Escalar a rango [-1, 1) para Q15
        scaled = np.clip(float_array, -0.9999999, 0.9999999)
        q15_values = (scaled * 32768).astype(np.int16)
        
        return q15_values
    
    @staticmethod
    def float_to_q31(float_array: np.ndarray) -> np.ndarray:
        """Convierte array de float a Q31 format"""
        # Q31: 1 bit signo, 31 bits fraccionarios
        q31_max = 0x7FFFFFFF
        q31_min = -0x80000000
        
        # Escalar a rango [-1, 1) para Q31
        scaled = np.clip(float_array, -0.9999999, 0.9999999)
        q31_values = (scaled * 2147483648).astype(np.int32)
        
        return q31_values
    
    @staticmethod
    def format_coefficients_string(coeffs: np.ndarray, config: ExportConfig) -> str:
        """Formatea coeficientes como string según la configuración"""
        if config.data_type == DataType.Q15:
            coeffs_formatted = FormatConverter.float_to_q15(coeffs)
            format_str = "0x{:04X}" if config.format_type.value.startswith('cmsis') else "{}"
        elif config.data_type == DataType.Q31:
            coeffs_formatted = FormatConverter.float_to_q31(coeffs)
            format_str = "0x{:08X}" if config.format_type.value.startswith('cmsis') else "{}"
        else:
            coeffs_formatted = coeffs
            format_str = "{:." + str(config.precision) + "f}f"
        
        # Formatear cada coeficiente
        formatted_coeffs = []
        for coeff in coeffs_formatted:
            if config.data_type in [DataType.Q15, DataType.Q31]:
                formatted_coeffs.append(format_str.format(coeff))
            else:
                formatted_coeffs.append(format_str.format(coeff))
        
        # Unir con delimitador
        if config.section_delimiter:
            sections = []
            coeffs_per_section = 5 if 'df2t' in config.format_type.value else 5  # Ajustar según formato
            for i in range(0, len(formatted_coeffs), coeffs_per_section):
                section = ", ".join(formatted_coeffs[i:i+coeffs_per_section])
                sections.append(section)
            return config.section_delimiter.join(sections)
        else:
            return ", ".join(formatted_coeffs)

class FormatFactory:
    """Factory para crear exportadores específicos"""
    
    @staticmethod
    def create_exporter(format_type: CoefficientFormat):
        """Crea un exportador para el formato específico"""
        exporters = {
            CoefficientFormat.CMSIS_DF1_FLOAT32: CMSISExporter,
            CoefficientFormat.CMSIS_DF2T_FLOAT32: CMSISExporter,
            CoefficientFormat.MATLAB_SOS: MATLABExporter,
            CoefficientFormat.PYTHON_SOS: PythonExporter,
            CoefficientFormat.CSV_TABLE: CSVExporter,
        }
        
        if format_type not in exporters:
            raise ValueError(f"Formato no soportado: {format_type}")
        
        return exporters[format_type]()
    
    @staticmethod
    def get_supported_formats() -> List[CoefficientFormat]:
        """Retorna lista de formatos soportados"""
        return [
            CoefficientFormat.CMSIS_DF1_FLOAT32,
            CoefficientFormat.CMSIS_DF2T_FLOAT32,
            CoefficientFormat.MATLAB_SOS,
            CoefficientFormat.PYTHON_SOS,
            CoefficientFormat.CSV_TABLE,
        ]

# Exportadores específicos (implementaciones base)
class CMSISExporter:
    def export(self, coefficient_set: CoefficientSet, config: ExportConfig) -> str:
        """Exporta en formato CMSIS-DSP"""
        if 'df1' in config.format_type.value:
            coeffs = FormatConverter.sos_to_cmsis_df1(
                coefficient_set.sos_coefficients, config.normalize_coeffs
            )
        else:
            coeffs = FormatConverter.sos_to_cmsis_df2t(
                coefficient_set.sos_coefficients, config.normalize_coeffs
            )
        
        return FormatConverter.format_coefficients_string(coeffs, config)

class MATLABExporter:
    def export(self, coefficient_set: CoefficientSet, config: ExportConfig) -> str:
        """Exporta en formato MATLAB"""
        sos = coefficient_set.sos_coefficients
        matlab_code = "sos = [\n"
        
        for i in range(sos.shape[0]):
            row = "    " + " ".join([f"{coeff:.{config.precision}f}" for coeff in sos[i]]) + ";\n"
            matlab_code += row
        
        matlab_code += "];\n"
        return matlab_code

class PythonExporter:
    def export(self, coefficient_set: CoefficientSet, config: ExportConfig) -> str:
        """Exporta en formato Python"""
        sos = coefficient_set.sos_coefficients
        python_code = "import numpy as np\n\n"
        python_code += "sos_coeffs = np.array([\n"
        
        for i in range(sos.shape[0]):
            row = "    [" + ", ".join([f"{coeff:.{config.precision}f}" for coeff in sos[i]]) + "],\n"
            python_code += row
        
        python_code += "])\n"
        return python_code

class CSVExporter:
    def export(self, coefficient_set: CoefficientSet, config: ExportConfig) -> str:
        """Exporta en formato CSV"""
        sos = coefficient_set.sos_coefficients
        csv_content = "Section,b0,b1,b2,a0,a1,a2\n"
        
        for i in range(sos.shape[0]):
            b0, b1, b2, a0, a1, a2 = sos[i]
            row = f"{i+1},{b0:.{config.precision}f},{b1:.{config.precision}f},{b2:.{config.precision}f},{a0:.{config.precision}f},{a1:.{config.precision}f},{a2:.{config.precision}f}\n"
            csv_content += row
        
        return csv_content