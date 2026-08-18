```c
int main()
{
    char s1[7] = "1234", *p;
    p = s1 + 2;
    *p = '0';
    printf("%s", s1);
}
```

What will be printed by the program?

A. 12

B. 120400

C. 1204

D. 1034

```txt
gatecse-2015-set3 programming programming-in-c normal array
```

# Answer key

# 5.2.6 Array: GATE CSE 2019 | Question: 24

Consider the following C program:


```c
#include <stdio.h>
int main() {
    int arr[]={1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 5}, *ip=arr+4;
    printf("%d\n", ip[1]);
    return 0;
}
```

The number that will be displayed on execution of the program is \_\_\_\_

```txt
gatecse-2019 numerical-answers programming-in-c programming array easy one-mark
```

# Answer key

# 5.2.7 Array: GATE CSE 2020 | Question: 22

Consider the following C program.


```c
#include <stdio.h>
int main () {
    int a[4] [5] = {{1, 2, 3, 4, 5},
        {6, 7,8, 9, 10},
        {11, 12, 13, 14, 15},
        {16, 17,18, 19, 20}};
    printf("%d\n", *(*(a+**a+2)+3));
    return(0);
}
```

The output of the program is \_\_\_\_.

```txt
gatecse-2020 numerical-answers programming-in-c array one-mark
```

# Answer key

# 5.2.8 Array: GATE CSE 2021 | Set 2 | Question: 10

Consider the following ANSI C program.


```c
#include <stdio.h>
int main()
{
    int arr[4][5];
    int i, j;
    for (i=0; i<4; i++)
    {
        for (j=0; j<5; j++)
        {
            arr[i][j] = 10 * i + j;
        }
    }
    printf("%d", *(arr[1]+9));
    return 0;
}
```

What is the output of the above program?

A. 14

B. 20

C. 24

D. 30

# 5.2.9 Array: GATE CSE 2022 | Question: 33

What is printed by the following ANSI C program?


```c
#include<stdio.h>

int main (int argc, char *argv[])
{
    int a[3][3][3] =
    {{1, 2, 3, 4, 5, 6, 7, 8, 9},
    {10, 11, 12, 13, 14, 15, 16, 17, 18},
    {19, 20, 21, 22, 23, 24, 25, 26, 27}};
    int i = 0, j = 0, k = 0;
    for ( i = 0; i < 3; i ++) {
        for ( k = 0; k < 3; k++)
            printf("%d", a[i][j][k]);
        printf ("\n");
    }
    return 0;
}
```

1 2 3

A. 10 11 12  
19 20 21
1 4 7

B. 10 13 16  
19 22 25
1 2 3

C. 4 5 6  
7 8 9
1 2 3

D. 13 14 15  
25 26 27

gatecse-2022 programming programming-in-c array output two-marks

# Answer key

# 5.2.10 Array: GATE IT 2004 | Question: 58

Consider the following C program which is supposed to compute the transpose of a given $4 \times 4$ matrix M. Note that, there is an X in the program which indicates some missing statements. Choose the correct option to replace X in the program.

```c
#include<stdio.h>
#define ROW 4
#define COL 4
int M[ROW][COL] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
main()
{
    int i, j, t;
    for (i = 0; i < 4; ++i)
    {
```


```txt
X
}
for (i = 0; i < 4; ++i)
    for (j = 0; j < 4; ++j)
        printf ("%d", M[i][j]);
}
```

A.

```txt
for(j = 0; j < 4; ++j){
    t = M[i][j];
    M[i][j] = M[j][i];
    M[j][i] = t;
```

B.

```txt
for(j = 0; j < 4; ++j){
    M[i][j] = t;
    t = M[j][i];
    M[j][i] = M[i][j];
```

C.

```txt
for(j = i; j < 4; ++j){
    t = M[i][j];
    M[i][j] = M[j][i];
    M[j][i] = t;
}
```

D.

```txt
for(j = i; j < 4; ++j){
    M[i][j] = t;
    t = M[j][i];
    M[j][i] = M[i][j];
}
```

gateit-2004 programming easy programming-in-c array

# Answer key

# 5.2.11 Array: GATE IT 2008 | Question: 49

What is the output printed by the following C code?


```c
# include <stdio.h>
int main ()
{
    char a [6] = "world";
    int i, j;
    for (i = 0, j = 5; i < j; a [i++] = a [j--]);
    printf ("%s\n", a);
}
```

A. dlrow

B. Null string

C. dlrld

D. worow

gateit-2008 programming programming-in-c normal array

# Answer key

# 5.2.12 Array: GATE IT 2008 | Question: 51

Consider the C program given below. What does it print?


```c
#include <stdio.h>
int main ()
{
    int i, j;
    int a [8] = {1, 2, 3, 4, 5, 6, 7, 8};
    for(i = 0; i < 3; i++) {
        a[i] = a[i] + 1;
        i++;
    }
    i--;
    for (j = 7; j > 4; j--) {
        int i = j/2;
        a[i] = a[i] - 1;
    }
    printf ("%d, %d", i, a[i]);
}
```

A. 2,3

B. 2,4

C. 3,2

D. 3,3

gateit-2008 programming programming-in-c normal array

# Answer key

# 5.2.13 Array: GATE IT 2008 | Question: 52

C program is given below:


```txt
# include <stdio.h>
int main ()
{
```

```txt
int i, j;
    char a [2] [3] = {{{'a', 'b', 'c'}, {{{'d', 'e', 'f'}}}};
    char b [3] [2];
    char *p = *b;
    for (i = 0; i < 2; i++) {
        for (j = 0; j < 3; j++) {
            *(p + 2*j + i) = a [i] [j];
        }
    }
}
```

What should be the contents of the array b at the end of the program?

A. a b
c d
e f  
B. a d
b e
c f  
C. a c
    e b
    d f  
D. a e
    d c
    b f

gateit-2008 programming programming-in-c normal array

Answer key

# 5.3

# Functions (2)

# 5.3.1 Functions: GATE CSE 2015 | Set 3 | Question: 54

Consider the following C program:


```c
#include<stdio.h>
int f1(void);
int f2(void);
int f3(void);
int x=10;
int main()
{
    int x=1;
    x += f1() + f2 () + f3() + f2();
    printf("%d", x);
    return 0;
}
int f1() { int x = 25; x++; return x;}
int f2() { static int x = 50; x++; return x;}
int f3() { x *= 10; return x;}
```

The output of the program is \_\_\_\_.

gatecse-2015-set3 programming programming-in-c functions normal numerical-answers

Answer key

# 5.3.2 Functions: GATE CSE 2024 | Set 2 | Question: 3

Consider the following C program. Assume parameters to a function are evaluated from right to left.


```c
#include <stdio.h>

int g(int p) { printf("%d", p); return p; }
int h(int q) { printf("%d", q); return q; }

void f(int x, int y) {
```

```txt
g(x);
    h(y);
}

int main() {
    f(g(10), h(20));
}
```

Which one of the following options is the CORRECT output of the above C program?

A. 20101020

B. 10202010

C. 20102010

D. 10201020

gatecse-2024-set2 programming programming-in-c functions one-mark

Answer key

# 5.4

# Goto (2)

# 5.4.1 Goto: GATE CSE 1989 | Question: 3-i

An unrestricted use of the "go to" statement is harmful because of which of the following reason (s):

A. It makes it more difficult to verify programs.  
B. It makes programs more inefficient.  
C. It makes it more difficult to modify existing programs.  
D. It results in the compiler generating longer machine code.

gate1989 normal programming goto

Answer key

# 5.4.2 Goto: GATE CSE 1994 | Question: 1.5

An unrestricted use of the "goto" statement is harmful because

A. it makes it more difficult to verify programs  
B. it increases the running time of the programs  
C. it increases the memory required for the programs  
D. it results in the compiler generating longer machine code

gate1994 programming easy goto

Answer key



# 5.5

# Identify Function (6)

# 5.5.1 Identify Function: GATE CSE 1995 | Question: 3

Consider the following high level programming segment. Give the contents of the memory locations for variables W, X, Y and Z after the execution of the program segment. The values of the variables A and B are 5CH and 92H, respectively. Also indicate error conditions if any.

```txt
var
  A, B, W, X, Y  :unsigned byte;
  Z           :unsigned integer, (each integer is represented by two bytes)
begin
  X           :=A+B
  Y           :=abs(A-B);
  W           :=A-B
  Z           :=A*B
end;
```

gate1995 programming identify-function descriptive

Answer key

# 5.5.2 Identify Function: GATE CSE 1998 | Question: 2.13

What is the result of the following program?



```julia
program side-effect (input, output);
var x, result: integer;
function f (var x:integer):integer;
begin
    x:x+1;f:=x;
end
begin
    x:=5;
    result:=f(x)*f(x);
    writeln(result);
end
```

A. 5

B. 25

C. 36

D. 42

```txt
gate1998 programming normal identify-function
```

Answer key

# 5.5.3 Identify Function: GATE CSE 2017 | Set 2 | Question: 14

Consider the following function implemented in C:


```c
void printxy(int x, int y) {
    int *ptr;
    x=0;
    ptr=&x;
    y=*ptr;
    *ptr=1;
    printf("%d, %d", x, y);
}
```

The output of invoking $\text{printxy}(1,1)$ is:

A. 0,0

B. 0,1

C. 1,0

D. 1,1

```txt
gatecse-2017-set2 programming-in-c identify-function pointers
```

Answer key

# 5.5.4 Identify Function: GATE CSE 2017 | Set 2 | Question: 43

Consider the following snippet of a C program. Assume that swap $(\& x, \& y)$ exchanges the content of $x$ and $y$ :


```txt
int main () {
    int array[] = {3, 5, 1, 4, 6, 2};
    int done =0;
    int i;
    while (done==0) {
        done =1;
        for (i=0; i<=4; i++) {
            if (array[i] < array[i+1]) {
                swap(&array[i], &array[i+1]);
                done=0;
            }
        }
        for (i=5; i>=1; i--) {
            if (array[i] > array[i-1]) {
                swap(&array[i], &array[i-1]);
                done =0;
            }
        }
    }
    printf("%d", array[3]);
}
```

The output of the program is \_\_\_\_

```txt
gatecse-2017-set2 programming algorithms numerical-answers identify-function
```

Answer key

# 5.5.5 Identify Function: GATE CSE 2019 | Question: 18

Consider the following C program :


#include<stdio.h>

```c
int jumble(int x, int y){
    x = 2*x+y;
    return x;
}
int main(){
    int x=2, y=5;
    y=jumble(y,x);
    x=jumble(y,x);
    printf("%d \n",x);
    return 0;
}
```

The value printed by the program is \_\_\_\_.

```txt
gatecse-2019 programming-in-c numerical-answers identify-function one-mark
```

# Answer key

# 5.5.6 Identify Function: GATE IT 2004 | Question: 15

Let $x$ be an integer which can take a value of 0 or 1. The statement


```javascript
if (x == 0) x = 1; else x = 0;
```

is equivalent to which one of the following ?

A. $x = 1 + x;$

B. x = 1 - x;

C. x = x - 1;

D. $x = 1\% x;$

```txt
gateit-2004 programming easy identify-function
```

# Answer key

# 5.6

# Loop Invariants (8)

# 5.6.1 Loop Invariants: GATE CSE 1987 | Question: 7a

List the invariant assertions at points $A, B, C, D$ and $E$ in program given below:


```txt
Program division (input, output)
Const
  dividend = 81;
  divisor = 9;
Var remainder, quotient:interger
begin
  (*(dividend >= 0) AND (divisor > 0)*)
  remainder := dividend;
  quotient := 0;
  (*A*)
While (remainder >= 0) do
begin (*B*)
  quotient := quotient + 1;
  remainder := remainder - divisor;
  (*C*)
end;
  (*D*)
  quotient := quotient - 1;
  remainder := remainder + divisor;
  (*E*)
end
```

```txt
gate1987 programming loop-invariants descriptive
```

# Answer key

# 5.6.2 Loop Invariants: GATE CSE 1988 | Question: 6ii

Below figure is the flow-chart corresponding to a program to calculate the gcd of two integers, M and N respectively, $(M, N > 0)$ . Use assertions at the cut point $C_{1}$ , $C_{2}$ and $C_{3}$ to prove that the flow-chart is correct.


![](images/4dd71c4b1281fa183a04a1035353dd85812930bed925d599feedef3b9ca5ea43.jpg)

<details>
<summary>flowchart</summary>

```mermaid
graph TD
  START["START"] --> M["M,N,K,L\nInteger\nL ← M, K ← N"]
  M --> C1["C1"]
  C1 --> K{"K ≠ L"}
  K -->|F| C3["C3"]
  K -->|T| K">L{"K>L"}
  K -->|F| L["L ← L - K"]
  L --> C2["C2"]
  C2 --> C1
  C3 --> RETURN["RETURN K"]
  K -->|T| K">L
  K -->|F| L
  L --> C2
  C2 --> C2
```
</details>

gate1988 normal descriptive loop-invariants

# Answer key

# 5.6.3 Loop Invariants: GATE CSE 1988 | Question: 8ii

Consider the two program segments below:


```elixir
a. for
    i:=1 to f(x) by 1 do
    S
end
```

```matlab
b. i:=1;
While i<=f(x) do
    S
    i:=i+1
end
```

Under what conditions are these two programs equivalent? Treat S as any sequence of statements and f as a function.

gate1988 programming descriptive loop-invariants

# Answer key

# 5.6.4 Loop Invariants: GATE CSE 1991 | Question: 1,vi

Consider the following PASCAL program segment:


```vhdl
if i mod 2 = 0 then
    while i >= 0 do
    begin
        i := i div 2;
        if i mod 2 <> 0 then i := i - 1;
        else i := i - 2;
    end;
```

An appropriate loop-invariant for the while-loop is \_\_\_\_

gate1991 programming loop-invariants normal fill-in-the-blanks

# Answer key

# 5.6.5 Loop Invariants: GATE CSE 2004 | Question: 32

Consider the following program fragment for reversing the digits in a given integer to obtain a new integer.

Let $n = d_{1}d_{2}\ldots d_{m}$ .


```txt
int n, rev;
rev = 0;
while(n > 0) {
    rev = rev * 10 + n%10;
```

$$
n = n / 1 0;
$$

The loop invariant condition at the end of the $i^{th}$ iteration is:

A. $n = d_{1}d_{2}\dots d_{m - i}$ and $\mathrm{rev} = d_m d_{m - 1}\dots d_{m - i + 1}$  
B. $n = d_{m - i + 1}\dots d_{m - 1}d_{m}$ or $\mathrm{rev} = d_{m - i}\dots d_2d_1$  
C. $n \neq \mathrm{rev}$  
D. $n = d_{1}d_{2}\dots d_{m}$ or $\mathrm{rev} = d_m\dots d_2d_1$

gatecse-2004 programming loop-invariants normal

# Answer key

# 5.6.6 Loop Invariants: GATE CSE 2015 | Set 1 | Question: 33

Consider the following pseudo code, where x and y are positive integers.


```txt
begin
    q := 0
    r := x
    while r ≥ y do
        begin
        r := r - y
        q := q + 1
    end
end
```

The post condition that needs to be satisfied after the program terminates is

A. $\{r = qx + y \land r < y\}$  
B. $\{x = qy + r \wedge r < y\}$  
C. $\{y = qx + r \wedge 0 < r < y\}$  
D. $\{q + 1 < r - y \land y > 0\}$

gatecse-2015-set1 programming loop-invariants normal

# Answer key

# 5.6.7 Loop Invariants: GATE CSE 2016 | Set 2 | Question: 35

The following function computes $X^{Y}$ for positive integers X and Y.


```lisp
int exp (int X, int Y) {
    int res =1, a = X, b = Y;

    while (b != 0) {
        if (b % 2 == 0) {a = a * a; b = b/2; }
        else        {res = res * a; b = b - 1; }
    }
    return res;
}
```

Which one of the following conditions is TRUE before every iteration of the loop?

A. $X^{Y} = a^{b}$  
C. $X^{Y}=res*a^{b}$  
B. $(res*a)^Y = (res*X)^b$  
D. $X^{Y} = (res*a)^{b}$

gatecse-2016-set2 programming loop-invariants normal

# Answer key

# 5.6.8 Loop Invariants: GATE CSE 2017 | Set 2 | Question: 37

Consider the C program fragment below which is meant to divide $x$ by $y$ using repeated subtractions. The variables $x, y, q$ and $r$ are all unsigned int.


```txt
while (r >= y) {
    r=r-y;
    q=q+1;
}
```

Which of the following conditions on the variables x, y, q and r before the execution of the fragment will ensure that the loop terminated in a state satisfying the condition $x == (y * q + r)$ ?

A. $(q == r)$ && $(r == 0)$  
B. $(x > 0)$ && $(r == x)$ && $(y > 0)$  
C. $(q == 0)$ && $(r == x)$ && $(y > 0)$  
D. (q == 0) && (y > 0)

gatecse-2017-set2 programming loop-invariants

# Answer key

5.7

# Output (8)

# 5.7.1 Output: GATE CSE 2022 | Question: 34

What is printed by the following ANSI C program?


```c
#include<stdio.h>

int main(int argc, char *argv[]) {
    char a = 'P';
    char b = 'x';
    char c = (a&b) + '*';
    char d = (a|b) - '-';
    char e = (a^b) + '+';
    printf("%c %c %c\n", c, d, e);
    return 0;
}
```

ASCII encoding for relevant characters is given below

<table><tr><td>A</td><td>B</td><td>C</td><td>...</td><td>Z</td></tr><tr><td>65</td><td>66</td><td>67</td><td>...</td><td>90</td></tr></table>

<table><tr><td>a</td><td>b</td><td>c</td><td>...</td><td>z</td></tr><tr><td>97</td><td>98</td><td>99</td><td>...</td><td>122</td></tr></table>

<table><tr><td>*</td><td>+</td><td>-</td></tr><tr><td>42</td><td>43</td><td>45</td></tr></table>

A. z K S

B. 122 75 83

C. \* - +

D. P x +

gatecse-2022 programming programming-in-c output two-marks

# Answer key

# 5.7.2 Output: GATE CSE 2023 | Question: 25

The integer value printed by the ANSI-C program given below is \_\_\_\_


```c
#include<stdio.h>

int funcp(){
    static int x = 1;
    x++;
    return x;
}

int main(){
    int x,y;
    x = funcp();
    y = funcp()+x;
    printf("%d\n", (x+y));
    return 0;
}
```

# 5.7.3 Output: GATE CSE 2024 | Set 1 | Question: 8

Consider the following C program:  

```c
#include <stdio.h>
int main() {
int a=6;
int b = 0;
while (a<10) {
a = a / 12+1 ;
a += b ;}
printf ("%d", a);
return 0 ; }
```

Which one of the following statements is CORRECT?

A. The program prints 9 as output  
C. The program gets stuck in an infinite loop

gatecse-2024-set1 programming programming-in-c output one-mark

B. The program prints 10 as output  
D. The program prints 6 as output

# Answer key

# 5.7.4 Output: GATE CSE 2024 | Set 1 | Question: 9


Consider the following C program:  
```c
#include <stdio.h>
void fX ();
int main(){
fX();
return 0 };
```

```txt
void fX () {
char a;
if ((a=g e t c h a r()) != '\n')
fX();
if (a != '\n')
putchar (a); }
```

Assume that the input to the program from the command line is 1234 followed by a newline character. Which one of the following statements is CORRECT?

A. The program will not terminate  
B. The program will terminate with no output  
C. The program will terminate with 4321 as output  
D. The program will terminate with 1234 as output

gatecse-2024-set1 programming programming-in-c output one-mark

# Answer key

# 5.7.5 Output: GATE CSE 2025 | Set 1 | Question: 53

Consider the following C program:  

```c
#include <stdio.h>
int gate (int n) {
int d, t, newnum, turn;
```

```txt
newnum = turn = 0; t=1;
while (n>=t) t *= 10;
t /=10;
while (t>0) {
d = n/t;
n = n%t;
t /= 10;
if (turn) newnum = 10*newnum + d;
turn = (turn + 1) % 2;
}
return newnum;
}
int main () {
printf ("%d", gate(14362));
return 0;
}
```

The value printed by the given C program is \_\_\_\_. (Answer in integer)

```txt
gatecse2025-set1 programming-in-c output numerical-answers two-marks
```

# Answer key

# 5.7.6 Output: GATE CSE 2025 | Set 2 | Question: 23


```txt
int x=126,y=105;
do {
    if(x>y) x=x-y;
    else y=y-x;
} while(x!=y);
printf("%d",x);
```

The output of the given C code segment is \_\_\_\_. (Answer in integer)

```txt
gatecse2025-set2 programming-in-c output numerical-answers one-mark
```

# Answer key

# 5.7.7 Output: GATE CSE 2025 | Set 2 | Question: 53

Consider the following C program:


```c
#include <stdio.h>

int g(int n) {
    return (n+10);
}

int f(int n) {
    return g(n*2);
}

int main() {
    int sum, n;
    sum=0;
    for (n=1; n<3; n++)
        sum += g(f(n));
    printf ("%d", sum);
    return 0;
}
```

The output of the given C program is \_\_\_\_. (Answer in integer)

```txt
gatecse2025-set2 programming-in-c output numerical-answers two-marks
```

# Answer key

# 5.7.8 Output: GATE CSE 2026 | Set 1 | Question: 24

Consider the following program in C:


```c
#include <stdio.h>
void func(int i, int j) {
    if(i < j) {
        int i = 0;
```