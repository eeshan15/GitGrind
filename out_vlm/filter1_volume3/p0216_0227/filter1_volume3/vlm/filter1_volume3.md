A. 8,8

B. 120,8

C. 960,8

D. 960,120

gatecse-2004 databases easy joins natural-join

# Answer key

# 3.12.2 Joins: GATE CSE 2012 | Question: 50

Consider the following relations $A, B$ and $C$ :

<table><tr><td colspan="3">A</td></tr><tr><td>ID</td><td>Name</td><td>Age</td></tr><tr><td>12</td><td>Arun</td><td>60</td></tr><tr><td>15</td><td>Shreya</td><td>24</td></tr><tr><td>99</td><td>Rohit</td><td>11</td></tr></table>


How many tuples does the result of the following relational algebra expression contain? Assume that the schema of $A \cup B$ is the same as that of $A$ .

$$
(A \cup B) \bowtie_ {A. I d > 4 0 \lor C. I d <   1 5} C
$$

A. 7

B. 4

C. 5

D. 9

gatecse-2012 databases joins normal

# Answer key

# 3.12.3 Joins: GATE CSE 2014 | Set 2 | Question: 30

Consider a join (relation algebra) between relations $r(R)$ and $s(S)$ using the nested loop method. There are 3 buffers each of size equal to disk block size, out of which one buffer is reserved for intermediate results. Assuming $\text{size}(r(R)) < \text{size}(s(S))$ , the join will have fewer number of disk block accesses if


A. relation $r(R)$ is in the outer loop.  
B. relation $s(S)$ is in the outer loop.  
C. join selection factor between $r(R)$ and $s(S)$ is more than 0.5.  
D. join selection factor between $r(R)$ and $s(S)$ is less than 0.5.

gatecse-2014-set2 databases normal joins

# Answer key

# 3.12.4 Joins: GATE IT 2005 | Question: 82a

A database table $T_{1}$ has 2000 records and occupies 80 disk blocks. Another table $T_{2}$ has 400 records and occupies 20 disk blocks. These two tables have to be joined as per a specified join condition that needs to be evaluated for every pair of records from these two tables. The memory buffer space available can hold one block of records for $T_{1}$ and one block of records for $T_{2}$ simultaneously at any point in time. No information available on either table.


If Nested-loop join algorithm is employed to perform the join, with the most appropriate choice of table to be used in outer loop, the number of block accesses required for reading the data are

A. 800000

B. 40080

C. 32020

D. 100

gateit-2005 databases normal joins

# Answer key

# 3.12.5 Joins: GATE IT 2005 | Question: 82b

A database table $T_{1}$ has 2000 records and occupies 80 disk blocks. Another table $T_{2}$ has 400 records and occupies 20 disk blocks. These two tables have to be joined as per a specified join condition that needs to be evaluated for every pair of records from these two tables. The memory buffer space available can hold of


one block of records for $T_{1}$ and one block of records for $T_{2}$ simultaneously at any point in time. No index is available on either table.

If, instead of Nested-loop join, Block nested-loop join is used, again with the most appropriate choice of table in the outer loop, the reduction in number of block accesses required for reading the data will be

A. 0

B. 30400

C. 38400

D. 798400

gateit-2005 databases normal joins

# Answer key

# 3.12.6 Joins: GATE IT 2006 | Question: 14

Consider the relations $r_1(\mathrm{P}, \mathrm{Q}, \mathrm{R})$ and $r_2(\mathrm{R}, \mathrm{S}, \mathrm{T})$ with primary keys $\mathbf{P}$ and $\mathbf{R}$ respectively. The relation $r_1$ contains 2000 tuples and $r_2$ contains 2500 tuples. The maximum size of the join $r_1 \bowtie r_2$ is:


A. 2000

B. 2500

C. 4500

D. 5000

gateit-2006 databases joins natural-join normal

# Answer key

# 3.12.7 Joins: GATE IT 2007 | Question: 68

Consider the following relation schemas :


- b-Schema = (b-name, b-city, assets)  
- a-Schema = (a-num, b-name, bal)  
- d-Schema = (c-name, a-number)

Let branch, account and depositor be respectively instances of the above schemas. Assume that account and depositor relations are much bigger than the branch relation.

Consider the following query:

$\Pi_{\mathrm{c - name}}$ ( $\sigma_{\mathrm{b - city}} =$ "Agra" $\wedge$ bal $< 0$ (branch $\bowtie$ (account $\bowtie$ depositor)

Which one of the following queries is the most efficient version of the above query ?

A. $\Pi_{\mathrm{c - name}}$ ( $\sigma_{\mathrm{bal}} < 0$ ( $\sigma_{\mathrm{b - city}} =$ "Agra" branch $\bowtie$ account) $\bowtie$ depositor)  
B. $\Pi_{\mathrm{c - name}}$ ( $\sigma_{\mathrm{b - city}} =$ "Agra" branch $\bowtie$ ( $\sigma_{\mathrm{bal}} < 0$ account $\bowtie$ depositor))  
C. $\Pi_{\mathrm{c - name}}$ (( $\sigma_{\mathrm{b - city}} =$ "Agra" branch $\bowtie$ $\sigma_{\mathrm{b - city}} =$ "Agra" $\wedge$ bal $< 0$ account) $\bowtie$ depositor)  
D. $\Pi_{\mathrm{c - name}}$ ( $\sigma_{\mathrm{b - city} = "Agra"}$ branch $\bowtie$ ( $\sigma_{\mathrm{b - city} = "Agra"} \wedge \text{bal} < 0$ account $\bowtie$ depositor))

gateit-2007 databases joins relational-algebra normal

# Answer key

# 3.13

# Multivalued Dependency 4nf (1)

# 3.13.1 Multivalued Dependency 4nf: GATE IT 2007 | Question: 67

Consider the following implications relating to functional and multivalued dependencies given below, which may or may not be correct.


i. if $A \to \to B$ and $A \to \to C$ then $A \to BC$  
ii. if $A\to B$ and $A\to C$ then $A\to \rightarrow BC$  
iii. if $A\to \rightarrow BC$ and $A\to B$ then $A\to C$  
iv. if $A\to BC$ and $A\to B$ then $A\to \to C$

Exactly how many of the above implications are valid?

A. 0

B. 1

C. 2

D. 3

gateit-2007 databases database-normalization multivalued-dependency-4nf normal

# Answer key

# 3.14

# Natural Join (3)

# 3.14.1 Natural Join: GATE CSE 2005 | Question: 30


Let r be a relation instance with schema $R = (A, B, C, D)$ . We define $r_{1} = \pi_{A,B,C}(R)$ and $r_{2} = \pi_{A,D}(r)$ . Let $s = r_{1} * r_{2}$ where $*$ denotes natural join. Given that the decomposition of r into $r_{1}$ and $r_{2}$ is lossy, which one of the following is TRUE?

A. $s \subset r$

B. $r \cup s = r$

C. $r\subset s$

D. $r * s = s$

gatecse-2005 databases relational-algebra natural-join normal

# Answer key

# 3.14.2 Natural Join: GATE CSE 2010 | Question: 43

The following functional dependencies hold for relations $R(A, B, C)$ and $S(B, D, E)$ .


- $B \to A$  
• A → C

The relation $R$ contains 200 tuples and the relation $S$ contains 100 tuples. What is the maximum number of tuples possible in the natural join $R \bowtie S$ ?

A. 100

B. 200

C. 300

D. 2000

gatecse-2010 databases normal natural-join

# Answer key

# 3.14.3 Natural Join: GATE CSE 2015 | Set 2 | Question: 32


Consider two relations $R_{1}(A,B)$ with the tuples $(1,5),(3,7)$ and $R_{2}(A,C) = (1,7),(4,9)$ .

Assume that $R(A, B, C)$ is the full natural outer join of $R_1$ and $R_2$ . Consider the following tuples of the form $(A, B, C)$ :

$$
a = (1, 5, n u l l), b = (1, n u l l, 7), c = (3, n u l l, 9), d = (4, 7, n u l l), e = (1, 5, 7),
$$

$$
f = (3, 7, n u l l), g = (4, n u l l, 9).
$$

Which one of the following statements is correct?

A. R contains a, b, e, f, g but not c, d.

B. $R$ contains all $a, b, c, d, e, f, g$ .

C. R contains e, f, g but not a, b.

D. $R$ contains $e$ but not $f, g$ .

gatecse-2015-set2 databases normal natural-join

# Answer key

# 3.15

# Normal Forms (1)

# Practice Test: Test 1 (11Q)

# 3.15.1 Normal Forms: GATE DA 2026 | Question: 51


Consider an ER model with the entities E1 ( $A_{11}$ , $A_{12}$ , $A_{13}$ ) and E2 ( $A_{21}$ , $A_{22}$ , $A_{23}$ ), where, $A_{11}$ , $A_{12}$ , $A_{13}$ are the attributes of E1, and $A_{21}$ , $A_{22}$ , $A_{23}$ are the attributes of E2. Let $A_{22}$ be a multivalued attribute. $A_{11}$ and $A_{21}$ are the primary keys of E1 and E2, respectively.

Let R12 be a many-to-many relationship between E1 and E2. Participation of both E1 and E2 in R12 is total.

The minimum number of relations required to convert the ER model into relational model (assuming there is no other functional dependency) where each relation is in third normal form (3NF) is \_\_\_\_. (Answer in integer)

gateda-2026 databases er-diagram normal-forms numerical-answers two-marks

# Answer key

# 3.16

# Query (3)

Consider the following relational database schema:

- EMP (eno name, age)  
- PROJ (pno name)  
• INVOLVED (eno, pno)

EMP contains information about employees. PROJ about projects and involved about which employees involved in which projects. The underlined attributes are the primary keys for the respective relations.

State in English (in not more than 15 words)

What the following relational algebra expressions are designed to determine

i. $\Pi_{eno}(\text{INVOLVED}) - \Pi_{eno}((\Pi_{eno}(\text{INVOLVED}) \times \Pi_{pno}(\text{PROJ})) - \text{INVOLVED})$  
ii. $\Pi_{age}(\mathrm{EMP}) - \Pi_{age}(\sigma_{E.age < Emp.age}((\rho E(\mathrm{EMP})\times \mathrm{EMP}))$

(Note: $\rho E(\text{EMP})$ conceptually makes a copy of EMP and names it E ( $\rho$ is called the rename operator))

gate1997 databases sql descriptive normal relational-algebra query

Answer key

# 3.16.2 Query: GATE DA 2026 | Question: 41


Consider a table Employee(EmpID, TeamID), where the column EmpID (ID of an employee) is the primary key. The column TeamID denotes the team ID of the team of which the employee is a member. TeamID is a NOT NULL column.

We want to display the size of the team (denoted as TeamSize) in which each employee is a member by using SQL. As an example, the desired output for the given Employee table is also shown in tabular form.

Which of the following is/are correct?

Employee

<table><tr><td>EmpID</td><td>TeamID</td></tr><tr><td>1</td><td>8</td></tr><tr><td>2</td><td>8</td></tr><tr><td>3</td><td>8</td></tr><tr><td>4</td><td>7</td></tr><tr><td>5</td><td>7</td></tr><tr><td>6</td><td>9</td></tr></table>

Output

<table><tr><td>EmpID</td><td>TeamSize</td></tr><tr><td>1</td><td>3</td></tr><tr><td>2</td><td>3</td></tr><tr><td>3</td><td>3</td></tr><tr><td>4</td><td>2</td></tr><tr><td>5</td><td>2</td></tr><tr><td>6</td><td>1</td></tr></table>

A.

SELECT E. EmpID, B. TeamSize  
FROM Employee AS E, (SELECT TeamID, COUNT(TeamID) AS  
TeamSize FROM Employee GROUP BY TeamID) AS B  
WHERE E.TeamID = B.TeamID

B. SELECT A. EmpID, COUNT(B.TeamID) AS TeamSize
FROM Employee AS A, Employee AS B
WHERE A.TeamID = B.TeamID AND A. EmpID = B. EmpID
GROUP BY A. EmpID  
C. SELECT B. EmpID, B. TeamSize
FROM (SELECT EmpID, COUNT(TeamID) AS TeamSize
FROM Employee GROUP BY EmpID) AS B  
D.
SELECT A.EmplD, B.TeamSize
FROM Employee AS A, (SELECT COUNT(TeamID) AS TeamSize FROM Employee GROUP BY TeamID) AS B
WHERE A.TeamID = B.TeamID

gateda-2026 databases sql query multiple-selects two-marks

Answer key

# 3.16.3 Query: GATE DA 2026 | Question: 50

Let Account be a relation as shown.


Account

<table><tr><td>AccNo</td><td>Balance</td></tr><tr><td>A1</td><td>5000</td></tr><tr><td>A2</td><td>5000</td></tr><tr><td>A3</td><td>10000</td></tr><tr><td>A4</td><td>15000</td></tr><tr><td>A5</td><td>18000</td></tr></table>

Consider the given SQL query.

SELECT AccNo FROM Account AS A

WHERE (SELECT COUNT(\*) FROM Account AS B

WHERE A.Balance < B.Balance) >= (SELECT COUNT(\*)

FROM Account AS C WHERE A.Balance > C.Balance)

The number of rows returned by the SQL query is \_\_\_\_. (Answer in integer)

gateda-2026 databases sql query numerical-answers two-marks

Answer key

# 3.17

# Referential Integrity (6)

Practice Test: Test 1 (7Q)

# 3.17.1 Referential Integrity: GATE CSE 1997 | Question: 6.10, ISRO2016-54

Let $R(a, b, c)$ and $S(d, e, f)$ be two relations in which $d$ is the foreign key of $S$ that refers to the primary key of $R$ . Consider the following four operations $R$ and $S$

I. Insert into R  
II. Insert into S  
III. Delete from R  
IV. Delete from S

Which of the following can cause violation of the referential integrity constraint above?

A. Both I and IV

B. Both II and III

C. All of these

D. None of these

gate1997 databases referential-integrity easy isro2016

Answer key


The following table has two attributes $A$ and $C$ where $A$ is the primary key and $C$ is the foreign key referencing $A$ with on-delete cascade.

<table><tr><td>A</td><td>C</td></tr><tr><td>2</td><td>4</td></tr><tr><td>3</td><td>4</td></tr><tr><td>4</td><td>3</td></tr><tr><td>5</td><td>2</td></tr><tr><td>7</td><td>2</td></tr><tr><td>9</td><td>5</td></tr><tr><td>6</td><td>4</td></tr></table>

The set of all tuples that must be additionally deleted to preserve referential integrity when the tuple $(2, 4)$ is deleted is:

A. (3,4) and (6,4)

B. (5,2) and (7,2)

C. $(5,2)$ , $(7,2)$ and $(9,5)$

D. (3,4), (4,3) and (6,4)

gatecse-2005 databases referential-integrity normal

# Answer key

# 3.17.3 Referential Integrity: GATE CSE 2012 | Question: 43

Suppose $R_{1}(\underline{A}, B)$ and $R_{2}(\underline{C}, D)$ are two relation schemas. Let $r_{1}$ and $r_{2}$ be the corresponding relation instances. B is a foreign key that refers to C in $R_{2}$ . If data in $r_{1}$ and $r_{2}$ satisfy referential integrity constraints, which of the following is ALWAYS TRUE?

A. $\prod_{B}(r_{1}) - \prod_{C}(r_{2}) = \varnothing$  
B. $\prod_{C}(r_{2})-\prod_{B}(r_{1})=\varnothing$  
C. $\prod_B(r_1) = \prod_C(r_2)$  
D. $\prod_{B}(r_{1})-\prod_{C}(r_{2})\neq\varnothing$

gatecse-2012 databases relational-algebra normal referential-integrity

# Answer key

# 3.17.4 Referential Integrity: GATE CSE 2017 | Set 2 | Question: 19

Consider the following tables T1 and T2.

<table><tr><td>P</td><td>Q</td></tr><tr><td>2</td><td>2</td></tr><tr><td>3</td><td>8</td></tr><tr><td>7</td><td>3</td></tr><tr><td>5</td><td>8</td></tr><tr><td>6</td><td>9</td></tr><tr><td>8</td><td>5</td></tr><tr><td>9</td><td>8</td></tr></table>

<table><tr><td>R</td><td>S</td></tr><tr><td>2</td><td>2</td></tr><tr><td>8</td><td>3</td></tr><tr><td>3</td><td>2</td></tr><tr><td>9</td><td>7</td></tr><tr><td>5</td><td>7</td></tr><tr><td>7</td><td>2</td></tr></table>



In table $T1$ P is the primary key and Q is the foreign key referencing R in table $T2$ with on-delete cascade and on-update cascade. In table $T2$ , R is the primary key and S is the foreign key referencing P in table $T1$ with on-delete set NULL and on-update cascade. In order to delete record $\langle 3,8 \rangle$ from the table $T1$ , the number of additional records that need to be deleted from table $T1$ is \_\_\_\_

# 3.17.5 Referential Integrity: GATE CSE 2021 | Set 2 | Question: 6

Consider the following statements S1 and S2 about the relational data model:


- S1: A relation scheme can have at most one foreign key.  
- S2: A foreign key in a relation scheme $R$ cannot be used to refer to tuples of $R$ .

Which one of the following choices is correct?

A. Both $S1$ and $S2$ are true  
C. $S1$ is false and $S2$ is true  
gatecse-2021-set2 databases referential-integrity one-mark

B. $S1$ is true and $S2$ is false  
D. Both $S1$ and $S2$ are false

# Answer key

# 3.17.6 Referential Integrity: GATE DA 2026 | Question: 16


Consider two relations $r$ and $s$ defined on the relational schemas $R(A, B)$ and $S(E, C)$ , respectively. $A$ is the primary key of $R$ and $E$ is a foreign key of $S$ referencing $A$ in $R$ .

Which of the following operations will NEVER violate the foreign key constraint?

A. Inserting records into relation r  
C. Deleting records from relation r  
gateda-2026 databases referential-integrity multiple-selects one-mark

B. Deleting records from relation s  
D. Inserting records into relation s

# Answer key

# 3.18

# Relational Algebra (33)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (15Q)

Test 4 (3Q)

# 3.18.1 Relational Algebra: GATE CSE 1992 | Question: 13b

Suppose we have a database consisting of the following three relations:


<table><tr><td>FREQUENTS</td><td>(CUSTOMER, HOTEL)</td></tr><tr><td>SERVES</td><td>(HOTEL, SNACKS)</td></tr><tr><td>LIKES</td><td>(CUSTOMER, SNACKS)</td></tr></table>

The first indicates the hotels each customer visits, the second tells which snacks each hotel serves and last indicates which snacks are liked by each customer. Express the following query in relational algebra:

Print the hotels the serve the snack that customer Rama likes.

gate1992 databases relational-algebra normal descriptive

# Answer key

# 3.18.2 Relational Algebra: GATE CSE 1994 | Question: 13

Consider the following relational schema:


• COURSES (cno, cname)  
• STUDENTS (rollno, sname, age, year)  
- REGISTERED\_FOR (cno, rollno)

The underlined attributes indicate the primary keys for the relations. The ‘year’ attribute for the STUDENTS relation indicates the year in which the student is currently studying (First year, Second year etc.)

A. Write a relational algebra query to print the roll number of students who have registered for cno 322.  
B. Write a SQL query to print the age and year of the youngest student in each year.


# 3.18.3 Relational Algebra: GATE CSE 1994 | Question: 3.8


Give a relational algebra expression using only the minimum number of operators from $(\cup, -)$ which is equivalent to $R \cap S$ .

gate1994 databases relational-algebra normal descriptive

Answer key

# 3.18.4 Relational Algebra: GATE CSE 1995 | Question: 27


Consider the relation scheme.

<table><tr><td>AUTHOR</td><td>(ANAME, INSTITUTION, ACITY, AGE)</td></tr><tr><td>PUBLISHER</td><td>(PNAME, PCITY)</td></tr><tr><td>BOOK</td><td>(TITLE, ANAME, PNAME)</td></tr></table>

Express the following queries using (one or more of) SELECT, PROJECT, JOIN and DIVIDE operations.

A. Get the names of all publishers.  
B. Get values of all attributes of all authors who have published a book for the publisher with PNAME='TECHNICAL PUBLISHERS'.  
C. Get the names of all authors who have published a book for any publisher located in Madras

gate1995 databases relational-algebra normal descriptive

Answer key

# 3.18.5 Relational Algebra: GATE CSE 1996 | Question: 27


A library relational database system uses the following schema

- USERS (User#, User Name, Home Town)  
• BOOKS (Book#, Book Title, Author Name)  
• ISSUED (Book#, User#, Date)

Explain in one English sentence, what each of the following relational algebra queries is designed to determine

a. $\sigma_{\mathrm{User\# = 6}}$ ( $\pi_{\mathrm{User\# , Book Title}}$ ((USERS $\bowtie$ ISSUED) $\bowtie$ BOOKS))  
b. $\pi_{\text{Author Name}}$ (BOOKS $\bowtie$ $\sigma_{\text{Home Town=Delhi}}$ (USERS $\bowtie$ ISSUED))

gate1996 databases relational-algebra descriptive

Answer key

# 3.18.6 Relational Algebra: GATE CSE 1997 | Question: 76-a


Consider the following relational database schema:

- EMP (eno name, age)  
- PROJ (pno name)  
- INVOLVED (eno, pno)

EMP contains information about employees. PROJ about projects and involved about which employees involved in which projects. The underlined attributes are the primary keys for the respective relations.

What is the relational algebra expression containing one or more of $\{\sigma,\pi,\times,\rho,-\}$ which is equivalent to SQL query.

select eno from EMP|INVOLVED where EMP.eno=INVOLVED.eno and INVOLVED.pno=3

# Answer key

# 3.18.7 Relational Algebra: GATE CSE 1998 | Question: 1.33

Given two union compatible relations $R_{1}(A,B)$ and $R_{2}(C,D)$ , what is the result of the operation $R_{1} \bowtie_{A = C \wedge B = D} R_{2}$ ?


A. $R_{1} \cup R_{2}$

B. $R_{1} \times R_{2}$

C. $R_{1}-R_{2}$

D. $R_{1} \cap R_{2}$

gate1998 normal relational-algebra

# Answer key

# 3.18.8 Relational Algebra: GATE CSE 1998 | Question: 27

Consider the following relational database schemes:


• COURSES (Cno, Name)  
- PRE\_REQ(Cno, Pre\_Cno)  
• COMPLETED (Student\_no, Cno)

COURSES gives the number and name of all the available courses.

PRE\_REQ gives the information about which courses are pre-requisites for a given course.

COMPLETED indicates what courses have been completed by students

Express the following using relational algebra:

List all the courses for which a student with Student\_no 2310 has completed all the pre-requisites.

gate1998 databases relational-algebra normal descriptive

# Answer key

# 3.18.9 Relational Algebra: GATE CSE 1999 | Question: 1.18, ISRO2016-53


Consider the join of a relation R with a relation S. If R has m tuples and S has n tuples then the maximum and minimum sizes of the join respectively are

A. $m + n$ and 0  
B. mn and 0  
C. $m + n$ and $|m - n|$  
D. mn and $m + n$

gate1999 databases relational-algebra easy isro2016

# Answer key

# 3.18.10 Relational Algebra: GATE CSE 2000 | Question: 1.23, ISRO2016-57


Given the relations

- employee (name, salary, dept-no), and  
- department (dept-no, dept-name, address),

Which of the following queries cannot be expressed using the basic relational algebra operations $(\sigma,\pi,\times,\bowtie,\cup,\cap,-)$ ?

A. Department address of every employee  
B. Employees whose name is the same as their department name  
C. The sum of all employees' salaries  
D. All employees of a given department

# Answer key

# 3.18.11 Relational Algebra: GATE CSE 2001 | Question: 1.24


Suppose the adjacency relation of vertices in a graph is represented in a table $\operatorname{Adj}(X, Y)$ . Which of the following queries cannot be expressed by a relational algebra expression of constant length?

A. List all vertices adjacent to a given vertex  
B. List all vertices which have self loops  
C. List all vertices which belong to cycles of less than three vertices  
D. List all vertices reachable from a given vertex

gatecse-2001 databases relational-algebra normal

Answer key

# 3.18.12 Relational Algebra: GATE CSE 2001 | Question: 1.25

Let $r$ and $s$ be two relations over the relation schemes $R$ and $S$ respectively, and let $A$ be an attribute in $R$ . The relational algebra expression $\sigma_{A = a}(r \bowtie s)$ is always equal to


A. $\sigma_{A=a}(r)$  
C. $\sigma_{A = a}(r) \bowtie s$  
gatecse-2001 databases relational-algebra

B. r  
D. None of the above

Answer key

# 3.18.13 Relational Algebra: GATE CSE 2001 | Question: 21-a

Consider a relation examinee (regno, name, score), where regno is the primary key to score is a real number.


Write a relational algebra using $(\Pi, \sigma, \rho, \times)$ to find the list of names which appear more than once in examinee.

gatecse-2001 databases normal descriptive relational-algebra

Answer key

# 3.18.14 Relational Algebra: GATE CSE 2002 | Question: 15

A university placement center maintains a relational database of companies that interview students on campus and make job offers to those successful in the interview. The schema of the database is given below:


<table><tr><td>COMPANY(cname, clocation)</td><td>STUDENT(srollno, sname, sdegree)</td></tr><tr><td>INTERVIEW(cname, srollno, idate)</td><td>OFFER(cname, srollno, osalary)</td></tr></table>

The COMPANY relation gives the name and location of the company. The STUDENT relation gives the student's roll number, name and the degree program for which the student is registered in the university. The INTERVIEW relation gives the date on which a student is interviewed by a company. The OFFER relation gives the salary offered to a student who is successful in a company's interview. The key for each relation is indicated by the underlined attributes

a. Write a relational algebra expressions (using only the operators $\bowtie$ , $\sigma$ , $\pi$ , $\cup$ , —) for the following queries.

i. List the rollnumbers and names of students who attended at least one interview but did not receive any job offer.  
ii. List the rollnumbers and names of students who went for interviews and received job offers from every company with which they interviewed.

b. Write an SQL query to list, for each degree program in which more than five students were offered jobs, the name of the degree and the average offered salary of students in this degree program.

gatecse-2002 databases normal descriptive relational-algebra sql

Answer key

# 3.18.15 Relational Algebra: GATE CSE 2003 | Question: 30


Consider the following SQL query

Select distinct $a_{1}, a_{2}, \ldots, a_{n}$

from $r_1, r_2, \ldots, r_m$

where P

For an arbitrary predicate P, this query is equivalent to which of the following relational algebra expressions?

A. $\Pi_{a_{1},a_{2},\ldots,a_{n}}\sigma_{p}\left(r_{1}\times r_{2}\times\cdots\times r_{m}\right)$  
B. $\Pi_{a_1, a_2, \ldots, a_n} \sigma_p(r_1 \bowtie r_2 \bowtie \cdots \bowtie r_m)$  
C. $\Pi_{a_1, a_2, \ldots, a_n} \sigma_p(r_1 \cup r_2 \cup \dots \cup r_m)$  
D. $\Pi_{a_1, a_2, \ldots, a_n} \sigma_p(r_1 \cap r_2 \cap \dots \cap r_m)$

gatecse-2003 databases relational-algebra normal

Answer key

# 3.18.16 Relational Algebra: GATE CSE 2004 | Question: 51


Consider the relation Student (name, sex, marks), where the primary key is shown underlined, pertaining to students in a class that has at least one boy and one girl. What does the following relational algebra expression produce? (Note: $\rho$ is the rename operator).

$\pi_{name}\left\{\sigma_{sex=female}\left(\text{Student}\right)\right\}-\pi_{name}\left(\text{Student}\bowtie_{(sex=female\wedge x=male\wedge marks\leq m)}\rho_{n,x,m}\left(\text{Student}\right)\right)$

A. names of girl students with the highest marks  
B. names of girl students with more marks than some boy student  
C. names of girl students with marks not less than some boy student  
D. names of girl students with more marks than all the boy students

gatecse-2004 databases relational-algebra normal

Answer key

# 3.18.17 Relational Algebra: GATE CSE 2007 | Question: 59


Information about a collection of students is given by the relation studInfo(studId, name, sex). The relation enroll(studId, coursework) gives which student has enrolled for (or taken) what course(s). Assume that every course is taken by at least one male and at least one female student. What does the following relational algebra expression represent?

$\pi_{\text{courseId}}\left(\left(\pi_{\text{studId}}\left(\sigma_{\text{sex} = ' \text{female'}}\right.\right.\right.\left.\left.\left(\text{studInfo}\right)\right)\times \pi_{\text{courseId}}\left(\text{enroll}\right)\right) - \text{enroll}$

A. Courses in which all the female students are enrolled.  
B. Courses in which a proper subset of female students are enrolled.  
C. Courses in which only male students are enrolled.  
D. None of the above

gatecse-2007 databases relational-algebra normal

Answer key

# 3.18.18 Relational Algebra: GATE CSE 2008 | Question: 68


Let R and S be two relations with the following schema

$$
R (P, Q, R 1, R 2, R 3)
$$

$$
S (P, Q, S 1, S 2)
$$

where $\{P,Q\}$ is the key for both schemas. Which of the following queries are equivalent?

1. $\Pi_P(R \bowtie S)$  
II. $\Pi_P(R) \bowtie \Pi_P(S)$

III. $\Pi_{P}\left(\Pi_{P,Q}\left(R\right)\cap\Pi_{P,Q}\left(S\right)\right)$  
IV. $\Pi_P(\Pi_{P,Q}(R) - (\Pi_{P,Q}(R) - \Pi_{P,Q}(S)))$

A. Only I and II

B. Only I and III

C. Only I, II and III

D. Only I, III and IV

gatecse-2008 databases relational-algebra normal

Answer key

# 3.18.19 Relational Algebra: GATE CSE 2014 | Set 3 | Question: 21

What is the optimized version of the relation algebra expression $\pi_{A1}(\pi_{A2}(\sigma_{F1}(\sigma_{F2}(r))))$ , where $A1, A2$ are sets of attributes in $r$ with $A1 \subset A2$ and $F1, F2$ are Boolean expressions based on the attributes in $r$ ?


A. $\pi_{A1}(\sigma_{(F1\land F2)}(r))$  
C. $\pi_{A2}\big(\sigma_{(F1\land F2)}(r)\big)$

gatecse-2014-set3 databases relational-algebra easy

B. $\pi_{A1}(\sigma_{(F1 \lor F2)}(r))$  
D. $\pi_{A2}\big(\sigma_{(F1\lor F2)}(r)\big)$

Answer key

# 3.18.20 Relational Algebra: GATE CSE 2014 | Set 3 | Question: 30

Consider the relational schema given below, where eld of the relation dependent is a foreign key referring to empld of the relation employee. Assume that every employee has at least one associated dependent in the dependent relation.


- employee (empld, empName, empAge)  
- dependent (depld, eld, depName, depAge)

Consider the following relational algebra query:

$$
\Pi_ {e m p I d} (e m p l o y e e) - \Pi_ {e m p I d} (e m p l o y e e \bowtie_ {(e m p I d = e I D) \wedge (e m p A g e \leq d e p A g e)} d e p e n d e n t)
$$

The above query evaluates to the set of emplds of employees whose age is greater than that of

A. some dependent.  
C. some of his/her dependents.

gatecse-2014-set3 databases relational-algebra normal

B. all dependents.  
D. all of his/her dependents.

Answer key

# 3.18.21 Relational Algebra: GATE CSE 2015 | Set 1 | Question: 7

SELECT operation in SQL is equivalent to


A. The selection operation in relational algebra  
B. The selection operation in relational algebra, except that SELECT in SQL retains duplicates  
C. The projection operation in relational algebra  
D. The projection operation in relational algebra, except that SELECT in SQL retains duplicates

gatecse-2015-set1 databases sql relational-algebra easy

Answer key

# 3.18.22 Relational Algebra: GATE CSE 2017 | Set 1 | Question: 46

Consider a database that has the relation schema CR(StudentName, CourseName). An instance of the schema CR is as given below.

