#include "FFT.hpp"

#include <iostream>

using namespace std;

int _log2(size_t n);
int bitReverse(int i, int logn);


void fft(complex<double> *in, complex<double> *out, size_t n) {

    // Caclcular gamma = floor(log2(n))
    int gamma = _log2(n);

    int r = 0;

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
        res = (res << 1) + (i & 1);
        i >>= 1;
    }
    return res;
}