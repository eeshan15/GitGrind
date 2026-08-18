<table><tr><td>StudentName</td><td>CourseName</td></tr><tr><td>SA</td><td>CA</td></tr><tr><td>SA</td><td>CB</td></tr><tr><td>SA</td><td>CC</td></tr><tr><td>SB</td><td>CB</td></tr><tr><td>SB</td><td>CC</td></tr><tr><td>SC</td><td>CA</td></tr><tr><td>SC</td><td>CB</td></tr><tr><td>SC</td><td>CC</td></tr><tr><td>SD</td><td>CA</td></tr><tr><td>SD</td><td>CB</td></tr><tr><td>SD</td><td>CC</td></tr><tr><td>SD</td><td>CD</td></tr><tr><td>SE</td><td>CD</td></tr><tr><td>SE</td><td>CA</td></tr><tr><td>SE</td><td>CB</td></tr><tr><td>SF</td><td>CA</td></tr><tr><td>SF</td><td>CB</td></tr><tr><td>SF</td><td>CC</td></tr></table>

The following query is made on the database.

$$
\cdot T 1 \leftarrow \pi_ {\text {CourseName}} \left(\sigma_ {\text {StudentName} = S A} (C R)\right)
$$

$$
\cdot T 2 \leftarrow C R \div T 1
$$

The number of rows in T2 is \_\_\_\_.

gatecse-2017-set1 databases relational-algebra normal numerical-answers

# Answer key

# 3.18.23 Relational Algebra: GATE CSE 2018 | Question: 41


Consider the relations $r(A, B)$ and $s(B, C)$ , where $s. B$ is a primary key and $r. B$ is a foreign key referencing $s. B$ . Consider the query

$$
Q: r \bowtie (\sigma_ {B <   5} (s))
$$

Let LOJ denote the natural left outer-join operation. Assume that $r$ and $s$ contain no null values.

Which of the following is NOT equivalent to Q?

A. $\sigma_{B < 5}(r \bowtie s)$  
C. $rLOJ(\sigma_{B < 5}(s))$

B. $\sigma_{B < 5}(r LOJ s)$

D. $\sigma_{B < 5}(r)LOJs$

gatecse-2018 databases relational-algebra normal two-marks

# Answer key

# 3.18.24 Relational Algebra: GATE CSE 2019 | Question: 55

Consider the following relations $P(X,Y,Z), Q(X,Y,T)$ and $R(Y,V)$ .


Table: P

<table><tr><td>X</td><td>Y</td><td>Z</td></tr><tr><td>X1</td><td>Y1</td><td>Z1</td></tr><tr><td>X1</td><td>Y1</td><td>Z2</td></tr><tr><td>X2</td><td>Y2</td><td>Z2</td></tr><tr><td>X2</td><td>Y4</td><td>Z4</td></tr></table>

Table: Q

<table><tr><td>X</td><td>Y</td><td>T</td></tr><tr><td>X2</td><td>Y1</td><td>2</td></tr><tr><td>X1</td><td>Y2</td><td>5</td></tr><tr><td>X1</td><td>Y1</td><td>6</td></tr><tr><td>X3</td><td>Y3</td><td>1</td></tr></table>

Table: R.

<table><tr><td>Y</td><td>V</td></tr><tr><td>Y1</td><td>V1</td></tr><tr><td>Y3</td><td>V2</td></tr><tr><td>Y2</td><td>V3</td></tr><tr><td>Y2</td><td>V2</td></tr></table>

How many tuples will be returned by the following relational algebra query?

$$
\Pi_ {x} (\sigma_ {(P. Y = R. Y \land R. V = V 2))} (P \times R)) - \Pi_ {x} (\sigma_ {(Q. Y = R. Y \land Q. T > 2))} (Q \times R))
$$

Answer: \_\_\_\_

gatecse-2019 numerical-answers databases relational-algebra two-marks

Answer key

# 3.18.25 Relational Algebra: GATE CSE 2021 | Set 1 | Question: 27


The following relation records the age of 500 employees of a company, where empNo (indicating the employee number) is the key:

$$
e m p A g e (\underline {{e m p N o}}, a g e)
$$

Consider the following relational algebra expression:

$$
\Pi_ {e m p N o} (e m p A g e \bowtie_ {(a g e > a g e 1)} \rho_ {e m p N o 1, a g e 1} (e m p A g e))
$$

What does the above expression generate?

A. Employee numbers of only those employees whose age is the maximum  
B. Employee numbers of only those employees whose age is more than the age of exactly one other employee  
C. Employee numbers of all employees whose age is not the minimum  
D. Employee numbers of all employees whose age is the minimum

gatecse-2021-set1 databases relational-algebra two-marks

Answer key

# 3.18.26 Relational Algebra: GATE CSE 2022 | Question: 15


Consider the following three relations in a relational database.

Employee(eId, Name), Brand(bId, bName), Own(eId, bId)

Which of the following relational algebra expressions return the set of $elds$ who own all the brands?

A. $\Pi_{eId}(\Pi_{eId,bId}(Own)/\Pi_{bId}(Brand))$  
B. $\Pi_{eId}(Own) - \Pi_{eId}((\Pi_{eId}(Own) \times \Pi_{bId}(Brand)) - \Pi_{eId,bId}(Own))$  
c. $\Pi_{eId}(\Pi_{eId,bId}(Own) / \Pi_{bId}(Own))$  
D. $\Pi_{eId}\left((\Pi_{eId}(Own) \times \Pi_{bId}(Own)) / \Pi_{bId}(Brand)\right)$

gatecse-2022 databases relational-algebra multiple-selects one-mark

Answer key

# 3.18.27 Relational Algebra: GATE CSE 2024 | Set 1 | Question: 25

Consider the following two relations, $R(A,B)$ and $S(A,C)$ :


<table><tr><td colspan="2">R</td></tr><tr><td>A</td><td>B</td></tr><tr><td>10</td><td>20</td></tr><tr><td>20</td><td>30</td></tr><tr><td>30</td><td>40</td></tr><tr><td>30</td><td>50</td></tr><tr><td>50</td><td>95</td></tr></table>

<table><tr><td colspan="2">S</td></tr><tr><td>A</td><td>C</td></tr><tr><td>10</td><td>90</td></tr><tr><td>30</td><td>45</td></tr><tr><td>40</td><td>80</td></tr></table>

The total number of tuples obtained by evaluating the following expression

$$
\sigma_ {B <   C} \left(R \bowtie_ {R. A = S. A} S\right) \text {is} \underline {{\quad}}.
$$

gatecse-2024-set1 numerical-answers databases relational-algebra one-mark

Answer key

# 3.18.28 Relational Algebra: GATE CSE 2024 | Set 2 | Question: 35


The relation schema, Person (pid, city), describes the city of residence for every person uniquely identified by pid. The following relational algebra operators are available: selection, projection, cross product, and rename.

To find the list of cities where at least 3 persons reside, using the above operators, the minimum number of cross product operations that must be used is

A. 1

B. 2

C. 3

D. 4

gatecse-2024-set2 databases relational-algebra two-marks

Answer key

# 3.18.29 Relational Algebra: GATE DA 2025 | Question: 52

Consider the following tables, Loan and Borrower, of a bank.


<table><tr><td colspan="3">Loan</td></tr><tr><td>loan\_number</td><td>branch\_name</td><td>amount</td></tr><tr><td>L11</td><td>Banjara Hills</td><td>90000</td></tr><tr><td>L14</td><td>Kondapur</td><td>50000</td></tr><tr><td>L15</td><td>SR Nagar</td><td>40000</td></tr><tr><td>L22</td><td>SR Nagar</td><td>25000</td></tr><tr><td>L23</td><td>Balanagar</td><td>80000</td></tr><tr><td>L25</td><td>Kondapur</td><td>70000</td></tr><tr><td>L19</td><td>SR Nagar</td><td>65000</td></tr></table>

<table><tr><td colspan="2">Borrower</td></tr><tr><td>customer\_name</td><td>loan\_num</td></tr><tr><td>Anand</td><td>L11</td></tr><tr><td>Karteek</td><td>L11</td></tr><tr><td>Karteek</td><td>L14</td></tr><tr><td>Ankita</td><td>L15</td></tr><tr><td>Gopal</td><td>L19</td></tr><tr><td>Karteek</td><td>L22</td></tr><tr><td>Karteek</td><td>L23</td></tr><tr><td>Sunil</td><td>L23</td></tr><tr><td>Sunil</td><td>L25</td></tr></table>

Query: $\pi_{\text{branch\_name, customer\_name}}$ (Loan $\bowtie$ Borrower) $\div$ $\pi_{\text{branch\_name}}$ (Loan) where $\bowtie$ denotes natural join.

The number of tuples returned by the above relational algebra query is \_\_\_\_ (Answer in integer)

gateda-2025 databases relational-algebra numerical-answers two-marks

Answer key

Consider the following three relations:

Car (model, year, serial, color)

Make (maker, model)

Own (owner, serial)

A tuple in Car represents a specific car of a given model, made in a given year, with a serial number and a color. A tuple in Make specifies that a maker company makes cars of a certain model. A tuple in Own specifies that an owner owns the car with a given serial number. Keys are underlined; (owner, serial) together form key for Own. (▷ denotes natural join)

$$
\pi_ {\text {owner}} \left(\text {Own} \bowtie \left(\sigma_ {\text {color} = ^ {\prime \prime} \text {red}} \right. ^ {\prime \prime} \left(\text {Car} \bowtie \left(\sigma_ {\text {maker} = ^ {\prime \prime} \text {ABC}} \right. ^ {\prime \prime} \text {Make}\right)\right)\left. \right)
$$

Which one of the following options describes what the above expression computes?

A. All owners of a red car, a car made by ABC, or a red car made by ABC  
B. All owners of more than one car, where at least one car is red and made by ABC  
C. All owners of a red car made by ABC  
D. All red cars made by ABC

gateda-2025 databases relational-algebra one-mark

# Answer key

# 3.18.31 Relational Algebra: GATE DA 2026 | Question: 32

Consider the given relations $X, Y$ and $Z$ . The relation $X$ has three columns $P, Q$ and $R$ . The relation $Y$ has three columns $P, Q$ and $S$ . The relation $Z$ has two columns $P$ and $T$ .


<table><tr><td>P</td><td>Q</td><td>R</td></tr><tr><td>P1</td><td>Q1</td><td>R1</td></tr><tr><td>P2</td><td>Q2</td><td>R2</td></tr><tr><td>P3</td><td>Q3</td><td>R2</td></tr></table>

x

<table><tr><td>P</td><td>Q</td><td>S</td></tr><tr><td>P1</td><td>Q1</td><td>2</td></tr><tr><td>P1</td><td>Q2</td><td>5</td></tr><tr><td>P2</td><td>Q1</td><td>6</td></tr><tr><td>P3</td><td>Q3</td><td>1</td></tr></table>

Y

Z

<table><tr><td>P</td><td>T</td></tr><tr><td>P1</td><td>T1</td></tr><tr><td>P3</td><td>T2</td></tr><tr><td>P4</td><td>T3</td></tr><tr><td>P4</td><td>NULL</td></tr></table>

Consider the relational algebra expression

$$
\pi_ {P, R, S} \left[ \left(\sigma_ {(Q = Q 3 \lor R = R 2)} (X \bowtie Y)\right) \bowtie \left(\sigma_ {(S > 1)} (Y \bowtie Z)\right) \right]
$$

where $\bowtie$ denotes natural join operation.

Which of the following options is the correct output for the given expression?

A. Two rows (P1, R1, 2) and (P1, R1, 5)

B. Three rows (P1, R1, 2), (P1, R1, 5) and (P2, R2, 6)

C. One row (P1, R1, 2)

D. Zero rows

# 3.18.32 Relational Algebra: GATE DS&AI 2024 | Question: 16


Consider a database that includes the following relations:

Defender(name, rating, side, goals)

Forward(name, rating, assists, goals)

Team(name, club, price)

Which ONE of the following relational algebra expressions checks that every name occurring in Team appears in either Defender or Forward, where $\phi$ denotes the empty set?

A. $\Pi_{\text{name}}$ (Team) $\backslash$ ( $\Pi_{\text{name}}$ (Defender) $\cap$ $\Pi_{\text{name}}$ (Forward)) = $\phi$  
B. $(\Pi_{\text{name}} (\text{Defender}) \cap \Pi_{\text{name}} (\text{Forward})) \setminus \Pi_{\text{name}} (\text{Team}) = \phi$  
C. $\Pi_{\text{name}}$ (Team) $\backslash$ ( $\Pi_{\text{name}}$ (Defender) $\cup \Pi_{\text{name}}$ (Forward)) = $\phi$  
D. $(\Pi_{\text{name}} (\text{Defender}) \cup \Pi_{\text{name}} (\text{Forward})) \setminus \Pi_{\text{name}} (\text{Team}) = \phi$

gate-ds-ai-2024 relational-algebra databases one-mark

# Answer key

# 3.18.33 Relational Algebra: GATE IT 2005 | Question: 68

A table 'student' with schema (roll, name, hostel, marks), and another table 'hobby' with schema (roll, hobbyname) contains records as shown below:


Table: student

<table><tr><td>Roll</td><td>Name</td><td>Hostel</td><td>Marks</td></tr><tr><td>1798</td><td>Manoj Rathor</td><td>7</td><td>95</td></tr><tr><td>2154</td><td>Soumic Banerjee</td><td>5</td><td>68</td></tr><tr><td>2369</td><td>Gumma Reddy</td><td>7</td><td>86</td></tr><tr><td>2581</td><td>Pradeep pendse</td><td>6</td><td>92</td></tr><tr><td>2643</td><td>Suhas Kulkarni</td><td>5</td><td>78</td></tr><tr><td>2711</td><td>Nitin Kadam</td><td>8</td><td>72</td></tr><tr><td>2872</td><td>Kiran Vora</td><td>5</td><td>92</td></tr><tr><td>2926</td><td>Manoj Kunkalikar</td><td>5</td><td>94</td></tr><tr><td>2959</td><td>Hemant Karkhanis</td><td>7</td><td>88</td></tr><tr><td>3125</td><td>Rajesh Doshi</td><td>5</td><td>82</td></tr></table>

Table: hobby

<table><tr><td>Roll</td><td>Hobby Name</td></tr><tr><td>1798</td><td>chess</td></tr><tr><td>1798</td><td>music</td></tr><tr><td>2154</td><td>music</td></tr><tr><td>2369</td><td>swimming</td></tr><tr><td>2581</td><td>cricket</td></tr><tr><td>2643</td><td>chess</td></tr><tr><td>2643</td><td>hockey</td></tr><tr><td>2711</td><td>volleyball</td></tr><tr><td>2872</td><td>football</td></tr><tr><td>2926</td><td>cricket</td></tr><tr><td>2959</td><td>photography</td></tr><tr><td>3125</td><td>music</td></tr><tr><td>3125</td><td>chess</td></tr></table>

The following SQL query is executed on the above tables:

select hostel

from student natural join hobby

where marks >= 75 and roll between 2000 and 3000;

Relations S and H with the same schema as those of these two tables respectively contain the same information as tuples. A new relation $S'$ is obtained by the following relational algebra operation:

$$
S ^ {\prime} = \Pi_ {\mathrm{hostel}} \left(\left(\sigma_ {s. r o l l = H. r o l l} \left(\sigma_ {m a r k s > 7 5 \text {and} r o l l > 2 0 0 0 \text {and} r o l l <   3 0 0 0} (S)\right) \times (H)\right) \right.
$$

The difference between the number of rows output by the SQL statement and the number of tuples in $S'$ is

A. 6

B. 4

C. 2

D. 0

# 3.19

# Relational Calculus (13)

Practice Test: Test 1 (13Q)

# 3.19.1 Relational Calculus: GATE CSE 1993 | Question: 23


The following relations are used to store data about students, courses, enrollment of students in courses and teachers of courses. Attributes for primary key in each relation are marked by ‘\*’.

```txt
Students (rollno*, sname, saddr)
courses (cno*, cname)
enroll(rollno*, cno*, grade)
teach(tno*, tname, cao*)
```

(cno is course number cname is course name, tno is teacher number, tname is teacher name, sname is student name, etc.)

Write a SQL query for retrieving roll number and name of students who got A grade in at least one course taught by teacher names Ramesh for the above relational database.

gate1993 databases sql relational-calculus normal descriptive

# Answer key

# 3.19.2 Relational Calculus: GATE CSE 1998 | Question: 2.19

Which of the following query transformations (i.e., replacing the l.h.s. expression by the r.h.s expression) is incorrect? R1 and R2 are relations, C1 and C2 are selection conditions and A1 and A2 are attributes of R1.


A. $\sigma_{C_1}(\sigma_{C_2}(R_1))\rightarrow \sigma_{C_2}(\sigma_{C_1}(R_1))$  
B. $\sigma_{C_1}(\pi_{A_1}(R_1))\to \pi_{A_1}(\sigma_{C_1}(R_1))$  
C. $\sigma_{C_1}(R_1\cup R_2)\to \sigma_{C_1}(R_1)\cup \sigma_{C_1}(R_2)$  
D. $\pi_{A_1}(\sigma_{C_1}(R_1))\to \sigma_{C_1}(\pi_{A_1}(R_1))$

gate1998 databases relational-calculus normal

# Answer key

# 3.19.3 Relational Calculus: GATE CSE 1999 | Question: 1.19

The relational algebra expression equivalent to the following tuple calculus expression:

$$
\{t \mid t \in r \land (t [ A ] = 1 0 \land t [ B ] = 2 0) \} \text {is}
$$

A. $\sigma_{(A=10\lor B=20)}(r)$

B. $\sigma_{(A = 10)}(r) \cup \sigma_{(B = 20)}(r)$

C. $\sigma_{(A = 10)}(r)\cap \sigma_{(B = 20)}(r)$

D. $\sigma_{(A = 10)}(r) - \sigma_{(B = 20)}(r)$

gate1999 databases relational-calculus normal

# Answer key


# 3.19.4 Relational Calculus: GATE CSE 2001 | Question: 2.24

Which of the following relational calculus expression is not safe?

A. $\{t \mid \exists u \in R_1(t[A] = u[A]) \land \neg \exists s \in R_2(t[A] = s[A])\}$  
B. $\{t \mid \forall u \in R_1 (u[A] = "x" \Rightarrow \exists s \in R_2 (t[A] = s[A] \land s[A] = u[A]))\}$  
C. $\{t\mid \neg (t\in R_1)\}$  
D. $\{t \mid \exists u \in R_1(t[A] = u[A]) \land \exists s \in R_2(t[A] = s[A])\}$

gatecse-2001 relational-calculus normal databases

# Answer key


# 3.19.5 Relational Calculus: GATE CSE 2002 | Question: 1.20


With regards to the expressive power of the formal relational query languages, which of the following statements is true?

A. Relational algebra is more powerful than relational calculus  
B. Relational algebra has the same power as relational calculus  
C. Relational algebra has the same power as safe relational calculus  
D. None of the above

gatecse-2002 databases relational-calculus normal

Answer key

# 3.19.6 Relational Calculus: GATE CSE 2004 | Question: 13


Let $R_{1}(\underline{A},B,C)$ and $R_{2}(\underline{D},E)$ be two relation schemas, where the primary keys are shown underlined, and let $\underline{C}$ be a foreign key in $R_{1}$ referring to $R_{2}$ . Suppose there is no violation of the above referential integrity constraint in the corresponding relation instances $r_{1}$ and $r_{2}$ . Which of the following relational algebra expressions would necessarily produce an empty relation?

A. $\Pi_D(r_2) - \Pi_C(r_1)$

B. $\Pi_C(r_1) - \Pi_D(r_2)$

C. $\Pi_D(r_1 \bowtie_{C \neq D} r_2)$

D. $\Pi_C(r_1 \bowtie_{C=D} r_2)$

gatecse-2004 databases relational-calculus easy

Answer key

# 3.19.7 Relational Calculus: GATE CSE 2007 | Question: 60


Consider the relation employee(name, sex, supervisorName) with name as the key, supervisorName gives the name of the supervisor of the employee under consideration. What does the following Tuple Relational Calculus query produce?

$\{e.\ name \mid employee(e) \land (\forall x) [\neg employee(x) \lor x.\ supervisorName \neq e.\ name \lor x.\ sex = "male"]\}$

A. Names of employees with a male supervisor.  
B. Names of employees with no immediate male subordinates.  
C. Names of employees with no immediate female subordinates.  
D. Names of employees with a female supervisor.

gatecse-2007 databases relational-calculus normal

Answer key

# 3.19.8 Relational Calculus: GATE CSE 2008 | Question: 15


Which of the following tuple relational calculus expression(s) is/are equivalent to $\forall t\in r(P(t))$ ?

1. $\neg \exists t\in r(P(t))$  
II. $\exists t \notin r(P(t))$  
III. $\neg \exists t\in r(\neg P(t))$  
IV. ∃t∉r(¬P(t))

A. I only

B. II only

C. III only

D. III and IV only

gatecse-2008 databases relational-calculus normal

Answer key

# 3.19.9 Relational Calculus: GATE CSE 2009 | Question: 45


Let $R$ and $S$ be relational schemes such that $R = \{a, b, c\}$ and $S = \{c\}$ . Now consider the following queries on the database:

1. $\pi_{R - S}(r) - \pi_{R - S}\left(\pi_{R - S}(r)\times s - \pi_{R - S,S}(r)\right)$  
2. $\{t \mid t \in \pi_{R-S}(r) \land \forall u \in s (\exists v \in r (u = v[S] \land t = v[R-S]))\}$

3. $\{t \mid t \in \pi_{R-S}(r) \land \forall v \in r (\exists u \in s (u = v[S] \land t = v[R-S]))\}$

4. Select R.a,R.b
From R,S
Where R.c = S.c

Which of the above queries are equivalent?

A. 1 and 2

B. 1 and 3

C. 2 and 4

D. 3 and 4

gatecse-2009 databases relational-calculus difficult

# Answer key

# 3.19.10 Relational Calculus: GATE CSE 2013 | Question: 35

Consider the following relational schema.

• Students(rollno: integer, sname: string)  
- Courses(courseno: integer, cname: string)  
- Registration(rollno: integer, courseno: integer, percent: real)

Which of the following queries are equivalent to this query in English?

"Find the distinct names of all students who score more than $90\%$ in the course numbered 107"

I. SELECT DISTINCT S.sname FROM Students as S, Registration as R WHERE
R.rollno=S.rollno AND R.courseno=107 AND R.percent >90

II. $\prod_{sname}(\sigma_{courseno=107\wedge percent>90}\left(Registration\bowtie Students\right))$ III. $\{T \mid \exists S \in Students, \exists R \in Registration(S. rollno = R. rollno \land R. courseno = 107 \land R. percent > 90 \land T. sname = S. sname)\}$

IV. $\{\langle S_N\rangle \mid \exists S_R\exists R_P(\langle S_R,S_N\rangle \in Students\land$ $\langle S_R,107,R_P\rangle \in Registration\land R_P > 90)\}$

A. I, II, III and IV

B. I, II and III only

C. I, II and IV only

D. II, III and IV only

gatecse-2013 databases sql relational-calculus normal

# Answer key

# 3.19.11 Relational Calculus: GATE IT 2006 | Question: 15

Which of the following relational query languages have the same expressive power?

I. Relational algebra  
II. Tuple relational calculus restricted to safe expressions  
III. Domain relational calculus restricted to safe expressions

A. II and III only

B. I and II only

C. I and III only

D. I, II and III

gateit-2006 databases relational-algebra relational-calculus easy

# Answer key

# 3.19.12 Relational Calculus: GATE IT 2007 | Question: 65

Consider a selection of the form $\sigma_{A\leq 100}(r)$ , where $r$ is a relation with 1000 tuples. Assume that the attribute values for $A$ among the tuples are uniformly distributed in the interval [0, 500]. Which one of the following options is the best estimate of the number of tuples returned by the given selection query?

A. 50

B. 100

C. 150

D. 200

gateit-2007 databases relational-calculus probability normal

# Answer key




# 3.19.13 Relational Calculus: GATE IT 2008 | Question: 75

Consider the following relational schema:

- Student(school-id, sch-roll-no, sname, saddress)  
- School(school-id, sch-name, sch-address, sch-phone)  
- Enrolment(school-id, sch-roll-no, erollno, examname)  
- ExamResult(erollno, examname, marks)

Consider the following tuple relational calculus query.

$\{t \mid \exists E \in \text{Enrolment } t = E.\text{ school-id} \land |\{x \mid x \in \text{Enrolment} \land x.\text{ school-id} = t \land (\exists B \in \text{ExamResult } B.\text{ end})\}$ If a student needs to score more than 35 marks to pass an exam, what does the query return?

A. The empty set  
B. schools with more than 35% of its students enrolled in some exam or the other  
C. schools with a pass percentage above 35% over all exams taken together  
D. schools with a pass percentage above 35% over each exam

gateit-2008 databases relational-calculus normal

Answer key

# 3.20

# Relational Model (2)

# 3.20.1 Relational Model: GATE CSE 2023 | Question: 6

Which one of the options given below refers to the degree (or arity) of a relation in relational database systems?


A. Number of attributes of its relation schema.  
B. Number of tuples stored in the relation.  
C. Number of entries in the relation.  
D. Number of distinct domains of its relation schema.

gatecse-2023 databases relational-model one-mark easy

Answer key

# 3.20.2 Relational Model: GATE DA 2025 | Question: 46

Consider the following two relations, named Customer and Person, in a database:


```txt
Person (
aadhaar CHAR(12) PRIMARY KEY,
name VARCHAR(32));

Customer (
name VARCHAR (32),
email VARCHAR(32) PRIMARY KEY,
phone CHAR(10),
aadhaar CHAR(12),
    FOREIGN KEY (aadhaar) REFERENCES Person(aadhaar));
```

Which of the following statements is/are correct?

A. aadhaar is a candidate key in the Customer relation  
B. phone can be NULL in the Customer relation  
C. aadhaar is a candidate key in the Person relation  
D. aadhaar can be NULL in the Person relation

gateda-2025 databases relational-model multiple-selects two-marks

Answer key

# 3.21

# SQL (58)

# 3.21.1 SQL: GATE CSE 1988 | Question: 12iii

Describe the relational algebraic expression giving the relation returned by the following SQL query.


```sql
Select     SNAME
from     S
Where     SNOin
    (select    SNO
    from     SP
    where     PNOin
        (select    PNO
        from     P
        Where     COLOUR='BLUE'))
```

```txt
gate1988 normal descriptive databases sql
```

# Answer key

# 3.21.2 SQL: GATE CSE 1988 | Question: 12iv


```sql
Select     SNAME
from     S
Where     SNOin
    (select    SNO
    from     SP
    where     PNOin
        (select    PNO
        from     P
        Where     COLOUR='BLUE'))
```

What relations are being used in the above SQL query? Given at least two attributes of each of these relations.

```txt
gate1988 normal descriptive databases sql
```

# Answer key

# 3.21.3 SQL: GATE CSE 1990 | Question: 10-a

Consider the following relational database:


• employees (eno, ename, address, basic-salary)  
- projects (pno, pname, nos-of-staffs-allotted)  
- working (pno, eno, pjob)

The queries regarding data in the above database are formulated below in SQL. Describe in ENGLISH sentences the two queries that have been posted:

```sql
i. SELECT ename
FROM employees
WHERE eno IN
(SELECT eno
FROM working
GROUP BY eno
HAVING COUNT(*)=
(SELECT COUNT(*)
FROM projects))
```

```sql
ii. SELECT pname
FROM projects
WHERE pno IN
(SELECT pno
FROM projects
MINUS
SELECT DISTINCT pno
FROM working);
```

# 3.21.4 SQL: GATE CSE 1991 | Question: 12,b


Suppose a database consist of the following relations:

```prolog
SUPPLIER (SCODE, SNAME, CITY).
PART (PCODE, PNAME, PDESC, CITY).
PROJECTS (PRCODE, PRNAME, PRCITY).
SPPR (SCODE, PCODE, PRCODE, QTY).
```

Write algebraic solution to the following :

i. Get SCODE values for suppliers who supply to both projects PR1 and PR2.  
ii. Get PRCODE values for projects supplied by at least one supplier not in the same city.

```txt
sql gate1991 normal databases descriptive
```

# Answer key

# 3.21.5 SQL: GATE CSE 1991 | Question: 12-a

Suppose a database consist of the following relations:


```prolog
SUPPLIER (SCODE, SNAME, CITY).
PART (PCODE, PNAME, PDESC, CITY).
PROJECTS (PRCODE, PRNAME, PRCITY).
SPPR (SCODE, PCODE, PRCODE, QTY).
```

Write SQL programs corresponding to the following queries:

i. Print PCODE values for parts supplied to any project in DEHLI by a supplier in DELHI.  
ii. Print all triples <CITY, PCODE, CITY> such that a supplier in first city supplies the specified part to a project in the second city, but do not print the triples in which the two CITY values are same.

```txt
gate1991 databases sql normal descriptive
```

# Answer key

# 3.21.6 SQL: GATE CSE 1993 | Question: 24

The following relations are used to store data about students, courses, enrollment of students in courses and teachers of courses. Attributes for primary key in each relation are marked by ‘\*’.


- students(rollno\*, sname, saddr)  
- courses(cno\*, cname)  
- enroll(rollno\*,cno\*,grade)  
- teach(tno\*, tname, cao\*)

(cno is course number, cname is course name, tno is teacher number, tname is teacher name, sname is student name, etc.)

For the relational database given above, the following functional dependencies hold:

- rollno $\rightarrow$ sname, saddr  
- cno $\rightarrow$ cname  
- tno $\rightarrow$ tname  
- rollno, cno $\rightarrow$ grade

a. Is the database in $3^{rd}$ normal form (3NF)?  
b. If yes, prove that it is in 3NF. If not, normalize the relations so that they are in 3NF (without proving).

```txt
gate1993 databases sql normal descriptive database-normalization
```

# Answer key

# 3.21.7 SQL: GATE CSE 1998 | Question: 7-a

Suppose we have a database consisting of the following three relations.


- FREQUENTS (student, parlor) giving the parlors each student visits.  
- SERVES (parlor, ice-cream) indicating what kind of ice-creams each parlor serves.  
- LIKES (student, ice-cream) indicating what ice-creams each student likes.

(Assume that each student likes at least one ice-cream and frequents at least one parlor)

Express the following in SQL:

Print the students that frequent at least one parlor that serves some ice-cream that they like.

gate1998 databases sql descriptive

Answer key

# 3.21.8 SQL: GATE CSE 1999 | Question: 2.25

Which of the following is/are correct?


A. An SQL query automatically eliminates duplicates  
B. An SQL query will not work if there are no indexes on the relations  
C. SQL permits attribute names to be repeated in the same relation  
D. None of the above

gate1999 databases sql easy

Answer key

# 3.21.9 SQL: GATE CSE 1999 | Question: 22-a

Consider the set of relations


- EMP (Employee-no. Dept-no, Employee-name, Salary)  
- DEPT (Dept-no. Dept-name, Location)

Write an SQL query to:

a. Find all employees names who work in departments located at ‘Calcutta’ and whose salary is greater than Rs.50,000.  
b. Calculate, for each department number, the number of employees with a salary greater than Rs. 1,00,000.

gate1999 databases sql easy descriptive

Answer key

# 3.21.10 SQL: GATE CSE 1999 | Question: 22-b

Consider the set of relations


- EMP (Employee-no. Dept-no, Employee-name, Salary)  
- DEPT (Dept-no. Dept-name, Location)

Write an SQL query to:

Calculate, for each department number, the number of employees with a salary greater than Rs. 1,00,000

gate1999 databases sql descriptive easy

Answer key

# 3.21.11 SQL: GATE CSE 2000 | Question: 2.25

Given relations $r(w, x)$ and $s(y, z)$ the result of


select distinct w, x from r, s