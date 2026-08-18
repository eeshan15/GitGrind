for algebraic structures like groups and rings.

# Definition and Core Idea:

A binary operation \* on a set $S$ is a function \* : $S \times S \to S$ . For any $a, b \in S$ , $a * b$ is a unique element in $S$ . The core idea is to define an internal way to combine elements.

# Important Formulas and Results:

# • Properties of a Binary Operation:

1. Closure: For all $a, b \in S$ , $a * b \in S$ . (This is inherent in the definition).  
2. Associativity: For all $a, b, c \in S$ , $(a * b) * c = a * (b * c)$ .  
3. Commutativity: For all $a, b \in S$ , $a * b = b * a$ .  
4. Identity Element: An element $e \in S$ such that for all $a \in S$ , $a * e = e * a = a$ . If it exists, it is unique.  
5. Inverse Element: For an element $a \in S$ , an element $a^{-1} \in S$ is its inverse if $a * a^{-1} = a^{-1} * a = e$ , where $e$ is the identity element. If an identity exists, inverses are unique for each element.

# Key Properties and Identities:

- If an identity element exists, it is unique.  
- If an identity element exists and the operation is associative, then inverses are unique.

# Common Pitfalls & Tricky Points:

- Forgetting to check closure: the result of the operation must always be in the original set.  
- Misidentifying the identity element or assuming it always exists.  
- Assuming commutativity or associativity when not explicitly stated or proven.

# Problem-Solving Techniques:

- To check properties, test with arbitrary elements or counterexamples.  
- For finite sets, construct a Cayley table (operation table) to check properties visually.

# Group Theory

Group theory studies algebraic structures called groups, which are sets equipped with a binary operation satisfying specific axioms. It's fundamental in cryptography, coding theory, and physics.

# Definition and Core Idea:

A group $(G, *)$ is a set G together with a binary operation $*$ that satisfies four axioms:

1. Closure: For all $a, b \in G$ , $a * b \in G$ .  
2. Associativity: For all $a, b, c \in G$ , $(a * b) * c = a * (b * c)$ .  
3. Identity Element: There exists an element $e \in G$ such that for all $a \in G$ , $a * e = e * a = a$ .  
4. Inverse Element: For each $a \in G$ , there exists an element $a^{-1} \in G$ such that $a * a^{-1} = a^{-1} * a = e$ .

The core idea is to formalize symmetry and transformations.

# Important Formulas and Results:

# - Related Structures:

- Semigroup: A set with an associative binary operation.  
- Monoid: A semigroup with an identity element.  
- Abelian Group (Commutative Group): A group where the operation is commutative ( $a * b = b * a$ ).

- Subgroup: A non-empty subset $H$ of a group $G$ is a subgroup if $H$ is itself a group under the same operation.  
- Subgroup Test: $H$ is a subgroup of $G$ if for all $a, b \in H$ , $a * b^{-1} \in H$ .

- Cyclic Group: A group $G$ is cyclic if there exists an element $g \in G$ such that every element of $G$ can be written as a power of $g$ (i.e., $G = \{g^n \mid n \in \mathbb{Z}\}$ ). $g$ is called a generator.  
- Order of an element: The smallest positive integer $n$ such that $a^n = e$ . If no such $n$ exists, the element has infinite

order.

\- Lagrange's Theorem: If $G$ is a finite group and $H$ is a subgroup of $G$ , then the order of $H$ divides the order of $G$ (i.e., $|H|$ divides $|G|$ ).

# Key Properties and Identities:

- The identity element is unique.  
• Every element has a unique inverse.  
- $(a^{-1})^{-1} = a$  
- $(a*b)^{-1} = b^{-1} * a^{-1}$

# Common Pitfalls & Tricky Points:

- Forgetting to check all four group axioms, especially the existence of inverses for every element.  
- Confusing the order of an element with the order of the group.  
- Misapplying Lagrange's Theorem (it states a necessary condition for a subgroup, not a sufficient one).

# Problem-Solving Techniques:

- To prove a set with an operation is a group, systematically verify all four axioms.  
- To find subgroups, look for subsets that are closed under the operation and contain the identity and inverses.  
- Use Lagrange's Theorem to quickly rule out potential subgroup orders.

# Identity Function

The identity function is a fundamental concept in functions and algebraic structures, acting as a neutral element for function composition.

# Definition and Core Idea:

For any set $A$ , the identity function on $A$ , denoted $I_A$ or $id_A$ , is a function $I_A : A \to A$ such that for every element $x \in A$ , $I_A(x) = x$ . The core idea is a mapping that leaves elements unchanged.

# Important Formulas and Results:

- If $f: A \to B$ is any function, then $f \circ I_A = f$ and $I_B \circ f = f$ .  
- If $f: A \to B$ is a bijective function, then its inverse $f^{-1}: B \to A$ satisfies $f^{-1} \circ f = I_A$ and $f \circ f^{-1} = I_B$ .

# Key Properties and Identities:

- The identity function is always bijective (one-to-one and onto).  
- It serves as the identity element for the operation of function composition.

# Common Pitfalls & Tricky Points:

- Confusing the identity function with a constant function (e.g., $f(x) = c$ ).  
- Forgetting that the identity function is specific to a set $A$ .

# Problem-Solving Techniques:

\- Use the properties of the identity function when simplifying compositions or proving inverse relationships.

# Lattice

Lattices are special types of partially ordered sets where every pair of elements has a unique "least upper bound" and "greatest lower bound." They are crucial in areas like logic, set theory, and computer science for modeling hierarchical structures.

# Definition and Core Idea:

A poset $(L, \preceq)$ is a lattice if for every pair of elements $a, b \in L$ , both their least upper bound (LUB or join, denoted $a \vee b$ ) and greatest lower bound (GLB or meet, denoted $a \wedge b$ ) exist and are unique. The core idea is a structure where elements always have well-defined "closest" common superiors and inferiors.

# Important Formulas and Results:

- Join (Supremum): $a \vee b = \sup \{a, b\}$ .  
- Meet (Infimum): $a \wedge b = \inf \{a, \bar{b}\}$ .  
- Types of Lattices:

\- Distributive Lattice: A lattice where the distributive laws hold:

- $a \wedge (b \vee c) = (a \wedge b) \vee (a \wedge c)$  
- $a \vee (b \wedge c) = (a \vee b) \wedge (a \vee c)$

Complemented Lattice: A bounded lattice (has a greatest element 1 and a least element 0) where every element $a$ has a complement $a'$ such that $a \wedge a' = 0$ and $a \vee a' = 1$ .

\- Boolean Algebra: A distributive and complemented lattice.

# Key Properties and Identities:

- Idempotent Laws: $a \land a = a$ , $a \lor a = a$  
- Commutative Laws: $a \wedge b = b \wedge a, a \vee b = b \vee a$  
- Associative Laws: $(a \land b) \land c = a \land (b \land c), (a \lor b) \lor c = a \lor (b \lor c)$  
- Absorption Laws: $a \land (a \lor b) = a, a \lor (a \land b) = a$  
- Duality Principle: If a statement is true for a lattice, its dual (exchanging $\wedge$ with $\vee$ , $\preceq$ with $\succeq$ , 0 with 1) is also true.

# Common Pitfalls & Tricky Points:

- Not every poset is a lattice. A poset fails to be a lattice if any pair of elements lacks a unique LUB or GLB.  
- Distinguishing between maximal/minimal elements and greatest/least elements in a poset (a lattice always has a greatest and least element if it's bounded).

# Problem-Solving Techniques:

- Draw Hasse diagrams to visually identify LUBs and GLBs for all pairs.  
- To check for distributivity, look for sublattices isomorphic to $N_{5}$ (pentagon lattice) or $M_{3}$ (diamond lattice) in the Hasse diagram (they are non-distributive).

# Mathematical Induction

Mathematical Induction is a powerful proof technique used to establish the truth of a statement for all natural numbers (or a subset thereof). It's essential for proving properties of algorithms, data structures, and number theory results.

# Definition and Core Idea:

The Principle of Mathematical Induction states that to prove a statement $P(n)$ is true for all integers $n \geq n_0$ :

1. Base Case: Show that $P(n_0)$ is true.  
2. Inductive Hypothesis: Assume that $P(k)$ is true for some arbitrary integer $k \geq n_0$ .  
3. Inductive Step: Show that $P(k + 1)$ is true, using the inductive hypothesis.

The core idea is like a chain reaction: if the first domino falls, and falling dominoes always knock over the next one, then all dominoes will fall.

# Important Formulas and Results:

\- Principle of Strong Induction:

1. Base Case: Show that $P(n_0)$ is true.  
2. Inductive Hypothesis: Assume that $P(j)$ is true for all integers $j$ such that $n_0 \leq j \leq k$ , for some arbitrary integer $k \geq n_0$ .  
3. Inductive Step: Show that $P(k + 1)$ is true, using the inductive hypothesis.

# Key Properties and Identities:

\- Both standard and strong induction are equivalent in power; strong induction is often more convenient for proofs where $P(k + 1)$ depends on more than just $P(k)$ .

# Common Pitfalls & Tricky Points:

- Incorrect base case: The statement must hold for the starting value.  
• Assuming what needs to be proven in the inductive step. The inductive hypothesis must be explicitly used.  
- Not clearly stating the inductive hypothesis or the inductive step.  
- Algebraic errors during the inductive step.

# Problem-Solving Techniques:

- Clearly label each step: Base Case, Inductive Hypothesis, Inductive Step.  
- In the inductive step, try to manipulate the expression for $P(k + 1)$ to isolate an instance of $P(k)$ that can be substituted using the hypothesis.  
- For inequalities, sometimes it's easier to prove $P(k + 1) - P(k) \geq 0$ or similar.

# Number Theory

Number theory is the study of integers and their properties, including divisibility, prime numbers, and modular arithmetic. It has direct applications in cryptography, error correction codes, and algorithm analysis.

# Definition and Core Idea:

Number theory explores the relationships and properties of integers. The core idea is to understand the structure and behavior of numbers under various operations.

# Important Formulas and Results:

- Divisibility: $a|b$ means $a$ divides $b$ (i.e., $b = ka$ for some integer $k$ ).  
- Division Algorithm: For integers $a$ (dividend) and $d$ (divisor) with $d > 0$ , there exist unique integers $q$ (quotient) and $r$ (remainder) such that $a = dq + r$ , where $0 \leq r < d$ .  
- Greatest Common Divisor (GCD): $\gcd(a, b)$ is the largest integer that divides both $a$ and $b$ .  
- Euclidean Algorithm: An efficient method to compute GCD. $\gcd(a, b) = \gcd(b, a \pmod{b})$ .  
- Bézout's Identity: For any integers $a, b$ , there exist integers $x, y$ such that $ax + by = \gcd(a, b)$ .  
- Least Common Multiple (LCM): $\operatorname{lcm}(a, b)$ is the smallest positive integer divisible by both $a$ and $b$ .  
- Relationship: $\gcd(a, b) \cdot \operatorname{lcm}(a, b) = |ab|$ .  
- Prime Numbers: A positive integer greater than 1 with exactly two positive divisors: 1 and itself.  
- Fundamental Theorem of Arithmetic: Every integer greater than 1 can be uniquely represented as a product of prime numbers (up to the order of factors).  
- Modular Arithmetic: $a \equiv b \pmod{m}$ means $m \mid (a - b)$ . This is an equivalence relation.  
- Properties:  
- If $a \equiv b \pmod{m}$ and $c \equiv d \pmod{m}$ , then $a + c \equiv b + d \pmod{m}$ and $ac \equiv bd \pmod{m}$ .  
- $(a \pmod{m} + b \pmod{m}) \pmod{m} = (a + b) \pmod{m}$  
- $(a \pmod{m} \cdot b \pmod{m}) \pmod{m} = (a \cdot b) \pmod{m}$  
- Fermat's Little Theorem: If $p$ is a prime number and $a$ is an integer not divisible by $p$ , then $a^{p-1} \equiv 1 \pmod{p}$ . Also, $a^p \equiv a \pmod{p}$ for any integer $a$ .  
- Euler's Totient Function $\phi(n)$ : Counts the number of positive integers up to $n$ that are relatively prime to $n$ .  
○ If $n = p_1^{k_1} p_2^{k_2} \ldots p_r^{k_r}$ is the prime factorization of $n$ , then $\phi(n) = n \left(1 - \frac{1}{p_1}\right) \left(1 - \frac{1}{p_2}\right) \ldots \left(1 - \frac{1}{p_r}\right)$ .  
- If $p$ is prime, $\phi(p) = p - 1$ .  
- Euler's Theorem: If $n$ is a positive integer and $a$ is an integer relatively prime to $n$ (i.e., $\gcd(a, n) = 1$ ), then $a^{\phi(n)} \equiv 1 \pmod{n}$ .

# Key Properties and Identities:

\- Congruence modulo $m$ is an equivalence relation.

\- The set of integers modulo $n$ , $\mathbb{Z}_n = \{0, 1, \dots, n - 1\}$ , forms a ring under addition and multiplication modulo $n$ . If $n$ is prime, $\mathbb{Z}_n$ is a field.

# Common Pitfalls & Tricky Points:

- Mistakes in applying modular arithmetic, especially with negative numbers or division. Remember division is not always well-defined in modular arithmetic (requires modular inverse).  
- Confusing prime numbers with relatively prime numbers.  
- Incorrectly calculating $\phi(n)$ for composite numbers.

# Problem-Solving Techniques:

- Use the Euclidean algorithm for GCD and extended Euclidean algorithm for modular inverses.  
- Simplify large powers in modular arithmetic using Fermat's Little Theorem or Euler's Theorem.  
- For divisibility problems, use properties of congruences.

# Onto (Surjective Functions)

Onto functions, also known as surjective functions, ensure that every element in the codomain is "hit" by at least one element from the domain. This property is vital for understanding mappings that cover their entire target set.

# Definition and Core Idea:

A function $f: A \to B$ is said to be onto (or surjective) if for every element $y \in B$ (the codomain), there exists at least one element $x \in A$ (the domain) such that $f(x) = y$ . The core idea is that the function's range completely fills its codomain.

# Important Formulas and Results:

- A function $f: A \to B$ is surjective if and only if $\text{range}(f) = B$ .  
- If $A$ and $B$ are finite sets, and $f: A \to B$ is surjective, then $|A| \geq |B|$ .  
- The number of surjective functions from a set of size $m$ to a set of size $n$ is given by $\sum_{k=0}^{n}(-1)^{k}\binom{n}{k}(n-k)^{m}$ .

# Key Properties and Identities:

- If $f$ and $g$ are surjective, then $g \circ f$ is surjective.  
- If $g \circ f$ is surjective, then $g$ must be surjective (but $f$ need not be).

# Common Pitfalls & Tricky Points:

- Confusing surjectivity with injectivity. An onto function doesn't require unique preimages.  
- Failing to demonstrate a preimage for an arbitrary element in the codomain, instead just showing some elements have preimages.

# Problem-Solving Techniques:

- To prove a function $f: A \to B$ is surjective, pick an arbitrary $y \in B$ , then show how to construct an $x \in A$ such that $f(x) = y$ . This often involves solving $y = f(x)$ for $x$ .  
- For finite sets, compare the cardinalities of the domain and codomain. If $|A| < |B|$ , no surjective function from $A$ to $B$ can exist.

# Partial Order

Partial order relations define a sense of relative order among elements in a set, but not necessarily for every pair. They are crucial for modeling hierarchies, dependencies, and precedence in computer science (e.g., task scheduling, class inheritance).

# Definition and Core Idea:

A relation $R$ on a set $A$ is a partial order relation if it is reflexive, antisymmetric, and transitive. A set $A$ with a partial order relation $\preceq$ is called a partially ordered set (poset), denoted $(A, \preceq)$ . The core idea is to establish an ordering where some elements might be incomparable.

# Important Formulas and Results:

# • Properties of Partial Order:

1. Reflexive: For all $a \in A$ , $a \prec a$ .  
2. Antisymmetric: For all $a, b \in A$ , if $a \preceq b$ and $b \preceq a$ , then $a = b$ .  
3. Transitive: For all $a, b, c \in A$ , if $a \preceq b$ and $b \preceq c$ , then $a \preceq c$ .  
- Comparability: Two elements $a, b \in A$ are comparable if $a \preceq b$ or $b \preceq a$ . Otherwise, they are incomparable.  
- Total Order (Linear Order): A partial order where every pair of elements is comparable.  
- Hasse Diagram: A graphical representation of a finite poset, where:  
- Elements are represented by nodes.  
- An edge goes upwards from $a$ to $b$ if $a \preceq b$ and there is no $c$ such that $a \preceq c \preceq b$ (i.e., $b$ covers $a$ ).  
- Reflexive loops and transitive edges are omitted.

# - Elements in a Poset:

- Maximal Element: An element $a$ such that there is no $b \in A$ with $a \preceq b$ and $a \neq b$ .  
- Minimal Element: An element $a$ such that there is no $b \in A$ with $b \preceq a$ and $a \neq b$ .  
- Greatest Element (Maximum): An element $g$ such that for all $x \in A$ , $x \preceq g$ . (If it exists, it is unique).  
- Least Element (Minimum): An element $l$ such that for all $x \in A$ , $l \preceq x$ . (If it exists, it is unique).  
- Upper Bound: For a subset $S \subseteq A$ , an element $u \in A$ is an upper bound of $S$ if $s \preceq u$ for all $s \in S$ .  
- Lower Bound: For a subset $S \subseteq A$ , an element $l \in A$ is a lower bound of $S$ if $l \preceq s$ for all $s \in S$ .  
- Least Upper Bound (LUB / Supremum): The least element among all upper bounds of $S$ , denoted $\sup(S)$ .  
- Greatest Lower Bound (GLB / Infimum): The greatest element among all lower bounds of $S$ , denoted $\inf(S)$ .

# Key Properties and Identities:

- A greatest element is always a maximal element, but a maximal element is not necessarily the greatest. Similarly for least and minimal elements.  
- A finite poset always has at least one maximal and one minimal element.

# Common Pitfalls & Tricky Points:

- Confusing maximal/minimal elements with greatest/least elements. A poset can have multiple maximal elements but at most one greatest element.  
- Errors in drawing Hasse diagrams, especially omitting necessary edges or including redundant ones.  
- Incorrectly identifying LUBs or GLBs for subsets.

# Problem-Solving Techniques:

- To verify a partial order, systematically check reflexivity, antisymmetry, and transitivity.  
- Draw Hasse diagrams to visualize the order and identify special elements (maximal, minimal, greatest, least, LUB, GLB).  
- For LUB/GLB, first find all upper/lower bounds, then identify the least/greatest among them.

# Polynomials

Polynomials are fundamental algebraic expressions used extensively in computer science for modeling, interpolation, error correction, and algorithm analysis (e.g., complexity). In discrete mathematics, they often appear in contexts like finite fields and generating functions.

# Definition and Core Idea:

A polynomial in a variable x is an expression of the form $P(x) = a_{n}x^{n} + a_{n-1}x^{n-1} + \cdots + a_{1}x + a_{0}$ , where $a_{i}$ are coefficients (often real or complex numbers, but can be from finite fields in discrete math) and n is a non-negative integer called the degree of the polynomial (if $a_{n} \neq 0$ ). The core idea is to represent relationships using sums of powers of a variable.

# Important Formulas and Results:

- Degree: The highest power of $x$ with a non-zero coefficient.  
- Root (or Zero): A value $c$ such that $P(c) = 0$ .  
- Polynomial Division Algorithm: For polynomials $P(x)$ (dividend) and $D(x)$ (divisor) with $D(x) \neq 0$ , there exist unique polynomials $Q(x)$ (quotient) and $R(x)$ (remainder) such that $P(x) = D(x)Q(x) + R(x)$ , where $\deg(R(x)) < \deg(D(x))$ or $R(x) = 0$ .  
- Remainder Theorem: If a polynomial $P(x)$ is divided by $(x - c)$ , the remainder is $P(c)$ .  
- Factor Theorem: $(x - c)$ is a factor of $P(x)$ if and only if $P(c) = 0$ (i.e., $c$ is a root of $P(x)$ ).  
- Fundamental Theorem of Algebra: Every non-constant polynomial with complex coefficients has at least one complex root. Consequently, a polynomial of degree $n$ has exactly $n$ complex roots (counting multiplicity).  
- Vieta's Formulas: Relate the coefficients of a polynomial to the sums and products of its roots. For a quadratic $ax^2 + bx + c = 0$ with roots $r_1, r_2: r_1 + r_2 = -b / a, r_1r_2 = c / a$ .

# Key Properties and Identities:

- A polynomial of degree $n$ has at most $n$ distinct roots.  
- Polynomials form a ring under addition and multiplication.

# Common Pitfalls & Tricky Points:

- Algebraic errors in polynomial division or evaluating polynomials.  
- Forgetting to count root multiplicities when applying the Fundamental Theorem of Algebra.  
- Not considering the domain of coefficients (e.g., real vs. complex vs. finite field).

# Problem-Solving Techniques:

- Use synthetic division for quick division by $(x - c)$ .  
- Apply the Remainder and Factor Theorems to find roots or factors efficiently.  
- For problems involving roots, Vieta's formulas can often provide shortcuts.

# Quick Formula Reference

\- Set Theory:

$\circ |P(A)| = 2^{|A|}$  
$\circ |A\cup \dot{B}| = |A| + |B| - |A\cap B|$  
- De Morgan's Laws: $\overline{A \cup B} = \overline{A} \cap \overline{B}, \overline{A \cap B} = \overline{A} \cup \overline{B}$

\- Relations:

○ Number of relations from A to B: $2^{|A||B|}$  
- Equivalence Relation: Reflexive, Symmetric, Transitive.  
- Partial Order: Reflexive, Antisymmetric, Transitive.

\- Functions (from $|A| = m$ to $|B| = n$ ):

• Total functions: $n^{m}$  
- Injective functions: $P(n, m) = \frac{n!}{(n - m)!}$ (if $m \leq n$ )  
- Bijective functions: $n!$ (if $m = n$ )  
- Surjective functions: $\sum_{k=0}^{n}(-1)^{k}\binom{n}{k}(n-k)^{m}$  
- Identity function $I_A(x) = x$

\- Group Theory:

- Group Axioms: Closure, Associativity, Identity, Inverse.  
- Lagrange's Theorem: $|H|$ divides $|G|$ for subgroup $H$ of group $G$ .

\- Lattice:

- Poset where every pair has unique LUB (join $\vee$ ) and GLB (meet $\wedge$ ).  
- Distributive Lattice: $a \wedge (b \vee c) = (a \wedge b) \vee (a \wedge c)$ , etc.

• Mathematical Induction:

\- Base Case $P(n_0)$ , Inductive Hypothesis $P(k)$ , Inductive Step $P(k + 1)$ .

\- Number Theory:

- Division Algorithm: $a = dq + r, 0 \leq r < d$  
$\circ \gcd (a,b)\cdot \operatorname {lcm}(a,b) = |ab|$  
- Fermat's Little Theorem: $a^{p-1} \equiv 1 \pmod{p}$ (for prime $p, p \nmid a$ )

- Euler's Totient Function: $\phi(n) = n \prod_{p \mid n, p \text{ prime}} \left(1 - \frac{1}{p}\right)$  
- Euler's Theorem: $a^{\phi(n)} \equiv 1 \pmod{n}$ (for $\gcd(a, n) = 1$ )

# - Polynomials:

- Remainder Theorem: $P(x) \pmod{(x - c)} = P(c)$  
- Factor Theorem: $(x - c)$ is a factor $\iff P(c) = 0$

# Important Tips for GATE

1. Master Definitions and Properties: Many GATE questions directly test your understanding of definitions (e.g., what makes a relation symmetric?) and properties (e.g., De Morgan's laws). Memorize them thoroughly.  
2. Practice with Hasse Diagrams: For partial orders and lattices, drawing Hasse diagrams is crucial. Practice identifying maximal/minimal elements, greatest/least elements, and LUB/GLB from diagrams.  
3. Systematic Verification: When asked to check if a structure is a group, a relation is an equivalence relation, or a function is bijective, systematically go through each axiom/property. Don't skip steps or assume properties.  
4. Number Theory Shortcuts: Familiarize yourself with the Euclidean algorithm for GCD, modular arithmetic properties, and theorems like Fermat's Little Theorem and Euler's Theorem. These are vital for efficiently solving problems involving large numbers or powers.  
5. Inclusion-Exclusion Principle: This principle is frequently tested for counting problems in set theory and functions (especially surjective functions). Practice applying it for 2, 3, and general cases.  
6. Mathematical Induction Structure: Always clearly state your base case, inductive hypothesis, and inductive step. Ensure your inductive step explicitly uses the inductive hypothesis to avoid circular reasoning.  
7. Cardinality vs. Countability: Understand the difference between finite, countably infinite, and uncountable sets. Be familiar with standard examples (e.g., $\mathbb{N},\mathbb{Z},\mathbb{Q}$ are countable; $\mathbb{R},P(\mathbb{N})$ are uncountable) and Cantor's diagonalization argument.  
8. Watch for "If and Only If": Pay close attention to conditions that are "if and only if" (iff) as they imply equivalence and are often key to proving properties or identifying specific structures.

4.1

# Binary Operation (8)

# 4.1.1 Binary Operation: GATE CSE 1989 | Question: 1-v

The number of possible commutative binary operations that can be defined on a set of $n$ elements (for a given $n$ ) is \_\_\_\_.


gate1989 descriptive set-theory&algebra binary-operation

Answer key

# 4.1.2 Binary Operation: GATE CSE 1994 | Question: 2.2

On the set N of non-negative integers, the binary operation \_\_\_\_ is associative and non-commutative.


gate1994 set-theory&algebra normal group-theory binary-operation fill-in-the-blanks

Answer key

# 4.1.3 Binary Operation: GATE CSE 2003 | Question: 38

Consider the set $\{a, b, c\}$ with binary operators + and \* defined as follows:


<table><tr><td>+</td><td>a</td><td>b</td><td>c</td></tr><tr><td>a</td><td>b</td><td>a</td><td>c</td></tr><tr><td>b</td><td>a</td><td>b</td><td>c</td></tr><tr><td>c</td><td>a</td><td>c</td><td>b</td></tr></table>

<table><tr><td>*</td><td>a</td><td>b</td><td>c</td></tr><tr><td>a</td><td>a</td><td>b</td><td>c</td></tr><tr><td>b</td><td>b</td><td>c</td><td>a</td></tr><tr><td>c</td><td>c</td><td>c</td><td>b</td></tr></table>

For example, $a + c = c, c + a = a, c * b = c$ and $b * c = a$ .

Given the following set of equations:

- $(a*x) + (a*y) = c$  
- $(b*x) + (c*y) = c$

The number of solution(s) (i.e., pair(s) $(x, y)$ that satisfy the equations) is

A. 0

B. 1

C. 2

D. 3

gatecse-2003 set-theory&algebra normal binary-operation

# Answer key

# 4.1.4 Binary Operation: GATE CSE 2006 | Question: 28

A logical binary relation $\odot$ , is defined as follows:

<table><tr><td>A</td><td>B</td><td>A ⊙ B</td></tr><tr><td>True</td><td>True</td><td>True</td></tr><tr><td>True</td><td>False</td><td>True</td></tr><tr><td>False</td><td>True</td><td>False</td></tr><tr><td>False</td><td>False</td><td>True</td></tr></table>


Let $\sim$ be the unary negation (NOT) operator, with higher precedence then $\odot$ .

Which one of the following is equivalent to $A \wedge B$ ?

A. $(\sim A\odot B)$ C. $\sim (\sim A\odot \sim B)$

B. $\sim (A\odot \sim B)$ D. $\sim (\sim A\odot B)$

gatecse-2006 set-theory&algebra binary-operation propositional-logic mathematical-logic

# Answer key

# 4.1.5 Binary Operation: GATE CSE 2013 | Question: 1

A binary operation $\oplus$ on a set of integers is defined as $x \oplus y = x^2 + y^2$ . Which one of the following statements is TRUE about $\oplus$ ?

A. Commutative but not associative

C. Associative but not commutative

B. Both commutative and associative

D. Neither commutative nor associative

gatecse-2013 set-theory&algebra easy binary-operation

# Answer key

# 4.1.6 Binary Operation: GATE CSE 2015 | Set 1 | Question: 28

The binary operator ≠ is defined by the following truth table.

<table><tr><td>p</td><td>q</td><td>p ≠ q</td></tr><tr><td>0</td><td>0</td><td>0</td></tr><tr><td>0</td><td>1</td><td>1</td></tr><tr><td>1</td><td>0</td><td>1</td></tr><tr><td>1</td><td>1</td><td>0</td></tr></table>



Which one of the following is true about the binary operator ≠ ?

A. Both commutative and associative

C. Not commutative but associative

B. Commutative but not associative

D. Neither commutative nor associative

gatecse-2015-set1 set-theory&algebra easy binary-operation boolean-algebra

# Answer key

# 4.1.7 Binary Operation: GATE CSE 2015 | Set 3 | Question: 2

Let # be the binary operator defined as

$X\# Y = X' + Y'$ where $X$ and $Y$ are Boolean variables.

Consider the following two statements.

\- $(S_{1})(P\# Q)\# R = P\# (Q\# R)$


$$
\cdot (S _ {2}) Q \# R = (R \# Q)
$$

Which are the following is/are true for the Boolean variables P, Q and R?

A. Only $S_{1}$ is true

B. Only $S_{2}$ is true

C. Both $S_{1}$ and $S_{2}$ are true

D. Neither $S_{1}$ nor $S_{2}$ are true

gatecse-2015-set3 set-theory&algebra binary-operation normal

# Answer key

# 4.1.8 Binary Operation: GATE IT 2006 | Question: 2

For the set $N$ of natural numbers and a binary operation $f: N \times N \to N$ , an element $z \in N$ is called an identity for $f$ , if $f(a, z) = a = f(z, a)$ , for all $a \in N$ . Which of the following binary operations have an identity?

1. $f(x,y) = x + y - 3$  
II. $f(x,y) = \max (x,y)$  
III. $f(x,y) = x^{y}$

A. I and II only

B. II and III only

C. I and III only

D. None of these

gateit-2006 set-theory&algebra easy binary-operation

# Answer key

# 4.2

# Countable Uncountable Set (2)

# 4.2.1 Countable Uncountable Set: GATE CSE 1994 | Question: 3.9

Every subset of a countable set is countable.

State whether the above statement is true or false with reason.

gate1994 set-theory&algebra normal set-theory countable-uncountable-set true-false

# Answer key

# 4.2.2 Countable Uncountable Set: GATE CSE 2018 | Question: 27

Let N be the set of natural numbers. Consider the following sets,

- $P$ : Set of Rational numbers (positive and negative)  
- $Q$ : Set of functions from $\{0,1\}$ to $N$  
- $R$ : Set of functions from $N$ to $\{0,1\}$  
- $S$ : Set of finite subsets of $N$

Which of the above sets are countable?

A. $Q$ and $S$ only

B. $P$ and $S$ only

C. $P$ and $R$ only

D. $P, Q$ and $S$ only

gatecse-2018 set-theory&algebra countable-uncountable-set normal two-marks

# Answer key

# 4.3

# Functions (30)

# 4.3.1 Functions: GATE CSE 1987 | Question: 9b

How many one-to-one functions are there from a set $A$ with $n$ elements onto itself?

gate1987 set-theory&algebra functions descriptive

# Answer key

# 4.3.2 Functions: GATE CSE 1988 | Question: 13ii

If the set S has a finite number of elements, prove that if f maps S onto S, then f is one-to-one.






# 4.3.3 Functions: GATE CSE 1989 | Question: 13c

Find the number of single valued functions from set $A$ to another set $B$ , given that the cardinalities of the sets $A$ and $B$ are $m$ and $n$ respectively.


gate1989 descriptive functions set-theory&algebra

Answer key

# 4.3.4 Functions: GATE CSE 1993 | Question: 8.6

Let $A$ and $B$ be sets with cardinalities $m$ and $n$ respectively. The number of one-one mappings from $A$ to $B$ , when $m < n$ , is


A. $m^{n}$

B. $^{n}P_{m}$

C. $^{m}C_{n}$

D. $^{n}C_{m}$

E. $^{m}P_{n}$

gate1993 set-theory&algebra functions easy

Answer key

# 4.3.5 Functions: GATE CSE 1996 | Question: 1.3

Suppose $X$ and $Y$ are sets and $|X|$ and $|Y|$ are their respective cardinality. It is given that there are exactly 97 functions from $X$ to $Y$ . From this one can conclude that


A. $|X| = 1, |Y| = 97$

C. $|X| = 97, |Y| = 97$

B. $|X| = 97, |Y| = 1$

D. None of the above

gate1996 set-theory&algebra functions normal

Answer key

# 4.3.6 Functions: GATE CSE 1996 | Question: 2.1

Let $R$ denote the set of real numbers. Let $f: R \times R \to R \times R$ be a bijective function defined by $f(x, y) = (x + y, x - y)$ . The inverse function of $f$ is given by


A. $f^{-1}(x,y) = \left(\frac{1}{x + y},\frac{1}{x - y}\right)$

B. $f^{-1}(x,y) = (x - y,x + y)$

C. $f^{-1}(x,y) = \left(\frac{x + y}{2},\frac{x - y}{2}\right)$

$$
f ^ {- 1} (x, y) = [ 2 (x - y), 2 (x + y) ]
$$

gate1996 set-theory&algebra functions normal

Answer key

# 4.3.7 Functions: GATE CSE 1997 | Question: 13

Let $F$ be the set of one-to-one functions from the set $\{1,2,\ldots,n\}$ to the set $\{1,2,\ldots,m\}$ where $m\geq n\geq 1$ .


a. How many functions are members of $F$ ?  
b. How many functions $f$ in $F$ satisfy the property $f(i) = 1$ for some $i, 1 \leq i \leq n$ ?  
c. How many functions $f$ in $F$ satisfy the property $f(i) < f(j)$ for all $i, j$ $1 \leq i \leq j \leq n$ ?

gate1997 set-theory&algebra functions normal descriptive difficult

Answer key

# 4.3.8 Functions: GATE CSE 1998 | Question: 1.8

The number of functions from an $m$ element set to an $n$ element set is

A. $m + n$

B. $m^n$

C. $n^{m}$

D. $m*n$

gate1998 set-theory&algebra combinatory functions easy

# Answer key

# 4.3.9 Functions: GATE CSE 2001 | Question: 2.3

Let $f: A \to B$ a function, and let $E$ and $F$ be subsets of $A$ . Consider the following statements about images.

- $S_{1}:f(E\cup F) = f(E)\cup f(F)$  
- $S_{2}:f(E\cap F) = f(E)\cap f(F)$

Which of the following is true about S1 and S2?

A. Only $S_{1}$ is correct

B. Only $S_{2}$ is correct

C. Both $S_{1}$ and $S_{2}$ are correct

D. None of $S_{1}$ and $S_{2}$ is correct

gatecse-2001 set-theory&algebra functions normal

# Answer key

# 4.3.10 Functions: GATE CSE 2001 | Question: 4

Consider the function $h: N \times N \to N$ so that $h(a, b) = (2a + 1)2^b - 1$ , where $N = \{0, 1, 2, 3, \ldots\}$ is the set of natural numbers.

a. Prove that the function $h$ is an injection (one-one).

b. Prove that it is also a Surjection (onto)

gatecse-2001 functions set-theory&algebra normal descriptive

# Answer key

# 4.3.11 Functions: GATE CSE 2003 | Question: 37

Let $f: A \to B$ be an injective (one-to-one) function. Define $g: 2^A \to 2^B$ as: $g(C) = \{f(x) \mid x \in C\}$ , for all subsets $C$ of $A$ .

Define $h: 2^B \to 2^A$ as: $h(D) = \{x \mid x \in A, f(x) \in D\}$ , for all subsets $D$ of $B$ . Which of the following statements is always true?

A. $g(h(D))\subseteq D$

B. $g(h(D))\supseteq D$

C. $g(h(D)) \cap D = \phi$

D. $g(h(D))\cap (B - D)\neq \phi$

gatecse-2003 set-theory&algebra functions difficult

# Answer key

# 4.3.12 Functions: GATE CSE 2003 | Question: 39

Let $\Sigma = \{a, b, c, d, e\}$ be an alphabet. We define an encoding scheme as follows:

$$
g (a) = 3, g (b) = 5, g (c) = 7, g (d) = 9, g (e) = 1 1.
$$

Let $p_{i}$ denote the i-th prime number $(p_{1}=2)$ .

For a non-empty string $s = a_1 \ldots a_n$ , where each $a_i \in \Sigma$ , define $f(s) = \Pi_{i=1}^n P_i^{g(a_i)}$ .

For a non-empty sequence $\langle s_j, \ldots, s_n \rangle$ of stings from $\Sigma^+$ , define $h(\langle s_i \ldots s_n \rangle) = \Pi_{i=1}^n P_i^{f(s_i)}$

Which of the following numbers is the encoding, h, of a non-empty sequence of strings?

A. $2^{7}3^{7}5^{7}$

B. $2^{8}3^{8}5^{8}$

C. $2^{9}3^{9}5^{9}$

D. $2^{10}3^{10}5^{10}$





