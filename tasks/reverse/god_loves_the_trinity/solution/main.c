#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#define MAX_LEN 64

uint8_t func_l0(char c, int i) { return c ^ (i * 3); }
uint8_t func_l1(char c, int i) { return (c + i) & 0xFF; }

uint8_t func_l2(char c, int i) { return (c << 1) ^ i; }
uint8_t func_l3(char c, int i) { return (c - i * 2) & 0xFF; }

uint8_t func_l4(char c, int i) { return (c ^ 0x55) + i; }
uint8_t func_l5(char c, int i) { return (c + 13) ^ (i * 4); }

uint8_t func_p0(char c, int i) { return (c ^ 0x33) + (i * 2); }
uint8_t func_p1(char c, int i) { return (c - i) ^ 0x77; }

uint8_t func_p2(char c, int i) { return (c * 2) + i; }
uint8_t func_p3(char c, int i) { return (c ^ (i * 5)) & 0xFF; }

uint8_t func_p4(char c, int i) { return ((c + i * 3) ^ 0xAA); }
uint8_t func_p5(char c, int i) { return ((c ^ 0x11) + (i << 1)); }

typedef uint8_t (*mod_func)(char, int);

mod_func login_mod_funcs[6][2] = {
    {func_l0, func_l1},
    {func_l2, func_l3},
    {func_l4, func_l5},
    {func_l0, func_l2},
    {func_l1, func_l3},
    {func_l4, func_l0}
};

mod_func pass_mod_funcs[6][2] = {
    {func_p0, func_l1},
    {func_l2, func_p3},
    {func_p4, func_l5},
    {func_p0, func_l2},
    {func_l1, func_p3},
    {func_p4, func_l0}
};

int modkey_index(int i) {
    return i % 3;
}

void modulate(const char *input, const char *modkey, mod_func funcs[6][2], uint8_t out[6]) {
    for (int i = 0; i < 6; ++i) {
        int bit_index = modkey_index(i);
        int bit = (modkey[bit_index] == '1') ? 1 : 0;
        char c = (i < strlen(input)) ? input[i] : 0;
        out[i] = funcs[i][bit](c, i);
    }
}

int check_match(uint8_t a[6], uint8_t b[6]) {
    int delta = 0;
    for (int i = 0; i < 6; ++i)
        delta |= a[i] ^ b[i];
    return delta == 0;
}

int main() {
    char login[MAX_LEN], password[MAX_LEN], modkey[4]; 
    uint8_t login_result[6], pass_result[6];

    puts("⚓ Воронеж. Год 1703.");
    puts("Ты стоишь у входа в секретное хранилище корабельных чертежей на верфи.");
    puts("Перед тобой массивный дубовый люк с механизмом, встроенным Петром лично.");
    puts("Чтобы открыть шлюз, нужны три вещи:");
    puts("   - Имя мастера");
    puts("   - Кодовая фраза");
    puts("   - Механический ключ");

    printf("\nИмя мастера: ");
    scanf("%63s", login);
    printf("Кодовая фраза: ");
    scanf("%63s", password);
    printf("Механический ключ: ");
    scanf("%3s", modkey);

    if (strlen(modkey) != 3 || strspn(modkey, "01") != 3) {
        fprintf(stderr, "\nОшибка: Ключ должен состоять из трёх символов 0 и 1.\n");
        puts("Механизм заблокирован. Возможно, дозор уже услышал щелчок.");
        return 1;
    }

    modulate(login, modkey, login_mod_funcs, login_result);
    modulate(password, modkey, pass_mod_funcs, pass_result);

    puts("\n🔎 Проводится сверка личных данных с архивом...");

    if (check_match(login_result, pass_result)) {
        puts("Замок прокрутился. Люк со скрипом приоткрывается.");
        puts("Добро пожаловать на тайную верфь!");
    } else {
        puts("\nКодовая фраза не соответствует ожиданиям.");
        puts("Механизм молчит.");
        puts("Возможно, стоит попробовать ещё раз... если успеешь.");
    }

    return 0;
}

