Let $a, b, d$ and \$ be indexed as follows:

<table><tr><td>a</td><td>b</td><td>d</td><td>$</td></tr><tr><td>3</td><td>2</td><td>1</td><td>0</td></tr></table>

Compute the FOLLOW set of the non-terminal B and write the index values for the symbols in the FOLLOW set in the descending order.(For example, if the FOLLOW set is (a, b, d, \$), then the answer should be 3210)

gatecse-2019 numerical-answers compiler-design parsing one-mark first-and-follow

Answer key

# 2.11.5 First and Follow: GATE CSE 2024 | Set 1 | Question: 28

Consider the following grammar $G$ , with $S$ as the start symbol. The grammar $G$ has three incomplete productions denoted by (1), (2), and (3).


$$
S \rightarrow d a T \mid \tag {1}
$$

$$
T \rightarrow a S | b T | \tag {2}
$$

$$
R \rightarrow (3) \mid \epsilon
$$

The set of terminals is $\{a, b, c, d, f\}$ . The FIRST and FOLLOW sets of the different non-terminals are as follows.

$$
\text {FIRST} (S) = \{c, d, f \}, \text {FIRST} (T) = \{a, b, \epsilon \}, \text {FIRST} (R) = \{c, \epsilon \}
$$

$$
\operatorname{FOLLOW} (S) = \operatorname{FOLLOW} (T) = \{c, f, \}, \operatorname{FOLLOW} (R) = \{f \}
$$

Which one of the following options CORRECTLY fills in the incomplete productions?

A. (1) $S \to Rf$ (2) $T \to \epsilon$ (3) $R \to cTR$  
B. (1) $S \rightarrow f\dot{R}$ (2) $T \rightarrow \epsilon$ (3) $R \rightarrow cTR$  
C. (1) $S \to fR$ (2) $T \to cT$ (3) $R \to cR$  
D. (1) $S \to Rf(2)T \to cT(3)R \to cR$

gatecse-2024-set1 compiler-design first-and-follow two-marks

Answer key

# 2.11.6 First and Follow: GATE CSE 2025 | Set 1 | Question: 36

Which of the following statement(s) is/are TRUE while computing First and Follow during top down parsing by a compiler?


A. For a production $A \to \epsilon, \epsilon$ will be added to $\operatorname{First}(A)$ .  
B. If there is any input right end marker, it will be added to First(S), where $S$ is the start symbol.  
C. For a production $A \to \epsilon, \epsilon$ will be added to Follow (A).  
D. If there is any input right end marker, it will be added to $\text{Follow}(S)$ , where S is the start symbol.

gatecse2025-set1 compiler-design first-and-follow parsing multiple-selects two-marks

Answer key

# 2.12 Grammar (47)

Practice Tests: Test 1 (15Q) Test 2 (15Q) Test 3 (6Q)

# 2.12.1 Grammar: GATE CSE 1988 | Question: 10ia

Consider the following grammar:

- $S \rightarrow S$  
- $S \to SS \mid a \mid \epsilon$

Construct the collection of sets of LR (0) items for this grammar and draw its goto graph.


# 2.12.2 Grammar: GATE CSE 1988 | Question: 10ib

Consider the following grammar:


- $S \rightarrow S$  
- $S \to SS \mid a \mid \epsilon$

Indicate the shift-reduce and reduce-reduce conflict (if any) in the various states of the LR(0) parser.

gate1988 compiler-design descriptive grammar parsing

Answer key

# 2.12.3 Grammar: GATE CSE 1990 | Question: 16a

Show that grammar $G_{1}$ is ambiguous using parse trees:


$$
G _ {1}: S \to \text { if   } S \text {   then   } S \text {   else   } S
$$

$$
S \rightarrow \text { if } S \text { then } S
$$

gate1990 descriptive compiler-design grammar

Answer key

# 2.12.4 Grammar: GATE CSE 1991 | Question: 10b


Consider the following grammar for arithmetic expressions using binary operators — and / which are not associative

- $E \rightarrow E - T \mid T$  
- $T \rightarrow T / F \mid \dot{F}$  
- $F \rightarrow (E) \mid id$

(E is the start symbol)

Does the grammar allow expressions with redundant parentheses as in $(id/id)$ or in $id - (id/id)$ ? If so, convert the grammar into one which does not generate expressions with redundant parentheses. Do this with minimum number of changes to the given production rules and adding at most one more production rule.

gate1991 grammar compiler-design normal descriptive

Answer key

# 2.12.5 Grammar: GATE CSE 1991 | Question: 10c


Consider the following grammar for arithmetic expressions using binary operators — and / which are not associative

- $E \rightarrow E - T \mid T$  
- $T \rightarrow T / F \mid \dot{F}$  
- $F \rightarrow (E) \mid id$

(E is the start symbol)

Does the grammar allow expressions with redundant parentheses as in $(id/id)$ or in $id - (id/id)$ ? If so, convert the grammar into one which does not generate expressions with redundant parentheses. Do this with minimum number of changes to the given production rules and adding at most one more production rule.

Convert the grammar obtained above into one that is not left recursive.

# 2.12.6 Grammar: GATE CSE 1992 | Question: 02,xviii


If $G$ is a context free grammar and $w$ is a string of length $l$ in $L(G)$ , how long is a derivation of $w$ in $G$ , if $G$ is in Chomsky normal form?

A. 2l

B. $2l+1$

C. 2l - 1

D. $l$

gate1992 compiler-design easy grammar

# Answer key

# 2.12.7 Grammar: GATE CSE 1994 | Question: 1.18

Which of the following features cannot be captured by context-free grammars?

A. Syntax of if-then-else statements

B. Syntax of recursive procedures

C. Whether a variable has been declared before its use

D. Variable names of arbitrary length

gate1994 compiler-design grammar normal

# Answer key


# 2.12.8 Grammar: GATE CSE 1994 | Question: 20

A grammar $G$ is in Chomsky-Normal Form (CNF) if all its productions are of the form $A \to BC$ or $A \to a$ , where $A, B$ and $C$ , are non-terminals and $a$ is a terminal. Suppose $G$ is a CFG in CNF and $w$ is a string in $L(G)$ of length $n$ , then how long is a derivation of $w$ in $G$ ?

gate1994 compiler-design grammar normal descriptive

# Answer key


# 2.12.9 Grammar: GATE CSE 1994 | Question: 3.5

Match the following items

<table><tr><td>(i)</td><td>Backus-Naur form</td><td>(a)</td><td>Regular expressions</td></tr><tr><td>(ii)</td><td>Lexical analysis</td><td>(b)</td><td>LALR(1) grammar</td></tr><tr><td>(iii)</td><td>YACC</td><td>(c)</td><td>LL(1) grammars</td></tr><tr><td>(iv)</td><td>Recursive descent parsing</td><td>(d)</td><td>General context-free grammars</td></tr></table>

gate1994 compiler-design grammar normal match-the-following

# Answer key

# 2.12.10 Grammar: GATE CSE 1995 | Question: 1.10

Consider a grammar with the following productions

- $S \to a\alpha b \mid b\alpha c \mid aB$  
- $S \to \alpha S \mid b$  
- $S \to \alpha bb \mid ab$  
- $S\alpha \rightarrow bdb \mid b$

The above grammar is:

A. Context free

B. Regular

C. Context sensitive

D. $LR(k)$

gate1995 compiler-design grammar normal

# Answer key

# 2.12.11 Grammar: GATE CSE 1995 | Question: 9




A. Translate the arithmetic expression $a^{*} - (b + c)$ into syntax tree.  
B. A grammar is said to have cycles if it is the case that $A \stackrel{+}{\Rightarrow} A$ Show that no grammar that has cycles can be LL(1).

gate1995 compiler-design grammar normal descriptive

# Answer key

# 2.12.12 Grammar: GATE CSE 1996 | Question: 11


Let $G$ be a context-free grammar where $G = (\{S, A, B, C\}, \{a, b, d\}, P, S)$ with the productions in $P$ given below.

- $S \rightarrow ABAC$  
- $A \rightarrow aA \mid \varepsilon$  
- $B \rightarrow bB \mid \varepsilon$  
• C → d

$(\varepsilon$ denotes the null string). Transform the grammar $G$ to an equivalent context-free grammar $G'$ that has no $\varepsilon$ productions and no unit productions. (A unit production is of the form $x \to y$ , and $x$ and $y$ are non terminals).

gate1996 compiler-design grammar normal descriptive

# Answer key

# 2.12.13 Grammar: GATE CSE 1996 | Question: 2.10

The grammar whose productions are


- $\langle \mathrm{stmt}\rangle \rightarrow$ if id then $\langle \mathrm{stmt}\rangle$  
- $\langle \mathrm{stmt}\rangle \to$ if id then $\langle \mathrm{stmt}\rangle$ else $\langle \mathrm{stmt}\rangle$  
- $\langle \mathrm{stmt}\rangle \rightarrow \mathrm{id} := \mathrm{id}$

is ambiguous because

(a) the sentence

if a then if b then c:=d

has more than two parse trees

(b) the left most and right most derivations of the sentence

if a then if b then c:=d

give rise to different parse trees

(c) the sentence

if a then if b then c:= d else c:= f

has more than two parse trees

(d) the sentence

if a then if b then c:= d else c:= f

has two parse trees

gate1996 compiler-design grammar normal

# Answer key

# 2.12.14 Grammar: GATE CSE 1997 | Question: 11

Consider the grammar

- $S \rightarrow bSe$  
- $S \rightarrow PQR$


- $P \rightarrow bPc$  
- $P \rightarrow \varepsilon$  
- $Q \rightarrow cQd$  
$\cdot Q\rightarrow \varepsilon$  
- $R \rightarrow dRe$  
- $R \to \varepsilon$

where $S, P, Q, R$ are non-terminal symbols with $S$ being the start symbol; $b, c, d, e$ are terminal symbols and $\varepsilon'$ is the empty string. This grammar generates strings of the form $b^i, c^j, d^k, e^m$ for some $i, j, k, m \geq 0$ .

a. What is the condition on the values of i, j, k, m?  
b. Find the smallest string that has two parse trees.

gate1997 compiler-design grammar normal theory-of-computation descriptive

Answer key

# 2.12.15 Grammar: GATE CSE 1998 | Question: 14


A. Let $G_{1} = (N, T, P, S_{1})$ be a CFG where, $N = \{S_{1}, A, B\}$ , $T = \{a, b\}$ and $P$ is given by

$$
\begin{array}{l l}S _ {1} \rightarrow a S _ {1} b&S _ {1} \rightarrow a B b\\S _ {1} \rightarrow a A b&B \rightarrow B b\\A \rightarrow a A&B \rightarrow b\\A \rightarrow a\end{array}
$$

What is $L(G_{1})$ ?

B. Use the grammar in Part(a) to give a CFG for $L_{2} = \{a^{i}b^{j}a^{k}b^{l} \mid i,j,k,l \geq 1, i = j \text{ or } k = l\}$ by adding not more than 5 production rules.  
C. Is $L_{2}$ inherently ambiguous?

gate1998 compiler-design grammar descriptive

Answer key

# 2.12.16 Grammar: GATE CSE 1998 | Question: 6b


Consider the grammar

- $\mathrm{S} \rightarrow Aa \mid b$  
- $A \to Ac \mid Sd \mid \epsilon$

Construct an equivalent grammar with no left recursion and with minimum number of production rules.

gate1998 compiler-design grammar descriptive

Answer key

# 2.12.17 Grammar: GATE CSE 1999 | Question: 2.15


A grammar that is both left and right recursive for a non-terminal, is

A. Ambiguous  
B. Unambiguous  
C. Information is not sufficient to decide whether it is ambiguous or unambiguous  
D. None of the above

# 2.12.18 Grammar: GATE CSE 2001 | Question: 1.18

Which of the following statements is false?

A. An unambiguous grammar has same leftmost and rightmost derivation  
B. An LL(1) parser is a top-down parser  
C. LALR is more powerful than SLR  
D. An ambiguous grammar can never be LR(k) for any k

gatecse-2001 compiler-design grammar normal

# Answer key

# 2.12.19 Grammar: GATE CSE 2001 | Question: 18

A. Remove left-recursion from the following grammar: $S \rightarrow Sa \mid Sb \mid a \mid b$  
B. Consider the following grammar:

$$
S \rightarrow a S b S \mid b S a S \mid \epsilon
$$

Construct all possible parse trees for the string abab. Is the grammar ambiguous?

gatecse-2001 compiler-design grammar descriptive

# Answer key

# 2.12.20 Grammar: GATE CSE 2003 | Question: 56

Consider the grammar shown below

- $S \to iEtSS' \mid a$  
- $S' \to eS \mid \epsilon$  
- $E \rightarrow b$

In the predictive parse table, $M$ , of this grammar, the entries $M[S', e]$ and $M[S', \$]$ respectively are

A. $\{S' \to eS\}$ and $\{S' \to \epsilon\}$  
B. $\{S' \to eS\}$ and $\{\}$  
C. $\{S^{\prime}\rightarrow \epsilon \}$ and $\{S^{\prime}\rightarrow \epsilon \}$  
D. $\{S^{\prime}\rightarrow eS,S^{\prime}\rightarrow \varepsilon \}$ and $\{S^{\prime}\rightarrow \epsilon \}$

gatecse-2003 compiler-design grammar normal parsing

# Answer key

# 2.12.21 Grammar: GATE CSE 2003 | Question: 57

Consider the grammar shown below.

- $S \to CC$  
- $C \rightarrow cC \mid d$

This grammar is

A. LL(1)  
C. LALR(1) but not SLR(1)  
gatecse-2003 compiler-design grammar parsing normal  
B. SLR(1) but not LL(1)  
D. LR(I) but not LALR(1)

# Answer key





# 2.12.22 Grammar: GATE CSE 2003 | Question: 58

Consider the translation scheme shown below.

- $S \rightarrow T R$  
- $R \to +T\{\text{print}('+');\}R \mid \varepsilon$  
- $T \to \mathsf{num}$ {print(num.val); }

Here num is a token that represents an integer and num.val represents the corresponding integer value. For an input string '9 + 5 + 2', this translation scheme will print

A. $9 + 5 + 2$

B. $95 + 2+$

C. 952++

D. $+ + 952$

gatecse-2003 compiler-design grammar normal

# Answer key

# 2.12.23 Grammar: GATE CSE 2004 | Question: 8

Which of the following grammar rules violate the requirements of an operator grammar? P, Q, R are nonterminals, and r, s, t are terminals.

1. $P \rightarrow QR$  
II. $P\to QsR$  
III. $P \rightarrow \varepsilon$  
IV. $P\to QtRr$

A. (I) only

B. (I) and (III) only

C. (II) and (III) only

D. (III) and (IV) only

gatecse-2004 compiler-design grammar normal

# Answer key

# 2.12.24 Grammar: GATE CSE 2004 | Question: 88

Consider the following grammar G:

$$
S \rightarrow b S \mid a A \mid b
$$

$$
A \rightarrow b A \mid a B
$$

$$
B \rightarrow b B \mid a S \mid a
$$

Let $N_{a}(w)$ and $N_{b}(w)$ denote the number of a's and b's in a string $\omega$ respectively.

The language $L(G)$ over $\{a,b\}^{+}$ generated by $G$ is

A. $\{w \mid N_a(w) > 3N_b(w)\}$  
B. $\{w \mid N_b(w) > 3N_a(w)\}$  
C. $\{w \mid N_a(w) = 3k, k \in \{0, 1, 2, \dots\}\}$  
D. $\{w \mid N_b(w) = 3k, k \in \{0, 1, 2, \dots\}\}$

gatecse-2004 compiler-design grammar normal

# Answer key

# 2.12.25 Grammar: GATE CSE 2005 | Question: 14

The grammar $A \to AA \mid (A) \mid \epsilon$ is not suitable for predictive-parsing because the grammar is:

A. ambiguous

B. left-recursive

C. right-recursive

D. an operator-grammar

gatecse-2005 compiler-design parsing grammar easy

# Answer key





Consider the grammar:

$$
E \rightarrow E + n \mid E \times n \mid n
$$

For a sentence $n + n \times n$ , the handles in the right-sentential form of the reduction are:

A. $n, E + n$ and $E + n \times n$

B. $n, E + n$ and $E + E \times n$

C. $n, n + n$ and $n + n \times n$

D. $n, E + n$ and $E \times n$

gatecse-2005 compiler-design grammar normal

# Answer key

# 2.12.27 Grammar: GATE CSE 2006 | Question: 32, ISRO2016-35

Consider the following statements about the context free grammar


$$
G = \{S \rightarrow S S, S \rightarrow a b, S \rightarrow b a, S \rightarrow \epsilon \}
$$

I. $G$ is ambiguous  
II. $G$ produces all strings with equal number of $a$ 's and $b$ 's  
III. G can be accepted by a deterministic PDA.

Which combination below expresses all the true statements about G?

A. I only

B. I and III only

C. II and III only

D. I, II and III

gatecse-2006 compiler-design grammar normal isro2016

# Answer key

# 2.12.28 Grammar: GATE CSE 2006 | Question: 59

Consider the following translation scheme.

- $S \rightarrow ER$  
- $R \to *E\{\text{print}('*');\} R \mid \varepsilon$  
- $E \to F + E\{\mathrm{print}(' + ');\}\mid F$  
- $F \to (S) \mid id \{\text{print}(id. value);\}$

Here $id$ is a token that represents an integer and $id.value$ represents the corresponding integer value. For an input $2 * 3 + 4$ , this translation scheme prints

A. $2 \times 3 + 4$

B. $2* + 34$

C. $23 \times 4+$

D. 234+\*

gatecse-2006 compiler-design grammar normal

# Answer key

# 2.12.29 Grammar: GATE CSE 2006 | Question: 84

Which one of the following grammars generates the language $L = \{a^i b^j \mid i \neq j\}$ ?

A. $S \rightarrow AC \mid CB$

$$
C \rightarrow a C b \mid a \mid b
$$

$$
A \rightarrow a A \mid \varepsilon
$$

$$
B \rightarrow B b \mid \varepsilon
$$

B. $S \to aS \mid Sb \mid a \mid b$

B. $S \to aS \mid Sb \mid a \mid b$

c. $S \to AC \mid CB$

$$
C \rightarrow a C b \mid \varepsilon
$$

$$
A \rightarrow a A \mid \varepsilon
$$

$$
B \rightarrow B b \mid \varepsilon
$$

D. $S \to AC \mid CB$

$$
C \to a C b \mid \varepsilon
$$

$$
A \rightarrow a A \mid a
$$

$$
B \rightarrow B b \mid b
$$

gatecse-2006 compiler-design grammar normal theory-of-computation

# Answer key



The grammar

- $S \to AC \mid CB$  
- $C \rightarrow aCb \mid \epsilon$  
- $A \rightarrow aA \mid a$  
- $B \to Bb \mid b$

generates the language $L = \{a^i b^j \mid i \neq j\}$ . In this grammar what is the length of the derivation (number of steps starting from $S$ ) to generate the string $a^l b^m$ with $l \neq m$

A. $\max(l,m)+2$

B. $l + m + 2$

C. $l + m + 3$

D. $\max (l,m) + 3$

gatecse-2006 compiler-design grammar normal

# Answer key

# 2.12.31 Grammar: GATE CSE 2007 | Question: 52

Consider the grammar with non-terminals $N = \{S, C, S_1\}$ , terminals $T = \{a, b, i, t, e\}$ , with $S$ as the start symbol, and the following set of rules:

$$
S \rightarrow i C t S S _ {1} \mid a
$$

$$
S _ {1} \rightarrow e S \mid \epsilon
$$

$$
C \rightarrow b
$$

The grammar is NOT LL(1) because:

A. it is left recursive

B. it is right recursive

C. it is ambiguous

D. it is not context-free

gatecse-2007 compiler-design grammar normal

# Answer key

# 2.12.32 Grammar: GATE CSE 2007 | Question: 53

Consider the following two statements:

• P: Every regular grammar is LL(1)  
• Q: Every regular set has a LR(1) grammar

Which of the following is TRUE?

A. Both P and Q are true

B. P is true and Q is false

C. P is false and Q is true

D. Both P and Q are false

gatecse-2007 compiler-design grammar normal

# Answer key

# 2.12.33 Grammar: GATE CSE 2007 | Question: 78

Consider the CFG with $\{S, A, B\}$ as the non-terminal alphabet, $\{a, b\}$ as the terminal alphabet, S as the start symbol and the following set of production rules:

$$
S \rightarrow a B \quad \quad S \rightarrow b A
$$

$$
B \rightarrow b \quad A \rightarrow a
$$

$$
B \rightarrow b S \quad A \rightarrow a S
$$

$$
B \rightarrow a B B \quad A \rightarrow b A A
$$

Which of the following strings is generated by the grammar?

A. aaaabb

B. aabbbb

C. aabbab

D. abbbba

gatecse-2007 compiler-design grammar normal

# Answer key




# 2.12.34 Grammar: GATE CSE 2007 | Question: 79


Consider the CFG with $\{S, A, B\}$ as the non-terminal alphabet, $\{a, b\}$ as the terminal alphabet, S as the start symbol and the following set of production rules:

$$
S \rightarrow a B \quad \quad S \rightarrow b A
$$

$$
B \rightarrow b \quad A \rightarrow a
$$

$$
B \rightarrow b S \quad A \rightarrow a S
$$

$$
B \rightarrow a B B \quad A \rightarrow b A A
$$

For the string aabbab, how many derivation trees are there?

A. 1

B. 2

C. 3

D. 4

gatecse-2007 compiler-design grammar normal

# Answer key

# 2.12.35 Grammar: GATE CSE 2008 | Question: 50

Which of the following statements are true?


I. Every left-recursive grammar can be converted to a right-recursive grammar and vice-versa  
II. All $\epsilon$ -productions can be removed from any context-free grammar by suitable transformations  
III. The language generated by a context-free grammar all of whose productions are of the form $X \to w$ or $X \to wY$ (where, $w$ is a string of terminals and $Y$ is a non-terminal), is always regular  
IV. The derivation trees of strings generated by a context-free grammar in Chomsky Normal Form are always binary trees

A. I, II, III and IV

B. II, III and IV only

C. I, III and IV only

D. I, II and IV only

gatecse-2008 normal compiler-design grammar

# Answer key

# 2.12.36 Grammar: GATE CSE 2010 | Question: 38

The grammar $S \to aSa \mid bS \mid c$ is


A. LL(1) but not LR(1)

B. LR(1) but not LL(1)

C. Both LL(1) and LR(1)

D. Neither LL(1) nor LR(1)

gatecse-2010 compiler-design grammar normal

# Answer key

# 2.12.37 Grammar: GATE CSE 2016 | Set 2 | Question: 45

Which one of the following grammars is free from left recursion?


A. $S \rightarrow AB$

B. $S \rightarrow Ab \mid Bb \mid c$

C. $S\to Aa\mid B$

D. $S \to Aa \mid Bb \mid c$

$$
A \rightarrow A a \mid b
$$

$$
A \rightarrow B d \mid \epsilon
$$

$$
A \rightarrow B b \mid S c \mid \epsilon
$$

$$
A \rightarrow B d \mid \epsilon
$$

$$
B \rightarrow c
$$

$$
B \rightarrow e
$$

$$
B \rightarrow d
$$

$$
B \rightarrow A e \mid \epsilon
$$

gatecse-2016-set2 compiler-design grammar easy

# Answer key

# 2.12.38 Grammar: GATE CSE 2016 | Set 2 | Question: 46

A student wrote two context-free grammars G1 and G2 for generating a single C-like array declaration. The dimension of the array is at least one. For example,


int a[10] [3];

The grammars use D as the start symbol, and use six terminal symbols int ; id [ ] num.

<table><tr><td>Grammar G1</td><td>Grammar G2</td></tr><tr><td>D → int L;</td><td>D → int L;</td></tr><tr><td>L → id [E</td><td>L → id E</td></tr><tr><td>E → num ]</td><td>E → E [num]</td></tr><tr><td>E → num ] [E</td><td>E → [num]</td></tr></table>

Which of the grammars correctly generate the declaration mentioned above?

A. Both G1 and G2

B. Only G1

C. Only G2

D. Neither G1 nor G2

gatecse-2016-set2 compiler-design grammar normal

# Answer key

# 2.12.39 Grammar: GATE CSE 2017 | Set 2 | Question: 32

Consider the following expression grammar G:

- $E \rightarrow E - T \mid T$  
- $T \rightarrow T + F \mid F$  
- $F \rightarrow (E) \mid id$

Which of the following grammars is not left recursive, but is equivalent to G?

A. $E \rightarrow E - T \mid T$

$$
T \rightarrow T + F \mid F
$$

$$
F \rightarrow (E) \mid i d
$$

B. $E \rightarrow TE'$

$$
E ^ {\prime} \rightarrow - T E ^ {\prime} \mid \epsilon
$$

$$
T \rightarrow T + F \mid F
$$

$$
F \rightarrow (E) \mid i d
$$

C. $E \rightarrow TX$

$$
X \rightarrow - T X \mid \epsilon
$$

$$
T \rightarrow F Y
$$

$$
Y \rightarrow + F Y \mid \epsilon
$$

$$
F \rightarrow (E) \mid i d
$$

D. $E \rightarrow TX \mid (TX)$

$$
X \rightarrow - T X \mid + T X \mid \epsilon
$$

$$
T \rightarrow i d
$$

gatecse-2017-set2 grammar

# Answer key

# 2.12.40 Grammar: GATE CSE 2019 | Question: 43

Consider the augmented grammar given below:

- $S' \to S$  
- $S \to \langle L \rangle \mid id$  
- $L \to \dot{L}, \dot{S} \mid S$

Let $I_0 = \text{CLOSURE}(\{[S' \to \cdot S]\})$ . The number of items in the set $\text{GOTO}(I_0, \langle \rangle)$ is \_\_\_\_

gatecse-2019 numerical-answers compiler-design grammar two-marks

# Answer key

# 2.12.41 Grammar: GATE CSE 2021 | Set 1 | Question: 31

Consider the following context-free grammar where the set of terminals is $\{a, b, c, d, f\}$ .

$$
\begin{array}{l} \mathrm{S} \quad \rightarrow \quad d a \mathrm{T} \mid \mathrm{R} f \\ \mathrm{T} \rightarrow a \mathrm{S} \mid b a \mathrm{T} \mid \epsilon \\ \mathrm{R} \rightarrow c a \mathrm{TR} | \epsilon \\ \end{array}
$$

The following is a partially-filled LL(1) parsing table.




<table><tr><td></td><td>a</td><td>b</td><td>c</td><td>d</td><td>f</td><td>$</td></tr><tr><td>S</td><td></td><td></td><td>1</td><td>S → daT</td><td>2</td><td></td></tr><tr><td>T</td><td>T → aS</td><td>T → baT</td><td>3</td><td></td><td>T → ε</td><td>4</td></tr><tr><td>R</td><td></td><td></td><td>R → caTR</td><td></td><td>R → ε</td><td></td></tr></table>

Which one of the following choices represents the correct combination for the numbered cells in the parsing table (“blank” denotes that the corresponding cell is empty)?

A. $\boxed{1}$ S → Rf  
B. 1 blank  
C. 1 S → Rf  
D. 1 blank  
2 S → Rf  
$2\mathrm{S}\rightarrow\mathrm{R}f$  
2 blank  
2 S → Rf  
3 T → ε  
3 T → ε  
3 blank  
3 blank  
4 T → ε  
4 T → ε  
4 T → ε  
4 blank

gatecse-2021-set1 compiler-design grammar two-marks

# Answer key

# 2.12.42 Grammar: GATE CSE 2024 | Set 1 | Question: 49


Let $G = (V, \Sigma, S, P)$ be a context-free grammar in Chomsky Normal Form with $\Sigma = \{a, b, c\}$ and $V$ containing 10 variable symbols including the start symbol $S$ . The string $w = a^{30} b^{30} c^{30}$ is derivable from $S$ . The number of steps (application of rules) in the derivation $S \to^* w$ is \_\_\_\_.

gatecse-2024-set1 numerical-answers compiler-design grammar two-marks

# Answer key

# 2.12.43 Grammar: GATE CSE 2024 | Set 2 | Question: 42


Consider a context-free grammar G with the following 3 rules.

$$
S \rightarrow a S, S \rightarrow a S b S, S \rightarrow c
$$

Let $w \in L(G)$ . Let $n_a(w), n_b(w), n_c(w)$ denote the number of times $a, b, c$ occur in $w$ , respectively. Which of the following statements is/are TRUE?

A. $n_a(w) > n_b(w)$

C. $n_c(w) = n_b(w) + 1$

B. $n_a(w) > n_c(w) - 2$

D. $n_c(w) = n_b(w)*2$

gatecse-2024-set2 compiler-design multiple-selects grammar two-marks

# Answer key

# 2.12.44 Grammar: GATE CSE 2025 | Set 2 | Question: 41

Consider two grammars $G_{1}$ and $G_{2}$ with the production rules given below:


$G_{1}:S\to if E then S|if E then S else S|a$

$$
E \to b
$$

$G_{2}:S\to if E then S\mid M$

$M\to if E then M else S|c$

$$
E \rightarrow b
$$

where if, then, else, $a, b, c$ are the terminals.

Which of the following option(s) is/are CORRECT?

A. $G_{1}$ is not $LL(1)$ and $G_{2}$ is $LL(1)$

C. $G_{1}$ and $G_{2}$ are not $LL(1)$

B. $G_{1}$ is $LL(1)$ and $G_{2}$ is not $LL(1)$

D. $G_{1}$ and $G_{2}$ are ambiguous.

gatecse2025-set2 compiler-design grammar multiple-selects easy two-marks