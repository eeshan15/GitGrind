IV. $\{xcy \mid x, y, \in \{a, b\}^*\}$

A. I and IV only

B. I and III only

C. I only

D. IV only

gatecse-2008 theory-of-computation normal regular-language

# Answer key

# 6.20.15 Regular Language: GATE CSE 2011 | Question: 24

Let P be a regular language and Q be a context-free language such that $Q \subseteq P$ . (For example, let P be the language represented by the regular expression $p^{*}q^{*}$ and Q be $\{p^{n}q^{n} \mid n \in N\}$ ). Then which of the following is ALWAYS regular?

A. $P \cap Q$

B. P - Q

C. $\Sigma^{*} - P$

D. $\Sigma^{*} - Q$

gatecse-2011 theory-of-computation easy regular-language

# Answer key

# 6.20.16 Regular Language: GATE CSE 2012 | Question: 25

Given the language $L = \{ab, aa, baa\}$ , which of the following strings are in $L^*$ ?

1. abaabaaabaa  
2. aaaabaaaa  
3. baaaaabaaaab  
4. baaaaabaa

A. 1, 2 and 3

B. 2, 3 and 4

C. 1, 2 and 4

D. 1, 3 and 4

gatecse-2012 theory-of-computation easy regular-language

# Answer key

# 6.20.17 Regular Language: GATE CSE 2013 | Question: 8

Consider the languages $L_{1} = \phi$ and $L_{2} = \{a\}$ . Which one of the following represents $L_{1}L_{2}^{*}\cup L_{1}^{*}$ ?

A. $\{\epsilon\}$

B. $\phi$

C. $a^{*}$

D. $\{\epsilon,a\}$

gatecse-2013 theory-of-computation normal regular-language

# Answer key

# 6.20.18 Regular Language: GATE CSE 2014 | Set 1 | Question: 15

Which one of the following is TRUE?

A. The language $L = \{a^n b^n \mid n \geq 0\}$ is regular.  
B. The language $L = \{a^n \mid n \text{ is prime} \}$ is regular.  
C. The language $L = \{w \mid w \text{ has } 3k + 1b's \text{ for some } k \in N \text{ with } \Sigma = \{a, b\}\}$ is regular.  
D. The language $L = \{ww \mid w \in \Sigma^* \text{ with } \Sigma = \{0,1\}\}$ is regular.

gatecse-2014-set1 theory-of-computation regular-language normal

# Answer key

# 6.20.19 Regular Language: GATE CSE 2014 | Set 2 | Question: 15

If $L_{1} = \{a^{n} \mid n \geq 0\}$ and $L_{2} = \{b^{n} \mid n \geq 0\}$ , consider

I. $L_{1}, L_{2}$ is a regular language  
$\| .L_{1}.L_{2} = \{a^{n}b^{n}\mid n\geq 0\}$

Which one of the following is CORRECT?

A. Only I

B. Only II

C. Both I and II

D. Neither I nor II






# Answer key

# 6.20.20 Regular Language: GATE CSE 2014 | Set 2 | Question: 36


Let $L_{1} = \{w \in \{0,1\}^{*} \mid w \quad \text{has at least as many occurrences of } (110)'\text{s as } (011)'\text{s}\}$ . Let $L_{2} = \{w \in \{0,1\}^{*} \mid w \text{ has at least as many occurrences of } (000)'\text{s as } (111)'\text{s}\}$ . Which one of the following is TRUE?

A. $L_{1}$ is regular but not $L_{2}$

B. $L_{2}$ is regular but not $L_{1}$

C. Both $L_{1}$ and $L_{2}$ are regular

D. Neither $L_{1}$ nor $L_{2}$ are regular

gatecse-2014-set2 theory-of-computation normal regular-language

# Answer key

# 6.20.21 Regular Language: GATE CSE 2015 | Set 2 | Question: 51


Which of the following is/are regular languages?

$L_{1}:\left\{wxw^{R}\mid w,x\in\{a,b\}^{*}\text{ and }|w|,|x|>0\right\},w^{R}\text{ is the reverse of string }w$

$L_{2}:\{a^{n}b^{m}\mid m\neq n\text{ and }m,n\geq 0\}$

$L_{3}:\{a^{p}b^{q}c^{r}\mid p,q,r\geq 0\}$

A. $L_{1}$ and $L_{3}$ only

B. $L_{2}$ only

C. $L_{2}$ and $L_{3}$ only

D. $L_{3}$ only

gatecse-2015-set2 theory-of-computation normal regular-language

# Answer key

# 6.20.22 Regular Language: GATE CSE 2016 | Set 2 | Question: 17


Language $L_{1}$ is defined by the grammar: $S_{1} \rightarrow aS_{1}b \mid \varepsilon$

Language $L_{2}$ is defined by the grammar: $S_{2} \rightarrow abS_{2} \mid \varepsilon$

Consider the following statements:

- P: $L_{1}$ is regular  
- Q: $L_{2}$ is regular

Which one of the following is TRUE?

A. Both $P$ and $Q$ are true.

B. $P$ is true and $Q$ is false.

C. $P$ is false and $Q$ is true.

D. Both $P$ and $Q$ are false.

gatecse-2016-set2 theory-of-computation easy regular-language

# Answer key

# 6.20.23 Regular Language: GATE CSE 2018 | Question: 52


Given a language L, define $L^{i}$ as follows:

$$
L ^ {0} = \{\varepsilon \}
$$

$$
L ^ {i} = L ^ {i - 1} \bullet L \text {   for   all   } I > 0
$$

The order of a language $L$ is defined as the smallest $k$ such that $L^k = L^{k+1}$ . Consider the language $L_1$ (over alphabet 0) accepted by the following automaton.

![](images/fe3e44b4a478dd81dbf5a315d12ca895cdb7e729f52a28d90b700eb7dcda3f25.jpg)

The order of $L_{1}$ is \_\_\_\_.

# 6.20.24 Regular Language: GATE CSE 2019 | Question: 7

If $L$ is a regular language over $\Sigma = \{a, b\}$ , which one of the following languages is NOT regular?

A. $L.L^{R} = \{xy\mid x\in L,y^{R}\in L\}$  
B. $\{ww^R \mid w \in L\}$  
C. Prefix $(L) = \{x\in \Sigma^{*}\mid \exists y\in \Sigma^{*}$ such that $xy\in L\}$  
D. Suffix $(L) = \{y\in \Sigma^{*}\mid \exists x\in \Sigma^{*}$ such that $xy\in L\}$

gatecse-2019 theory-of-computation regular-language one-mark

# Answer key

# 6.20.25 Regular Language: GATE CSE 2020 | Question: 51

Consider the following language.

$L = \{x\in \{a,b\}^{*}|$ number of $a$ 's in $x$ divisible by 2 but not divisible by 3}

The minimum number of states in DFA that accepts $L$ is \_\_\_\_

gatecse-2020 numerical-answers theory-of-computation regular-language two-marks

# Answer key

# 6.20.26 Regular Language: GATE CSE 2020 | Question: 8

Consider the following statements.

I. If $L_{1} \cup L_{2}$ is regular, then both $L_{1}$ and $L_{2}$ must be regular.  
II. The class of regular languages is closed under infinite union.

Which of the above statements is/are TRUE?

A. I only

C. Both I and II

gatecse-2020 theory-of-computation regular-language one-mark

B. II only

D. Neither I nor II

# Answer key

# 6.20.27 Regular Language: GATE CSE 2021 | Set 2 | Question: 9

Let $L \subseteq \{0,1\}^{*}$ be an arbitrary regular language accepted by a minimal DFA with k states. Which one of the following languages must necessarily be accepted by a minimal DFA with k states?

A. $L - \{01\}$

B. $L \cup \{01\}$

C. $\{0,1\}^{*} - L$

D. $L \cdot L$

gatecse-2021-set2 theory-of-computation finite-automata regular-language one-mark

# Answer key

# 6.20.28 Regular Language: GATE CSE 2024 | Set 1 | Question: 13

Let $L_{1}, L_{2}$ be two regular languages and $L_{3}$ a language which is not regular.

Which of the following statements is/are always TRUE?

A. $L_{1} = L_{2}$ if and only if

$$
L _ {1} \cap \overline {{L _ {2}}} = \phi
$$

C. $\overline{L_3}$ is not regular

B. $L_{1} \cup L_{3}$ is not regular

D. $\overline{L_1} \cup \overline{L_2}$ is regular

gatecse-2024-set1 multiple-selects theory-of-computation regular-language one-mark

# Answer key






A regular language $L$ is accepted by a non-deterministic finite automaton (NFA) with $n$ states. Which of the following statement(s) is/are FALSE?

A. L may have an accepting NFA with < n states.  
B. $L$ may have an accepting DFA with $< n$ states.  
C. There exists a DFA with $\leq 2^n$ states that accepts $L$ .  
D. Every DFA that accepts $L$ has $>2^{n}$ states.

gatecse2025-set1 theory-of-computation finite-automata regular-language multiple-selects one-mark

Answer key

# 6.20.30 Regular Language: GATE CSE 2025 | Set 1 | Question: 34

Consider the following two languages over the alphabet $\{a, b\}$ :

$$
L _ {1} = \{\alpha \beta \alpha \mid \alpha \in \{a, b \} ^ {+} \text {AND} \beta \in \{a, b \} ^ {+} \}
$$

$$
L _ {2} = \{\alpha \beta \alpha \mid \alpha \in \{a \} ^ {+} \text {AND} \beta \in \{a, b \} ^ {+} \}
$$

Which ONE of the following statements is CORRECT?

A. Both $L_{1}$ and $L_{2}$ are regular languages.  
B. $L_{1}$ is a regular language but $L_{2}$ is not a regular language.  
C. $L_{1}$ is not a regular language but $L_{2}$ is a regular language.  
D. Neither $L_{1}$ nor $L_{2}$ is a regular language.

gatecse2025-set1 theory-of-computation regular-language two-marks

Answer key

# 6.20.31 Regular Language: GATE CSE 2025 | Set 2 | Question: 42

Let $\Sigma = \{a, b, c\}$ . For $x \in \Sigma^{*}$ , and $\alpha \in \Sigma$ , let $\#_{\alpha}(x)$ denote the number of occurrences of $\alpha$ in $x$ . Which one or more of the following option(s) define(s) regular language(s)?

A. $\{a^m b^n \mid m, n \geq 0\}$  
B. $\{a, b\}^* \cap \{a^m b^n c^{m-n} \mid m \geq n \geq 0\}$  
C. $\{w \mid w \in \{a, b\}^*, \#_a(w) \equiv 2 (\bmod 7), \text{and} \#_b(w) \equiv 3 (\bmod 9)\}$  
D. $\{w \mid w \in \{a, b\}^*, \#_a(w) \equiv 2 (\bmod 7), \text{and} \#_a(w) = \#_b(w)\}$

gatecse2025-set2 theory-of-computation regular-language multiple-selects two-marks

Answer key

# 6.20.32 Regular Language: GATE IT 2006 | Question: 30

Which of the following statements about regular languages is NOT true?

A. Every language has a regular superset  
B. Every language has a regular subset  
C. Every subset of a regular language is regular  
D. Every subset of a finite language is regular

gateit-2006 theory-of-computation easy regular-language

Answer key




# 6.20.33 Regular Language: GATE IT 2006 | Question: 80

Let L be a regular language. Consider the constructions on L below:

I. repeat (L) = {ww | w ∈ L}  
II. prefix (L) = {u | ∃v : uv ∈ L}  
II. suffix (L) = {v | ∃u : uv ∈ L}  
IV. half $(L) = \{u\mid \exists v:|v| = |u|$ and $uv\in L\}$

Which of the constructions could lead to a non-regular language?

A. Both I and IV

B. Only I

C. Only IV

D. Both II and III

gateit-2006 theory-of-computation normal regular-language

# Answer key

# 6.20.34 Regular Language: GATE IT 2006 | Question: 81

Let L be a regular language. Consider the constructions on L below:

1. repeat(L) = {ww | w ∈ L}  
$\| .\operatorname{prefix}(L) = \{u\mid \exists v:uv\in L\}$  
$\| \cdot$ . suffix(L) = {v | ∃u : uv ∈ L}  
IV. half(L) = {u | ∃v : |v| = |u| and uv ∈ L}

Which of the constructions could lead to a non-regular language?

a. Both I and IV

b. Only I

d. Both II and III

Which choice of L is best suited to support your answer above?

A. $(a + b)^{*}$  
C. $(ab)^{*}$

B. $\{\epsilon, a, ab, bab\}$  
D. $\{a^n b^n \mid n \geq 0\}$

gateit-2006 theory-of-computation normal regular-language

# Answer key

# 6.20.35 Regular Language: GATE IT 2008 | Question: 35

Which of the following languages is (are) non-regular?

- $L_{1} = \{0^{m}1^{n} \mid 0 \leq m \leq n \leq 10000\}$  
- $L_{2} = \{w \mid w \text{ reads the same forward and backward}\}$  
- $L_{3} = \{w \in \{0,1\}^{*} \mid w \text{ contains an even number of } 0's \text{ and an even number of } 1's\}$

A. $L_{2}$ and $L_{3}$ only

B. $L_{1}$ and $L_{2}$ only

C. $L_{3}$ only

D. $L_{2}$ only

gateit-2008 theory-of-computation normal regular-language

# Answer key

# 6.21

# Turing Machine (1)

# Practice Test: Test 1 (13Q)

# 6.21.1 Turing Machine: GATE CSE 2026 | Set 2 | Question: 3

Which one of the following statements is equivalent to the following assertion?

Turing machine $M$ decides the language $L \subseteq \{0,1\}^*$

A. Turing machine M halts on all input strings in $\{0,1\}^{*}$  
B. Turing machine M accepts all input strings in L  
C. Turing machine $M$ rejects all input strings in $\{0,1\}^{*} - L$  
D. Turing machine M accepts all input strings in L and rejects all input strings in $\{0,1\}^{*}-L$





Answer Keys

<table><tr><td>6.1.1</td><td>A;C</td><td>6.1.2</td><td>A;B</td><td>6.1.3</td><td>A</td><td>6.1.4</td><td>C</td><td>6.1.5</td><td>D</td></tr><tr><td>6.1.6</td><td>B</td><td>6.1.7</td><td>B</td><td>6.1.8</td><td>B;C</td><td>6.1.9</td><td>C</td><td>6.1.10</td><td>D</td></tr><tr><td>6.2.1</td><td>A</td><td>6.2.2</td><td>A;B;C</td><td>6.3.1</td><td>False</td><td>6.3.2</td><td>A;D</td><td>6.3.3</td><td>A</td></tr><tr><td>6.3.4</td><td>B</td><td>6.3.5</td><td>B</td><td>6.3.6</td><td>B</td><td>6.3.7</td><td>N/A</td><td>6.3.8</td><td>N/A</td></tr><tr><td>6.3.9</td><td>B</td><td>6.3.10</td><td>C</td><td>6.3.11</td><td>B</td><td>6.3.12</td><td>D</td><td>6.3.13</td><td>B</td></tr><tr><td>6.3.14</td><td>B</td><td>6.3.15</td><td>D</td><td>6.3.16</td><td>D</td><td>6.3.17</td><td>B</td><td>6.3.18</td><td>B</td></tr><tr><td>6.3.19</td><td>D</td><td>6.3.20</td><td>A</td><td>6.3.21</td><td>C</td><td>6.3.22</td><td>C</td><td>6.3.23</td><td>C</td></tr><tr><td>6.3.24</td><td>B;C;D</td><td>6.3.25</td><td>B;C;D</td><td>6.3.26</td><td>B</td><td>6.3.27</td><td>C</td><td>6.3.28</td><td>B;D</td></tr><tr><td>6.3.29</td><td>A;C;D</td><td>6.3.30</td><td>B</td><td>6.3.31</td><td>B</td><td>6.3.32</td><td>A</td><td>6.3.33</td><td>C</td></tr><tr><td>6.3.34</td><td>D</td><td>6.3.35</td><td>B</td><td>6.4.1</td><td>B</td><td>6.4.2</td><td>C</td><td>6.4.3</td><td>B</td></tr><tr><td>6.5.1</td><td>True</td><td>6.5.2</td><td>True</td><td>6.5.3</td><td>N/A</td><td>6.5.4</td><td>B;D</td><td>6.5.5</td><td>B;C</td></tr><tr><td>6.5.6</td><td>N/A</td><td>6.5.7</td><td>D</td><td>6.5.8</td><td>B</td><td>6.5.9</td><td>N/A</td><td>6.5.10</td><td>A</td></tr><tr><td>6.5.11</td><td>B</td><td>6.5.12</td><td>N/A</td><td>6.5.13</td><td>N/A</td><td>6.5.14</td><td>C</td><td>6.5.15</td><td>A</td></tr><tr><td>6.5.16</td><td>B</td><td>6.5.17</td><td>B</td><td>6.5.18</td><td>D</td><td>6.5.19</td><td>D</td><td>6.5.20</td><td>A</td></tr><tr><td>6.5.21</td><td>D</td><td>6.5.22</td><td>C</td><td>6.5.23</td><td>C</td><td>6.5.24</td><td>A</td><td>6.5.25</td><td>D</td></tr><tr><td>6.5.26</td><td>D</td><td>6.5.27</td><td>A</td><td>6.5.28</td><td>C</td><td>6.5.29</td><td>A;B;C</td><td>6.5.30</td><td>D</td></tr><tr><td>6.6.1</td><td>A</td><td>6.7.1</td><td>N/A</td><td>6.7.2</td><td>N/A</td><td>6.7.3</td><td>N/A</td><td>6.7.4</td><td>N/A</td></tr><tr><td>6.7.5</td><td>N/A</td><td>6.7.6</td><td>A</td><td>6.7.7</td><td>N/A</td><td>6.7.8</td><td>A</td><td>6.7.9</td><td>N/A</td></tr><tr><td>6.7.10</td><td>C</td><td>6.7.11</td><td>B</td><td>6.7.12</td><td>A</td><td>6.7.13</td><td>X</td><td>6.7.14</td><td>B</td></tr><tr><td>6.7.15</td><td>C</td><td>6.7.16</td><td>A</td><td>6.7.17</td><td>C</td><td>6.7.18</td><td>C</td><td>6.7.19</td><td>B</td></tr><tr><td>6.7.20</td><td>D</td><td>6.7.21</td><td>D</td><td>6.7.22</td><td>A</td><td>6.7.23</td><td>B</td><td>6.7.24</td><td>C</td></tr><tr><td>6.7.25</td><td>D</td><td>6.7.26</td><td>256:256</td><td>6.7.27</td><td>B</td><td>6.7.28</td><td>B;C</td><td>6.7.29</td><td>A</td></tr><tr><td>6.7.30</td><td>B</td><td>6.7.31</td><td>C</td><td>6.7.32</td><td>C;D</td><td>6.7.33</td><td>B</td><td>6.7.34</td><td>A</td></tr><tr><td>6.7.35</td><td>B</td><td>6.7.36</td><td>D</td><td>6.7.37</td><td>A</td><td>6.7.38</td><td>D</td><td>6.7.39</td><td>A</td></tr><tr><td>6.7.40</td><td>A</td><td>6.7.41</td><td>A</td><td>6.7.42</td><td>A</td><td>6.7.43</td><td>X</td><td>6.8.1</td><td>5:5</td></tr><tr><td>6.9.1</td><td>C</td><td>6.9.2</td><td>N/A</td><td>6.9.3</td><td>N/A</td><td>6.9.4</td><td>N/A</td><td>6.9.5</td><td>A;C</td></tr><tr><td>6.9.6</td><td>B</td><td>6.9.7</td><td>B</td><td>6.9.8</td><td>B</td><td>6.9.9</td><td>A</td><td>6.9.10</td><td>D</td></tr><tr><td>6.9.11</td><td>B</td><td>6.9.12</td><td>B</td><td>6.9.13</td><td>C</td><td>6.9.14</td><td>D</td><td>6.9.15</td><td>C</td></tr><tr><td>6.9.16</td><td>D</td><td>6.9.17</td><td>C</td><td>6.9.18</td><td>D</td><td>6.9.19</td><td>C</td><td>6.9.20</td><td>B</td></tr><tr><td>6.9.21</td><td>D</td><td>6.9.22</td><td>B</td><td>6.9.23</td><td>C</td><td>6.9.24</td><td>A</td><td>6.9.25</td><td>B;C;D</td></tr><tr><td>6.9.26</td><td>B;C;D</td><td>6.9.27</td><td>A;B;C</td><td>6.9.28</td><td>A;C;D</td><td>6.9.29</td><td>D</td><td>6.9.30</td><td>A</td></tr><tr><td>6.9.31</td><td>B</td><td>6.10.1</td><td>C</td><td>6.11.1</td><td>0</td><td>6.11.2</td><td>N/A</td><td>6.11.3</td><td>N/A</td></tr><tr><td>6.11.4</td><td>B</td><td>6.11.5</td><td>N/A</td><td>6.11.6</td><td>B</td><td>6.11.7</td><td>B</td><td>6.11.8</td><td>D</td></tr><tr><td>6.11.9</td><td>B</td><td>6.11.10</td><td>D</td><td>6.11.11</td><td>A</td><td>6.11.12</td><td>B</td><td>6.11.13</td><td>C</td></tr><tr><td>6.11.14</td><td>B</td><td>6.11.15</td><td>A</td><td>6.11.16</td><td>1</td><td>6.11.17</td><td>3</td><td>6.11.18</td><td>B</td></tr><tr><td>6.11.19</td><td>2</td><td>6.11.20</td><td>4</td><td>6.11.21</td><td>8</td><td>6.11.22</td><td>D</td><td>6.11.23</td><td>120</td></tr></table>

<table><tr><td>6.11.24</td><td>4</td></tr><tr><td>6.12.4</td><td>D</td></tr><tr><td>6.14.1</td><td>D</td></tr><tr><td>6.15.4</td><td>A</td></tr><tr><td>6.15.9</td><td>D</td></tr><tr><td>6.15.14</td><td>B</td></tr><tr><td>6.16.4</td><td>D</td></tr><tr><td>6.16.9</td><td>B</td></tr><tr><td>6.16.14</td><td>C</td></tr><tr><td>6.18.1</td><td>N/A</td></tr><tr><td>6.18.6</td><td>C</td></tr><tr><td>6.18.11</td><td>C</td></tr><tr><td>6.18.16</td><td>3</td></tr><tr><td>6.18.21</td><td>C</td></tr><tr><td>6.18.26</td><td>B</td></tr><tr><td>6.19.2</td><td>C</td></tr><tr><td>6.20.4</td><td>D</td></tr><tr><td>6.20.9</td><td>X</td></tr><tr><td>6.20.14</td><td>A</td></tr><tr><td>6.20.19</td><td>A</td></tr><tr><td>6.20.24</td><td>B</td></tr><tr><td>6.20.29</td><td>D</td></tr><tr><td>6.20.34</td><td>A</td></tr></table>

<table><tr><td>6.11.25</td><td>A</td></tr><tr><td>6.12.5</td><td>B</td></tr><tr><td>6.14.2</td><td>D</td></tr><tr><td>6.15.5</td><td>N/A</td></tr><tr><td>6.15.10</td><td>50 : 50</td></tr><tr><td>6.15.15</td><td>C</td></tr><tr><td>6.16.5</td><td>A</td></tr><tr><td>6.16.10</td><td>C</td></tr><tr><td>6.16.15</td><td>D</td></tr><tr><td>6.18.2</td><td>A;C</td></tr><tr><td>6.18.7</td><td>D</td></tr><tr><td>6.18.12</td><td>A</td></tr><tr><td>6.18.17</td><td>B</td></tr><tr><td>6.18.22</td><td>C</td></tr><tr><td>6.18.27</td><td>A</td></tr><tr><td>6.19.3</td><td>A</td></tr><tr><td>6.20.5</td><td>C</td></tr><tr><td>6.20.10</td><td>A</td></tr><tr><td>6.20.15</td><td>C</td></tr><tr><td>6.20.20</td><td>A</td></tr><tr><td>6.20.25</td><td>6</td></tr><tr><td>6.20.30</td><td>C</td></tr><tr><td>6.20.35</td><td>D</td></tr></table>

<table><tr><td>6.12.1</td><td>A;C</td></tr><tr><td>6.12.6</td><td>C</td></tr><tr><td>6.15.1</td><td>N/A</td></tr><tr><td>6.15.6</td><td>N/A</td></tr><tr><td>6.15.11</td><td>A</td></tr><tr><td>6.16.1</td><td>A;D</td></tr><tr><td>6.16.6</td><td>B</td></tr><tr><td>6.16.11</td><td>D</td></tr><tr><td>6.16.16</td><td>A</td></tr><tr><td>6.18.3</td><td>A</td></tr><tr><td>6.18.8</td><td>C;D</td></tr><tr><td>6.18.13</td><td>C</td></tr><tr><td>6.18.18</td><td>X</td></tr><tr><td>6.18.23</td><td>44</td></tr><tr><td>6.18.28</td><td>C</td></tr><tr><td>6.20.1</td><td>True</td></tr><tr><td>6.20.6</td><td>D</td></tr><tr><td>6.20.11</td><td>D</td></tr><tr><td>6.20.16</td><td>C</td></tr><tr><td>6.20.21</td><td>A</td></tr><tr><td>6.20.26</td><td>D</td></tr><tr><td>6.20.31</td><td>A;C</td></tr><tr><td>6.21.1</td><td>D</td></tr></table>

<table><tr><td>6.12.2</td><td>C</td></tr><tr><td>6.13.1</td><td>6:6</td></tr><tr><td>6.15.2</td><td>A</td></tr><tr><td>6.15.7</td><td>D</td></tr><tr><td>6.15.12</td><td>B</td></tr><tr><td>6.16.2</td><td>A</td></tr><tr><td>6.16.7</td><td>D</td></tr><tr><td>6.16.12</td><td>B</td></tr><tr><td>6.17.1</td><td>C</td></tr><tr><td>6.18.4</td><td>N/A</td></tr><tr><td>6.18.9</td><td>D</td></tr><tr><td>6.18.14</td><td>B</td></tr><tr><td>6.18.19</td><td>A;B;C</td></tr><tr><td>6.18.24</td><td>15</td></tr><tr><td>6.18.29</td><td>C</td></tr><tr><td>6.20.2</td><td>False</td></tr><tr><td>6.20.7</td><td>B</td></tr><tr><td>6.20.12</td><td>C</td></tr><tr><td>6.20.17</td><td>A</td></tr><tr><td>6.20.22</td><td>C</td></tr><tr><td>6.20.27</td><td>C</td></tr><tr><td>6.20.32</td><td>C</td></tr></table>

<table><tr><td>6.12.3</td><td>B</td></tr><tr><td>6.13.2</td><td>B;D</td></tr><tr><td>6.15.3</td><td>N/A</td></tr><tr><td>6.15.8</td><td>B</td></tr><tr><td>6.15.13</td><td>D</td></tr><tr><td>6.16.3</td><td>D</td></tr><tr><td>6.16.8</td><td>D</td></tr><tr><td>6.16.13</td><td>D</td></tr><tr><td>6.17.2</td><td>C</td></tr><tr><td>6.18.5</td><td>C</td></tr><tr><td>6.18.10</td><td>N/A</td></tr><tr><td>6.18.15</td><td>B</td></tr><tr><td>6.18.20</td><td>D</td></tr><tr><td>6.18.25</td><td>C</td></tr><tr><td>6.19.1</td><td>N/A</td></tr><tr><td>6.20.3</td><td>B;C</td></tr><tr><td>6.20.8</td><td>N/A</td></tr><tr><td>6.20.13</td><td>B</td></tr><tr><td>6.20.18</td><td>C</td></tr><tr><td>6.20.23</td><td>2</td></tr><tr><td>6.20.28</td><td>C;D</td></tr><tr><td>6.20.33</td><td>B</td></tr></table>