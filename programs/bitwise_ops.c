#include <stdio.h>

unsigned int crc32_chunk(const unsigned char *buf, size_t len) {
    unsigned int crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= buf[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

int main() {
    unsigned char buffer[1024];
    for (int i = 0; i < 1024; i++) buffer[i] = (unsigned char)(i & 0xFF);

    unsigned int checksum = 0;
    for (int iter = 0; iter < 2500; iter++) {
        checksum += crc32_chunk(buffer, 1024);
    }
    printf("Bitwise complete: checksum=0x%X\n", checksum);
    return 0;
}
