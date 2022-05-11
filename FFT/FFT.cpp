#include "FFT.hpp"

#include <iostream>
#include <vector>

#define PI (3.14159265359)

using namespace std;

int _log2(size_t n);
int bitReverse(int i, int logn);
void bitReverse(complex<double> *in, complex<double> *out, size_t n);
void swap(complex<double> &a, complex<double> &b);

void fft(complex<double> *in, complex<double> *out, size_t n) {

    const complex<double> j = complex<double>(0, 1);    // imaginary unit

    // Caclcular gamma = floor(log2(n))
    int gamma = _log2(n);

    int E = gamma;     // Cantidad de etapas
    int G = 1;         // Cantidad de grupos inicial
    int M = n >> 1;    // Cantidad de mariposas por grupo inicial: N/2

    vector<complex<double>> W(M);

    for (size_t i = 0; i < n/2; i++)
    {
        W[i] = exp(-j*(2*PI*bitReverse(i << 1, gamma)/n));    // w[g] = (W_N)^BR(2*g)
        if (in != out){
            out[i] = in[i];
            out[i + n/2] = in[i + n/2];
        }
    }

    for(int r = 0; r < E; r++) {    // Etapa
        int m_sep = M << 1;     // Separacion entre mariposas: N/2^(r+1)
        int sep = M;            // Separacion entre nodos duales: m_sep/2 
        for(int g = 0; g < G; g++) {    // Grupo
            for(int m = 0; m < M; m++) {    // Mariposa
                int index = g*m_sep + m;  // Indice del primer nodo la mariposa
                complex<double> Y = out[index];
                complex<double> Z = out[index + sep];
                complex<double> WZ = W[g]*Z;

                out[index] = Y + WZ;
                out[index + sep] = Y - WZ;
            }
        }
        M >>= 1;    // M = M/2
        G <<= 1;    // G = G*2
    }

    // Ordenamiento de la salida
    for (size_t i = 1; i < (n >> 1); i++)  // Desde 1 hasta N/2
    {
        swap(out[i], out[bitReverse(i, gamma)]);
    }
    

}

int _log2(size_t n) {
    int res = 0;
    while (n > 1) {
        n >>= 1;
        res++;
    }
    return res;
}

int bitReverse(int i, int logn) {
    int res = 0;
    for (int k = 0; k < logn; k++) {
        res = (res << 1) | (i & 1);
        i >>= 1;
    }
    return res;
}

void bitReverse(complex<double> *in, complex<double> *out, size_t n) {
    int logn = _log2(n);
    for (size_t i = 0; i < n; i++) {
        out[bitReverse(i, logn)] = in[i];
    }
}

void swap(complex<double> &a, complex<double> &b) {
    complex<double> tmp = a;
    a = b;
    b = tmp;
}