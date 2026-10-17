"""
Re-integration implementation for cBench and MiBench benchmarks.
Extracts full directory sources, merges headers and companion C files,
adds minimal synthetic main/input wrappers,
tests compilation under -O0, -O1, -O2, -O3, -Os, runs execution test,
saves to programs/cbench_<name>_merged.c and programs/mibench_<name>_merged.c,
and logs all actions to logs/cbench_mibench_fix_log.txt and updates manifest.json.
"""

import os
import sys
import re
import json
import time
import subprocess

BASE_DIR = r"E:\AI_Compiler_Optimization"
PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
FIX_LOG = os.path.join(LOGS_DIR, "cbench_mibench_fix_log.txt")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")

CBENCH_DIR = os.path.join(BASE_DIR, ".temp_cbench", "program")
MIBENCH_DIR = os.path.join(BASE_DIR, ".temp_mibench")

FLAGS = ["-O0", "-O1", "-O2", "-O3", "-Os"]


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def strip_includes(code: str, header_names: list) -> str:
    for h in header_names:
        code = re.sub(r'#include\s*["<]' + re.escape(h) + r'[">]', '', code)
    return code


def test_and_install(out_filename: str, code: str, original_files: list, fix_desc: str) -> bool:
    unique_tag = f"{int(time.time() * 1000)}_{os.getpid()}"
    test_src = os.path.join(BASE_DIR, f"temp_{unique_tag}.c")

    with open(test_src, "w", encoding="utf-8") as f:
        f.write(code)

    status_str = "SUCCESS"
    created_exes = []
    try:
        for idx, fl in enumerate(FLAGS):
            test_exe = os.path.join(BASE_DIR, f"temp_{unique_tag}_{idx}.exe")
            created_exes.append(test_exe)
            res = subprocess.run(
                ["gcc", fl, test_src, "-o", test_exe, "-lm"],
                capture_output=True,
                text=True,
                timeout=25
            )
            if res.returncode != 0:
                status_str = f"FAILED: compile {fl}: {res.stderr[:200].strip()}"
                break

        if status_str == "SUCCESS":
            # Run the -O0 binary
            run_res = subprocess.run(
                [created_exes[0]],
                capture_output=True,
                text=True,
                timeout=5
            )
            if run_res.returncode != 0:
                status_str = f"FAILED: exit code {run_res.returncode}: {run_res.stderr[:150].strip()}"

    except subprocess.TimeoutExpired:
        status_str = "FAILED: execution timed out (>5.0s)"
    except Exception as e:
        status_str = f"FAILED: {e}"
    finally:
        if os.path.exists(test_src):
            try:
                os.remove(test_src)
            except Exception:
                pass
        for exe in created_exes:
            if os.path.exists(exe):
                try:
                    os.remove(exe)
                except Exception:
                    pass

    # Log to logs/cbench_mibench_fix_log.txt
    log_entry = (
        f'{{"filename": "{out_filename}", '
        f'"original_files_merged": {json.dumps(original_files)}, '
        f'"fix_applied": "{fix_desc}", '
        f'"compile_status": "{status_str}"}}\n'
    )
    with open(FIX_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"[{status_str}] {out_filename}")

    if status_str == "SUCCESS":
        target_path = os.path.join(PROGRAMS_DIR, out_filename)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(code)
        return True
    return False


# ==============================================================================
# cBench Builders
# ==============================================================================

def build_cbench_qsort1():
    p = os.path.join(CBENCH_DIR, "cbench-automotive-qsort1")
    qsort_c = read_file(os.path.join(p, "qsort.c"))
    qsort_large_c = read_file(os.path.join(p, "qsort_large.c"))
    
    idx = qsort_large_c.find("main1")
    cut_idx = qsort_large_c.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = qsort_large_c.rfind("int", 0, idx)
    qsort_large_body = qsort_large_c[:cut_idx]
    
    main_code = """
int main(int argc, char *argv[]) {
    int i, count = 0;
    FILE *fp;
    long x = 0, y = 0, z = 0;

    if (argc >= 2 && (fp = fopen(argv[1], "r")) != NULL) {
        while ((fscanf(fp, "%ld", &x) == 1) && (fscanf(fp, "%ld", &y) == 1) && (fscanf(fp, "%ld", &z) == 1) && (count < MAXARRAY)) {
            array[count].x = x;
            array[count].y = y;
            array[count].z = z;
            array[count].distance = sqrt((double)(x*x + y*y + z*z));
            count++;
        }
        fclose(fp);
    } else {
        for (i = 0; i < 500; i++) {
            x = (i * 37) % 1000 - 500;
            y = (i * 73) % 1000 - 500;
            z = (i * 101) % 1000 - 500;
            array[count].x = x;
            array[count].y = y;
            array[count].z = z;
            array[count].distance = sqrt((double)(x*x + y*y + z*z));
            count++;
        }
    }
    qsortx(array, count, sizeof(struct my3DVertexStruct), compare);
    double sum = 0.0;
    for (i = 0; i < count; i++) {
        sum += array[i].distance;
    }
    printf("Sorted %d vectors, distance sum: %f\\n", count, sum);
    return 0;
}
"""
    code = (
        "#include <stdlib.h>\n#include <stdio.h>\n#include <math.h>\n\n"
        + qsort_c + "\n\n"
        + qsort_large_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_automotive_qsort1_merged.c",
        code,
        ["qsort.c", "qsort_large.c"],
        "Merged qsortx sorting kernel with qsort_large and added standalone synthetic 3D vertex generator"
    )


def build_cbench_dijkstra():
    p = os.path.join(CBENCH_DIR, "cbench-network-dijkstra")
    dijkstra_c = read_file(os.path.join(p, "dijkstra_large.c"))
    body = dijkstra_c[:dijkstra_c.find("int main(")]
    
    main_code = """
int main(int argc, char *argv[]) {
    int i, j, k;
    FILE *fp;

    if (argc >= 2 && (fp = fopen(argv[1], "r")) != NULL) {
        fscanf(fp, "%d", &NUM_NODES);
        AdjMatrix = (int *)malloc(sizeof(int) * (NUM_NODES + 1) * (NUM_NODES + 1));
        rgnNodes = (NODE *)malloc(sizeof(NODE) * (NUM_NODES + 1));
        for (i = 0; i < NUM_NODES; i++) {
            for (j = 0; j < NUM_NODES; j++) {
                fscanf(fp, "%d", &k);
                AdjMatrix[i * NUM_NODES + j] = k;
            }
        }
        fclose(fp);
    } else {
        NUM_NODES = 64;
        AdjMatrix = (int *)malloc(sizeof(int) * (NUM_NODES + 1) * (NUM_NODES + 1));
        rgnNodes = (NODE *)malloc(sizeof(NODE) * (NUM_NODES + 1));
        for (i = 0; i < NUM_NODES; i++) {
            for (j = 0; j < NUM_NODES; j++) {
                AdjMatrix[i * NUM_NODES + j] = (i == j) ? 0 : ((i * 17 + j * 31) % 50 + 1);
            }
        }
    }

    for (i = 0; i < NUM_NODES; i++) {
        dijkstra(0, i);
    }
    printf("Dijkstra completed for %d nodes.\\n", NUM_NODES);
    free(AdjMatrix);
    free(rgnNodes);
    return 0;
}
"""
    code = body + "\n\n" + main_code
    return test_and_install(
        "cbench_network_dijkstra_merged.c",
        code,
        ["dijkstra_large.c"],
        "Added self-contained synthetic 64x64 adjacency matrix to dijkstra_large"
    )


def build_cbench_patricia():
    p = os.path.join(CBENCH_DIR, "cbench-network-patricia")
    pat_h = read_file(os.path.join(p, "patricia.h"))
    pat_c = read_file(os.path.join(p, "patricia.c"))
    pat_test = read_file(os.path.join(p, "patricia_test.c"))
    
    pat_c = strip_includes(pat_c, ["patricia.h"])
    pat_test = strip_includes(pat_test, ["patricia.h"])
    
    idx = pat_test.find("main1")
    cut_idx = pat_test.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = pat_test.rfind("int", 0, idx)
    pat_test_body = pat_test[:cut_idx]
    
    main_code = """
int main(int argc, char **argv) {
    struct ptree *phead;
    struct ptree_mask *pm;
    struct ptree *p;
    float time = 0.0f;
    struct in_addr addr;
    int i;

    phead = (struct ptree *)malloc(sizeof(struct ptree));
    if (!phead) exit(1);
    memset(phead, 0, sizeof(*phead));

    pm = (struct ptree_mask *)malloc(sizeof(struct ptree_mask));
    if (!pm) exit(1);
    memset(pm, 0, sizeof(*pm));
    pm->pm_data = (struct ptree_mask_data *)malloc(sizeof(struct ptree_mask_data));
    if (!pm->pm_data) exit(1);
    memset(pm->pm_data, 0, sizeof(*pm->pm_data));

    phead->p_mlen = 1;
    phead->p_left = phead->p_right = phead;

    for (i = 0; i < 200; i++) {
        time = (float)i * 0.1f;
        addr.s_addr = htonl((unsigned int)(0x0A000000 + i * 257));
        p = (struct ptree *)malloc(sizeof(struct ptree));
        if (!p) exit(1);
        memset(p, 0, sizeof(*p));
        p->p_m = (struct ptree_mask *)malloc(sizeof(struct ptree_mask));
        if (!p->p_m) exit(1);
        memset(p->p_m, 0, sizeof(*p->p_m));
        p->p_m->pm_data = (struct ptree_mask_data *)malloc(sizeof(struct ptree_mask_data));
        if (!p->p_m->pm_data) exit(1);
        memset(p->p_m->pm_data, 0, sizeof(*p->p_m->pm_data));

        p->p_key = addr.s_addr;
        ((struct ptree_mask_data *)p->p_m->pm_data)->pmd_time = time;
        p->p_mlen = 24;
        pat_insert(p, phead);
    }

    for (i = 0; i < 100; i++) {
        addr.s_addr = htonl((unsigned int)(0x0A000000 + i * 257));
        pat_search(addr.s_addr, phead);
    }
    printf("Patricia trie tests completed successfully.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "#define bcopy(b1,b2,len) memmove(b2, b1, len)\n"
        "#define bzero(b,len) memset(b, 0, len)\n\n"
        + pat_h + "\n\n"
        + "struct ptree_mask_data { float pmd_time; };\n\n"
        + pat_c + "\n\n"
        + pat_test_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_network_patricia_merged.c",
        code,
        ["patricia.h", "patricia.c", "patricia_test.c"],
        "Merged patricia trie library and test driver with synthetic IP prefix insertions and lookups"
    )


def build_cbench_stringsearch2():
    p = os.path.join(CBENCH_DIR, "cbench-office-stringsearch2")
    src = read_file(os.path.join(p, "fgg_search.c"))
    body = src[:src.find("int main(")]
    
    main_code = """
int main(int argc, char *argv[]) {
    char *text_corpus[] = {
        "The quick brown fox jumps over the lazy dog repeatedly.",
        "Computer compilers translate high-level code to assembly.",
        "Optimization passes enhance execution speed and decrease binary code size.",
        "Machine learning models predict optimal compiler flag sequences.",
        "Static code features include loops, arrays, pointers, and arithmetic ops.",
        "Benchmarking requires representative sample programs and stable measurement.",
        "Polybench, MiBench, cBench, and BEEBS serve as diverse empirical benchmarks.",
        NULL
    };
    char *search_patterns[] = {
        "compiler", "optimize", "bench", "speed", "model", "code", "dog", NULL
    };

    int matches = 0;
    int i, j;
    for (i = 0; text_corpus[i] != NULL; i++) {
        int tlen = strlen(text_corpus[i]);
        for (j = 0; search_patterns[j] != NULL; j++) {
            int plen = strlen(search_patterns[j]);
            int k;
            for (k = 0; k <= tlen - plen; k++) {
                if (local_strncmp(&text_corpus[i][k], search_patterns[j], plen) == 0) {
                    matches++;
                }
            }
        }
    }
    printf("String search completed with %d pattern matches.\\n", matches);
    return 0;
}
"""
    code = body + "\n\n" + main_code
    return test_and_install(
        "cbench_office_stringsearch2_merged.c",
        code,
        ["fgg_search.c"],
        "Added synthetic in-memory text corpus and search patterns using local_strncmp kernel"
    )


def build_cbench_rijndael():
    p = os.path.join(CBENCH_DIR, "cbench-security-rijndael")
    aes_h = read_file(os.path.join(p, "aes.h"))
    aestab_h = read_file(os.path.join(p, "aestab.h"))
    aes_c = read_file(os.path.join(p, "aes.c"))
    aesxam_c = read_file(os.path.join(p, "aesxam.c"))

    # Replace include statements directly where they occur
    aes_c = aes_c.replace('#include "aes.h"', aes_h)
    aes_c = aes_c.replace('#include "aestab.h"', aestab_h)
    aesxam_c = aesxam_c.replace('#include "aes.h"', '')
    
    aesxam_body = aesxam_c[:aesxam_c.find("int main1(")]

    main_code = """
int main(int argc, char *argv[]) {
    byte key[16] = {0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f};
    byte in_block[16] = {0x32,0x43,0xf6,0xa8,0x88,0x5a,0x30,0x8d,0x31,0x31,0x98,0xa2,0xe0,0x37,0x07,0x34};
    byte out_block[16];
    byte dec_block[16];
    aes ctx[1];
    int round;

    set_key(key, 16, both, ctx);
    for (round = 0; round < 500; round++) {
        encrypt(in_block, out_block, ctx);
        decrypt(out_block, dec_block, ctx);
        in_block[round % 16] ^= out_block[round % 16];
    }
    printf("Rijndael AES 500 rounds completed. Final block byte: %02x\\n", dec_block[0]);
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <ctype.h>\n\n"
        + aes_c + "\n\n"
        + aesxam_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_security_rijndael_merged.c",
        code,
        ["aes.h", "aestab.h", "aes.c", "aesxam.c"],
        "Inlined aes.h and aestab.h in place, merged cipher implementation with synthetic encryption loop"
    )


def build_cbench_sha():
    p = os.path.join(CBENCH_DIR, "cbench-security-sha")
    sha_h = read_file(os.path.join(p, "sha.h"))
    sha_c = read_file(os.path.join(p, "sha.c"))
    sha_driver_c = read_file(os.path.join(p, "sha_driver.c"))

    sha_c = strip_includes(sha_c, ["sha.h"])
    sha_driver_c = strip_includes(sha_driver_c, ["sha.h"])
    sha_driver_body = sha_driver_c[:sha_driver_c.find("int main1")]

    main_code = """
int main(int argc, char *argv[]) {
    SHA_INFO sha_info;
    BYTE sample[64] = "The quick brown fox jumps over the lazy dog 0123456789 ABCDEF!";
    int i;
    for (i = 0; i < 500; i++) {
        sample[i % 60] ^= (BYTE)(i & 0xFF);
        sha_init(&sha_info);
        sha_update(&sha_info, sample, 62);
        sha_final(&sha_info);
    }
    printf("SHA-1 500 rounds complete: %08lx %08lx\\n", sha_info.digest[0], sha_info.digest[1]);
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        + sha_h + "\n\n"
        + sha_c + "\n\n"
        + sha_driver_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_security_sha_merged.c",
        code,
        ["sha.h", "sha.c", "sha_driver.c"],
        "Included stdio.h before sha.h and replaced stdin stream with in-memory hashing rounds"
    )


def build_cbench_adpcm_c():
    p = os.path.join(CBENCH_DIR, "cbench-telecom-adpcm-c")
    adpcm_h = read_file(os.path.join(p, "adpcm.h"))
    adpcm_c = read_file(os.path.join(p, "adpcm.c"))
    adpcm_c = strip_includes(adpcm_c, ["adpcm.h"])

    main_code = """
int main(void) {
    struct adpcm_state state;
    state.valprev = 0;
    state.index = 0;

    #define SAMPLES 1000
    short pcm_in[SAMPLES];
    char adpcm_out[SAMPLES / 2];
    int i, rep;

    for (i = 0; i < SAMPLES; i++) {
        pcm_in[i] = (short)(sin(i * 0.05) * 16000.0);
    }

    for (rep = 0; rep < 100; rep++) {
        struct adpcm_state cur = state;
        adpcm_coder(pcm_in, adpcm_out, SAMPLES, &cur);
    }
    printf("ADPCM coder 100 iterations completed.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n"
        + adpcm_h + "\n\n"
        + adpcm_c + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_telecom_adpcm_c_merged.c",
        code,
        ["adpcm.h", "adpcm.c", "rawcaudio.c"],
        "Merged adpcm.h and adpcm.c, replaced blocking read(0, ...) with in-memory sinusoidal PCM coder"
    )


def build_cbench_adpcm_d():
    p = os.path.join(CBENCH_DIR, "cbench-telecom-adpcm-d")
    adpcm_h = read_file(os.path.join(p, "adpcm.h"))
    adpcm_c = read_file(os.path.join(p, "adpcm.c"))
    adpcm_c = strip_includes(adpcm_c, ["adpcm.h"])

    main_code = """
int main(void) {
    struct adpcm_state state;
    state.valprev = 0;
    state.index = 0;

    #define SAMPLES 1000
    char adpcm_in[SAMPLES / 2];
    short pcm_out[SAMPLES];
    int i, rep;

    for (i = 0; i < SAMPLES / 2; i++) {
        adpcm_in[i] = (char)((i * 37) & 0xFF);
    }

    for (rep = 0; rep < 100; rep++) {
        struct adpcm_state cur = state;
        adpcm_decoder(adpcm_in, pcm_out, SAMPLES, &cur);
    }
    printf("ADPCM decoder 100 iterations completed.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n"
        + adpcm_h + "\n\n"
        + adpcm_c + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_telecom_adpcm_d_merged.c",
        code,
        ["adpcm.h", "adpcm.c", "rawdaudio.c"],
        "Merged adpcm.h and adpcm.c, replaced blocking stdin with in-memory ADPCM decoder loop"
    )


def build_cbench_crc32():
    p = os.path.join(CBENCH_DIR, "cbench-telecom-crc32")
    snip_h = read_file(os.path.join(p, "sniptype.h"))
    crc_h = read_file(os.path.join(p, "crc.h"))
    crc_c = read_file(os.path.join(p, "crc_32.c"))

    crc_h = strip_includes(crc_h, ["sniptype.h"])
    crc_c = strip_includes(crc_c, ["sniptype.h", "crc.h"])
    
    idx = crc_c.find("main1")
    cut_idx = crc_c.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = crc_c.rfind("int", 0, idx)
    crc_body = crc_c[:cut_idx]

    main_code = """
int main(int argc, char *argv[]) {
    char test_buf[1024];
    DWORD crc = 0;
    int i, rep;
    for (i = 0; i < 1024; i++) test_buf[i] = (char)((i * 31) & 0xFF);
    for (rep = 0; rep < 1000; rep++) {
        crc = crc32buf(test_buf, sizeof(test_buf));
        test_buf[rep % 1024] ^= (char)(crc & 0xFF);
    }
    printf("CRC32 result: %08lX\\n", crc);
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        + snip_h + "\n\n"
        + crc_h + "\n\n"
        + crc_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "cbench_telecom_crc32_merged.c",
        code,
        ["sniptype.h", "crc.h", "crc_32.c"],
        "Inlined sniptype.h and crc.h and added in-memory buffer CRC-32 benchmark loop"
    )


# ==============================================================================
# MiBench Builders
# ==============================================================================

def build_mibench_basicmath_small():
    p = os.path.join(MIBENCH_DIR, "automotive", "basicmath")
    snip_h = read_file(os.path.join(p, "sniptype.h"))
    snipmath_h = read_file(os.path.join(p, "snipmath.h"))
    round_h = read_file(os.path.join(p, "round.h"))
    pi_h = read_file(os.path.join(p, "pi.h"))
    cubic_c = read_file(os.path.join(p, "cubic.c"))
    isqrt_c = read_file(os.path.join(p, "isqrt.c"))
    rad2deg_c = read_file(os.path.join(p, "rad2deg.c"))
    basic_c = read_file(os.path.join(p, "basicmath_small.c"))

    headers_to_strip = ["sniptype.h", "snipmath.h", "round.h", "pi.h"]
    snipmath_h = strip_includes(snipmath_h, headers_to_strip)
    cubic_c = strip_includes(cubic_c, headers_to_strip)
    isqrt_c = strip_includes(isqrt_c, headers_to_strip)
    rad2deg_c = strip_includes(rad2deg_c, headers_to_strip)
    basic_c = strip_includes(basic_c, headers_to_strip)

    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n"
        + snip_h + "\n\n"
        + round_h + "\n\n"
        + "#undef rad2deg\n#undef deg2rad\n"
        + snipmath_h + "\n\n"
        + pi_h + "\n\n"
        + cubic_c + "\n\n"
        + isqrt_c + "\n\n"
        + rad2deg_c + "\n\n"
        + basic_c
    )
    return test_and_install(
        "mibench_basicmath_small_merged.c",
        code,
        ["sniptype.h", "snipmath.h", "round.h", "pi.h", "cubic.c", "isqrt.c", "rad2deg.c", "basicmath_small.c"],
        "Merged all math helper files and headers into standalone basicmath benchmark"
    )


def build_mibench_bitcnts():
    p = os.path.join(MIBENCH_DIR, "automotive", "bitcount")
    snip_h = read_file(os.path.join(p, "sniptype.h"))
    bitops_h = read_file(os.path.join(p, "bitops.h"))
    b1 = read_file(os.path.join(p, "bitcnt_1.c"))
    b2 = read_file(os.path.join(p, "bitcnt_2.c"))
    b3 = read_file(os.path.join(p, "bitcnt_3.c"))
    b4 = read_file(os.path.join(p, "bitcnt_4.c"))
    bstr = read_file(os.path.join(p, "bstr_i.c"))
    bitcnts = read_file(os.path.join(p, "bitcnts.c"))

    headers_to_strip = ["sniptype.h", "extkword.h", "conio.h", "bitops.h"]
    bitops_h = strip_includes(bitops_h, headers_to_strip)
    b1 = strip_includes(b1, headers_to_strip)
    b2 = strip_includes(b2, headers_to_strip)
    b3 = strip_includes(b3, headers_to_strip)
    b4 = strip_includes(b4, headers_to_strip)
    bstr = strip_includes(bstr, headers_to_strip)
    bitcnts = strip_includes(bitcnts, headers_to_strip)

    b4 = b4.replace("static char bits[256]", "static char bits_b4[256]").replace("bits[", "bits_b4[")
    b4 = b4.replace(
        "int cnt = bits_b4[(int)(x & 0x0000000FL)];\n\n      if (0L != (x >>= 4))\n            cnt += ntbl_bitcnt(x);",
        "unsigned long ux = (unsigned long)x;\n      int cnt = bits_b4[(int)(ux & 0x0000000FL)];\n\n      if (0UL != (ux >>= 4))\n            cnt += ntbl_bitcnt((long)ux);"
    )

    # In bitcnts.c, replace argc check with default iterations = 1000
    bitcnts = bitcnts.replace(
        "if (argc<2) {\n    fprintf(stderr,\"Usage: bitcnts <iterations>\\n\");\n    exit(-1);\n\t}\n  iterations=atoi(argv[1]);",
        "iterations = (argc >= 2) ? atoi(argv[1]) : 1000;"
    )

    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <limits.h>\n#include <time.h>\n#include <float.h>\n\n"
        "#define CDECL\n"
        + snip_h + "\n\n"
        + bitops_h + "\n\n"
        + b1 + "\n\n" + b2 + "\n\n" + b3 + "\n\n" + b4 + "\n\n" + bstr + "\n\n"
        + bitcnts
    )
    return test_and_install(
        "mibench_bitcnts_merged.c",
        code,
        ["sniptype.h", "bitops.h", "bitcnt_1.c", "bitcnt_2.c", "bitcnt_3.c", "bitcnt_4.c", "bstr_i.c", "bitcnts.c"],
        "Merged 7 bit counting subroutines, dropped DOS conio.h, added default iterations=1000"
    )


def build_mibench_qsort_small():
    p = os.path.join(MIBENCH_DIR, "automotive", "qsort")
    src = read_file(os.path.join(p, "qsort_small.c"))
    
    idx = src.find("main(")
    cut_idx = src.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = src.rfind("int", 0, idx)
    body = src[:cut_idx]

    main_code = """
static struct myStringStruct array[MAXARRAY];

int main(int argc, char *argv[]) {
    FILE *fp;
    int i, count = 0;

    if (argc >= 2 && (fp = fopen(argv[1], "r")) != NULL) {
        while ((fscanf(fp, "%127s", array[count].qstring) == 1) && (count < MAXARRAY)) {
            count++;
        }
        fclose(fp);
    } else {
        const char *words[] = {
            "compiler", "optimization", "pipeline", "benchmark", "dataset", "features",
            "runtime", "instruction", "register", "allocation", "vectorization", "loop",
            "unrolling", "inlining", "clang", "gcc", "llvm", "binary", "profile", "speed"
        };
        for (i = 0; i < 200; i++) {
            snprintf(array[count].qstring, sizeof(array[count].qstring), "%s_%03d", words[i % 20], (i * 37) % 100);
            count++;
        }
    }
    qsort(array, count, sizeof(struct myStringStruct), compare);
    printf("Sorted %d words successfully.\\n", count);
    return 0;
}
"""
    code = body + "\n\n" + main_code
    return test_and_install(
        "mibench_qsort_small_merged.c",
        code,
        ["qsort_small.c"],
        "Deduplicated self-concatenated source and provided synthetic string vocabulary"
    )


def build_mibench_dijkstra_small():
    p = os.path.join(MIBENCH_DIR, "network", "dijkstra")
    src = read_file(os.path.join(p, "dijkstra_small.c"))
    body = src[:src.find("int main(")]

    main_code = """
int main(int argc, char *argv[]) {
    int i, j, k;
    FILE *fp;

    if (argc >= 2 && (fp = fopen(argv[1], "r")) != NULL) {
        for (i = 0; i < NUM_NODES; i++) {
            for (j = 0; j < NUM_NODES; j++) {
                fscanf(fp, "%d", &k);
                AdjMatrix[i][j] = k;
            }
        }
        fclose(fp);
    } else {
        for (i = 0; i < NUM_NODES; i++) {
            for (j = 0; j < NUM_NODES; j++) {
                AdjMatrix[i][j] = (i == j) ? 0 : ((i * 13 + j * 29) % 40 + 1);
            }
        }
    }

    for (i = 0; i < 20; i++) {
        dijkstra(0, i);
    }
    printf("MiBench Dijkstra completed successfully.\\n");
    return 0;
}
"""
    code = "#include <stdio.h>\n#include <stdlib.h>\n" + body + "\n\n" + main_code
    return test_and_install(
        "mibench_dijkstra_small_merged.c",
        code,
        ["dijkstra_small.c"],
        "Deduplicated self-concatenated source, included stdlib.h, added in-memory graph generator"
    )


def build_mibench_patricia():
    p = os.path.join(MIBENCH_DIR, "network", "patricia")
    pat_h = read_file(os.path.join(p, "patricia.h"))
    pat_c = read_file(os.path.join(p, "patricia.c"))
    pat_test = read_file(os.path.join(p, "patricia_test.c"))

    pat_c = strip_includes(pat_c, ["patricia.h"])
    pat_test = strip_includes(pat_test, ["patricia.h", "err.h"])
    
    idx = pat_test.find("main(")
    cut_idx = pat_test.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = pat_test.rfind("int", 0, idx)
    pat_test_body = pat_test[:cut_idx]

    main_code = """
int main(int argc, char **argv) {
    struct ptree *phead;
    struct ptree_mask *pm;
    struct ptree *p;
    float time = 0.0f;
    struct in_addr addr;
    int i;

    phead = (struct ptree *)malloc(sizeof(struct ptree));
    if (!phead) exit(1);
    memset(phead, 0, sizeof(*phead));

    pm = (struct ptree_mask *)malloc(sizeof(struct ptree_mask));
    if (!pm) exit(1);
    memset(pm, 0, sizeof(*pm));
    pm->pm_data = (struct ptree_mask_data *)malloc(sizeof(struct ptree_mask_data));
    if (!pm->pm_data) exit(1);
    memset(pm->pm_data, 0, sizeof(*pm->pm_data));

    phead->p_mlen = 1;
    phead->p_left = phead->p_right = phead;

    for (i = 0; i < 150; i++) {
        time = (float)i * 0.1f;
        addr.s_addr = htonl((unsigned int)(0xC0A80000 + i * 257));
        p = (struct ptree *)malloc(sizeof(struct ptree));
        if (!p) exit(1);
        memset(p, 0, sizeof(*p));
        p->p_m = (struct ptree_mask *)malloc(sizeof(struct ptree_mask));
        if (!p->p_m) exit(1);
        memset(p->p_m, 0, sizeof(*p->p_m));
        p->p_m->pm_data = (struct ptree_mask_data *)malloc(sizeof(struct ptree_mask_data));
        if (!p->p_m->pm_data) exit(1);
        memset(p->p_m->pm_data, 0, sizeof(*p->p_m->pm_data));

        p->p_key = addr.s_addr;
        ((struct ptree_mask_data *)p->p_m->pm_data)->pmd_time = time;
        p->p_mlen = 24;
        pat_insert(p, phead);
    }

    for (i = 0; i < 75; i++) {
        addr.s_addr = htonl((unsigned int)(0xC0A80000 + i * 257));
        pat_search(addr.s_addr, phead);
    }
    printf("MiBench Patricia trie completed successfully.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
        "#define bcopy(b1,b2,len) memmove(b2, b1, len)\n"
        "#define bzero(b,len) memset(b, 0, len)\n\n"
        + pat_h + "\n\n"
        + "struct ptree_mask_data { float pmd_time; };\n\n"
        + pat_c + "\n\n"
        + pat_test_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "mibench_patricia_merged.c",
        code,
        ["patricia.h", "patricia.c", "patricia_test.c"],
        "Merged patricia.h and patricia.c with test harness and synthetic IPv4 prefix queries"
    )


def build_mibench_stringsearch():
    p = os.path.join(MIBENCH_DIR, "office", "stringsearch")
    src = read_file(os.path.join(p, "pbmsrch_small.c"))
    src = src.replace("main()\n{", "int main(void)\n{")
    code = "#include <stdio.h>\n#include <stdlib.h>\n" + src
    return test_and_install(
        "mibench_stringsearch_merged.c",
        code,
        ["pbmsrch_small.c", "search.h"],
        "Clean single Pratt-Boyer-Moore stringsearch implementation with in-memory pattern suite"
    )


def build_mibench_blowfish():
    p = os.path.join(MIBENCH_DIR, "security", "blowfish")
    bf_h = read_file(os.path.join(p, "blowfish.h"))
    locl_h = read_file(os.path.join(p, "bf_locl.h"))
    pi_h = read_file(os.path.join(p, "bf_pi.h"))
    b1 = read_file(os.path.join(p, "bf_enc.c"))
    b2 = read_file(os.path.join(p, "bf_skey.c"))
    b3 = read_file(os.path.join(p, "bf_cbc.c"))
    b4 = read_file(os.path.join(p, "bf_cfb64.c"))
    b5 = read_file(os.path.join(p, "bf_ecb.c"))
    b6 = read_file(os.path.join(p, "bf_ofb64.c"))
    btest = read_file(os.path.join(p, "bftest.c"))

    headers_to_strip = ["blowfish.h", "bf_locl.h", "bf_pi.h"]
    cleaned_sources = []
    for src in [b1, b2, b3, b4, b5, b6, btest]:
        s = strip_includes(src, headers_to_strip)
        s = re.sub(r'#include\s*<sys/times\.h>', '#include <time.h>', s)
        cleaned_sources.append(s)

    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <time.h>\n\n"
        + bf_h + "\n\n"
        + locl_h + "\n\n"
        + pi_h + "\n\n"
        + "\n\n".join(cleaned_sources)
    )
    return test_and_install(
        "mibench_blowfish_merged.c",
        code,
        ["blowfish.h", "bf_locl.h", "bf_pi.h", "bf_enc.c", "bf_skey.c", "bf_cbc.c", "bf_cfb64.c", "bf_ecb.c", "bf_ofb64.c", "bftest.c"],
        "Merged Blowfish cipher modes and test suite, removed POSIX sys/times.h dependency"
    )


def build_mibench_sha():
    p = os.path.join(MIBENCH_DIR, "security", "sha")
    sha_h = read_file(os.path.join(p, "sha.h"))
    sha_c = read_file(os.path.join(p, "sha.c"))
    sha_driver = read_file(os.path.join(p, "sha_driver.c"))

    sha_c = strip_includes(sha_c, ["sha.h"])
    sha_driver = strip_includes(sha_driver, ["sha.h"])
    sha_driver_body = sha_driver[:sha_driver.find("int main(")]

    main_code = """
int main(int argc, char *argv[]) {
    SHA_INFO sha_info;
    BYTE sample[64] = "The quick brown fox jumps over the lazy dog 0123456789 ABCDEF!";
    int i;
    for (i = 0; i < 500; i++) {
        sample[i % 60] ^= (BYTE)(i & 0xFF);
        sha_init(&sha_info);
        sha_update(&sha_info, sample, 62);
        sha_final(&sha_info);
    }
    printf("MiBench SHA-1 500 rounds complete: %08lx %08lx\\n", sha_info.digest[0], sha_info.digest[1]);
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        + sha_h + "\n\n"
        + sha_c + "\n\n"
        + sha_driver_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "mibench_sha_merged.c",
        code,
        ["sha.h", "sha.c", "sha_driver.c"],
        "Included stdio.h before sha.h, merged sha.c and in-memory digest calculation loop"
    )


def build_mibench_adpcm_rawcaudio():
    p = os.path.join(MIBENCH_DIR, "telecomm", "adpcm", "src")
    adpcm_h = read_file(os.path.join(p, "adpcm.h"))
    adpcm_c = read_file(os.path.join(p, "adpcm.c"))
    adpcm_c = strip_includes(adpcm_c, ["adpcm.h"])

    main_code = """
int main(void) {
    struct adpcm_state state;
    state.valprev = 0;
    state.index = 0;

    #define SAMPLES 1000
    short pcm_in[SAMPLES];
    char adpcm_out[SAMPLES / 2];
    int i, rep;

    for (i = 0; i < SAMPLES; i++) {
        pcm_in[i] = (short)(sin(i * 0.05) * 16000.0);
    }

    for (rep = 0; rep < 100; rep++) {
        struct adpcm_state cur = state;
        adpcm_coder(pcm_in, adpcm_out, SAMPLES, &cur);
    }
    printf("MiBench ADPCM coder 100 iterations completed.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n"
        + adpcm_h + "\n\n"
        + adpcm_c + "\n\n"
        + main_code
    )
    return test_and_install(
        "mibench_adpcm_rawcaudio_merged.c",
        code,
        ["adpcm.h", "adpcm.c", "rawcaudio.c"],
        "Merged adpcm.h and adpcm.c with in-memory sinusoidal PCM audio coder loop"
    )


def build_mibench_adpcm_rawdaudio():
    p = os.path.join(MIBENCH_DIR, "telecomm", "adpcm", "src")
    adpcm_h = read_file(os.path.join(p, "adpcm.h"))
    adpcm_c = read_file(os.path.join(p, "adpcm.c"))
    adpcm_c = strip_includes(adpcm_c, ["adpcm.h"])

    main_code = """
int main(void) {
    struct adpcm_state state;
    state.valprev = 0;
    state.index = 0;

    #define SAMPLES 1000
    char adpcm_in[SAMPLES / 2];
    short pcm_out[SAMPLES];
    int i, rep;

    for (i = 0; i < SAMPLES / 2; i++) {
        adpcm_in[i] = (char)((i * 37) & 0xFF);
    }

    for (rep = 0; rep < 100; rep++) {
        struct adpcm_state cur = state;
        adpcm_decoder(adpcm_in, pcm_out, SAMPLES, &cur);
    }
    printf("MiBench ADPCM decoder 100 iterations completed.\\n");
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <math.h>\n\n"
        + adpcm_h + "\n\n"
        + adpcm_c + "\n\n"
        + main_code
    )
    return test_and_install(
        "mibench_adpcm_rawdaudio_merged.c",
        code,
        ["adpcm.h", "adpcm.c", "rawdaudio.c"],
        "Merged adpcm.h and adpcm.c with in-memory ADPCM audio decoder loop"
    )


def build_mibench_crc32():
    p = os.path.join(MIBENCH_DIR, "telecomm", "CRC32")
    snip_h = read_file(os.path.join(p, "sniptype.h"))
    crc_h = read_file(os.path.join(p, "crc.h"))
    crc_c = read_file(os.path.join(p, "crc_32.c"))

    crc_h = strip_includes(crc_h, ["sniptype.h"])
    crc_c = strip_includes(crc_c, ["sniptype.h", "crc.h"])
    
    idx = crc_c.find("main(")
    cut_idx = crc_c.rfind("\nint\n", 0, idx)
    if cut_idx == -1:
        cut_idx = crc_c.rfind("int", 0, idx)
    crc_body = crc_c[:cut_idx]

    main_code = """
int main(int argc, char *argv[]) {
    char test_buf[1024];
    DWORD crc = 0;
    int i, rep;
    for (i = 0; i < 1024; i++) test_buf[i] = (char)((i * 31) & 0xFF);
    for (rep = 0; rep < 1000; rep++) {
        crc = crc32buf(test_buf, sizeof(test_buf));
        test_buf[rep % 1024] ^= (char)(crc & 0xFF);
    }
    printf("MiBench CRC32 result: %08lX\\n", crc);
    return 0;
}
"""
    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        + snip_h + "\n\n"
        + crc_h + "\n\n"
        + crc_body + "\n\n"
        + main_code
    )
    return test_and_install(
        "mibench_crc32_merged.c",
        code,
        ["sniptype.h", "crc.h", "crc_32.c"],
        "Merged sniptype.h, crc.h, crc_32.c with in-memory buffer CRC-32 benchmark loop"
    )


def build_mibench_fft():
    p = os.path.join(MIBENCH_DIR, "telecomm", "FFT")
    fourier_h = read_file(os.path.join(p, "fourier.h"))
    ddc_h = read_file(os.path.join(p, "ddc.h"))
    ddcmath_h = read_file(os.path.join(p, "ddcmath.h"))
    fourierf_c = read_file(os.path.join(p, "fourierf.c"))
    fftmisc_c = read_file(os.path.join(p, "fftmisc.c"))
    main_c = read_file(os.path.join(p, "main.c"))

    headers_to_strip = ["fourier.h", "ddc.h", "ddcmath.h"]
    ddcmath_h = strip_includes(ddcmath_h, headers_to_strip)
    fourierf_c = strip_includes(fourierf_c, headers_to_strip)
    fftmisc_c = strip_includes(fftmisc_c, headers_to_strip)
    main_c = strip_includes(main_c, headers_to_strip)

    # In main.c, handle argc
    main_c = main_c.replace(
        "int main(int argc, char *argv[]) {",
        "int main(int argc, char *argv[]) {\n\t#include <string.h>\n"
    )
    main_c = main_c.replace(
        """	if (argc<3)
	{
		printf("Usage: fft <waves> <length> -i\\n");
		printf("-i performs an inverse fft\\n");
		printf("make <waves> random sinusoids");
		printf("<length> is the number of samples\\n");
		exit(-1);
	}
	else if (argc==4)
		invfft = !strncmp(argv[3],"-i",2);
	MAXSIZE=atoi(argv[2]);
	MAXWAVES=atoi(argv[1]);""",
        """	if (argc >= 3) {
		MAXWAVES = atoi(argv[1]);
		MAXSIZE = atoi(argv[2]);
		if (argc == 4) invfft = !strncmp(argv[3], "-i", 2);
	} else {
		MAXWAVES = 4;
		MAXSIZE = 512;
		invfft = 0;
	}"""
    )

    code = (
        "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <math.h>\n\n"
        + fourier_h + "\n\n"
        + ddc_h + "\n\n"
        + ddcmath_h + "\n\n"
        + fourierf_c + "\n\n"
        + fftmisc_c + "\n\n"
        + main_c
    )
    return test_and_install(
        "mibench_fft_merged.c",
        code,
        ["fourier.h", "ddc.h", "ddcmath.h", "fourierf.c", "fftmisc.c", "main.c"],
        "Merged fourier.h, ddc.h, ddcmath.h, fourierf.c, fftmisc.c, added default waves=4, samples=512 for standalone execution"
    )


def update_manifest():
    manifest = []
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    existing_programs = {m["program"] for m in manifest}

    cbench_merged = sorted([f for f in os.listdir(PROGRAMS_DIR) if f.startswith("cbench_") and f.endswith("_merged.c")])
    mibench_merged = sorted([f for f in os.listdir(PROGRAMS_DIR) if f.startswith("mibench_") and f.endswith("_merged.c")])

    today = "2026-10-14"
    added = 0
    for p in cbench_merged:
        if p not in existing_programs:
            manifest.append({
                "program": p,
                "source": "cbench",
                "original_path": f"programs/{p}",
                "license": "Open Source / cTuning",
                "date_added": today
            })
            added += 1

    for p in mibench_merged:
        if p not in existing_programs:
            manifest.append({
                "program": p,
                "source": "mibench",
                "original_path": f"programs/{p}",
                "license": "GPL / BSD / Public Domain",
                "date_added": today
            })
            added += 1

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest updated: {added} new merged benchmark programs registered.")


def main():
    print("=" * 60)
    print("STEP 2: RE-INTEGRATING CBENCH & MIBENCH")
    print("=" * 60)

    with open(FIX_LOG, "w", encoding="utf-8") as f:
        f.write("# cBench & MiBench Fix Log\n# Format: {filename, original_files_merged, fix_applied, compile_status}\n\n")

    print("\n--- Processing cBench ---")
    cbench_results = [
        build_cbench_qsort1(),
        build_cbench_dijkstra(),
        build_cbench_patricia(),
        build_cbench_stringsearch2(),
        build_cbench_rijndael(),
        build_cbench_sha(),
        build_cbench_adpcm_c(),
        build_cbench_adpcm_d(),
        build_cbench_crc32(),
    ]

    print("\n--- Processing MiBench ---")
    mibench_results = [
        build_mibench_basicmath_small(),
        build_mibench_bitcnts(),
        build_mibench_qsort_small(),
        build_mibench_dijkstra_small(),
        build_mibench_patricia(),
        build_mibench_stringsearch(),
        build_mibench_blowfish(),
        build_mibench_sha(),
        build_mibench_adpcm_rawcaudio(),
        build_mibench_adpcm_rawdaudio(),
        build_mibench_crc32(),
        build_mibench_fft(),
    ]

    print("\n" + "=" * 60)
    print(f"cBench merged and tested: {sum(cbench_results)} / {len(cbench_results)} succeeded")
    print(f"MiBench merged and tested: {sum(mibench_results)} / {len(mibench_results)} succeeded")
    print("=" * 60)

    update_manifest()


if __name__ == "__main__":
    main()
