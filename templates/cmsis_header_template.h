#ifndef IIR_FILTER_COEFFS_H
#define IIR_FILTER_COEFFS_H

/**
 * @file    iir_filter_coeffs.h
 * @brief   Coeficientes de filtro IIR para CMSIS-DSP
 * @author  CMSIS IIR Designer Tool
 * @date    {{ design_date }}
 * @version 1.0
 */

#include "arm_math.h"

// Configuración del filtro
#define IIR_FILTER_SECTIONS     {{ num_sections }}
#define IIR_FILTER_STATE_SIZE   {{ state_size }}
#define IIR_FILTER_FORMAT       {{ form_type }}
#define IIR_FILTER_DATA_TYPE    {{ data_type }}
#define IIR_FILTER_SAMPLE_RATE  {{ sample_rate }}

// Información del diseño
#define IIR_FILTER_TYPE         "{{ filter_type }}"
#define IIR_FILTER_BAND_TYPE    "{{ band_type }}"
#define IIR_FILTER_ORDER        {{ filter_order }}
#define IIR_FILTER_CUTOFF       {{ cutoff_freq }}

// Coeficientes del filtro IIR
static const {{ data_type }} iirCoeffs[IIR_FILTER_SECTIONS * {{ coeffs_per_section }}] = {
    {{ coefficients_array }}
};

// Buffer de estado (debe ser definido por el usuario)
// static {{ data_type }} iirState[IIR_FILTER_STATE_SIZE];

/**
 * @brief Inicializa la estructura del filtro IIR
 * 
 * @param S Pointer to an instance of the filter structure
 * @param numStages number of 2nd order stages in the filter
 * @param pCoeffs points to the filter coefficients
 * @param pState points to the state buffer
 */
/*
void iir_filter_init(arm_biquad_casd_{{ form_type_lower }}_inst_{{ data_type }} *S, 
                     uint32_t numStages, 
                     {{ data_type }} *pCoeffs, 
                     {{ data_type }} *pState)
{
    arm_biquad_cascade_{{ form_type_lower }}_init_{{ data_type }}(
        S, numStages, pCoeffs, pState);
}
*/

/**
 * @brief Procesa un bloque de datos through the filter
 * 
 * @param S points to an instance of the filter structure
 * @param pSrc points to the input buffer
 * @param pDst points to the output buffer
 * @param blockSize number of samples to process
 */
/*
void iir_filter_process(arm_biquad_casd_{{ form_type_lower }}_inst_{{ data_type }} *S,
                        {{ data_type }} *pSrc,
                        {{ data_type }} *pDst,
                        uint32_t blockSize)
{
    arm_biquad_cascade_{{ form_type_lower }}_{{ data_type }}(
        S, pSrc, pDst, blockSize);
}
*/

// Ejemplo de uso completo:
/*
#include "iir_filter_coeffs.h"

// Buffer de estado
static {{ data_type }} iirState[IIR_FILTER_STATE_SIZE];

// Instancia del filtro
arm_biquad_casd_{{ form_type_lower }}_inst_{{ data_type }} iirFilter;

void init_iir_filter(void)
{
    // Inicializar filtro
    arm_biquad_cascade_{{ form_type_lower }}_init_{{ data_type }}(
        &iirFilter,
        IIR_FILTER_SECTIONS,
        ({{ data_type }}*)iirCoeffs,
        iirState);
}

void process_iir_filter({{ data_type }} *input, 
                       {{ data_type }} *output, 
                       uint32_t blockSize)
{
    // Procesar bloque de datos
    arm_biquad_cascade_{{ form_type_lower }}_{{ data_type }}(
        &iirFilter, input, output, blockSize);
}

// Para fixed-point (Q15/Q31), usar funciones de escalado apropiadas
#if defined({{ data_type }}_Q15) || defined({{ data_type }}_Q31)
void process_iir_filter_scaled({{ data_type }} *input,
                              {{ data_type }} *output,
                              uint32_t blockSize,
                              int32_t scale)
{
    arm_biquad_cascade_{{ form_type_lower }}_{{ data_type }}_scale(
        &iirFilter, input, output, blockSize, scale);
}
#endif
*/

#endif // IIR_FILTER_COEFFS_H