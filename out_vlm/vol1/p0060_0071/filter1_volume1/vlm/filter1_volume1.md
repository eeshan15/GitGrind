$$
\frac {p \land q}{\therefore p}
$$

\- Conjunction:

$$
\begin{array}{c} p \\ \hline q \\ \hline \therefore p \wedge q \end{array}
$$

\- Resolution:

$$
\begin{array}{c} p \lor q \\ \hline \neg q \lor r \\ \hline \therefore p \lor r \end{array}
$$

This is particularly useful in automated theorem proving and for converting to CNF.

■ Constructive Dilemma:

$$
\begin{array}{l} (p \to q) \land (r \to s) \\ \frac {p \lor r}{\therefore q \lor s} \end{array}
$$

\- Destructive Dilemma:

$$
\begin{array}{l} (p \rightarrow q) \land (r \rightarrow s) \\ \frac {\neg q \lor \neg s}{\therefore \neg p \lor \neg r} \\ \end{array}
$$

3. Rules of Inference (for First Order Logic):

\- Universal Instantiation (UI): If $\forall xP(x)$ is true, then $P(c)$ is true for any arbitrary individual $c$ in the domain.

$$
\frac {\forall x P (x)}{\therefore P (c)}
$$

\- Universal Generalization (UG): If $P(c)$ is true for an arbitrary individual $c$ in the domain, then $\forall xP(x)$ is true.

$$
\frac {P (c) \text {for an arbitrary} c}{\therefore \forall x P (x)}
$$

\- Existential Instantiation (EI): If $\exists xP(x)$ is true, then $P(c)$ is true for some specific individual $c$ in the domain. This $c$ must be a new constant not previously used in the proof.

$$
\frac {\exists x P (x)}{\therefore P (c) \text {(for some new c)}}
$$

\- Existential Generalization (EG): If $P(c)$ is true for some specific individual $c$ in the domain, then $\exists x P(x)$ is true.

$$
\frac {P (c) \text {for some specific} c}{\therefore \exists x P (x)}
$$

4. Proof Methods:

\- Direct Proof: Assume premises are true, and use inference rules and logical equivalences to derive the conclusion.

- Indirect Proof (Proof by Contradiction): To prove $C$ from premises $P_1, \ldots, P_n$ , assume $\neg C$ is true along with $P_1, \ldots, P_n$ , and derive a contradiction $(F)$ .  
- Proof by Contraposition: To prove $p \to q$ , prove its contrapositive $\neg q \to \neg p$ .

\- Key Properties and Identities: The validity of each inference rule is a key property. Understanding that these rules preserve truth is fundamental.

• Common Pitfalls or Tricky Points:

\- Fallacies: Invalid argument forms that resemble valid ones.

- Fallacy of Affirming the Consequent: $((p \to q) \land q) \to p$ (NOT a tautology). Example: "If it rains, the ground is wet. The ground is wet. Therefore, it rained." (Could be wet from a sprinkler).  
- Fallacy of Denying the Antecedent: $((p \to q) \land \neg p) \to \neg q$ (NOT a tautology). Example: "If it rains, the ground is wet. It did not rain. Therefore, the ground is not wet." (Could be wet from a sprinkler).

Confusing Validity with Soundness: A valid argument can have false premises and a false conclusion. A sound argument is a valid argument with all true premises (and thus, a true conclusion). GATE questions usually focus on validity.  
- Incorrect Application of Quantifier Rules: Especially with EI and UG, ensure the constant chosen for instantiation is new (for EI) or truly arbitrary (for UG).  
Circular Reasoning: Assuming the conclusion (or something equivalent to it) as a premise.

\- Standard Problem-Solving Techniques or Shortcuts:

- Formal Proofs: List premises and then systematically apply inference rules and logical equivalences to derive the conclusion, citing the rule for each step.  
- Truth Tables (for small arguments): Convert the argument into a single conditional statement $(P_{1} \wedge \ldots \wedge P_{n}) \to C$ and check if it's a tautology.  
- Resolution Principle: Convert all premises and the negation of the conclusion into CNF clauses. Add the negation of the conclusion as a clause. If an empty clause (☐) can be derived through resolution, the original argument is valid.  
Look for Fallacies: If an argument resembles a common fallacy, it's likely invalid.

# Quick Formula Reference

# Propositional Logic Equivalences

- $\neg (\neg p)\equiv p$ (Double Negation)  
- $p \lor q \equiv q \lor p$ (Commutative)  
- $p \land q \equiv q \land p$ (Commutative)  
- $(p \vee q) \vee r \equiv p \vee (q \vee r)$ (Associative)  
- $(p \land q) \land r \equiv p \land (q \land r)$ (Associative)  
- $p \land (q \lor r) \equiv (p \land q) \lor (p \land r)$ (Distributive)  
- $p \lor (q \land r) \equiv (p \lor q) \land (p \lor r)$ (Distributive)  
- $\neg(p \land q) \equiv \neg p \lor \neg q$ (De Morgan's)  
- $\neg(p \lor q) \equiv \neg p \land \neg q$ (De Morgan's)  
- $p \rightarrow q \equiv \neg p \lor q$  
- $p \to q \equiv \neg q \to \neg p$ (Contrapositive)  
- $\neg(p \to q) \equiv p \land \neg q$  
- $p \leftrightarrow q \equiv (p \rightarrow q) \land (q \rightarrow p)$  
- $p \leftrightarrow q \equiv (\underline{p} \land q) \lor (\neg p \land \neg q)$  
- $p \lor \neg p \equiv T$ (Inverse Law)  
- $p \land \neg p \equiv F$ (Inverse Law)  
- $p \vee T \equiv T$ (Domination Law)  
- $p \land F \equiv F$ (Domination Law)  
- $p \land T \equiv p$ (Identity Law)  
- $p \lor F \equiv p$ (Identity Law)  
- $p \vee p \equiv p$ (Idempotent Law)  
- $p \land p \equiv p$ (Idempotent Law)  
- $p \vee (p \wedge q) \equiv p$ (Absorption Law)  
- $p \land (p \lor q) \equiv p$ (Absorption Law)

# Quantifier Equivalences

- $\neg \forall xP(x) \equiv \exists x \neg P(x)$  
- $\neg \exists xP(x) \equiv \forall x \neg P(x)$

- $\forall x(P(x) \land Q(x)) \equiv \forall xP(x) \land \forall xQ(x)$  
- $\exists x(P(x) \vee Q(x)) \equiv \exists xP(x) \vee \exists xQ(x)$  
- $\forall x \forall y P(x, y) \equiv \forall y \forall x P(x, y)$  
- $\exists x \exists y P(x, y) \equiv \exists y \exists x P(x, y)$

# Rules of Inference (Propositional Logic)

- Modus Ponens: $(p \to q) \land p \implies q$  
- Modus Tollens: $(p \to q) \land \neg q \implies \neg p$  
- Hypothetical Syllogism: $(p \to q) \land (q \to r) \implies p \to r$  
- Disjunctive Syllogism: $(p \vee q) \wedge \neg p \implies q$  
- Addition: $p \implies p \lor q$  
- Simplification: $p \land q \implies p$  
- Conjunction: $p, q \implies p \land q$  
- Resolution: $(p \lor q) \land (\neg q \lor r) \implies p \lor r$

# Rules of Inference (First Order Logic)

- Universal Instantiation (UI): $\forall x P(x) \implies P(c)$  
- Universal Generalization (UG): $P(c)$ for arbitrary $c \implies \forall x P(x)$  
- Existential Instantiation (EI): $\exists x P(x) \implies P(c)$ (for new c)  
- Existential Generalization (EG): $P(c)$ for specific $c \implies \exists x P(x)$

# Important Tips for GATE

1. Master Truth Tables: They are the foundation. Be able to quickly construct and interpret truth tables for any compound proposition, especially for 2-3 variables. This helps in verifying tautologies, contradictions, and equivalences.  
2. Memorize Key Equivalences and Inference Rules: Speed and accuracy in GATE questions heavily rely on your ability to recall and apply De Morgan's laws, implication equivalences, and the common rules of inference (Modus Ponens, Modus Tollens, etc.) without hesitation.  
3. Practice Natural Language Translation: A significant portion of GATE questions involves translating English sentences into logical expressions (and vice-versa). Pay close attention to keywords like "all", "some", "no", "only if", "unless", and the correct use of quantifiers and connectives.  
4. Understand Quantifier Scope and Order: Incorrectly interpreting the scope of quantifiers or swapping the order of mixed quantifiers ( $\forall x \exists y$ vs. $\exists y \forall x$ ) is a very common mistake. Always visualize the domain and what each quantifier implies.  
5. Distinguish Validity from Soundness: GATE questions usually ask about the validity of an argument (whether the conclusion logically follows from the premises), not its soundness (which also requires premises to be true in the real world). Focus on the logical structure.  
6. Systematic Approach to Proofs: When asked to prove an argument's validity, don't guess. Start with the premises and systematically apply inference rules and logical equivalences, one step at a time, until you reach the conclusion. Clearly state the rule used for each step.  
7. Identify Common Fallacies: Be aware of fallacies like "Affirming the Consequent" and "Denying the Antecedent". If an argument structure matches a known fallacy, you can quickly identify it as invalid.  
8. Time Management: Some logical reasoning problems can be lengthy, especially those involving formal proofs or complex translations. If a question seems too time-consuming, make an educated guess or mark it for review if time permits, and move on to other questions.

3.1

# First Order Logic (35)

# 3.1.1 First Order Logic: GATE CSE 1989 | Question: 14a

Symbolize the expression "Every mother loves her children" in predicate logic.

gate1989 descriptive first-order-logic mathematical-logic

Answer key


Consider the following first order formula:

$$
\left( \begin{array}{c} \forall x \exists y: R (x, y) \\ \wedge \\ \forall x \forall y: (R (x, y) \Longrightarrow \neg R (y, x)) \\ \wedge \\ \forall x \forall y \forall z: (R (x, y) \wedge R (y, z) \Longrightarrow R (x, z)) \\ \wedge \\ \forall x: \neg R (x, x) \end{array} \right)
$$

Does it have finite models?

Is it satisfiable? If so, give a countable model for it.

gate1991 mathematical-logic first-order-logic descriptive

Answer key

# 3.1.3 First Order Logic: GATE CSE 1992 | Question: 92,xv

Which of the following predicate calculus statements is/are valid?

A. $(\forall (x))P(x)\lor (\forall (x))Q(x)\implies (\forall (x))(P(x)\lor Q(x))$  
B. $(\exists (x))P(x)\land (\exists (x))Q(x)\implies (\exists (x))(P(x)\land Q(x))$  
C. $(\forall (x))(P(x)\lor Q(x))\implies (\forall (x))P(x)\lor (\forall (x))Q(x)$  
D. $(\exists (x))(P(x)\lor Q(x))\implies \sim (\forall (x))P(x)\lor (\exists (x))Q(x)$

gate1992 mathematical-logic normal first-order-logic

Answer key

# 3.1.4 First Order Logic: GATE CSE 2003 | Question: 32

Which of the following is a valid first order formula? (Here $\alpha$ and $\beta$ are first order formulae with $x$ as their only free variable)

A. $((\forall x)[\alpha ]\Rightarrow (\forall x)[\beta ])\Rightarrow (\forall x)[\alpha \Rightarrow \beta ]$  
B. $(\forall x)[\alpha] \Rightarrow (\exists x)[\alpha \land \beta]$  
C. $((\forall x)[\alpha \lor \beta] \Rightarrow (\exists x)[\alpha]) \Rightarrow (\forall x)[\alpha]$  
D. $(\forall x)[\alpha \Rightarrow \beta ]\Rightarrow ((\forall x)[\alpha ])\Rightarrow (\forall x)[\beta ])$

gatecse-2003 mathematical-logic first-order-logic normal

Answer key

# 3.1.5 First Order Logic: GATE CSE 2003 | Question: 33

Consider the following formula and its two interpretations $I_{1}$ and $I_{2}$ .

$$
\alpha : (\forall x) \left[ P _ {x} \Leftrightarrow (\forall y) \left[ Q _ {x y} \Leftrightarrow \neg Q _ {y y} \right] \right] \Rightarrow (\forall x) \left[ \neg P _ {x} \right]
$$

$I_{1}$ : Domain: the set of natural numbers

$P_{x} = 'x$ is a prime number'

$Q_{xy} = 'y$ divides $x'$

$I_{2}$ : same as $I_{1}$ except that $P_{x} = 'x$ is a composite number'.

Which of the following statements is true?

A. $I_{1}$ satisfies $\alpha, I_{2}$ does not  
B. $I_{2}$ satisfies $\alpha, I_{1}$ does not  
C. Neither $I_{1}$ nor $I_{2}$ satisfies $\alpha$  
D. Both $I_{1}$ and $I_{2}$ satisfies $\alpha$

gatecse-2003 mathematical-logic difficult first-order-logic

# Answer key

# 3.1.6 First Order Logic: GATE CSE 2004 | Question: 23, ISRO2007-32

Identify the correct translation into logical notation of the following assertion.

Some boys in the class are taller than all the girls

Note: taller(x, y) is true if x is taller than y.

A. $(\exists x)(\mathrm{boy}(x)\to (\forall y)(\mathrm{girl}(y)\land \mathrm{taller}(x,y)))$  
B. $(\exists x)(\mathrm{boy}(x) \land (\forall y)(\mathrm{girl}(y) \land \mathrm{taller}(x, y)))$  
C. $(\exists x)(\mathrm{boy}(x)\to (\forall y)(\mathrm{girl}(y)\to \mathrm{taller}(x,y)))$  
D. $(\exists x)(\mathrm{boy}(x)\land (\forall y)(\mathrm{girl}(y)\to \mathrm{taller}(x,y)))$

gatecse-2004 mathematical-logic easy isro2007 first-order-logic

# Answer key

# 3.1.7 First Order Logic: GATE CSE 2005 | Question: 41

What is the first order predicate calculus statement equivalent to the following?

"Every teacher is liked by some student"

A. $\forall (x)$ [teacher $(x)\rightarrow \exists (y)$ [student $(y)\rightarrow$ likes $(y,x)$ ]]  
B. $\forall (x)$ [teacher $(x)\to \exists (y)$ [student $(y)\land$ likes $(y,x)$ ]]  
C. $\exists (y)\forall (x)$ [teacher $(x)\to [\text{student}(y)\land \text{likes}(y,x)]]$  
D. $\forall (x)$ [teacher $(x)\land \exists (y)$ [student $(y)\to$ likes $(y,x)$ ]]

gatecse-2005 mathematical-logic easy first-order-logic

# Answer key

# 3.1.8 First Order Logic: GATE CSE 2006 | Question: 26

Which one of the first order predicate calculus statements given below correctly expresses the following English statement?

# Tigers and lions attack if they are hungry or threatened.

A. $\forall x[(\text{tiger}(x) \land \text{lion}(x)) \to (\text{hungry}(x) \lor \text{threatened}(x)) \to \text{attacks}(x)]$  
B. $\forall x[(\mathrm{tiger}(x)\lor \mathrm{lion}(x))\to (\mathrm{hungry}(x)\lor \mathrm{threatened}(x))\land \mathrm{attacks}(x)]$  
C. $\forall x[(\text{tiger}(x) \lor \text{lion}(x)) \to \text{attacks}(x) \to (\text{hungry}(x) \lor \text{threatened}(x))]$  
D. $\forall x[(\text{tiger}(x) \lor \text{lion}(x)) \to (\text{hungry}(x) \lor \text{threatened}(x)) \to \text{attacks}(x)]$




# 3.1.9 First Order Logic: GATE CSE 2007 | Question: 22


Let $\operatorname{Graph}(x)$ be a predicate which denotes that $x$ is a graph. Let $\operatorname{Connected}(x)$ be a predicate which denotes that $x$ is connected. Which of the following first order logic sentences DOES NOT represent the statement:

"Not every graph is connected"

A. $\neg \forall x$ (Graph $(x)\Rightarrow$ Connected $(x)$ )  
C. $\neg \forall x$ $\left(\neg \operatorname{Graph}(x) \lor \operatorname{Connected}(x)\right)$

B. $\exists x\left(\operatorname{Graph}(x) \land \neg \operatorname{Connected}(x)\right)$  
D. $\forall x\left(\operatorname{Graph}(x) \implies \neg \operatorname{Connected}(x)\right)$

gatecse-2007 mathematical-logic easy first-order-logic

# Answer key

# 3.1.10 First Order Logic: GATE CSE 2008 | Question: 30


Let fsa and pda be two predicates such that fsa(x) means x is a finite state automaton and pda(y) means that y is a pushdown automaton. Let equivalent be another predicate such that equivalent(a, b) means a and b are equivalent. Which of the following first order logic statements represent the following?

Each finite state automaton has an equivalent pushdown automaton

A. $(\forall x \text{ fsa } (x)) \implies (\exists y \text{ pda } (y) \land \text{equivalent } (x, y))$  
B. $\neg\forall y\left(\exists x\operatorname{fsa}(x)\implies\operatorname{pda}(y)\land\operatorname{equivalent}(x,y)\right)$  
C. $\forall x\exists y$ (fsa $(x)\land \mathrm{pda}(y)\land$ equivalent $(x,y))$  
D. $\forall x\exists y$ (fsa $(y)\land \mathrm{pda}(x)\land$ equivalent $(x,y))$

gatecse-2008 easy mathematical-logic first-order-logic

# Answer key

# 3.1.11 First Order Logic: GATE CSE 2009 | Question: 23


Which one of the following is the most appropriate logical formula to represent the statement?

"Gold and silver ornaments are precious".

The following notations are used:

- $G(x): x$ is a gold ornament  
- $S(x): x$ is a silver ornament  
- $P(x): x$ is precious

A. $\forall x(P(x) \implies (G(x) \land S(x)))$

C. $\exists x((G(x) \land S(x))) \implies P(x))$

gatecse-2009 mathematical-logic easy first-order-logic

B. $\forall x((G(x) \land S(x)) \implies P(x))$  
D. $\forall x((G(x) \vee S(x)) \implies P(x))$

# Answer key

# 3.1.12 First Order Logic: GATE CSE 2009 | Question: 26


Consider the following well-formed formulae:

1. $\neg \forall x(P(x))$  
II. $\neg \exists x(P(x))$  
III. $\neg \exists x(\neg P(x))$  
IV. $\exists x(\neg P(x))$

Which of the above are equivalent?

A. I and III

B. I and IV

C. II and III

D. II and IV

# 3.1.13 First Order Logic: GATE CSE 2010 | Question: 30


Suppose the predicate $F(x,y,t)$ is used to represent the statement that person $x$ can fool person $y$ at time $t$ .

Which one of the statements below expresses best the meaning of the formula,

$$
\forall x \exists y \exists t (\neg F (x, y, t))
$$

A. Everyone can fool some person at some time  
B. No one can fool everyone all the time  
C. Everyone cannot fool some person all the time  
D. No one can fool some person at some time

gatecse-2010 mathematical-logic easy first-order-logic

# Answer key

# 3.1.14 First Order Logic: GATE CSE 2011 | Question: 30

Which one of the following options is CORRECT given three positive integers $x, y$ and $z$ , and a predicate

$$
P (x) = \neg (x = 1) \land \forall y (\exists z (x = y * z) \Rightarrow (y = x) \lor (y = 1))
$$

A. $P(x)$ being true means that $x$ is a prime number  
B. $P(x)$ being true means that $x$ is a number other than 1  
C. $P(x)$ is always true irrespective of the value of $x$  
D. $P(x)$ being true means that $x$ has exactly two factors other than 1 and $x$

gatecse-2011 mathematical-logic normal first-order-logic

# Answer key


# 3.1.15 First Order Logic: GATE CSE 2012 | Question: 13

What is the correct translation of the following statement into mathematical logic?

"Some real numbers are rational"

A. $\exists x(\mathrm{real}(x)\lor \mathrm{rational}(x))$  
C. $\exists x(\mathrm{real}(x)\land \mathrm{rational}(x))$  
gatecse-2012 mathematical-logic easy first-order-logic

# Answer key


# 3.1.16 First Order Logic: GATE CSE 2013 | Question: 27

What is the logical translation of the following statement?

"None of my friends are perfect."

A. $\exists x(F(x) \land \neg P(x))$  
C. $\exists x(\neg F(x) \land \neg P(x))$

gatecse-2013 mathematical-logic easy first-order-logic

# Answer key


# 3.1.17 First Order Logic: GATE CSE 2013 | Question: 47

Which one of the following is NOT logically equivalent to $\neg \exists x(\forall y(\alpha) \land \forall z(\beta))$ ?

A. $\forall x(\exists z(\neg \beta)\rightarrow \forall y(\alpha))$  
C. $\forall x(\forall y(\alpha)\to \exists z(\neg \beta))$

mathematical-logic normal marks-to-all gatecse-2013 first-order-logic

# Answer key


# 3.1.18 First Order Logic: GATE CSE 2014 | Set 1 | Question: 1

Consider the statement


"Not all that glitters is gold"

Predicate glitters $(x)$ is true if $x$ glitters and predicate gold $(x)$ is true if $x$ is gold. Which one of the following logical formulae represents the above statement?

A. $\forall x:\mathrm{glitters}(x)\Rightarrow \neg \mathrm{gold}(x)$  
B. $\forall x:\mathrm{gold}(x)\Rightarrow \mathrm{glitters}(x)$  
C. $\exists x:\mathrm{gold}(x)\land \neg \mathrm{glitters}(x)$  
D. $\exists x:\mathrm{glitters}(x)\land \neg \mathrm{gold}(x)$

gatecse-2014-set1 mathematical-logic first-order-logic

# Answer key

# 3.1.19 First Order Logic: GATE CSE 2014 | Set 3 | Question: 53

The CORRECT formula for the sentence, "not all Rainy days are Cold" is

A. $\forall d(\text{Rainy}(d) \land \text{-Cold}(d))$  
C. $\exists d(\sim\text{Rainy}(d)\rightarrow\text{Cold}(d))$  
gatecse-2014-set3 mathematical-logic easy first-order-logic

B. $\forall d(\sim \mathrm{Rainy}(d)\rightarrow \mathrm{Cold}(d))$  
D. $\exists d(\mathrm{Rainy}(d) \land \sim\mathrm{Cold}(d))$

# Answer key

# 3.1.20 First Order Logic: GATE CSE 2015 | Set 2 | Question: 55

Which one of the following well-formed formulae is a tautology?

A. $\forall x\exists yR(x,y)\leftrightarrow \exists y\forall xR(x,y)$  
B. $(\forall x[\exists yR(x,y)\to S(x,y)])\to \forall x\exists yS(x,y)$  
C. $[\forall x\exists y (P(x,y)\rightarrow R(x,y))] \leftrightarrow [\forall x\exists y (\neg P(x,y)\lor R(x,y))]]$  
D. $\forall x\forall yP(x,y)\to \forall x\forall yP(y,x)$

gatecse-2015-set2 mathematical-logic normal first-order-logic

# Answer key

# 3.1.21 First Order Logic: GATE CSE 2016 | Set 2 | Question: 27

Which one of the following well-formed formulae in predicate calculus is NOT valid?

A. $(\forall_{x}p(x)\implies \forall_{x}q(x))\implies (\exists_{x}\neg p(x)\lor \forall_{x}q(x))$  
B. $(\exists xp(x) \vee \exists xq(x)) \implies \exists x(p(x) \vee q(x))$  
C. $\exists x(p(x) \land q(x)) \implies (\exists xp(x) \land \exists xq(x))$  
D. $\forall x(p(x) \vee q(x)) \implies (\forall xp(x) \vee \forall xq(x))$

gatecse-2016-set2 mathematical-logic first-order-logic normal

# Answer key

# 3.1.22 First Order Logic: GATE CSE 2017 | Set 1 | Question: 02

Consider the first-order logic sentence $F : \forall x(\exists y R(x, y))$ . Assuming non-empty logical domains, which of the sentences below are implied by F?

1. $\exists y(\exists xR(x,y))$  
II. $\exists y(\forall xR(x,y))$  
III. $\forall y(\exists xR(x,y))$  
IV. $\neg \exists x(\forall y\neg R(x,y))$





A. IV only

B. I and IV only

C. II only

D. II and III only

gatecse-2017-set1 mathematical-logic first-order-logic

# Answer key

# 3.1.23 First Order Logic: GATE CSE 2018 | Question: 28

Consider the first-order logic sentence

$$
\varphi \equiv \exists s \exists t \exists u \forall v \forall w \forall x \forall y \psi (s, t, u, v, w, x, y)
$$

where $\psi(s, t, u, v, w, x, y,)$ is a quantifier-free first-order logic formula using only predicate symbols, and possibly equality, but no function symbols. Suppose $\varphi$ has a model with a universe containing 7 elements.

Which one of the following statements is necessarily true?

A. There exists at least one model of $\varphi$ with universe of size less than or equal to 3  
B. There exists no model of $\varphi$ with universe of size less than or equal to 3  
C. There exists no model of $\varphi$ with universe size of greater than 7  
D. Every model of $\varphi$ has a universe of size equal to 7

gatecse-2018 mathematical-logic normal first-order-logic two-marks

# Answer key

# 3.1.24 First Order Logic: GATE CSE 2019 | Question: 35

Consider the first order predicate formula $\varphi$ :

$$
\forall x [ (\forall z z | x \Rightarrow ((z = x) \lor (z = 1))) \rightarrow \exists w (w > x) \land (\forall z z | w \Rightarrow ((w = z) \lor (z = 1))) ]
$$

Here $a \mid b$ denotes that $a$ divides $b'$ , where $a$ and $b$ are integers. Consider the following sets:

- $S_{1}:\{1,2,3,\ldots ,100\}$  
- $S_{2}$ : Set of all positive integers  
- $S_{3}$ : Set of all integers

Which of the above sets satisfy $\varphi$ ?

A. $S_{1}$ and $S_{2}$

B. $S_{1}$ and $S_{3}$

C. $S_{2}$ and $S_{3}$

D. $S_{1}, S_{2}$ and $S_{3}$

gatecse-2019 discrete-mathematics mathematical-logic first-order-logic two-marks normal

# Answer key

# 3.1.25 First Order Logic: GATE CSE 2020 | Question: 39

Which one of the following predicate formulae is NOT logically valid?

Note that W is a predicate formula without any free occurrence of x.

A. $\forall x(p(x) \vee W) \equiv \forall x p(x) \vee W$  
B. $\exists x(p(x) \wedge W) \equiv \exists x p(x) \wedge W$  
C. $\forall x(p(x)\to W)\equiv \forall x p(x)\to W$  
D. $\exists x(p(x)\to W)\equiv \forall x p(x)\to W$

gatecse-2020 first-order-logic mathematical-logic two-marks

# Answer key

# 3.1.26 First Order Logic: GATE CSE 2023 | Question: 16

Geetha has a conjecture about integers, which is of the form

$$
\forall x (P (x) \Longrightarrow \exists y Q (x, y)),
$$





where P is a statement about integers, and Q is a statement about pairs of integers. Which of the following (one or

more) option(s) would imply Geetha's conjecture?

A. $\exists x(P(x) \land \forall yQ(x, y))$  
B. $\forall x \forall y Q(x, y)$  
C. $\exists y \forall x (P(x) \Longrightarrow Q(x, y))$  
D. $\exists x(P(x) \land \exists yQ(x, y))$

gatecse-2023 mathematical-logic first-order-logic multiple-selects one-mark difficult

# Answer key

# 3.1.27 First Order Logic: GATE CSE 2025 | Set 1 | Question: 38

Which of the following predicate logic formulae/formula is/are CORRECT representation(s) of the statement: "Everyone has exactly one mother"?


The meanings of the predicates used are:

- mother $(y, x): y$ is the mother of $x$  
- noteq $(x,y):x$ and $y$ are not equal

A. $\forall x\exists y\exists z(\mathrm{mother}(y,x)\land \neg \mathrm{mother}(z,x))$  
B. $\forall x\exists y[\mathrm{mother}(y,x)\land \forall z(\mathrm{noteq}(z,y)\rightarrow \neg \mathrm{mother}(z,x))]$  
C. $\forall x \forall y[\text{mother}(y, x) \to \exists z(\text{mother}(z, x) \land \neg \text{note } q(z, y))]$  
D. $\forall x\exists y[\mathrm{mother}(y,x)\land\neg\exists z(\mathrm{note}q(z,y)\land\mathrm{mother}(z,x))]$

gatecse2025-set1 mathematical-logic first-order-logic multiple-selects two-marks

# Answer key

# 3.1.28 First Order Logic: GATE CSE 2025 | Set 2 | Question: 5

Let $P(x)$ be an arbitrary predicate over the domain of natural numbers. Which ONE of the following statements is TRUE?


A. $\left(P(0) \wedge (\forall x[P(x) \Rightarrow P(x+1)])\right) \Rightarrow \forall xP(x)$  
B. $\left(P(0) \wedge (\forall x[P(x) \Rightarrow P(x-1)])\right) \Rightarrow \forall xP(x)$  
C. $\left(P(1000) \wedge (\forall x[P(x) \Rightarrow P(x-1)]\right) \Rightarrow \forall xP(x)$  
D. $\left(P(1000) \wedge (\forall x[P(x) \Rightarrow P(x+1)])\right) \Rightarrow \forall xP(x)$

gatecse2025-set2 mathematical-logic first-order-logic one-mark

# Answer key

# 3.1.29 First Order Logic: GATE CSE 2026 | Set 2 | Question: 1

For two different persons $x$ and $y$ , the predicate $M(x, y)$ denotes that $x$ knows $y$ . Consider the following statement.


There is a person who does not know anyone else, but that person is known by everyone else.

Which one of the following expressions represents the above statement?

A. $(\exists y)(\forall x)((x \neq y) \to (M(x, y) \land \neg M(y, x)))$  
B. $(\forall y)(\exists x)((x \neq y) \to (M(x, y) \land \neg M(y, x)))$  
C. $(\exists y)(\exists x)((x \neq y) \to (M(x,y) \land \neg M(y,x)))$  
D. $(\forall y)(\forall x)((x \neq y) \to (M(x,y) \land \neg M(y,x)))$

gatecse-2026-set2 mathematical-logic first-order-logic one-mark

# Answer key

# 3.1.30 First Order Logic: GATE IT 2004 | Question: 3


Let $a(x,y), b(x,y,)$ and $c(x,y)$ be three statements with variables x and y chosen from some universe. Consider the following statement:

$$
(\exists x) (\forall y) [ (a (x, y) \land b (x, y)) \land \neg c (x, y) ]
$$

Which one of the following is its equivalent?

A. $(\forall x)(\exists y)[(a(x,y) \lor b(x,y)) \to c(x,y)]$  
B. $(\exists x)(\forall y)[(a(x,y)\lor b(x,y))\land \neg c(x,y)]$  
C. $\neg (\forall x)(\exists y)[(a(x,y)\land b(x,y))\to c(x,y)]$  
D. $\neg (\forall x)(\exists y)[(a(x,y)\lor b(x,y))\to c(x,y)]$

gateit-2004 mathematical-logic normal discrete-mathematics first-order-logic

# Answer key

# 3.1.31 First Order Logic: GATE IT 2005 | Question: 36

Let $P(x)$ and $Q(x)$ be arbitrary predicates. Which of the following statements is always TRUE?

A. $((\forall x(P(x) \vee Q(x)))) \implies ((\forall xP(x)) \vee (\forall xQ(x)))$  
B. $(\forall x(P(x) \Longrightarrow Q(x))) \Longrightarrow ((\forall xP(x)) \Longrightarrow (\forall xQ(x)))$  
C. $(\forall x(P(x)) \Rightarrow \forall x(Q(x))) \Rightarrow (\forall x(P(x) \Rightarrow Q(x)))$  
D. $(\forall x(P(x)) \Leftrightarrow (\forall x(Q(x)))) \implies (\forall x(P(x) \Leftrightarrow Q(x)))$

gateit-2005 mathematical-logic first-order-logic normal

# Answer key


# 3.1.32 First Order Logic: GATE IT 2006 | Question: 21

Consider the following first order logic formula in which $R$ is a binary relation symbol.

$$
\forall x \forall y (R (x, y) \implies R (y, x))
$$

The formula is

A. satisfiable and valid  
C. unsatisfiable but its negation is valid

B. satisfiable and so is its negation  
D. satisfiable but its negation is unsatisfiable

gateit-2006 mathematical-logic normal first-order-logic

# Answer key

# 3.1.33 First Order Logic: GATE IT 2007 | Question: 21

Which one of these first-order logic formulae is valid?

A. $\forall x(P(x) \Rightarrow Q(x)) \Rightarrow (\forall xP(x) \Rightarrow \forall xQ(x))$  
B. $\exists x(P(x) \vee Q(x)) \implies (\exists xP(x) \implies \exists xQ(x))$  
C. $\exists x(P(x) \land Q(x)) \iff (\exists xP(x) \land \exists xQ(x))$  
D. $\forall x\exists yP(x,y)\implies \exists y\forall xP(x,y)$

gateit-2007 mathematical-logic normal first-order-logic

# Answer key


# 3.1.34 First Order Logic: GATE IT 2008 | Question: 21

Which of the following first order formulae is logically valid? Here $\alpha(x)$ is a first order formula with $x$ as a free variable, and $\beta$ is a first order formula with no free variable.



A. $[\beta \rightarrow (\exists x, \alpha(x))] \rightarrow [\forall x, \beta \rightarrow \alpha(x)]$  
B. $[\exists x, \beta \rightarrow \alpha(x)] \rightarrow [\beta \rightarrow (\forall x, \alpha(x))]]$  
C. $[\left(\exists x, \alpha(x)\right) \rightarrow \beta] \rightarrow [\forall x, \alpha(x) \rightarrow \beta]$  
D. $[\left(\forall x, \alpha(x)\right) \rightarrow \beta] \rightarrow [\forall x, \alpha(x) \rightarrow \beta]$

gateit-2008 first-order-logic normal

# Answer key

# 3.1.35 First Order Logic: GATE IT 2008 | Question: 22

Which of the following is the negation of $[\forall x, \alpha \to (\exists y, \beta \to (\forall u, \exists v, y))]$

A. $[\exists x, \alpha \rightarrow (\forall y, \beta \rightarrow (\exists u, \forall v, y))] \quad$  
B. $[\exists x, \alpha \to (\forall y, \beta \to (\exists u, \forall v, \neg y))] \quad$  
C. $[\forall x, \neg \alpha \rightarrow (\exists y, \neg \beta \rightarrow (\forall u, \exists v, \neg y))]$  
D. \([\exists x, \alpha \land (\forall y, \beta \land (\exists u, \forall v, \neg y))] \]

gateit-2008 mathematical-logic normal first-order-logic

# Answer key


# 3.2

# Logical Reasoning (3)

# 3.2.1 Logical Reasoning: GATE CSE 2012 | Question: 1

Consider the following logical inferences.

$I_{1}$ : If it rains then the cricket match will not be played.

The cricket match was played.

Inference: There was no rain.

$I_{2}$ : If it rains then the cricket match will not be played.

It did not rain.

Inference: The cricket match was played.

Which of the following is TRUE?

A. Both $I_{1}$ and $I_{2}$ are correct inferences  
B. $I_{1}$ is correct but $I_{2}$ is not a correct inference  
C. $I_{1}$ is not correct but $I_{2}$ is a correct inference  
D. Both $I_{1}$ and $I_{2}$ are not correct inferences

gatecse-2012 mathematical-logic easy logical-reasoning

# Answer key


# 3.2.2 Logical Reasoning: GATE CSE 2015 | Set 2 | Question: 3

Consider the following two statements.

- $S_{1}$ : If a candidate is known to be corrupt, then he will not be elected  
- $S_{2}$ : If a candidate is kind, he will be elected

Which one of the following statements follows from $S_{1}$ and $S_{2}$ as per sound inference rules of logic?

A. If a person is known to be corrupt, he is kind  
B. If a person is not known to be corrupt, he is not kind  
C. If a person is kind, he is not known to be corrupt  
D. If a person is not kind, he is not known to be corrupt

gatecse-2015-set2 mathematical-logic normal logical-reasoning

# Answer key

