#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define POLY64 0x42F0E1EBA9EA3693ULL
#define BUF_SZ (64 * 1024)

static uint64_t crc_table[256];

void init_crc64_table() {
    for (int i = 0; i < 256; i++) {
        uint64_t crc = (uint64_t)i << 56;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000000000000000ULL) {
                crc = (crc << 1) ^ POLY64;
            } else {
                crc <<= 1;
            }
        }
        crc_table[i] = crc;
    }
}

uint64_t compute_crc64(const uint8_t *data, size_t len) {
    uint64_t crc = 0xFFFFFFFFFFFFFFFFULL;
    for (size_t i = 0; i < len; i++) {
        uint8_t table_idx = (uint8_t)((crc >> 56) ^ data[i]);
        crc = (crc << 8) ^ crc_table[table_idx];
    }
    return crc ^ 0xFFFFFFFFFFFFFFFFULL;
}

int main() {
    init_crc64_table();
    uint8_t *buf = (uint8_t *)malloc(BUF_SZ);
    for (size_t i = 0; i < BUF_SZ; i++) {
        buf[i] = (uint8_t)((i * 31 + 17) & 0xFF);
    }

    uint64_t final_crc = 0;
    for (int iter = 0; iter < 15; iter++) {
        buf[iter % 1024] ^= (uint8_t)iter;
        final_crc ^= compute_crc64(buf, BUF_SZ);
    }
    printf("CRC64 complete: crc=0x%016llX\n", (unsigned long long)final_crc);
    free(buf);
    return 0;
}
