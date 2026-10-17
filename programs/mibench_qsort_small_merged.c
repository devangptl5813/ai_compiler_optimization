#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define UNLIMIT
#define MAXARRAY 60000 /* this number, if too large, will cause a seg. fault!! */

struct myStringStruct {
  char qstring[128];
};

int compare(const void *elem1, const void *elem2)
{
  int result;
  
  result = strcmp((*((struct myStringStruct *)elem1)).qstring, (*((struct myStringStruct *)elem2)).qstring);

  return (result < 0) ? 1 : ((result == 0) ? 0 : -1);
}




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
    printf("Sorted %d words successfully.\n", count);
    return 0;
}
