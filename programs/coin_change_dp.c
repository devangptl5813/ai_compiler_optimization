#include <stdio.h>
#include <stdlib.h>

#define COINS 10
#define AMOUNT 15000

int min_coins(int coins[], int n, int amount) {
    int *dp = (int *)malloc((amount + 1) * sizeof(int));
    dp[0] = 0;
    for (int i = 1; i <= amount; i++) dp[i] = 1000000;

    for (int i = 1; i <= amount; i++) {
        for (int j = 0; j < n; j++) {
            if (coins[j] <= i) {
                int sub_res = dp[i - coins[j]];
                if (sub_res != 1000000 && sub_res + 1 < dp[i]) {
                    dp[i] = sub_res + 1;
                }
            }
        }
    }
    int ans = dp[amount];
    free(dp);
    return ans;
}

int main() {
    int coins[] = {1, 2, 5, 10, 20, 50, 100, 200, 500, 1000};
    int res = min_coins(coins, COINS, AMOUNT);
    printf("Coin change complete: min_coins=%d\n", res);
    return 0;
}
