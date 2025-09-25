
#ifndef IIR_FILTER_COEFFS_H
#define IIR_FILTER_COEFFS_H

#include "arm_math.h"

#define IIR_NUM_SECTIONS    2
#define IIR_STATE_SIZE      4
#define IIR_FORM_TYPE       DF2T

// Coeficientes del filtro IIR para CMSIS-DSP (DF2T)
// Diseñado el: 2025-09-25T15:53:08
// Secciones: 2
// Tipo de datos: float32

static const float32_t iirCoeffs_DF2T[IIR_NUM_SECTIONS * 5] = {
    0.0048243431f,
    0.0096486863f,
    0.0048243431f,
    -1.0485996008f,
    0.2961403430f,
    1.0000000000f,
    2.0000000000f,
    1.0000000000f,
    -1.3209134340f,
    0.6327387691f
};

// Ejemplo de inicialización para CMSIS-DSP:

/*
#include "arm_math.h"
#include "iir_coeffs.h"

// Buffer de estado
static float32_t iirState[IIR_STATE_SIZE];

// Instancia del filtro
arm_biquad_casd_df2t_inst_float32 iirFilter;

// Función de inicialización
void init_iir_filter(void) {
    arm_biquad_cascade_df2t_init_float32(
        &iirFilter, 
        IIR_NUM_SECTIONS, 
        (float32_t*)iirCoeffs_DF2T, 
        iirState
    );
}

// Función de procesamiento (ejecutar por bloques)
void process_iir_filter(float32_t *input, float32_t *output, uint32_t blockSize) {
    arm_biquad_cascade_df2t_float32(
        &iirFilter, input, output, blockSize
    );
}
*/

#endif /* IIR_FILTER_COEFFS_H */
