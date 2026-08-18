\- Trigonometric Identities: Use identities to simplify powers of trig functions or products of trig functions.

# Definite Integral

Definition and Core Idea: A definite integral represents the net signed area between the graph of a function and the x-axis over a specified interval $[a, b]$ . It is evaluated by finding the antiderivative of the function and then evaluating it at the upper and lower limits of integration.

# Important Formulas, Theorems, and Results:

1. Fundamental Theorem of Calculus (Part 1): If $f$ is continuous on $[a, b]$ , then the function $G(x) = \int_{a}^{x} f(t) dt$ has a derivative at every point in $(a, b)$ , and $G'(x) = f(x)$ .

2. Fundamental Theorem of Calculus (Part 2): If $f$ is continuous on $[a, b]$ and $F$ is any antiderivative of $f$ on $[a, b]$ , then $\int_{a}^{b} f(x) dx = F(b) - F(a)$ .

3. Properties of Definite Integrals:

$\circ \int_{a}^{b}f(x)dx = -\int_{b}^{a}f(x)dx$  
$\circ \int_{a}^{a}f(x)dx = 0$  
$\circ \int_{a}^{b}cf(x)dx = c\int_{a}^{b}f(x)dx$  
$\circ \int_{a}^{b}[f(x)\pm g(x)]dx = \int_{a}^{b}f(x)dx\pm \int_{a}^{b}g(x)dx$  
$\circ \int_{a_{x}}^{b}f(x)dx = \int_{a_{x}}^{c}f(x)dx + \int_{c}^{b}f(x)dx,$ where $a <   c <   b$  
$\circ \int_0^a f(x)dx = \int_0^a f(a - x)dx$ (useful for simplifying integrals)

\- Even/Odd Functions:

\- If $f(x)$ is an even function $(f(-x) = f(x))$ , then $\int_{-a}^{a} f(x) dx = 2 \int_{0}^{a} f(x) dx$ .

\- If $f(x)$ is an odd function $(f(-x) = -f(x))$ , then $\int_{-a}^{a} f(x) \, dx = 0$ .

# Key Properties and Identities:

- The definite integral evaluates to a numerical value, not a function.  
- The constant of integration $+C$ is not included in definite integrals because it cancels out (

$$
F (b) + C - (F (a) + C) = F (b) - F (a)).
$$

# Common Pitfalls or Tricky Points:

- Incorrectly applying the limits of integration (upper limit minus lower limit).  
- Sign errors when evaluating $F(b) - F(a)$ .  
- Forgetting to change the limits of integration when using substitution for definite integrals.  
- Not recognizing even/odd function properties to simplify integrals over symmetric intervals.  
- Improper integrals (involving infinite limits or discontinuities within the interval) are less common in GATE CS but good to be aware of.

# Standard Problem-Solving Techniques or Shortcuts:

- Direct Application of FTC: Find the antiderivative and evaluate at the limits.  
- Substitution: If using substitution, either change the limits of integration to be in terms of $u$ or revert back to $x$ before applying the original limits.  
- Properties of Definite Integrals: Use properties like linearity, interval splitting, and even/odd function rules to simplify the integral before evaluation.  
- Symmetry: For integrals over $[-a, a]$ , check if the integrand is even or odd.

# Polynomials

Definition and Core Idea: A polynomial is an expression consisting of variables and coefficients, involving only the operations of addition, subtraction, multiplication, and non-negative integer exponents of variables. They are fundamental building blocks in calculus as they are continuous and differentiable everywhere.

# Important Formulas, Theorems, and Results:

1. General Form: $P(x) = a_{n}x^{n} + a_{n-1}x^{n-1} + \cdots + a_{1}x + a_{0}$ , where $a_{i}$ are coefficients and n is a non-negative integer (degree).  
2. Remainder Theorem: If a polynomial $P(x)$ is divided by $(x - a)$ , the remainder is $P(a)$ .

3. Factor Theorem: $(x - a)$ is a factor of a polynomial $P(x)$ if and only if $P(a) = 0$ (i.e., $a$ is a root of the polynomial).

4. Fundamental Theorem of Algebra: Every non-constant single-variable polynomial with complex coefficients has at least one complex root. Consequently, a polynomial of degree $n$ has exactly $n$ roots (counting multiplicity) in the complex numbers.

5. Vieta's Formulas (for quadratic and cubic):

- For $ax^2 + bx + c = 0$ with roots $\alpha, \beta$ :  
- $\alpha + \beta = -\frac{b}{a}$  
$\cdot \alpha \beta = \frac{c}{a}$  
- For $ax^3 + bx^2 + cx + d = 0$ with roots $\alpha, \beta, \gamma$ :  
- $\alpha + \beta + \gamma = -\frac{b}{a}$  
- $\alpha \beta + \beta \gamma + \gamma \alpha = \frac{c}{a}$  
- $\alpha \beta \gamma = -\frac{d}{a}$

# Key Properties and Identities:

- Polynomials are continuous and infinitely differentiable everywhere.  
- The degree of a polynomial determines the maximum number of roots it can have.  
- If a polynomial has real coefficients, then any complex roots must occur in conjugate pairs.

# Common Pitfalls or Tricky Points:

- Errors in polynomial division or synthetic division.  
- Misapplying Vieta's formulas (e.g., sign errors).  
- Not considering multiplicity of roots.  
- Confusing roots with factors.

# Standard Problem-Solving Techniques or Shortcuts:

- Synthetic Division: A quick method for dividing a polynomial by a linear factor $(x - a)$ .  
- Rational Root Theorem: Helps find potential rational roots of a polynomial with integer coefficients.  
- Factoring: Look for common factors, use grouping, or quadratic formula for quadratic factors.  
- Derivative for Repeated Roots: If $a$ is a root of $P(x)$ with multiplicity $k > 1$ , then $a$ is also a root of $P'(x)$ with multiplicity $k - 1$ .

# Summation

Definition and Core Idea: Summation is the process of adding a sequence of numbers or terms. It is often represented using sigma notation ( $\sum$ ). In calculus, summation is foundational to understanding series, Riemann sums (for integration), and numerical methods.

# Important Formulas, Theorems, and Results:

1. Arithmetic Progression (AP) Sum: For an AP with first term $a$ , common difference $d$ , and $n$ terms:

$\circ S_{n} = \frac{n}{2} [2a + (n - 1)d]$  
$\circ S_{n} = \frac{\tilde{n}}{2}[a + l]$ , where $l$ is the last term.

2. Geometric Progression (GP) Sum: For a GP with first term a, common ratio r, and n terms:

$\circ S_{n} = \frac{a(r^{n} - 1)}{r - 1},\text{for} r\neq 1$  
$\circ S_{n} = \frac{a(1 - r^{n})}{1 - r},\text{for} r\neq 1$  
- Sum to Infinity for GP: $S_{\infty} = \frac{a}{1 - r}$ , for $|r| < 1$

3. Standard Summation Formulas:

$\circ \sum_{i = 1}^{n}c = nc$  
$\circ \sum_{i = 1}^{n}i = \frac{n(n + 1)}{2}$  
$\circ \sum_{i = 1}^{n}i^{2} = \frac{n(n + 1)(2n + 1)}{6}$  
$\circ \sum_{i = 1}^{n}i^{3} = \left(\frac{n(n + 1)}{2}\right)^{2}$

# Key Properties and Identities:

• Linearity of Summation:

$$
\begin{array}{l} \circ \sum_ {i = 1} ^ {n} (a _ {i} \pm b _ {i}) = \sum_ {i = 1} ^ {n} a _ {i} \pm \sum_ {i = 1} ^ {n} b _ {i} \\ \circ \sum_ {i = 1} ^ {n} c \cdot a _ {i} = c \cdot \sum_ {i = 1} ^ {n} a _ {i} \\ \end{array}
$$

\- Telescoping Sums: Sums where intermediate terms cancel out, e.g., $\sum_{i=1}^{n}(a_i - a_{i+1})$ .

# Common Pitfalls or Tricky Points:

- Off-by-one errors in summation limits.  
- Confusing AP and GP formulas.  
- Incorrectly applying the sum to infinity formula (only valid for $|r| < 1$ ).  
- Errors in algebraic manipulation when simplifying complex summations.

# Standard Problem-Solving Techniques or Shortcuts:

- Identify Series Type: Determine if it's an AP, GP, or a combination.  
- Use Standard Formulas: Apply the formulas for $\sum i, \sum i^2, \sum i^3$ .  
- Split and Combine: Use linearity to break down complex summations into simpler ones.  
- Method of Differences (Telescoping Sums): Express each term as a difference of two consecutive terms to simplify the sum.  
- Generating Functions: (Advanced, less common for direct GATE CS questions, but good for understanding series).

# Quick Formula Reference

# Limits

- L'Hopital's Rule: If $\frac{f(x)}{g(x)}$ is $\frac{0}{0}$ or $\frac{\infty}{\infty}$ , then $\lim \frac{f(x)}{g(x)} = \lim \frac{f'(x)}{g'(x)}$ .

$$
\cdot \lim _ {x \to 0} \frac {\sin x}{x} = 1
$$

$$
\cdot \lim _ {x \to 0} \frac {\tan x}{x} = 1
$$

$$
\cdot \lim _ {x \to 0} \frac {1 - \cos x}{x ^ {2}} = \frac {1}{2}
$$

$$
\cdot \lim _ {x \to 0} \frac {e ^ {x} - 1}{x} = 1
$$

$$
\cdot \lim _ {x \to 0} \frac {a ^ {x} - 1}{x} = \ln a
$$

$$
\cdot \lim _ {x \to 0} \frac {\ln (1 + x)}{x} = 1
$$

$$
\cdot \lim _ {x \to a} \frac {x ^ {n} - a ^ {n}}{x - a} = n a ^ {n - 1}
$$

$$
\cdot \lim _ {x \to \infty} (1 + \frac {1}{x}) ^ {x} = e
$$

$$
\cdot \lim _ {x \to 0} (1 + x) ^ {1 / x} = e
$$

# Continuity

\- Continuous at $x = a$ if: $f(a)$ defined, $\lim_{x \to a} f(x)$ exists, and $\lim_{x \to a} f(x) = f(a)$ .

# Differentiation

Let $u, v$ be functions of $x, c$ be a constant.

$$
\cdot \frac {d}{d x} (c) = 0
$$

$$
\cdot \frac {d}{d x} (x ^ {n}) = n x ^ {n - 1}
$$

$$
\cdot \frac {d}{d x} (e ^ {x}) = e ^ {x}
$$

$$
\cdot \frac {d}{d x} (a ^ {x}) = a ^ {x} \ln a
$$

$$
\cdot \frac {d}{d x} (\ln x) = \frac {1}{x}
$$

$$
\cdot \frac {d}{d x} (\sin x) = \cos x
$$

$$
\cdot \frac {d}{d x} (\cos x) = - \sin x
$$

$$
\cdot \frac {d}{d x} (\tan x) = \sec^ {2} x
$$

$$
\cdot \frac {d}{d x} (c u) = c \frac {d u}{d x}
$$

$$
\cdot \frac {d}{d x} (u \pm v) = \frac {d u}{d x} \pm \frac {d v}{d x}
$$

$$
\cdot \frac {d}{d x} (u v) = u \frac {d v}{d x} + v \frac {d u}{d x}
$$

$\cdot \frac{d}{dx}\left(\frac{u}{v}\right) = \frac{v\frac{du}{dx} - u\frac{dv}{dx}}{v^2}$  
- $\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)$ (Chain Rule)  
- Rolle's Theorem: $f(a) = f(b) \implies \exists c \in (a, b)$ s.t. $f'(c) = 0$  
- Mean Value Theorem: $\exists c \in (a, b)$ s.t. $f'(c) = \frac{f(b) - f(a)}{b - a}$

# Maxima Minima

- Critical points: $f'(x) = 0$ or $f'(x)$ undefined.  
- First Derivative Test: Sign change of $f'(x)$ at critical point.  
- Second Derivative Test: If $f'(c) = 0$ : $f''(c) > 0 \implies \text{local min}$ ; $f''(c) < 0 \implies \text{local max}$ .

# Integration (Indefinite)

- $\int k dx = kx + C$  
- $\int x^n dx = \frac{x^{n + 1}}{n + 1} + C$ , for $n \neq -1$  
$\cdot \int \frac{1}{x} dx = \ln |x| + C$  
$\cdot \int e^{x}dx = e^{x} + C$  
- $\int a^x dx = \frac{a^x}{\ln a} + C$  
- $\int \sin x dx = -\cos x + C$  
- $\int \cos x dx = \sin x + C$  
- $\int \sec^2 x dx = \tan x + C$  
- $\int \frac{1}{\sqrt{a^2 - x^2}} dx = \sin^{-1}\left(\frac{x}{a}\right) + C$  
$\cdot \int \frac{1}{a^2 + x^2} dx = \frac{1}{a}\tan^{-1}\left(\frac{x}{a}\right) + C$  
- Integration by Parts: $\int u dv = uv - \int v du$

# Definite Integral

- Fundamental Theorem of Calculus: $\int_{a}^{b} f(x) dx = F(b) - F(a)$ where $F'(x) = f(x)$ .  
- $\int_{a}^{b}f(x)dx = -\int_{b}^{a}f(x)dx$  
$\cdot \int_{a_{c}}^{b}f(x)dx = \int_{a_{c}}^{c}f(x)dx + \int_{c}^{b}f(x)dx$  
- $\int_0^a f(x)dx = \int_0^a f(a - x)dx$  
- Even function $(f(-x) = f(x))$ : $\int_{-a}^{a} f(x) dx = 2 \int_{0}^{a} f(x) dx$  
- Odd function $(f(-x) = -f(x))$ : $\int_{-a}^{a} f(x) dx = 0$

# Polynomials

- Remainder Theorem: $P(x)$ divided by $(x - a)$ has remainder $P(a)$ .  
- Factor Theorem: $(x - a)$ is a factor of $P(x)$ iff $P(a) = 0$ .  
- Vieta's Formulas (for $ax^2 + bx + c = 0$ ): $\alpha + \beta = -b / a$ , $\alpha \beta = c / a$ .

# Summation

- AP Sum: $S_{n} = \frac{n}{2}[2a + (n - 1)d]$ or $S_{n} = \frac{n}{2}[a + l]$  
- GP Sum: $S_{n} = \frac{a(r^{n} - 1)}{r - 1}$  
- GP Sum to Infinity: $S_{\infty} = \frac{a}{1 - r}$ for $|r| < 1$  
- $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$  
$\cdot \sum_{i = 1}^{n}i^{2} = \frac{n(n + 1)(2n + 1)}{6}$  
$\cdot \sum_{i = 1}^{n}i^{3} = \left(\frac{n(n + 1)}{2}\right)^{2}$

# Important Tips for GATE

1. Master the Fundamentals: Calculus builds upon basic algebra, trigonometry, and functions. Ensure your foundation in these areas is strong to avoid silly mistakes.  
2. Practice with PYQs: Solve previous year's GATE questions extensively. This helps you understand the typical question patterns, difficulty levels, and time constraints.  
3. Understand Concepts, Don't Just Memorize: While formulas are crucial, knowing \*why\* they work (e.g., the geometric interpretation of derivatives and integrals) will help you tackle trickier conceptual questions and apply them correctly in unfamiliar scenarios.  
4. Pay Attention to Domains and Conditions: For limits, continuity, and differentiability, always check the domain of the function and any specific conditions (e.g., $g(x) \neq 0$ for quotient rule, $|r| < 1$ for infinite GP sum). Piecewise functions are common traps.  
5. Be Careful with Signs and Constants: A common source of error in differentiation and integration is incorrect signs or forgetting the constant of integration $(+C)$ for indefinite integrals. Double-check your calculations.  
6. Time Management: Some calculus problems can be lengthy. Learn to identify problems that might take too much time and mark them for review. Practice solving problems within a strict time limit. Shortcuts like L'Hopital's rule or properties of definite integrals can save valuable time.  
7. Visualize Functions: For problems involving maxima/minima or definite integrals, sketching a rough graph of the function can often provide intuition and help verify your analytical results.  
8. Review Properties of Even/Odd Functions: These properties are frequently tested in definite integral problems, especially over symmetric intervals like $[-a, a]$ , and can significantly simplify calculations.

# 5.1

# Continuity (11)

Practice Test: Test 1 (14Q)

# 5.1.1 Continuity: GATE CSE 1996 | Question: 3

Let $f$ be a function defined by


$$
f (x) = \left\{ \begin{array}{l l} x ^ {2} & \text {for} x \leq 1 \\ a x ^ {2} + b x + c & \text {for} 1 \\ x + d & \text {for} x > 2 \end{array} \right. l t x \leq 2
$$

Find the values for the constants $a, b, c$ and $d$ so that $f$ is continuous and differentiable everywhere on the real line.

gate1996 calculus continuity differentiation normal descriptive

# Answer key

# 5.1.2 Continuity: GATE CSE 1998 | Question: 1.4

Consider the function $y = |x|$ in the interval $[-1, 1]$ . In this interval, the function is

A. continuous and differentiable  
C. differentiable but not continuous

B. continuous but not differentiable  
D. neither continuous nor differentiable

gate1998 calculus continuity differentiation easy

# Answer key

# 5.1.3 Continuity: GATE CSE 2007 | Question: 1

Consider the following two statements about the function $f(x) = |x|$ :

- P. $f(x)$ is continuous for all real values of $x$ .  
• Q. $f(x)$ is differentiable for all real values of x.

Which of the following is TRUE?

A. $P$ is true and $Q$ is false.

C. Both $P$ and $Q$ are true.

B. $P$ is false and $Q$ is true.

D. Both $P$ and $Q$ are false.

gatecse-2007 calculus continuity differentiation easy



# 5.1.4 Continuity: GATE CSE 2013 | Question: 22

Which one of the following functions is continuous at x = 3?


A. $f(x) = \left\{ \begin{array}{ll}2, & \text{if} x = 3\\ x - 1, & \text{if} x > 3\\ \frac{x + 3}{3}, & \text{if} x <   3 \end{array} \right.$  
B. $f(x) = \left\{ \begin{array}{ll}4, & \text{if} x = 3\\ 8 - x, & \text{if} x\neq 3 \end{array} \right.$  
C. $f(x) = \left\{ \begin{array}{ll}x + 3, & \text{if} x\leq 3\\ x - 4, & \text{if} x > 3 \end{array} \right.$  
D. $f(x) = \{\frac{1}{x^3 - 27}, \text{ if } x \neq 3\}$

gatecse-2013 calculus continuity normal

# Answer key

# 5.1.5 Continuity: GATE CSE 2014 | Set 1 | Question: 47


A function $f(x)$ is continuous in the interval [0, 2]. It is known that $f(0) = f(2) = -1$ and $f(1) = 1$ . Which one of the following statements must be true?

A. There exists a $y$ in the interval $(0,1)$ such that $f(y) = f(y + 1)$  
B. For every $y$ in the interval $(0,1), f(y) = f(2 - y)$  
C. The maximum value of the function in the interval $(0,2)$ is 1  
D. There exists a $y$ in the interval $(0,1)$ such that $f(y) = -f(2 - y)$

gatecse-2014-set1 calculus continuity tricky

# Answer key

# 5.1.6 Continuity: GATE CSE 2015 | Set 2 | Question: 26


Let $f(x) = x^{-(\frac{1}{3})}$ and $A$ denote the area of region bounded by $f(x)$ and the X-axis, when $x$ varies from -1 to 1. Which of the following statements is/are TRUE?

I. $f$ is continuous in $[-1, 1]$  
II. $f$ is not bounded in $[-1,1]$  
III. $A$ is nonzero and finite

A. II only

B. III only

C. II and III only

D. I, II and III

gatecse-2015-set2 calculus continuity functions normal

# Answer key

# 5.1.7 Continuity: GATE CSE 2021 | Set 2 | Question: 25


Suppose that $f: \mathbb{R} \to \mathbb{R}$ is a continuous function on the interval $[-3, 3]$ and a differentiable function in the interval $(-3, 3)$ such that for every $x$ in the interval, $f'(x) \leq 2$ . If $f(-3) = 7$ , then $f(3)$ is at most

gatecse-2021-set2 numerical-answers calculus continuity one-mark

# Answer key

# 5.1.8 Continuity: GATE CSE 2026 | Set 1 | Question: 22

Consider the function $f:\mathbb{R}\to\mathbb{R}$ defined as follows:


$$
f (x) = \left\{ \begin{array}{l l} c _ {1} e ^ {x} - c _ {2} \log_ {\mathrm{e}} \bigl (\frac {1}{x} \bigr), & \text {if} x > 0 \\ 3 & \text {otherwise} \end{array} \right.
$$

where $c_{1}, c_{2} \in \mathbb{R}$ .

If $f$ is continuous at $x = 0$ , then $c_1 + c_2 =$ \_\_\_\_. (answer in integer)

gatecse-2026-set1 calculus continuity numerical-answers one-mark

Answer key

# 5.1.9 Continuity: GATE CSE 2026 | Set 2 | Question: 54

Consider a function $f:(0,1)\to \{0,1\}$ defined as follows.

For a real number $r \in (0,1)$ , $f(r) = 1$ if the second digit after the decimal point in $r$ is one of the four digits 2, 3, 6 and 7. Otherwise, $f(r)$ is equal to 0.

The number of points in (0,1) at which $f$ is discontinuous is \_\_\_\_. (answer in integer)

gatecse-2026-set2 calculus continuity numerical-answers two-marks

Answer key

# 5.1.10 Continuity: GATE DS&AI 2024 | Question: 27

Let $f: \mathbb{R} \to \mathbb{R}$ be a function. Note: $\mathbb{R}$ denotes the set of real numbers.

$$
f (x) = \left\{ \begin{array}{c l l} - x, & \text {if} x & l t - 2 \\ a x ^ {2} + b x + c, & \text {if} x \in [ - 2, 2 ] \\ x, & \text {if} x > 2 \end{array} \right.
$$



Which ONE of the following choices gives the values of $a, b, c$ that make the function $f$ continuous and differentiable?

A. $a = \frac{1}{4}, b = 0, c = 1$  
C. $a=0, b=0, c=0$

B. $a = \frac{1}{2}, b = 0, c = 0$  
D. $a = \tilde{1}, b = 1, c = -4$

gate-ds-ai-2024 calculus continuity differentiation two-marks

Answer key

# 5.1.11 Continuity: GATE2010 ME

The function $y = |2 - 3x|$

A. is continuous $\forall x\in R$ and differentiable $\forall x\in R$  
B. is continuous $\forall x\in R$ and differentiable $\forall x\in R$ except at $x = \frac{3}{2}$  
C. is continuous $\forall x\in R$ and differentiable $\forall x\in R$ except at $x = \frac{2}{3}$  
D. is continuous $\forall x\in R$ except $x = 3$ and differentiable $\forall x\in R$

calculus gate2010me engineering-mathematics continuity

Answer key


# 5.2

# Definite Integral (4)

Practice Test: Test 1 (12Q)

# 5.2.1 Definite Integral: GATE CSE 2023 | Question: 21

The value of the definite integral

$$
\int_ {- 3} ^ {3} \int_ {- 2} ^ {2} \int_ {- 1} ^ {1} \left(4 x ^ {2} y - z ^ {3}\right) \mathrm{d} z \mathrm{d} y \mathrm{d} x
$$

is \_\_\_\_. (Rounded off to the nearest integer)

gatecse-2023 calculus definite-integral numerical-answers one-mark

Answer key

# 5.2.2 Definite Integral: GATE CSE 2024 | Set 2 | Question: 6

Let $f(x)$ be a continuous function from R to R such that

$$
f (x) = 1 - f (2 - x)
$$

Which one of the following options is the CORRECT value of $\int_0^2 f(x)dx$ ?

A. 0

B. 1

C. 2

D. -1

gatecse-2024-set2 calculus definite-integral one-mark

Answer key

# 5.2.3 Definite Integral: GATE CSE 2025 | Set 2 | Question: 2

The value of $x$ such that $x > 1$ , satisfying the equation $\int_{1}^{x} t \ln t dt = \frac{1}{4}$ is

A. $\sqrt{e}$

B. e

C. $e^{2}$

D. $e - 1$

gatecse2025-set2 calculus definite-integral one-mark

Answer key

# 5.2.4 Definite Integral: GATE CSE 2026 | Set 2 | Question: 17

For a real number $a$ , let $I(a) = \int_{-1}^{1} (3x^2 - ax + 1) dx$ . Which of the following statements is/are true?

A. The value of $I(a)$ is independent of the value of $a$  
B. The value of $I(a)$ can vary with the value of a  
C. There exists $a \in (-\infty, +\infty)$ such that $I(a)$ is a positive real number  
D. There exists $a \in (-\infty, +\infty)$ such that $I(a)$ is a negative real number

gatecse-2026-set2 calculus definite-integral multiple-selects one-mark

Answer key

# 5.3

# Differentiation (11)

Practice Tests: Test 1 (15Q) Test 2 (10Q)

# 5.3.1 Differentiation: GATE CSE 1996 | Question: 1.6

The formula used to compute an approximation for the second derivative of a function $f$ at a point $x_0$ is

A. $\frac{f(x_0 + h) + f(x_0 - h)}{2}$  
C. $\frac{f(x_0 + h) + 2f(x_0) + f(x_0 - h)}{h^2}$

B. $\frac{f(x_0 + h) - f(x_0 - h)}{2h}$  
D. $\frac{f(x_0 + h) - 2f(x_0) + f(x_0 - h)}{h^2}$

gate1996 calculus differentiation normal






# 5.3.2 Differentiation: GATE CSE 2014 | Set 1 | Question: 46

The function $f(x) = x \sin x$ satisfies the following equation:

$$
f ^ {\prime \prime} (x) + f (x) + t \cos x = 0
$$

The value of $t$ is \_\_\_\_.

gatecse-2014-set1 calculus easy numerical-answers differentiation

Answer key

# 5.3.3 Differentiation: GATE CSE 2014 | Set 1 | Question: 6

Let the function



$$
f (\theta) = \left| \begin{array}{c c c} \sin \theta & \cos \theta & \tan \theta \\ \sin (\frac {\pi}{6}) & \cos (\frac {\pi}{6}) & \tan (\frac {\pi}{6}) \\ \sin (\frac {\pi}{3}) & \cos (\frac {\pi}{3}) & \tan (\frac {\pi}{3}) \end{array} \right|
$$

where

$\theta \in \left[\frac{\pi}{6},\frac{\pi}{3}\right]$ and $f^{\prime}(\theta)$ denote the derivative of $f$ with respect to $\theta$ . Which of the following statements is/are TRUE?

I. There exists $\theta \in (\frac{\pi}{6},\frac{\pi}{3})$ such that $f^{\prime}(\theta) = 0$  
II. There exists $\theta \in (\frac{\pi}{6},\frac{\pi}{3})$ such that $f^{\prime}(\theta)\neq 0$

A. I only

B. II only

C. Both I and II

D. Neither I nor II

gatecse-2014-set1 calculus differentiation normal

Answer key

# 5.3.4 Differentiation: GATE CSE 2016 | Set 2 | Question: 02

Let $f(x)$ be a polynomial and $g(x) = f'(x)$ be its derivative. If the degree of $(f(x) + f(-x))$ is 10, then the degree of $(g(x) - g(-x))$ is \_\_\_\_.


gatecse-2016-set2 calculus normal numerical-answers differentiation

Answer key

# 5.3.5 Differentiation: GATE CSE 2017 | Set 2 | Question: 10

If $f(x) = R \sin \left(\frac{\pi x}{2}\right) + S$ , $f' \left(\frac{1}{2}\right) = \sqrt{2}$ and $\int_0^1 f(x) dx = \frac{2R}{\pi}$ , then the constants $R$ and $S$ are


A. $\frac{2}{\pi}$ and $\frac{16}{\pi}$

B. $\frac{2}{\pi}$ and 0

C. $\frac{4}{\pi}$ and 0

D. $\frac{4}{\pi}$ and $\frac{16}{\pi}$

gatecse-2017-set2 engineering-mathematics calculus differentiation

Answer key

# 5.3.6 Differentiation: GATE CSE 2024 | Set 1 | Question: 1

Let $f: \mathbb{R} \to \mathbb{R}$ be a function such that $f(x) = \max \{x, x^3\}, x \in \mathbb{R}$ , where $\mathbb{R}$ is the set of all real numbers. The set of all points where $f(x)$ is NOT differentiable is


A. $\{-1,1,2\}$

B. $\{-2,-1,1\}$

C. $\{0,1\}$

D. $\{-1,0,1\}$

gatecse-2024-set1 calculus differentiation one-mark

Answer key

# 5.3.7 Differentiation: GATE CSE 2025 | Set 1 | Question: 21

Consider the given function $f(x)$ .

$$
f (x) = \left\{ \begin{array}{l l} a x + b & \text {for} x <   1 \\ x ^ {3} + x ^ {2} + 1 & \text {for} x \geq 1 \end{array} \right.
$$

If the function is differentiable everywhere, the value of $b$ must be \_\_\_\_. (rounded off to one decimal place)

gatecse2025-set1 calculus differentiation numerical-answers one-mark

Answer key

# 5.3.8 Differentiation: GATE CSE 2026 | Set 1 | Question: 36

Let $f: \mathbb{R} \to \mathbb{R}$ be defined as follows:


$$
f (x) = \left(\frac {| x |}{2} - x\right) \left(x - \frac {| x |}{2}\right)
$$

Which of the following statements is/are true?

A. $f$ has a local maximum

B. $f$ has a local minimum

C. $f'$ is continuous over $\mathbb{R}$

D. $f'$ is not differentiable over $\mathbb{R}$

gatecse-2026-set1 two-marks differentiation calculus multiple-selects

Answer key

# 5.3.9 Differentiation: GATE DA 2025 | Question: 14

Consider two functions $f: \mathbb{R} \to \mathbb{R}$ and $g: \mathbb{R} \to (1, \infty)$ . Both functions are differentiable at a point $c$ . Which of the following functions is/are ALWAYS differentiable at $c$ ? The symbol $\cdot$ denotes product and the symbol $\circ$ denotes composition of functions.


A. $f \pm g$

B. $f \cdot g$

C. $\frac{f}{g}$

D. $f \circ g + g \circ f$

gateda-2025 calculus differentiation limits multiple-selects one-mark

Answer key

# 5.3.10 Differentiation: GATE DA 2025 | Question: 4

Let $f(x) = \frac{e^x - e^{-x}}{2}, x \in \mathbb{R}$ . Let $f^{(k)}(a)$ denote the $k^{th}$ derivative of $f$ evaluated at $a$ . What is the value of $f^{(10)}(0)$ ? (Note: ! denotes factorial)


A. 0

B. 1

C. $\frac{1}{10!}$

D. $\frac{2}{10!}$

gateda-2025 calculus differentiation one-mark

Answer key

# 5.3.11 Differentiation: GATE DA 2025 | Question: 41

Let $f: \mathbb{R} \to \mathbb{R}$ be a twice-differentiable function and suppose its second derivative satisfies $f''(x) > 0$ for all $x \in \mathbb{R}$ . Which of the following statements is/are ALWAYS correct?


A. $f$ has a local minima  
B. There does not exist $x$ and $y, x \neq y$ , such that $f'(x) = f'(y) = 0$  
C. f has at most one global minimum  
D. $f$ has at most one local minimum

gateda-2025 calculus maxima-minima differentiation multiple-selects two-marks

Answer key

# 5.4.1 Integration: GATE CSE 1993 | Question: 02.6

The value of the double integral $\int_{0}^{1}\int_{0}^{\frac{1}{x}}\frac{x}{1+y^{2}}dxdy$ is \_\_\_\_.

gate1993 calculus integration normal fill-in-the-blanks

Answer key


# 5.4.2 Integration: GATE CSE 1998 | Question: 8

a. Find the points of local maxima and minima, if any, of the following function defined in $0 \leq x \leq 6$ .

$$
x ^ {3} - 6 x ^ {2} + 9 x + 1 5
$$

b. Integrate

$$
\int_ {- \pi} ^ {\pi} x \cos x d x
$$

gate1998 calculus maxima-minima integration normal descriptive

Answer key

# 5.4.3 Integration: GATE CSE 2000 | Question: 2.3

Let $S = \sum_{i=3}^{100} i \log_2 i$ , and $T = \int_2^{100} x \log_2 x dx$ .

Which of the following statements is true?

A. S > T

B. S = T

C. $S <   T$ and $2S > T$

D. $2S \leq T$

gatecse-2000 calculus integration normal

Answer key



# 5.4.4 Integration: GATE CSE 2009 | Question: 25

$$
\int_ {0} ^ {\pi / 4} (1 - \tan x) / (1 + \tan x)   d x
$$

A. 0

B. 1

C. ln2

D. $1 / 2 \ln 2$

gatecse-2009 calculus integration normal

Answer key

# 5.4.5 Integration: GATE CSE 2011 | Question: 31

Given $i = \sqrt{-1}$ , what will be the evaluation of the definite integral $\int_{0}^{\pi/2} \frac{\cos x + i \sin x}{\cos x - i \sin x} dx$ ?

A. 0

B. 2

C. -i

D. i

gatecse-2011 calculus integration normal

Answer key

# 5.4.6 Integration: GATE CSE 2014 | Set 3 | Question: 47

The value of the integral given below is




$$
\int_ {0} ^ {\pi} x ^ {2} \cos x d x
$$

A. $-2\pi$

B. $\pi$

C. $-\pi$

D. $2 \pi$

gatecse-2014-set3 calculus limits integration normal

# Answer key

# 5.4.7 Integration: GATE CSE 2014 | Set 3 | Question: 6

If $\int_{0}^{2\pi}|x\sin x|dx = k\pi$ , then the value of $k$ is equal to \_\_\_\_.

gatecse-2014-set3 calculus integration limits numerical-answers easy

# Answer key

# 5.4.8 Integration: GATE CSE 2015 | Set 1 | Question: 44

Compute the value of:



$$
\int_{\frac{1}{\pi}}^{\frac{2}{\pi}}\frac{\cos(1 / x)}{x^2} dx
$$

gatecse-2015-set1 calculus integration normal numerical-answers

# Answer key

# 5.4.9 Integration: GATE CSE 2015 | Set 3 | Question: 45

If for non-zero $x$ , $af(x) + bf(\frac{1}{x}) = \frac{1}{x} - 25$ where $a \neq b$ then $\int_{1}^{2} f(x) dx$ is

A. $\frac{1}{a^2 - b^2}\left[a(\ln 2 - 25) + \frac{47b}{2}\right]$  
C. $\frac{1}{a^2 - b^2}\left[a(2\ln 2 - 25) + \frac{47b}{2}\right]$

gatecse-2015-set3 calculus integration normal

B. $\frac{1}{a^2 - b^2}\left[a(2\ln 2 - 25) - \frac{47b}{2}\right]$  
D. $\frac{1}{a^2 - b^2}\left[a(\ln 2 - 25) - \frac{47b}{2}\right]$

# Answer key

# 5.4.10 Integration: GATE CSE 2018 | Question: 16

The value of $\int_0^{\pi /4}x\cos (x^2)dx$ correct to three decimal places (assuming that $\pi = 3.14$ ) is \_\_\_\_

gatecse-2018 calculus integration normal numerical-answers one-mark

# Answer key

# 5.4.11 Integration: GATE IT 2005 | Question: 35

What is the value of $\int_0^{2\pi}(x - \pi)^2 (\sin x)dx$

A. -1

B. 0

C. 1

D. $\pi$

gateit-2005 calculus integration normal

# Answer key

# 5.5

# Limits (15)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (8Q)



