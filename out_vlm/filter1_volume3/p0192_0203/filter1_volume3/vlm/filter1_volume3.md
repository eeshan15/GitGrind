# Answer key

# 3.4.5 Conflict Serializable: GATE CSE 2014 | Set 3 | Question: 29

Consider the transactions $T1, T2$ , and $T3$ and the schedules $S1$ and $S2$ given below.

- $T1: r1(X); r1(Z); w1(X); w1(Z)$  
- $T2: r2(Y); r2(Z); w2(Z)$  
- $T3: r3(Y); r3(X); w3(Y)$  
- $S1: r1(X); r3(Y); r3(X); r2(Y); r2(Z); w3(Y); w2(Z); r1(Z); w1(X); w1(Z)$  
- $S2: r1(X); r3(Y); r2(Y); r3(X); r1(Z); r2(Z); w3(Y); w1(X); w2(Z); w1(Z)$

Which one of the following statements about the schedules is TRUE?

A. Only S1 is conflict-serializable.  
C. Both S1 and S2 are conflict-serializable.

B. Only $S2$ is conflict-serializable.

D. Neither S1 nor S2 is conflict-serializable.

gatecse-2014-set3 databases transaction-and-concurrency conflict-serializable normal

# Answer key

# 3.4.6 Conflict Serializable: GATE CSE 2017 | Set 2 | Question: 44

Two transactions $T_{1}$ and $T_{2}$ are given as

$$
T _ {1}: r _ {1} (X) w _ {1} (X) r _ {1} (Y) w _ {1} (Y)
$$

$$
T _ {2}: r _ {2} (Y) w _ {2} (Y) r _ {2} (Z) w _ {2} (Z)
$$

where $r_i(V)$ denotes a read operation by transaction $T_i$ on a variable $V$ and $w_i(V)$ denotes a write operation by transaction $T_i$ on a variable $V$ . The total number of conflict serializable schedules that can be formed by $T_1$ and $T_2$ is \_\_\_\_

gatecse-2017-set2 databases transaction-and-concurrency numerical-answers conflict-serializable

# Answer key

# 3.4.7 Conflict Serializable: GATE CSE 2020 | Question: 37

Consider a schedule of transactions $T_{1}$ and $T_{2}$ :

<table><tr><td> $T_1$ </td><td> $RA$ </td><td></td><td></td><td> $RC$ </td><td></td><td> $WD$ </td><td></td><td> $WB$ </td><td>Commit</td><td></td></tr><tr><td> $T_2$ </td><td></td><td> $RB$ </td><td> $WB$ </td><td></td><td> $RD$ </td><td></td><td> $WC$ </td><td></td><td></td><td>Commit</td></tr></table>

Here, RX stands for “Read(X)” and WX stands for “Write(X)”. Which one of the following schedules is conflict equivalent to the above schedule?

A.

<table><tr><td> $T_1$ </td><td></td><td></td><td></td><td> $RA$ </td><td> $RC$ </td><td> $WD$ </td><td> $WB$ </td><td></td><td>Commit</td><td></td></tr><tr><td> $T_2$ </td><td> $RB$ </td><td> $WB$ </td><td> $RD$ </td><td></td><td></td><td></td><td></td><td> $WC$ </td><td></td><td>Commit</td></tr></table>

B.

<table><tr><td> $T_1$ </td><td> $RA$ </td><td> $RC$ </td><td> $WD$ </td><td> $WB$ </td><td></td><td></td><td></td><td></td><td>Commit</td><td></td></tr><tr><td> $T_2$ </td><td></td><td></td><td></td><td></td><td> $RB$ </td><td> $WB$ </td><td> $RD$ </td><td> $WC$ </td><td></td><td>Commit</td></tr></table>

C.

<table><tr><td> $T_1$ </td><td> $RA$ </td><td> $RC$ </td><td> $WD$ </td><td></td><td></td><td></td><td> $WB$ </td><td></td><td>Commit</td><td></td></tr><tr><td> $T_2$ </td><td></td><td></td><td></td><td> $RB$ </td><td> $WB$ </td><td> $RD$ </td><td></td><td> $WC$ </td><td></td><td>Commit</td></tr></table>

D.

<table><tr><td> $T_1$ </td><td></td><td></td><td></td><td></td><td> $RA$ </td><td> $RC$ </td><td> $WD$ </td><td> $WB$ </td><td>Commit</td><td></td></tr><tr><td> $T_2$ </td><td> $RB$ </td><td> $WB$ </td><td> $RD$ </td><td> $WC$ </td><td></td><td></td><td></td><td></td><td></td><td>Commit</td></tr></table>




# Answer key

# 3.4.8 Conflict Serializable: GATE CSE 2021 | Set 1 | Question: 32


Let $r_i(z)$ and $w_i(z)$ denote read and write operations respectively on a data item $z$ by a transaction $T_i$ . Consider the following two schedules.

- $S_{1}: r_{1}(x) r_{1}(y) r_{2}(x) r_{2}(y) w_{2}(y) w_{1}(x)$  
- $S_{2}:r_{1}(x)r_{2}(x)r_{2}(y)w_{2}(y)r_{1}(y)w_{1}(x)$

Which one of the following options is correct?

A. $S_{1}$ is conflict serializable, and $S_{2}$ is not conflict serializable  
B. $S_{1}$ is not conflict serializable, and $S_{2}$ is conflict serializable  
C. Both $S_{1}$ and $S_{2}$ are conflict serializable  
D. Niether $S_{1}$ nor $S_{2}$ is conflict serializable

gatecse-2021-set1 databases transaction-and-concurrency conflict-serializable two-marks

# Answer key

# 3.4.9 Conflict Serializable: GATE CSE 2021 | Set 2 | Question: 32


Let $S$ be the following schedule of operations of three transactions $T_{1}$ , $T_{2}$ and $T_{3}$ in a relational database system:

$$
R _ {2} (Y), R _ {1} (X), R _ {3} (Z), R _ {1} (Y) W _ {1} (X), R _ {2} (Z), W _ {2} (Y), R _ {3} (X), W _ {3} (Z)
$$

Consider the statements P and Q below:

- $P$ : $S$ is conflict-serializable.  
- $Q$ : If $T_{3}$ commits before $T_{1}$ finishes, then $S$ is recoverable.

Which one of the following choices is correct?

A. Both $P$ and $Q$ are true  
C. $P$ is false and $Q$ is true

B. $P$ is true and $Q$ is false  
D. Both $P$ and $Q$ are false

gatecse-2021-set2 databases transaction-and-concurrency conflict-serializable two-marks

# Answer key

# 3.4.10 Conflict Serializable: GATE CSE 2022 | Question: 29


Let $R_{i}(z)$ and $W_{i}(z)$ denote read and write operations on a data element z by a transaction $T_{i}$ , respectively. Consider the schedule S with four transactions.

$$
S: R _ {4} (x) R _ {2} (x) R _ {3} (x) R _ {1} (y) W _ {1} (y) W _ {2} (x) W _ {3} (y) R _ {4} (y)
$$

Which one of the following serial schedules is conflict equivalent to $S$ ?

A. $T_{1} \rightarrow T_{3} \rightarrow T_{4} \rightarrow T_{2}$  
C. $T_{4} \rightarrow T_{1} \rightarrow T_{3} \rightarrow T_{2}$

B. $T_{1} \rightarrow T_{4} \rightarrow T_{3} \rightarrow T_{2}$  
D. $T_{3} \rightarrow T_{1} \rightarrow T_{4} \rightarrow T_{2}$

gatecse-2022 databases transaction-and-concurrency conflict-serializable two-marks

# Answer key

# 3.4.11 Conflict Serializable: GATE CSE 2024 | Set 1 | Question: 36


Consider the following read-write schedule S over three transactions $T_1, T_2,$ and $T_3$ , where the subscripts in the schedule indicate transaction IDs:

$$
S: r _ {1} (z); w _ {1} (z); r _ {2} (x); r _ {3} (y); w _ {3} (y); r _ {2} (y); w _ {2} (x); w _ {2} (y);
$$

Which of the following transaction schedules is/are conflict equivalent to S?

A. $T_{1}T_{2}T_{3}$

B. $T_{1}T_{3}T_{2}$

C. $T_{3}T_{2}T_{1}$

D. $T_{3}T_{1}T_{2}$

# 3.4.12 Conflict Serializable: GATE CSE 2025 | Set 2 | Question: 43

Consider the database transactions T1 and T2, and data items X and Y. Which of the schedule(s) is/are conflict serializable?


Transaction T1

<table><tr><td>R1(X)</td></tr><tr><td>W1(Y)</td></tr><tr><td>R1(X)</td></tr><tr><td>W1(X)</td></tr><tr><td>COMMIT(T1)</td></tr></table>

Transaction T2

<table><tr><td>W2(X)</td></tr><tr><td>W2(Y)</td></tr><tr><td>COMMIT(T2)</td></tr></table>

A. R1(X), W2(X), W1(Y), W2(Y), R1(X), W1(X), COMMIT(T2), COMMIT(T1)  
B. W2(X), R1(X), W2(Y), W1(Y), R1(X), COMMIT(T2), W1(X), COMMIT(T1)  
C. R1(X), W1(Y), W2(X), W2(Y), R1(X), W1(X), COMMIT(T1), COMMIT(T2)  
D. W2(X), R1(X), W1(Y), W2(Y), R1(X), COMMIT(T2), W1(X), COMMIT(T1)

gatecse2025-set2 databases conflict-serializable multiple-selects two-marks

Answer key

# 3.5

# Database Design (1)

# 3.5.1 Database Design: GATE CSE 1994 | Question: 3.11

State True or False with reason

Logical data independence is easier to achieve than physical data independence.

gate1994 databases normal database-design true-false

Answer key


# 3.6

# Database Normalization (56)

![](images/ca8b58b47f9371d8ea20b93ae794c130fd18a615281256153b6cda87e853860f.jpg)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (15Q)

Test 4 (6Q)

# 3.6.1 Database Normalization: GATE CSE 1987 | Question: 2n

State whether the following statements are TRUE or FALSE:


A relation $r$ with schema $(X, Y)$ satisfies the function dependency $X \to Y$ , The tuples $\langle 1, 2 \rangle$ and $\langle 2, 2 \rangle$ can both be in $r$ simultaneously.

gate1987 databases database-normalization true-false

Answer key

# 3.6.2 Database Normalization: GATE CSE 1988 | Question: 12i

What are the three axioms of functional dependency for the relational databases given by Armstrong.


gate1988 normal descriptive databases database-normalization

Answer key

# 3.6.3 Database Normalization: GATE CSE 1988 | Question: 12iia

Using Armstrong's axioms of functional dependency derive the following rules:


$$
\{x \rightarrow y, x \rightarrow z \} \models x \rightarrow y z
$$

(Note: $x \to y$ denotes $y$ is functionally dependent on $x, z \subseteq y$ denotes $z$ is subset of $y$ , and $| =$ means derives).

gate1988 easy descriptive databases database-normalization

# Answer key

# 3.6.4 Database Normalization: GATE CSE 1988 | Question: 12iib

Using Armstrong's axioms of functional dependency derive the following rules:

$$
\{x \rightarrow y, w y \rightarrow z \} \models x w \rightarrow z
$$

(Note: $x \to y$ denotes $y$ is functionally dependent on $x, z \subseteq y$ denotes $z$ is subset of $y$ , and $| =$ means derives).

gate1988 normal descriptive databases database-normalization

# Answer key

# 3.6.5 Database Normalization: GATE CSE 1988 | Question: 12iic

Using Armstrong's axioms of functional dependency derive the following rules:

$$
\{x \rightarrow y, z \subset y \} \mid = x \rightarrow z
$$

(Note: $x \to y$ denotes $y$ is functionally dependent on $x, z \subseteq y$ denotes $z$ is subset of $y$ , and $| =$ means derives).

gate1988 normal descriptive databases database-normalization

# Answer key

# 3.6.6 Database Normalization: GATE CSE 1990 | Question: 2-iv

Match the pairs in the following questions:

<table><tr><td>(a)</td><td>Secondary index</td><td>(p)</td><td>Function dependency</td></tr><tr><td>(b)</td><td>Non-procedural query language</td><td>(q)</td><td>B-tree</td></tr><tr><td>(c)</td><td>Closure of a set of attributes</td><td>(r)</td><td>Domain calculus</td></tr><tr><td>(d)</td><td>Natural join</td><td>(s)</td><td>Relational algebraic operations</td></tr></table>




gate1990 match-the-following database-normalization databases

# Answer key

# 3.6.7 Database Normalization: GATE CSE 1990 | Question: 3-ii

Indicate which of the following statements are true:

A relational database which is in 3NF may still have undesirable data redundancy because there may exist:

A. Transitive functional dependencies  
B. Non-trivial functional dependencies involving prime attributes on the right-side.  
C. Non-trivial functional dependencies involving prime attributes only on the left-side.  
D. Non-trivial functional dependencies involving only prime attributes.

gate1990 normal databases database-normalization multiple-selects

# Answer key

# 3.6.8 Database Normalization: GATE CSE 1994 | Question: 3.6

State True or False with reason



There is always a decomposition into Boyce-Codd normal form (BCNF) that is lossless and dependency preserving.

# Answer key

# 3.6.9 Database Normalization: GATE CSE 1995 | Question: 26

Consider the relation scheme $R(A, B, C)$ with the following functional dependencies:

- $A, B \to C$ ,  
• C → A

A. Show that the scheme R is in 3NF but not in BCNF.

B. Determine the minimal keys of relation R.

gate1995 databases database-normalization normal descriptive

# Answer key

# 3.6.10 Database Normalization: GATE CSE 1997 | Question: 6.9

For a database relation $R(a,b,c,d)$ , where the domains a, b, c, d include only atomic values, only the following functional dependencies and those that can be inferred from them hold

- $a \rightarrow c$  
- $b \rightarrow d$

This relation is

A. in first normal form but not in second normal form

C. in third normal form

gate1997 databases database-normalization normal

# Answer key

B. in second normal form but not in first normal form  
D. none of the above

# 3.6.11 Database Normalization: GATE CSE 1998 | Question: 1.34

Which normal form is considered adequate for normal relational database design?

A. $2NF$

B. $5NF$

C. $4NF$

D. $3NF$

gate1998 databases database-normalization easy

# Answer key

# 3.6.12 Database Normalization: GATE CSE 1998 | Question: 26

Consider the following database relations containing the attributes

- Book\_id  
- Subject\_Category\_of\_book  
- Name\_of\_Author  
- Nationality\_of\_Author

With Book\_id as the primary key.

a. What is the highest normal form satisfied by this relation?

b. Suppose the attributes Book\_title and Author\_address are added to the relation, and the primary key is changed to {Name\_of\_Author, Book\_title}, what will be the highest normal form satisfied by the relation?

gate1998 databases database-normalization normal descriptive

# Answer key

# 3.6.13 Database Normalization: GATE CSE 1999 | Question: 1.24

Let $R = (A, B, C, D, E, F)$ be a relation scheme with the following dependencies






$C \rightarrow F, E \rightarrow A, EC \rightarrow D, A \rightarrow B.$ Which one of the following is a key for R?

A. CD

B. EC

C. AE

D. AC

gate1999 databases database-normalization easy

# Answer key

# 3.6.14 Database Normalization: GATE CSE 1999 | Question: 2.7, UGCNET-June2014-III: 25

Consider the schema $R = (S, T, U, V)$ and the dependencies $S \to T, T \to U, U \to V$ and $V \to S$ . Let $R = (R1 \text{ and } R2)$ be a decomposition such that $R1 \cap R2 \neq \phi$ . The decomposition is


A. not in 2NF

B. in 2NF but not 3NF

C. in 3NF but not in 2NF

D. in both 2NF and 3NF

gate1999 databases database-normalization normal ugcnetjune2014iii

# Answer key

# 3.6.15 Database Normalization: GATE CSE 2000 | Question: 2.24

Given the following relation instance.


<table><tr><td>X</td><td>Y</td><td>Z</td></tr><tr><td>1</td><td>4</td><td>2</td></tr><tr><td>1</td><td>5</td><td>3</td></tr><tr><td>1</td><td>6</td><td>3</td></tr><tr><td>3</td><td>2</td><td>2</td></tr></table>

Which of the following functional dependencies are satisfied by the instance?

A. $XY \rightarrow Z$ and $Z \rightarrow Y$

B. $YZ \to X$ and $Y \to Z$

C. $YZ \to X$ and $X \to Z$

D. $XZ\to Y$ and $Y\to X$

gatecse-2000 databases database-normalization easy

# Answer key

# 3.6.16 Database Normalization: GATE CSE 2001 | Question: 2.23

$R(A,B,C,D)$ is a relation. Which of the following does not have a lossless join, dependency preserving BCNF decomposition?


A. $A \rightarrow B, B \rightarrow CD$

B. $A \to B, B \to C, C \to D$

C. $AB\to C,C\to AD$

D. $A \rightarrow BCD$

gatecse-2001 databases database-normalization normal

# Answer key

# 3.6.17 Database Normalization: GATE CSE 2002 | Question: 1.19

Relation R with an associated set of functional dependencies, F, is decomposed into BCNF. The redundancy (arising out of functional dependencies) in the resulting set of relations is


A. Zero  
B. More than zero but less than that of an equivalent 3NF decomposition  
C. Proportional to the size of $F^{+}$  
D. Indeterminate

gatecse-2002 databases database-normalization normal

# Answer key

# 3.6.18 Database Normalization: GATE CSE 2002 | Question: 16

For relation $\mathbf{R} = (\mathbf{L}, \mathbf{M}, \mathbf{N}, \mathbf{O}, \mathbf{P})$ , the following dependencies hold:


$$
M \rightarrow O, N O \rightarrow P, P \rightarrow L \text { and } L \rightarrow M N
$$

R is decomposed into $\mathbf{R1} = (\mathbf{L}, \mathbf{M}, \mathbf{N}, \mathbf{P})$ and $\mathbf{R2} = (\mathbf{M}, \mathbf{O})$ .

A. Is the above decomposition a lossless-join decomposition? Explain.  
B. Is the above decomposition dependency-preserving? If not, list all the dependencies that are not preserved.  
C. What is the highest normal form satisfied by the above decomposition?

gatecse-2002 databases database-normalization normal descriptive

# Answer key

# 3.6.19 Database Normalization: GATE CSE 2002 | Question: 2.24

Relation $R$ is decomposed using a set of functional dependencies, $F$ , and relation $S$ is decomposed using another set of functional dependencies, $G$ . One decomposition is definitely BCNF, the other is definitely $3NF$ , but it is not known which is which. To make a guaranteed identification, which one of the following should be used on the decompositions? (Assume that the closures of $F$ and $G$ are available).


A. Dependency-preservation

C. BCNF definition

B. Lossless-join

D. 3NF definition

gatecse-2002 databases database-normalization easy

# Answer key

# 3.6.20 Database Normalization: GATE CSE 2002 | Question: 2.25

From the following instance of a relation schema $R(A, B, C)$ , we can conclude that:

<table><tr><td>A</td><td>B</td><td>C</td></tr><tr><td>1</td><td>1</td><td>1</td></tr><tr><td>1</td><td>1</td><td>0</td></tr><tr><td>2</td><td>3</td><td>2</td></tr><tr><td>2</td><td>3</td><td>2</td></tr></table>


A. A functionally determines B and B functionally determines C  
B. $A$ functionally determines $B$ and $B$ does not functionally determine $C$  
C. $B$ does not functionally determine $C$  
D. $A$ does not functionally determine $B$ and $B$ does not functionally determine $C$

gatecse-2002 databases database-normalization

# Answer key

# 3.6.21 Database Normalization: GATE CSE 2003 | Question: 85

Consider the following functional dependencies in a database.

<table><tr><td>Date_of_Birth → Age</td><td>Age → Eligibility</td></tr><tr><td>Name → Roll_number</td><td>Roll_number → Name</td></tr><tr><td>Course_number → Course_name</td><td>Course_number → Instructor</td></tr><tr><td>(Roll_number, Course_number) → Grade</td><td></td></tr></table>


The relation (Roll\_number, Name, Date\_of\_birth, Age) is

A. in second normal form but not in third normal form

C. in BCNF

B. in third normal form but not in BCNF

D. in none of the above

gatecse-2003 databases database-normalization normal

# Answer key

# 3.6.22 Database Normalization: GATE CSE 2004 | Question: 50


The relation scheme Student Performance (name, courseNo, rollNo, grade) has the following functional dependencies:

- name, courseNo, → grade  
- rollNo, courseNo $\rightarrow$ grade  
- name $\rightarrow$ rollNo  
- rollNo $\rightarrow$ name

The highest normal form of this relation scheme is

A. 2NF

B. 3NF

C. BCNF

D. 4NF

gatecse-2004 databases database-normalization normal

Answer key

# 3.6.23 Database Normalization: GATE CSE 2005 | Question: 29, UGCNET-June2015-III: 9

Which one of the following statements about normal forms is FALSE?


A. BCNF is stricter than 3NF  
B. Lossless, dependency-preserving decomposition into 3NF is always possible  
C. Lossless, dependency-preserving decomposition into BCNF is always possible  
D. Any relation with two attributes is in BCNF

gatecse-2005 databases database-normalization easy ugcnetcse-june2015-paper3

Answer key

# 3.6.24 Database Normalization: GATE CSE 2006 | Question: 70

The following functional dependencies are given:


$$
A B \rightarrow C D, A F \rightarrow D, D E \rightarrow F, C \rightarrow G, F \rightarrow E, G \rightarrow A
$$

Which one of the following options is false?

A. $\{CF\}^{*} = \{ACDEFG\}$  
C. $\{AF\}^{*} = \{ACDEFG\}$

gatecse-2006 databases database-normalization normal

Answer key

# 3.6.25 Database Normalization: GATE CSE 2007 | Question: 62, UGCNET-June2014-II: 47

Which one of the following statements is FALSE?


A. Any relation with two attributes is in BCNF  
B. A relation in which every key has only one attribute is in 2NF  
C. A prime attribute can be transitively dependent on a key in a 3 NF relation  
D. A prime attribute can be transitively dependent on a key in a BCNF relation

gatecse-2007 databases database-normalization normal ugcnetcse-june2014-paper2

Answer key

# 3.6.26 Database Normalization: GATE CSE 2008 | Question: 69

Consider the following relational schemes for a library database:


Book (Title, Author, Catalog\_no, Publisher, Year, Price)

Collection(Title, Author, Catalog\_no)

with the following functional dependencies:

I. Title Author → Catalog\_no  
II. Catalog\_no → Title Author Publisher Year  
III. Publisher Title Year → Price

Assume { Author, Title } is the key for both schemes. Which of the following statements is true?

A. Both Book and Collection are in BCNF

B. Both Book and Collection are in 3NF only

C. Book is in 2NF and Collection in 3NF

D. Both Book and Collection are in 2NF only

gatecse-2008 databases database-normalization normal

# Answer key

# 3.6.27 Database Normalization: GATE CSE 2012 | Question: 2

Which of the following is TRUE?


A. Every relation in 3NF is also in BCNF  
B. A relation $\mathbf{R}$ is in 3NF if every non-prime attribute of $\mathbf{R}$ is fully functionally dependent on every key of $R$  
C. Every relation in BCNF is also in 3NF  
D. No relation can be in both BCNF and 3NF

gatecse-2012 databases easy database-normalization

# Answer key

# 3.6.28 Database Normalization: GATE CSE 2013 | Question: 54


Relation $R$ has eight attributes ABCDEFGH. Fields of $R$ contain only atomic values. $F = \{CH \to G, A \to BC, B \to CFH, E \to A, F \to EG\}$ is a set of functional dependencies (FDs) so that $F^{+}$ is exactly the set of FDs that hold for $R$ .

How many candidate keys does the relation R have?

A. 3

B. 4

C. 5

D. 6

gatecse-2013 databases database-normalization normal

# Answer key

# 3.6.29 Database Normalization: GATE CSE 2013 | Question: 55


Relation R has eight attributes ABCDEFGH. Fields of R contain only atomic values. $F = \{CH \rightarrow G, A \rightarrow BC, B \rightarrow CFH, E \rightarrow A, F \rightarrow EG\}$ is a set of functional dependencies (FDs) so that $F^{+}$ is exactly the set of FDs that hold for R.

The relation $R$ is

A. in 1NF, but not in 2NF.

B. in 2NF, but not in 3NF.

C. in 3NF, but not in BCNF.

D. in BCNF.

gatecse-2013 databases database-normalization normal

# Answer key

# 3.6.30 Database Normalization: GATE CSE 2014 | Set 1 | Question: 21


Consider the relation scheme $R = (E, F, G, H, I, J, K, L, M, N)$ and the set of functional dependencies

$$
\{\{E, F \} \rightarrow \{G \}, \{F \} \rightarrow \{I, J \}, \{E, H \} \rightarrow \{K, L \},
$$

$$
\{K \} \to \{M \}, \{L \} \to \{N \} \}
$$

on $R$ . What is the key for $R$ ?

A. $\{E,F\}$

B. $\{E,F,H\}$

C. $\{E,F,H,K,L\}$

D. $\{E\}$

# Answer key

# 3.6.31 Database Normalization: GATE CSE 2014 | Set 1 | Question: 30


Given the following two statements:

S1: Every table with two single-valued attributes is in 1NF, 2NF, 3NF and BCNF.

S2: $AB \to C, D \to E, E \to C$ is a minimal cover for the set of functional dependencies $AB \to C, D \to E, AB \to E, E \to C$ .

Which one of the following is CORRECT?

A. S1 is TRUE and S2 is FALSE.

C. S1 is FALSE and S2 is TRUE.

gatecse-2014-set1 databases database-normalization normal

B. Both S1 and S2 are TRUE.

D. Both S1 and S2 are FALSE.

# Answer key

# 3.6.32 Database Normalization: GATE CSE 2015 | Set 3 | Question: 20


Consider the relation $X(P, Q, R, S, T, U)$ with the following set of functional dependencies

$$
\begin{array}{l} F = \{ \begin{array}{c} \end{array} \\ \{P, R \} \to \{S, T \}, \\ \begin{array}{l} \{P, S, U \} \to \{Q, R \} \\ \} \end{array} \\ \end{array}
$$

Which of the following is the trivial functional dependency in $F^{+}$ , where $F^{+}$ is closure to $F$ ?

A. $\{P,R\} \rightarrow \{S,T\}$

C. $\{P, S\} \to \{S\}$

gatecse-2015-set3 databases database-normalization easy

B. $\{P,R\} \rightarrow \{R,T\}$

D. $\{P,S,U\} \to \{Q\}$

# Answer key

# 3.6.33 Database Normalization: GATE CSE 2016 | Set 1 | Question: 21


Which of the following is NOT a superkey in a relational schema with attributes V, W, X, Y, Z and primary key V Y?

A. VXYZ

B. VWXZ

C. VWXY

D. VWXYZ

gatecse-2016-set1 databases database-normalization easy

# Answer key

# 3.6.34 Database Normalization: GATE CSE 2016 | Set 1 | Question: 23


A database of research articles in a journal uses the following schema.

(VOLUME, NUMBER, STARTPAGE, ENDPAGE, TITLE, YEAR, PRICE)

The primary key is '(VOLUME, NUMBER, STARTPAGE, ENDPAGE)

and the following functional dependencies exist in the schema.

(VOLUME, NUMBER, STARTPAGE, ENDPAGE) → TITLE

(VOLUME, NUMBER) → YEAR

(VOLUME, NUMBER, STARTPAGE, ENDPAGE) → PRICE

The database is redesigned to use the following schemas

(VOLUME, NUMBER, STARTPAGE, ENDPAGE, TITLE, PRICE)

(VOLUME, NUMBER, YEAR)

Which is the weakest normal form that the new database satisfies, but the old one does not?

A. 1NF

B. 2NF

C. 3NF

D. BCNF

# 3.6.35 Database Normalization: GATE CSE 2017 | Set 1 | Question: 16

The following functional dependencies hold true for the relational schema $R\{V,W,X,Y,Z\}$ :


- $V \rightarrow W$  
- $VW \rightarrow X$  
- $Y \rightarrow VX$  
- $Y \to Z$

Which of the following is irreducible equivalent for this set of functional dependencies?

A. $V \rightarrow W$

$$
V \rightarrow X
$$

$$
Y \rightarrow V
$$

$$
Y \rightarrow Z
$$

B. $V \rightarrow W$

$$
W \rightarrow X
$$

$$
Y \rightarrow V
$$

$$
Y \to Z
$$

C. $V \rightarrow W$

$$
V \rightarrow X
$$

$$
Y \rightarrow V
$$

$$
Y \rightarrow X
$$

$$
Y \rightarrow Z
$$

D. $V \to W$

$$
W \rightarrow X
$$

$$
Y \rightarrow V
$$

$$
Y \rightarrow X
$$

$$
Y \to Z
$$

gatecse-2017-set1 databases database-normalization normal

# Answer key

# 3.6.36 Database Normalization: GATE CSE 2018 | Question: 42

Consider the following four relational schemas. For each schema, all non-trivial functional dependencies are listed, The bolded attributes are the respective primary keys.

Schema I: Registration(rollno, courses)

Field ‘courses’ is a set-valued attribute containing the set of courses a student has registered for.

Non-trivial functional dependency

rollno → courses

Schema II: Registration (rollno, coursid, email)

Non-trivial functional dependencies:

rollno, courseid → email

email → rollno

Schema III: Registration (rollno, courseid, marks, grade)

Non-trivial functional dependencies:

rollno, courseid, → marks, grade

marks → grade

Schema IV: Registration (rollno, courseid, credit)

Non-trivial functional dependencies:

rollno, courseid → credit

courseid → credit

Which one of the relational schemas above is in 3NF but not in BCNF?

A. Schema I

B. Schema II

C. Schema III

D. Schema IV

gatecse-2018 databases database-normalization normal two-marks

# Answer key

# 3.6.37 Database Normalization: GATE CSE 2019 | Question: 32

Let the set of functional dependencies $F = \{QR \to S, R \to P, S \to Q\}$ hold on a relation schema $X = (PQRS)$ . $X$ is not in BCNF. Suppose $X$ is decomposed into two schemas $Y$ and $Z$ , where $Y = (PR)$ and $Z = (QRS)$ .



Consider the two statements given below.

I. Both $Y$ and $Z$ are in BCNF  
II. Decomposition of X into Y and Z is dependency preserving and lossless

Which of the above statements is/are correct?

A. Both I and II

B. I only

C. II only

D. Neither I nor II

gatecse-2019 databases database-normalization two-marks

Answer key

# 3.6.38 Database Normalization: GATE CSE 2020 | Question: 36

Consider a relational table R that is in 3NF, but not in BCNF. Which one of the following statements is TRUE?


A. $R$ has a nontrivial functional dependency $X \to A$ , where $X$ is not a superkey and $A$ is a prime attribute.  
B. $R$ has a nontrivial functional dependency $X \to A$ , where $X$ is not a superkey and $A$ is a non-prime attribute and $X$ is not a proper subset of any key.  
C. $R$ has a nontrivial functional dependency $X \to A$ , where $X$ is not a superkey and $A$ is a non-prime attribute and $X$ is a proper subset of some key  
D. A cell in R holds a set instead of an atomic value.

gatecse-2020 databases database-normalization two-marks

Answer key

# 3.6.39 Database Normalization: GATE CSE 2021 | Set 1 | Question: 33

Consider the relation $R(P, Q, S, T, X, Y, Z, W)$ with the following functional dependencies.

$$
P Q \rightarrow X; \quad P \rightarrow Y X; \quad Q \rightarrow Y; \quad Y \rightarrow Z W
$$

Consider the decomposition of the relation R into the constituent relations according to the following two decomposition schemes.

- $D_{1}: \quad R = [(P, Q, S, T); (P, T, X); (Q, Y); (Y, Z, W)]$  
- $D_{2}: \quad R = [(P, Q, S); (T, X); (Q, Y); (Y, Z, W)]$

Which one of the following options is correct?

A. $D_{1}$ is a lossless decomposition, but $D_{2}$ is a lossy decomposition  
B. $D_{1}$ is a lossy decomposition, but $D_{2}$ is a lossless decomposition  
C. Both $D_{1}$ and $D_{2}$ are lossless decompositions  
D. Both $D_{1}$ and $D_{2}$ are lossy decompositions

gatecse-2021-set1 databases database-normalization two-marks

Answer key

# 3.6.40 Database Normalization: GATE CSE 2021 | Set 2 | Question: 40

Suppose the following functional dependencies hold on a relation $U$ with attributes $P, Q, R, S$ , and $T$ :

- $P \rightarrow QR$  
- $RS \rightarrow T$

Which of the following functional dependencies can be inferred from the above functional dependencies?

A. $PS \rightarrow T$

B. $R \rightarrow T$

C. $P \rightarrow R$

D. $PS \rightarrow Q$

gatecse-2021-set2 multiple-selects databases database-normalization two-marks

Answer key


