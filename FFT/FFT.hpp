#ifndef FFT_H
#define FFT_H

#include <complex>

// in: Puntero al buffer con datos de entrada.
// out: Puntero al buffer con datos de salida.
// n: Cantidad de puntos. En caso de no ser una potencia de dos, el comportamiento
//    es indeterminado.
// El buffer de salida puede ser el mismo que el buffer de entrada. La función debe
// operar correctamente aún en este caso. 

void fft(std::complex<double> *in, std::complex<double> *out, size_t n);

#endif