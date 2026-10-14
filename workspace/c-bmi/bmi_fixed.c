/*
 * BMI 测试机器人 —— 修正版（可直接编译运行）
 *
 * 编译（任选其一）：
 *   MSVC : cl /utf-8 /W4 bmi_fixed.c
 *   GCC  : gcc -std=c11 -Wall -Wextra bmi_fixed.c -o bmi
 *   Clang: clang -std=c11 -Wall -Wextra bmi_fixed.c -o bmi
 *
 * 与原始版本相比的改动见文件末尾注释。
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * 读取一整行（自动去掉行尾的 '\n'）。
 * 返回 1 表示成功读到一行；返回 0 表示输入已结束(EOF)，调用方应结束程序。
 * 要点：fgets 有长度上限，不会像 scanf("%s") 那样写出缓冲区。
 */
static int read_line(char *buf, size_t size)
{
    if (fgets(buf, (int)size, stdin) == NULL) {
        return 0;                       /* EOF：没有更多输入 */
    }

    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';            /* 去掉换行 */
    } else {
        int ch;                         /* 这一行超长，丢掉剩余字符，避免污染下一次读取 */
        while ((ch = getchar()) != '\n' && ch != EOF) {
            /* 空循环 */
        }
    }
    return 1;
}

/*
 * 反复提示并读取一个合法数字，直到成功为止。
 * 返回 1 表示读到数字；返回 0 表示 EOF（此时调用方应结束程序，绝不能死循环）。
 * 要点：检查 strtod 的解析结果，非法输入不会被静默忽略。
 */
static int read_number(const char *prompt, double *value)
{
    char line[64];

    for (;;) {
        printf("%s", prompt);
        if (!read_line(line, sizeof line)) {
            printf("\n");
            return 0;
        }
        if (line[0] == '\0') {
            printf("Robot: That was an empty line. Please type a number.\n");
            continue;
        }

        char *end = NULL;
        double parsed = strtod(line, &end);
        if (end == line) {              /* 一个数字都没解析出来 */
            printf("Robot: \"%s\" is not a number. Please try again.\n", line);
            continue;
        }
        while (*end == ' ' || *end == '\t') {
            end++;                      /* 允许数字后面跟空白 */
        }
        if (*end != '\0') {             /* 数字后面还有别的东西 */
            printf("Robot: Please type only a number (unexpected \"%s\").\n", end);
            continue;
        }

        *value = parsed;
        return 1;
    }
}

int main(void)
{
    char name[40];
    double age = 0.0;                   /* 原程序读了年龄却没用到；这里同样保留 */
    double weight = 0.0, height_cm = 0.0;
    double height_m, bmi;

    printf("Robot: Hi, What's your name?\nI:");
    if (!read_line(name, sizeof name)) {
        printf("\nRobot: I could not read your name. Bye.\n");
        return 0;
    }
    if (name[0] == '\0') {
        snprintf(name, sizeof name, "%s", "friend");  /* 直接回车时给个默认称呼 */
    }

    printf("Robot: Hello, %s, Nice to meet you. Let's test your BMI.\n", name);

    printf("Robot: Well, %s, how old are you?\n", name);
    if (!read_number("I:", &age)) {
        printf("Robot: I could not read your age. Bye.\n");
        return 0;
    }

    printf("Robot: Ok, %s, what's your weight in kilograms?\n", name);
    if (!read_number("I:", &weight)) {
        printf("Robot: I could not read your weight. Bye.\n");
        return 0;
    }

    printf("Robot: Well, %s, what's your height in centimeters?\n", name);
    if (!read_number("I:", &height_cm)) {
        printf("Robot: I could not read your height. Bye.\n");
        return 0;
    }

    /* 防止除零或负数造成 inf / nan 这类无意义结果 */
    if (height_cm <= 0.0) {
        printf("Robot: Height must be greater than 0. Cannot compute BMI.\n");
        return 0;
    }
    if (weight <= 0.0) {
        printf("Robot: Weight must be greater than 0. Cannot compute BMI.\n");
        return 0;
    }

    height_m = height_cm / 100.0;       /* 厘米换算成米 */
    bmi = weight / (height_m * height_m);

    printf("Robot: Well, %s, your BMI is %.2f, ", name, bmi);
    if (bmi < 18.5) {
        printf("you are underweight.\n");
    } else if (bmi < 24.0) {
        printf("you are normal.\n");
    } else if (bmi < 28.0) {
        printf("you are overweight.\n");
    } else {
        printf("you are obese.\n");
    }

    return 0;
}

/*
 * 与原版相比的改动：
 *  1. 姓名用 fgets 读取并限制长度 —— 原版 scanf("%s", name) 一旦输入超过 39 个字符
 *     就会越界写内存（栈溢出）。顺带还能正确接受带空格的名字。
 *  2. 删除手工清缓冲的 while(getchar()) —— 它会吞掉"同一行里后面输入的内容"。
 *  3. 数字全部改用 read_line + strtod，并检查解析结果：输入非数字时会提示重输，
 *     而不是让 scanf 失败后残留的数据继续错位。
 *  4. 增加 height/weight <= 0 的检查 —— 原版身高为 0 时会做浮点除零，得到 inf/nan，
 *     然后被当成 obese 打印出来。
 *  5. 处理 EOF（输入流结束）时正常退出，不会卡在死循环里。
 *  6. 分档条件改为 < 18.5 / < 24.0 / < 28.0，与原版 18.4/18.5/23.9/24.0 的分界等价，
 *     但不会漏掉 18.45 这类夹缝值。
 *  7. 修正输出里的笔误 "you BMI is" -> "your BMI is"。
 */
