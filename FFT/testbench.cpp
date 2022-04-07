#include "FFT.hpp"
#include <iostream>
#include <vector>

using namespace std;

int main() {
    
    vector<complex<double>> in(1024);
    vector<complex<double>> out(1024);
    
    in[0] = complex<double>(1, 1);
    in[1] = 2;
    in[2] = 3;
    in[3] = 4;
    in[4] = 5;
    in[5] = 6;
    in[6] = 7;
    in[7] = 8;
    fft(in.data(), out.data(), 8);
    return 0;
}