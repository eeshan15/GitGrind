```c
while (i < 10) {
    j += 2;
    i++;
}
}
printf("%d", i);
}
int main() {
    int i = 9, j = 10;
    func(i, j);
    return 0;
}
```

The output of the program is \_\_\_\_. (answer in integer)

Note: Assume that the program compiles and runs successfully.

```txt
gatecse-2026-set1 programming-in-c output numerical-answers one-mark
```

# Answer key

# 5.8

# Parameter Passing (12)

# 5.8.1 Parameter Passing: GATE CSE 1992 | Question: 10b

Show the activation records and the display structure just after the procedures called at lines marked x and y have started their execution. Be sure to indicate which of the two procedures named A you are referring to.

```txt
Program Test;
  Procedure A;
    Procedure B;
      Procedure A;
      begin
      ......
      end A;
    begin
      y: A;
    end B;
  begin
    B;
  end A;

begin
  x: A;
end Test
```

```txt
gate1992 parameter-passing programming runtime-environment normal descriptive
```

# Answer key

# 5.8.2 Parameter Passing: GATE CSE 1994 | Question: 1.20

In which of the following cases is it possible to obtain different results for call-by-reference and call-by-name parameter passing methods?

A. Passing a constant value as a parameter

C. Passing an array element as a parameter

```txt
gate1994 programming parameter-passing easy
```

B. Passing the address of an array as a parameter

D. Passing an array

# Answer key

# 5.8.3 Parameter Passing: GATE CSE 2001 | Question: 2.17 | UGCNET-AUG2016-III: 21

What is printed by the print statements in the program P1 assuming call by reference parameter passing?

```txt
Program P1()
{
    x = 10;
    y = 3;
    func1(y,x,x)
    print x;
```




```matlab
print y;
}

func1(x,y,z)
{
    y = y + 4;
    z = x + y + z
}
```

A. 10,3

B. 31,3

C. 27, 7

D. None of the above

gatecse-2001 programming-in-c parameter-passing normal ugcnetcse-aug2016-paper3

# Answer key

# 5.8.4 Parameter Passing: GATE CSE 2003 | Question: 73

The following program fragment is written in a programming language that allows global variables and does not allow nested declarations of functions.


```txt
global int i=100, j=5;
void P(x) {
    int i=10;
        print(x+10);
        i=200;
        j=20;
        print (x);
}
main() {P(i+j);}
```

If the programming language uses static scoping and call by need parameter passing mechanism, the values printed by the above program are:

A. 115,220

B. 25,220

C. 25,15

D. 115,105

gatecse-2003 compiler-design normal runtime-environment parameter-passing

# Answer key

# 5.8.5 Parameter Passing: GATE CSE 2008 | Question: 60

What is printed by the following C program?


```c
int f(int x, int *py, int **ppz)
{
    int y, z;
    **ppz += 1; z = **ppz;  // corrected z = *ppz; to z = **ppz;
    *py += 2; y = *py;
    x += 3;
    return x+y+z;
}

void main()
{
    int c, *b, **a;
    c = 4; b = &c; a = &b;
    printf("%d", f(c, b, a));
}
```

A. 18

B. 19

C. 21

D. 22

gatecse-2008 programming programming-in-c normal parameter-passing

# Answer key

# 5.8.6 Parameter Passing: GATE CSE 2010 | Question: 11

What does the following program print?


```c
#include<stdio.h>

void f(int *p, int *q) {
    p=q;
    *p=2;
}
```

```txt
int i=0, j=1;

int main() {
    f(&i, &j);
    printf("%d %d\n", i,j);
    return 0;
}
```

A. 22

B. 21

C. 01

D. 02

gatecse-2010 programming programming-in-c easy parameter-passing

Answer key

# 5.8.7 Parameter Passing: GATE CSE 2013 | Question: 42


What is the return value of $f(p,p)$ , if the value of p is initialized to 5 before the call? Note that the first parameter is passed by reference, whereas the second parameter is passed by value.

```c
int f (int &x, int c) {
    c = c - 1;
    if (c==0) return 1;
    x = x + 1;
    return f(x,c) * x;
}
```

gatecse-2013 compiler-design normal marks-to-all numerical-answers parameter-passing runtime-environment

Answer key

# 5.8.8 Parameter Passing: GATE CSE 2016 | Set 1 | Question: 15

Consider the following C program.


```c
#include <stdio.h>
void mystery (int *ptra, int *ptrb) {
    int *temp;
    temp = ptrb;
    ptrb =ptra;
    ptra = temp;
}
int main () {
    int a = 2016, b=0, c= 4, d= 42;
    mystery (&a, &b);
    if (a < c)
        mystery (&c, &a);
    mystery (&a, &d);
    printf("%d\n", a);
}
```

The output of the program is \_\_\_\_.

gatecse-2016-set1 programming-in-c easy numerical-answers parameter-passing

Answer key

# 5.8.9 Parameter Passing: GATE CSE 2016 | Set 2 | Question: 12

The value printed by the following program is \_\_\_\_.


```c
void f (int * p, int m) {
    m = m + 5;
    *p = *p + m;
    return;
}
void main () {
    int i=5, j=10;

    f (&i, j);
    printf ("%d", i+j);
}
```

# 5.8.10 Parameter Passing: GATE CSE 2018 | Question: 29


```c
#include<stdio.h>
void fun1(char* s1, char* s2){
    char* temp;
    temp = s1;
    s1 = s2;
    s2 = temp;
}
void fun2(char** s1, char** s2){
    char* temp;
    temp = *s1;
    *s1 = *s2;
    *s2 = temp;
}
int main(){
    char *str1="Hi", *str2 = "Bye";
    fun1(str1, str2); printf("%s %s", str1, str2);
    fun2(&str1, &str2); printf("%s %s", str1, str2);
    return 0;
}
```

The output of the program above is:

A. Hi Bye Bye Hi

C. Bye Hi Hi Bye

gatecse-2018 programming-in-c pointers parameter-passing normal programming two-marks

B. Hi Bye Hi Bye

D. Bye Hi Bye Hi

# Answer key

# 5.8.11 Parameter Passing: GATE IT 2006 | Question: 50

Which one of the choices given below would be printed when the following program is executed?


```c
#include <stdio.h>
void swap (int *x, int *y)
{
    static int *temp;
    temp = x;
    x = y;
    y = temp;
}
void printab ()
{
    static int i, a = -3, b = -6;
    i = 0;
    while (i <= 4)
    {
        if ((i++)%2 == 1) continue;
        a = a + i;
        b = b + i;
    }
    swap (&a, &b);
    printf("a = %d, b = %d\n", a, b);
}
main()
{
    printab();
    printab();
}
```

A. $a = 0, b = 3$

$$
a = 0, b = 3
$$

C. $a = 3, b = 6$

$$
a = 3, b = 6
$$

gateit-2006 programming programming-in-c normal parameter-passing

B. $a = 3, b = 0$

$$
a = 1 2, b = 9
$$

D. $a = 6, b = 3$

$$
a = 1 5, b = 1 2
$$

# Answer key

# 5.8.12 Parameter Passing: GATE IT 2008 | Question: 50

Consider the C program below. What does it print?


\# include <stdio.h>

```txt
# define swap1 (a, b) tmp = a; a = b; b = tmp
void swap2 ( int a, int b)
{
    int tmp;
    tmp = a; a = b; b = tmp;
}
void swap3 (int*a, int*b)
{
    int tmp;
    tmp = *a; *a = *b; *b = tmp;
}
int main ()
{
    int num1 = 5, num2 = 4, tmp;
    if (num1 < num2) {swap1 (num1, num2);}
    if (num1 < num2) {swap2 (num1 + 1, num2);}
    if (num1 >= num2) {swap3 (&num1, &num2);}
    printf ("%d, %d", num1, num2);
}
```

A. 5,5

B. 5,4

C. 4,5

D. 4,4

gateit-2008 programming programming-in-c easy parameter-passing

# Answer key

# 5.9

# Pointers (15)

# 5.9.1 Pointers: GATE CSE 2000 | Question: 1.12

The most appropriate matching for the following pairs

<table><tr><td>X: m = malloc(5); m = NULL;</td><td>1: using dangling pointers</td></tr><tr><td>Y: free(n); n -&gt; value = 5;</td><td>2: using uninitialized pointers</td></tr><tr><td>Z: char *p, *p = ‘a’;</td><td>3: lost memory</td></tr></table>

is:

A. $X - 1$ Y-3 Z-2

B. $X - 2$ Y-1 Z-3

C. $X - 3$ Y-2 Z-1

D. $X - 3$ $Y - 1$ $Z - 2$

gatecse-2000 programming programming-in-c easy match-the-following pointers

# Answer key

# 5.9.2 Pointers: GATE CSE 2001 | Question: 2.18

Consider the following three C functions:

[P1]

```c
int *g(void)
{
    int x = 10;
    return (&x);
}
```

[P2]

```c
int *g(void)
{
    int *px;
    *px = 10;
    return px
```

[P3]

```c
int *g(void)
{
    int *px;
    px = (int*) malloc (sizeof(int));
    *px = 10;
    return px;
}
```




Which of the above three functions are likely to cause problems with pointers?

A. Only P3

B. Only $P1$ and $P3$

C. Only $P1$ and $P2$

D. $P1, P2$ and $P3$

gatecse-2001 programming programming-in-c normal pointers

Answer key

# 5.9.3 Pointers: GATE CSE 2003 | Question: 2

Assume the following C variable declaration:

int \*A[10], B[10][10];

Of the following expressions:

1. $A[2]$  
II. $A[2][3]$  
III. $B[1]$  
IV. $B[2][3]$

which will not give compile-time errors if used as left hand sides of assignment statements in a C program?

A. I, II, and IV only

B. II, III, and IV only

C. II and IV only

D. IV only

gatecse-2003 programming programming-in-c easy pointers

Answer key

# 5.9.4 Pointers: GATE CSE 2003 | Question: 89

Consider the C program shown below:

```lisp
#include<stdio.h>
#define print(x) printf("%d", x)

int x;
void Q(int z)
{
    z+=x;
    print(z);
}

void P(int *y)
{
    int x = *y + 2;
    Q(x);
    *y = x - 1;
    print(x);
}
main(void) {
    x = 5;
    P(&x);
    print(x);
}
```

The output of this program is:

A. 1276

B. 22 12 11

C. 1466

D. 766

gatecse-2003 programming programming-in-c normal pointers

Answer key

# 5.9.5 Pointers: GATE CSE 2005 | Question: 1, ISRO2017-55

What does the following C-statement declare?

int (\*f) (int \*);

A. A function that takes an integer pointer as argument and returns an integer  
B. A function that takes an integer as argument and returns an integer pointer  
C. A pointer to a function that takes an integer pointer as argument and returns an integer




D. A function that takes an integer pointer as argument and returns a function pointer

gatecse-2005 programming programming-in-c pointers easy isro2017

Answer key

# 5.9.6 Pointers: GATE CSE 2006 | Question: 57

Consider this C code to swap two integers and these five statements: the code


```lisp
void swap (int *px, int *py)
{
    *px = *px - *py;
    *py = *px + *py;
    *px = *py - *px;
}
```

S1: will generate a compilation error  
S2: may generate a segmentation fault at runtime depending on the arguments passed  
S3: correctly implements the swap procedure for all input pointers referring to integers stored in memory locations accessible to the process  
S4: implements the swap procedure correctly for some but not all valid input pointers  
S5: may add or subtract integers and pointers

A. S1

B. S2 and S3

C. S2 and S4

D. S2 and S5

gatecse-2006 programming programming-in-c normal pointers

Answer key

# 5.9.7 Pointers: GATE CSE 2014 | Set 1 | Question: 10

Consider the following program in C language:


```c
#include <stdio.h>

main()
{
    int i;
    int*pi = &i;

    scanf("%d",pi);
    printf("%d\n", i+5);
}
```

Which one of the following statements is TRUE?

A. Compilation fails.  
B. Execution results in a run-time error.  
C. On execution, the value printed is 5 more than the address of variable $i$ .  
D. On execution, the value printed is 5 more than the integer value entered.

gatecse-2014-set1 programming programming-in-c easy pointers

Answer key

# 5.9.8 Pointers: GATE CSE 2015 | Set 3 | Question: 26

Consider the following C program


```c
#include<stdio.h>
int main() {
    static int a[] = {10, 20, 30, 40, 50};
    static int *p[] = {a, a+3, a+4, a+1, a+2};
    int **ptr = p;
    ptr++;
    printf("%d%d", ptr-p, **ptr);
}
```

The output of the program is \_\_\_\_.

# Answer key

# 5.9.9 Pointers: GATE CSE 2017 | Set 1 | Question: 13

Consider the following C code:  

```c
#include<stdio.h>
int *assignval (int *x, int val) {
    *x = val;
    return x;
}

void main () {
    int *x = malloc(sizeof(int));
    if (NULL == x) return;
    x = assignval (x,0);
    if (x) {
        x = (int *)malloc(sizeof(int));
        if (NULL == x) return;
        x = assignval (x,10);
    }
    printf("%d\n", *x);
    free(x);
}
```

The code suffers from which one of the following problems:

A. compiler error as the return of malloc is not typecast appropriately.  
B. compiler error because the comparison should be made as x == NULL and not as shown.  
C. compiles successfully but execution may result in dangling pointer.  
D. compiles successfully but execution may result in memory leak.

gatecse-2017-set1 programming-in-c programming pointers

# Answer key

# 5.9.10 Pointers: GATE CSE 2017 | Set 2 | Question: 55

Consider the following C program.  

```c
#include<stdio.h>
#include<string.h>
int main() {
    char* c="GATECSIT2017";
    char* p=c;
    printf("%d", (int)strlen(c+2[p]-6[p]-1));
    return 0;
}
```

The output of the program is \_\_\_\_

gatecse-2017-set2 programming-in-c numerical-answers array pointers

# Answer key

# 5.9.11 Pointers: GATE CSE 2022 | Question: 11

What is printed by the following ANSI C program?  

```c
#include<stdio.h>

int main(int argc, char *argv[])
{
    int x = 1, z[2] = {10, 11};
    int *p = NULL;
    p = &x;
    *p = 10;
```

```txt
p = &z[1];

*(&z[0] + 1) += 3;

printf("%d, %d, %d\n", x, z[0], z[1]);

return 0;

}
```

A. 1,10,11

B. 1,10,14

c. 10,14,11

D. 10,10,14

gatecse-2022 programming programming-in-c pointers output one-mark

Answer key

# 5.9.12 Pointers: GATE CSE 2024 | Set 2 | Question: 26

What is the output of the following C program?


```c
#include <stdio.h>
int main() {
double a[2]={20.0,25.0},* p,* q;
p=a ;
q=p+1 ;
printf("%d,%d", (int) (q-p),( int)(* q- * p));
return 0;}
```

A. 4,8

B. 1,5

C. 8,5

D. 1,8

gatecse-2024-set2 programming programming-in-c pointers two-marks

Answer key

# 5.9.13 Pointers: GATE CSE 2025 | Set 1 | Question: 24


```c
#include <stdio.h>
void foo(int *p, int x) {
*p=x;
}
int main(){
int *z;
int a = 20, b = 25;
z = &a;
foo(z,b);
printf("%d",a);
return 0;
}
```

The output of the given C program is \_\_\_\_. (Answer in integer)

gatecse2025-set1 programming-in-c pointers output numerical-answers easy one-mark

Answer key

# 5.9.14 Pointers: GATE CSE 2025 | Set 2 | Question: 52

Consider the following C program:


```c
#include<stdio.h>
int main(){
    int a;
    int arr[5] = {30,50,10};
    int *ptr;
    ptr = &arr[0] + 1;
    a = *ptr;
    (*ptr)++;
    ptr++;
    printf("%d", a + (*ptr) + arr[1]);
    return 0;
}
```

The output of the above program is \_\_\_\_. (Answer in integer)

# Answer key

# 5.9.15 Pointers: GATE CSE 2026 | Set 2 | Question: 50

Consider the following ANSI-C program.


```c
#include <stdio.h>
int main(){
    int *ptr, a, b, c;
    a=5; b=11; c=20;
    ptr=&a; *ptr=c; ptr=&c;
    a=(*(&b); c=*ptr-a;
    printf("%d",c);
    return(0);
}
```

The output of this program is \_\_\_\_ . (answer in integer)

Note: Assume that the program compiles and runs successfully.

gatecse-2026-set2 programming-in-c pointers output numerical-answers two-marks

# Answer key

# 5.10

# Programming Constructs (1)

# 5.10.1 Programming Constructs: GATE CSE 1999 | Question: 2.5

Given the programming constructs


i. assignment  
ii. for loops where the loop parameter cannot be changed within the loop  
iii. if-then-else  
iv. forward go to  
v. arbitrary go to  
vi. non-recursive procedure call  
vii. recursive procedure/function call  
viii. repeat loop,

which constructs will you not include in a programming language such that it should be possible to program the terminates (i.e., halting) function in the same programming language

A. (ii), (iii), (iv)  
C. (vi), (vii), (viii)

B. (v), (vii), (viii)  
D. (iii), (vii), (viii)

gate1999 programming normal programming-constructs

# Answer key

# 5.11

# Programming In C (29)

# 5.11.1 Programming In C: GATE CSE 2000 | Question: 2.20

The value of j at the end of the execution of the following C program:


```c
int incr (int i)
{
    static int count = 0;
    count = count + i;
    return (count);
}
main () {
    int i, j;
    for (i = 0; i <= 4; i++)
        j = incr (i);
}
```

is:

A. 10

B. 4

C. 6

D. 7

gatecse-2000 programming programming-in-c easy

# Answer key

# 5.11.2 Programming In C: GATE CSE 2002 | Question: 1.17

# In the C language:


A. At most one activation record exists between the current activation record and the activation record for the main  
B. The number of activation records between the current activation record and the activation records from the main depends on the actual function calling sequence.  
C. The visibility of global variables depends on the actual function calling sequence  
D. Recursion requires the activation record for the recursive function to be saved in a different stack before the recursive function can be called.

gatecse-2002 programming programming-in-c easy descriptive

# Answer key

# 5.11.3 Programming In C: GATE CSE 2002 | Question: 2.18

# The C language is:


A. A context free language  
C. A regular language

B. A context sensitive language  
D. Parsable fully only by a Turing machine

gatecse-2002 programming programming-in-c normal

# Answer key

# 5.11.4 Programming In C: GATE CSE 2005 | Question: 32

# Consider the following C program:


```txt
double foo (double); /* Line 1 */
int main() {
    double da, db;
    //input da
    db = foo(da);
}
double foo (double a) {
    return a;
}
```

The above code compiled without any error or warning. If Line 1 is deleted, the above code will show:

A. no compile warning or error  
B. some compiler-warnings not leading to unintended results  
C. some compiler-warnings due to type-mismatch eventually leading to unintended results  
D. compiler errors

gatecse-2005 programming programming-in-c compiler-design easy

# Answer key

# 5.11.5 Programming In C: GATE CSE 2008 | Question: 18

Which combination of the integer variables $x, y$ , and $z$ makes the variable $a$ get the value 4 in the following expression?

$$
a = (x > y)? ((x > z)? x: z): ((y > z)? y: z)
$$

A. $x = 3, y = 4, z = 2$  
C. $x = 6, y = 3, z = 5$

B. $x = 6, y = 5, z = 3$  
D. $x = 5, y = 4, z = 5$

gatecse-2008 programming programming-in-c easy


# 5.11.6 Programming In C: GATE CSE 2008 | Question: 61


Choose the correct option to fill ?1 and ?2 so that the program below prints an input string in reverse order. Assume that the input string is terminated by a new line character.

```c
void reverse(void)
{
    int c;
    if(?1) reverse();
    ?2
}
main()
{
    printf("Enter text");
    printf("\n");
    reverse();
    printf("\n");
}
```

A. ?1 is (getchar()!='\n')  
?2 is getchar(c);  
B. ?1 is ((c = getchar())!=' \n')  
?2 is getchar(c);  
C. ?1 is (c! =' \n')  
?2 is putchar(c);  
D. ?1 is ((c = getchar())!=' \n')  
?2 is putchar(c);

gatecse-2008 programming normal programming-in-c

# Answer key

# 5.11.7 Programming In C: GATE CSE 2012 | Question: 48

Consider the following C code segment.


```c
int a, b, c = 0;
void prtFun(void);
main()
{
    static int a = 1;      /* Line 1 */
    prtFun();
    a += 1;
    prtFun();
    printf("\n %d %d ", a, b);
}

void prtFun(void)
{
    static int a = 2;      /* Line 2 */
    int b = 1;
    a += ++b;
    printf("\n %d %d ", a, b);
}
```

What output will be generated by the given code segment?

<table><tr><td>3</td><td>1</td><td>4</td><td>2</td><td>4</td><td>2</td><td>3</td><td>1</td></tr><tr><td>4</td><td>1</td><td>B. 6</td><td>1</td><td>C. 6</td><td>2</td><td>D. 5</td><td>2</td></tr><tr><td>4</td><td>2</td><td>6</td><td>1</td><td>2</td><td>0</td><td>5</td><td>2</td></tr></table>

gatecse-2012 programming programming-in-c normal

# Answer key