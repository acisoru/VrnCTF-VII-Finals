#include <stdio.h>
#include <string.h>
#include <stdio.h>

char key_correct[] = "ЦАРЬ_ПЕТР_ВЕЛИКИЙ";

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin, NULL, _IONBF, 0);

    printf("Указъ Царя Петра Алексеевича о корабельных командахъ:\n1) Поднять_флагъ - поднять Андреевский флаг\n2) Опустить_флагъ - спустить флаг\n3) Палить_из_пушекъ - дать залп из всех орудий\n4) Уйти_в_тень - скрыть корабль в тумане\n");

    char check[] = "ВОРОНЕЖСКАЯ_ВЕРФЬ";
    char command[10];
    
    while(1) {
        printf(">> ");
        gets(command);

        if(!strcmp(command, "Поднять_флагъ")) 
            printf("Андреевский флаг поднят! Слава Русскому Флоту!\n");
        else if(!strcmp(command, "Опустить_флагъ"))
            printf("Флаг спущен. Корабль в гавани.\n");
        else if(!strcmp(command, "Паить_из_пушекъ"))
            printf("Пушки заряжены... Пли!\n");
        else if(!strcmp(command, "Уйти_в_тень"))
            printf("Корабль скрылся в тумане. Невидим для врага.\n");
        else if (strcmp(check, key_correct) == 0) {
            FILE* file = fopen("flag", "r");
            char flag[29];
            fgets(flag, 29, file);
            printf("%s\n", flag);
        }
    }


    return 0;
}
