#include "FFT.hpp"
#include <iostream>
#include <vector>

using namespace std;

void printArr(complex<double> *arr, size_t n);

int main() {
    
    vector<complex<double>> in(1024);
    // vector<complex<double>> out(1024);
    
    for(int i =0; i < 16; i++) {
        in[i] = complex<double>(0, 1);
    }
    printArr(in.data(), 16);
    fft(in.data(), in.data(), 16);
    printArr(in.data(), 16);
    // Resultado: [0.+16.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j, 0. +0.j]
    cout << endl;

    // in[0] = complex<double>(1, 1);
    in[0] = 1;
    in[1] = 0;
    in[2] = -1;
    in[3] = 0;
    in[4] = 1;
    in[5] = 0;
    in[6] = -1;
    in[7] = 0;
    printArr(in.data(), 8);
    fft(in.data(), in.data(), 8);
    printArr(in.data(), 8);
    // Resultado: [0.-0.j, 0.+0.j, 4.-0.j, 0.+0.j, 0.-0.j, 0.-0.j, 4.+0.j, 0.-0.j]
    cout << endl;
    
    for(int i = 0; i < 16; i++) {
        in[i] = complex<double>(i%4, 0);
    }

    printArr(in.data(), 16);
    fft(in.data(), in.data(), 16);
    printArr(in.data(), 16);
    // Resultado: [24.-0.j,  0.+0.j,  0.-0.j,  0.+0.j, -8.+8.j,  0.+0.j,  0.+0.j, 0.+0.j,
    //             -8.-0.j,  0.-0.j,  0.-0.j,  0.-0.j, -8.-8.j, 0.-0.j, 0.+0.j,  0.-0.j]

    return 0;
}

void printArr(complex<double> *arr, size_t n) {
    for (size_t i = 0; i < n; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;
}