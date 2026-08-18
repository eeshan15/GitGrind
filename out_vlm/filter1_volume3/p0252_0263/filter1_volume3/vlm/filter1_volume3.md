# 3.21.43 SQL: GATE CSE 2021 | Set 1 | Question: 23

A relation $r(A, B)$ in a relational database has 1200 tuples. The attribute A has integer values ranging from 6 to 20, and the attribute B has integer values ranging from 1 to 20. Assume that the attributes A and B are independently distributed.


The estimated number of tuples in the output of $\sigma_{(A>10)\vee(B=18)}(r)$ is \_\_\_\_.

gatecse-2021-set1 databases sql numerical-answers one-mark

# Answer key

# 3.21.44 SQL: GATE CSE 2021 | Set 2 | Question: 31

The relation scheme given below is used to store information about the employees of a company, where empld is the key and deptId indicates the department to which the employee is assigned. Each employee is assigned to exactly one department.


emp(empId, name, gender, salary, deptId)

Consider the following SQL query:

```sql
select deptId, count(*)
from emp
where gender = "female" and salary > (select avg(salary)from emp)
group by deptId;
```

The above query gives, for each department in the company, the number of female employees whose salary is greater than the average salary of

A. employees in the department  
C. female employees in the department

B. employees in the company

D. female employees in the company

gatecse-2021-set2 databases sql easy two-marks

# Answer key

# 3.21.45 SQL: GATE CSE 2022 | Question: 46

Consider the relational database with the following four schemas and their respective instances.

- Student(sNo, sName, dNo) Dept(dNo, dName)  
- Course(cNo, cName, dNo) Register(sNo, cNo)

<table><tr><td></td><td>Students</td><td></td></tr><tr><td>sNo</td><td>sName</td><td>dNo</td></tr><tr><td>S01</td><td>James</td><td>D01</td></tr><tr><td>S02</td><td>Rocky</td><td>D01</td></tr><tr><td>S03</td><td>Jackson</td><td>D02</td></tr><tr><td>S04</td><td>Jane</td><td>D01</td></tr><tr><td>S05</td><td>Milli</td><td>D02</td></tr></table>

<table><tr><td></td><td>Depth</td></tr><tr><td>dNo</td><td>dName</td></tr><tr><td>D01</td><td>CSE</td></tr><tr><td>D02</td><td>EEE</td></tr></table>

<table><tr><td></td><td>Course</td><td></td></tr><tr><td>cNo</td><td>cName</td><td>dNo</td></tr><tr><td>C11</td><td>DS</td><td>D01</td></tr><tr><td>C12</td><td>OS</td><td>D01</td></tr><tr><td>C21</td><td>DE</td><td>D02</td></tr><tr><td>C22</td><td>PT</td><td>D02</td></tr><tr><td>C23</td><td>CV</td><td>D03</td></tr></table>

<table><tr><td></td><td>Register</td></tr><tr><td>sNo</td><td>cNo</td></tr><tr><td>S01</td><td>C11</td></tr><tr><td>S01</td><td>C12</td></tr><tr><td>S02</td><td>C11</td></tr><tr><td>S03</td><td>C21</td></tr><tr><td>S03</td><td>C22</td></tr><tr><td>S03</td><td>C23</td></tr><tr><td>S04</td><td>C11</td></tr><tr><td>S04</td><td>C12</td></tr><tr><td>S05</td><td>C11</td></tr><tr><td>S05</td><td>C21</td></tr></table>


SELECT \* FROM Student AS S WHERE NOT EXIST

(SELECT cNo FROM Course WHERE dNo = "D01"

EXCEPT

SELECT cNo FROM Register WHERE sNo = S.sNo)

The number of rows returned by the above SQL query is \_\_\_\_.

gatecse-2022 numerical-answers databases sql two-marks

# Answer key

# 3.21.46 SQL: GATE CSE 2023 | Question: 51

Consider the following table named Student in a relational database. The primary key of this table is rollNum.


Student

<table><tr><td>rollNum</td><td>name</td><td>gender</td><td>marks</td></tr><tr><td>1</td><td>Naman</td><td>M</td><td>62</td></tr><tr><td>2</td><td>Aliya</td><td>F</td><td>70</td></tr><tr><td>3</td><td>Aliya</td><td>F</td><td>80</td></tr><tr><td>4</td><td>James</td><td>M</td><td>82</td></tr><tr><td>5</td><td>Swati</td><td>F</td><td>65</td></tr></table>

The SQL query below is executed on this database.

SELECT \*

FROM Student

WHERE gender = 'F' AND

marks > 65;

The number of rows returned by the query is \_\_\_\_.

gatecse-2023 databases sql numerical-answers two-marks easy

# Answer key

# 3.21.47 SQL: GATE CSE 2025 | Set 1 | Question: 45

Consider the following database tables of a sports league.


player (pid, pname, age) team(tid, lname, city, cid)

coach (cid, cname) members (pid,tid)

An instance of the table and an SQL query are given.

player

<table><tr><td>pid</td><td>pname</td><td>age</td></tr><tr><td>1</td><td>Jasprit</td><td>31</td></tr><tr><td>2</td><td>Atharva</td><td>24</td></tr><tr><td>3</td><td>Ishan</td><td>26</td></tr><tr><td>4</td><td>Axar</td><td>30</td></tr></table>

coach

<table><tr><td>cid</td><td>cname</td></tr><tr><td>101</td><td>Ricky</td></tr><tr><td>102</td><td>Mark</td></tr><tr><td>103</td><td>Trevor</td></tr></table>

team

<table><tr><td>tid</td><td>tname</td><td>city</td><td>cid</td></tr><tr><td>10</td><td>MI</td><td>Mumbai</td><td>102</td></tr><tr><td>20</td><td>DC</td><td>Delhi</td><td>101</td></tr><tr><td>30</td><td>PK</td><td>Mohali</td><td>103</td></tr></table>

members

<table><tr><td>pid</td><td>tid</td></tr><tr><td>1</td><td>10</td></tr><tr><td>2</td><td>30</td></tr><tr><td>3</td><td>10</td></tr><tr><td>4</td><td>20</td></tr></table>

SELECT MIN (P.age)

FROM player P

WHERE P.pid IN (

SELECT M.pid

FROM team T, coach C, members M

WHERE C.cname = 'Mark'

AND T.cid = C.cid

AND M.tid = T.tid

)

The value returned by the given SQL query is \_\_\_\_. (Answer in integer)

# 3.21.48 SQL: GATE CSE 2025 | Set 2 | Question: 44

Consider the following relational schema:

Students (rollno: integer, name: string, age: integer, cgpa: real)

Courses (courseno: integer, cname: string, credits: integer)

Enrolled (rollno: integer, courseno: integer, grade: string)

Which of the following options is/are correct SQL query/queries to retrieve the names of the students enrolled in course number (i.e., courseno) 1470?

A. SELECT S.name

FROM Students S

WHERE EXISTS (SELECT \* FROM Enrolled E

WHERE E.courseno = 1470

AND E.rollno = S.rollno);

B. SELECT S.name

FROM Students S

WHERE SIZEOF (SELECT \* FROM Enrolled E

WHERE E.courseno = 1470

AND E.rollno = S.rollno) > 0;

C. SELECT S.name

FROM Students S

WHERE 0 < (SELECT COUNT(\*)

FROM Enrolled E

WHERE E.courseno = 1470

AND E.rollno = S.rollno);

D. SELECT S.name

FROM Students S NATURAL JOIN Enrolled E

WHERE E.courseno = 1470;

gatecse2025-set2 databases sql multiple-selects two-marks

# Answer key

# 3.21.49 SQL: GATE DA 2025 | Question: 23

On a relation named Loan of a bank:

<table><tr><td colspan="3">Loan</td></tr><tr><td>loan_number</td><td>branch_name</td><td>amount</td></tr><tr><td>L11</td><td>Banjara Hills</td><td>90000</td></tr><tr><td>L14</td><td>Kondapur</td><td>50000</td></tr><tr><td>L15</td><td>SR Nagar</td><td>40000</td></tr><tr><td>L22</td><td>SR Nagar</td><td>25000</td></tr><tr><td>L23</td><td>Balanagar</td><td>80000</td></tr><tr><td>L25</td><td>Kondapur</td><td>70000</td></tr><tr><td>L19</td><td>SR Nagar</td><td>65000</td></tr></table>



the following SQL query is executed.

SELECT L1.loan\_number

FROM Loan L1

WHERE L1.amount > (SELECT MAX (L2.amount)

FROM Loan L2

WHERE L2.branch\_name = 'SR Nagar');

The number of rows returned by the query is \_\_\_\_ (Answer in integer).

# 3.21.50 SQL: GATE DS&AI 2024 | Question: 21

Consider the following two tables named Raider and Team in a relational database maintained by a Kabaddi league. The attribute ID in table Team references the primary key of the Raider table, ID.


<table><tr><td colspan="4">Raider</td></tr><tr><td>ID</td><td>Name</td><td>Raids</td><td>Raidpoints</td></tr><tr><td>1</td><td>Arjun</td><td>200</td><td>250</td></tr><tr><td>2</td><td>Ankush</td><td>190</td><td>219</td></tr><tr><td>3</td><td>Sunil</td><td>150</td><td>200</td></tr><tr><td>4</td><td>Reza</td><td>150</td><td>190</td></tr><tr><td>5</td><td>Pratham</td><td>175</td><td>220</td></tr><tr><td>6</td><td>Gopal</td><td>193</td><td>215</td></tr></table>

<table><tr><td colspan="3">Team</td></tr><tr><td>City</td><td>ID</td><td>BidPoints</td></tr><tr><td>Jaipur</td><td>2</td><td>200</td></tr><tr><td>Patna</td><td>3</td><td>195</td></tr><tr><td>Hyderabad</td><td>5</td><td>175</td></tr><tr><td>Jaipur</td><td>1</td><td>250</td></tr><tr><td>Patna</td><td>4</td><td>200</td></tr><tr><td>Jaipur</td><td>6</td><td>200</td></tr></table>

The SQL query described below is executed on this database:

SELECT \*

FROM Raider, Team

WHERE Raider.ID=Team.ID AND City="Jaipur" AND

RaidPoints > 200;

The number of rows returned by this query is \_\_\_\_.

gate-ds-ai-2024 numerical-answers databases sql one-mark

# Answer key

# 3.21.51 SQL: GATE DS&AI 2024 | Question: 45

An OTT company is maintaining a large disk-based relational database of different movies with the following schema:

Movie (ID, CustomerRating)

Genre (ID, Name)

Movie\_Genre (MovieID, GenreID)

Consider the following SQL query on the relation database above:

SELECT \*

FROM Movie, Genre, Movie\_Genre

WHERE

Movie.CustomerRating > 3.4 AND

Genre.Name = "Comedy" AND

Movie\_Genre.MovieID = Movie.ID AND

Movie\_Genre.GenreID = Genre.ID;

This SQL query can be sped up using which of the following indexing options?

A. $B^{+}$ tree on all the attributes.  
B. Hash index on Genre.Name and $B^{+}$ tree on the remaining attributes.  
C. Hash index on Movie.CustomerRating and $B^{+}$ tree on the remaining attributes.  
D. Hash index on all the attributes.


A relational database contains two tables student and department in which student table has columns roll\_no, name and dept\_id and department table has columns dept\_id and dept\_name. The following insert statements were executed successfully to populate the empty tables:

```sql
Insert into department values (1, 'Mathematics')
Insert into department values (2, 'Physics')
Insert into student values (I, 'Navin', 1)
Insert into student values (2, 'Mukesh', 2)
Insert into student values (3, 'Gita', 1)
```

How many rows and columns will be retrieved by the following SQL statement?

```sql
Select * from student, department
```

A. 0 row and 4 columns  
C. 3 rows and 5 columns

gateit-2004 databases sql normal

B. 3 rows and 4 columns  
D. 6 rows and 5 columns

# Answer key

# 3.21.53 SQL: GATE IT 2004 | Question: 76

A table T1 in a relational database has the following rows and columns:


<table><tr><td>Roll no.</td><td>Marks</td></tr><tr><td>1</td><td>10</td></tr><tr><td>2</td><td>20</td></tr><tr><td>3</td><td>30</td></tr><tr><td>4</td><td>NULL</td></tr></table>

The following sequence of SQL statements was successfully executed on table T1.

```txt
Update T1 set marks = marks + 5
Select avg(marks) from T1
```

What is the output of the select statement?

A. 18.75

B. 20

C. 25

D. Null

gateit-2004 databases sql normal

# Answer key

# 3.21.54 SQL: GATE IT 2004 | Question: 78

Consider two tables in a relational database with columns and rows as follows:

Table: Student

<table><tr><td>Roll_no</td><td>Name</td><td>Dept_id</td></tr><tr><td>1</td><td>ABC</td><td>1</td></tr><tr><td>2</td><td>DEF</td><td>1</td></tr><tr><td>3</td><td>GHI</td><td>2</td></tr><tr><td>4</td><td>JKL</td><td>3</td></tr></table>

Table: Department

<table><tr><td>Dept_id</td><td>Dept_name</td></tr><tr><td>1</td><td>A</td></tr><tr><td>2</td><td>B</td></tr><tr><td>3</td><td>C</td></tr></table>

Roll\_no is the primary key of the Student table, Dept\_id is the primary key of the Department table and Student.Dept\_id is a foreign key from Department.Dept\_id
What will happen if we try to execute the following two SQL statements?

i. update Student set Dept id = Null where Roll on = 1  
ii. update Department set Dept\_id = Null where Dept\_id = 1

A. Both i and ii will fail

B. i will fail but ii will succeed


# 3.21.55 SQL: GATE IT 2005 | Question: 69


In an inventory management system implemented at a trading corporation, there are several tables designed to hold all the information. Amongst these, the following two tables hold information on which items are supplied by which suppliers, and which warehouse keeps which items along with the stock-level of these

Supply = (supplierid, itemcode)

Inventory = (itemcode, warehouse, stocklevel)

For a specific information required by the management, following SQL query has been written

Select distinct STMP.supplierid

From Supply as STMP

Where not unique (Select ITMP.supplierid

From Inventory, Supply as ITMP

Where STMP.supplierid = ITMP.supplierid

And ITMP.itemcode = Inventory.itemcode

And Inventory.warehouse = 'Nagpur');

For the warehouse at Nagpur, this query will find all suppliers who

A. do not supply any item

C. supply one or more items

gateit-2005 databases sql normal

B. supply exactly one item

D. supply two or more items

# Answer key

# 3.21.56 SQL: GATE IT 2006 | Question: 84

Consider a database with three relation instances shown below. The primary keys for the Drivers and Cars relation are did and cid respectively and the records are stored in ascending order of these primary keys as given in the tables. No indexing is available in the database.

D: Drivers relation

<table><tr><td>did</td><td>dname</td><td>rating</td><td>age</td></tr><tr><td>22</td><td>Karthikeyan</td><td>7</td><td>25</td></tr><tr><td>29</td><td>Salman</td><td>1</td><td>33</td></tr><tr><td>31</td><td>Boris</td><td>8</td><td>55</td></tr><tr><td>32</td><td>Amoldt</td><td>8</td><td>25</td></tr><tr><td>58</td><td>Schumacher</td><td>10</td><td>35</td></tr><tr><td>64</td><td>Sachin</td><td>7</td><td>35</td></tr><tr><td>71</td><td>Senna</td><td>10</td><td>16</td></tr><tr><td>74</td><td>Sachin</td><td>9</td><td>35</td></tr><tr><td>85</td><td>Rahul</td><td>3</td><td>25</td></tr><tr><td>95</td><td>Ralph</td><td>3</td><td>53</td></tr></table>

R: Reserves relation

<table><tr><td>did</td><td>Cid</td><td>day</td></tr><tr><td>22</td><td>101</td><td>10 / 10 / 06</td></tr><tr><td>22</td><td>102</td><td>10 / 10 / 06</td></tr><tr><td>22</td><td>103</td><td>08 / 10 / 06</td></tr><tr><td>22</td><td>104</td><td>07 / 10 / 06</td></tr><tr><td>31</td><td>102</td><td>10 / 11 / 16</td></tr><tr><td>31</td><td>103</td><td>06 / 11 / 16</td></tr><tr><td>31</td><td>104</td><td>12 / 11 / 16</td></tr><tr><td>64</td><td>101</td><td>05 / 09 / 06</td></tr><tr><td>64</td><td>102</td><td>08 / 09 / 06</td></tr><tr><td>74</td><td>103</td><td>08 / 09 / 06</td></tr></table>


C: Cars relation

<table><tr><td>Cid</td><td>Cname</td><td>colour</td></tr><tr><td>101</td><td>Renault</td><td>blue</td></tr><tr><td>102</td><td>Renault</td><td>red</td></tr><tr><td>103</td><td>Ferrari</td><td>green</td></tr><tr><td>104</td><td>Jaguar</td><td>red</td></tr></table>

What is the output of the following SQL query?

```sql
select D.dname
from Drivers D
where D.did in (
    select R.did
    from Cars C, Reserves R
    where R.cid = C.cid and C.colour = 'red'
    intersect
    select R.did
    from Cars C, Reserves R
    where R.cid = C.cid and C.colour = 'green'
)
```

A. Karthikeyan, Boris

B. Sachin, Salman

C. Karthikeyan, Boris, Sachin

D. Schumacher, Senna

gateit-2006 databases sql normal

# Answer key

# 3.21.57 SQL: GATE IT 2006 | Question: 85

Consider a database with three relation instances shown below. The primary keys for the Drivers and Cars relation are did and cid respectively and the records are stored in ascending order of these primary keys as given in the tables. No indexing is available in the database.

D: Drivers relation

<table><tr><td>did</td><td>dname</td><td>rating</td><td>age</td></tr><tr><td>22</td><td>Karthikeyan</td><td>7</td><td>25</td></tr><tr><td>29</td><td>Salman</td><td>1</td><td>33</td></tr><tr><td>31</td><td>Boris</td><td>8</td><td>55</td></tr><tr><td>32</td><td>Amoldt</td><td>8</td><td>25</td></tr><tr><td>58</td><td>Schumacher</td><td>10</td><td>35</td></tr><tr><td>64</td><td>Sachin</td><td>7</td><td>35</td></tr><tr><td>71</td><td>Senna</td><td>10</td><td>16</td></tr><tr><td>74</td><td>Sachin</td><td>9</td><td>35</td></tr><tr><td>85</td><td>Rahul</td><td>3</td><td>25</td></tr><tr><td>95</td><td>Ralph</td><td>3</td><td>53</td></tr></table>

R: Reserves relation

<table><tr><td>did</td><td>Cid</td><td>day</td></tr><tr><td>22</td><td>101</td><td>10 - 10 - 06</td></tr><tr><td>22</td><td>102</td><td>10 - 10 - 06</td></tr><tr><td>22</td><td>103</td><td>08 - 10 - 06</td></tr><tr><td>22</td><td>104</td><td>07 - 10 - 06</td></tr><tr><td>31</td><td>102</td><td>10 - 11 - 16</td></tr><tr><td>31</td><td>103</td><td>06 - 11 - 16</td></tr><tr><td>31</td><td>104</td><td>12 - 11 - 16</td></tr><tr><td>64</td><td>101</td><td>05 - 09 - 06</td></tr><tr><td>64</td><td>102</td><td>08 - 09 - 06</td></tr><tr><td>74</td><td>103</td><td>08 - 09 - 06</td></tr></table>

C: Cars relation

<table><tr><td>Cid</td><td>Cname</td><td>colour</td></tr><tr><td>101</td><td>Renault</td><td>blue</td></tr><tr><td>102</td><td>Renault</td><td>red</td></tr><tr><td>103</td><td>Ferrari</td><td>green</td></tr><tr><td>104</td><td>Jaguar</td><td>red</td></tr></table>

select D.dname

from Drivers D

where D.did in (

select R.did


```txt
from Cars C, Reserves R
where R.cid = C.cid and C.colour = 'red'
intersect
select R.did
from Cars C, Reserves R
where R.cid = C.cid and C.colour = 'green'
)
```

Let $n$ be the number of comparisons performed when the above SQL query is optimally executed. If linear search is used to locate a tuple in a relation using primary key, then $n$ lies in the range:

A. 36 - 40

B. 44 - 48

C. 60 - 64

D. 100 - 104

gateit-2006 databases sql normal

# Answer key

# 3.21.58 SQL: GATE IT 2008 | Question: 74

Consider the following relational schema:

- Student(school-id, sch-roll-no, sname, saddress)  
- School(school-id, sch-name, sch-address, sch-phone)  
- Enrolment(school-id, sch-roll-no, erollno, examname)  
- ExamResult(erollno, examname, marks)

What does the following SQL query output?

```sql
SELECT sch-name, COUNT (*)
FROM School C, Enrolment E, ExamResult R
WHERE E.school-id = C.school-id
AND
E.examname = R.examname AND E.erollno = R.erollno
AND
R.marks = 100 AND E.school-id IN (SELECT school-id
                      FROM student
                      GROUP BY school-id
                      HAVING COUNT (*) > 200)
GROUP By school-id
```

A. for each school with more than 200 students appearing in exams, the name of the school and the number of 100s scored by its students  
B. for each school with more than 200 students in it, the name of the school and the number of 100s scored by its students  
C. for each school with more than 200 students in it, the name of the school and the number of its students scoring 100 in at least one exam  
D. nothing; the query has a syntax error

gateit-2008 databases sql normal

# Answer key

# 3.22

# Safe Query (1)

# 3.22.1 Safe Query: GATE CSE 2017 | Set 1 | Question: 41

Consider a database that has the relation schemas EMP(EmpId, EmpName, DeptId), and DEPT(DeptName, DeptId). Note that the DeptId can be permitted to be NULL in the relation EMP. Consider the following queries on the database expressed in tuple relational calculus.

I. $\{t \mid \exists u \in \text{EMP}(t[\text{EmpName}] = u[\text{EmpName}] \land \forall v \in \text{DEPT}(t[\text{DeptId}] \neq v[\text{DeptId}]))\}$  
II. $\{t \mid \exists u \in \text{EMP}(t[\text{EmpName}] = u[\text{EmpName}] \land \exists v \in \text{DEPT}(t[\text{DeptId}] \neq v[\text{DeptId}]))\}$  
III. {t | ∃u ∈ EMP(t[EmpName] = u[EmpName] ∧ ∃v ∈ DEPT(t[DeptId] = v[DeptId]))}

Which of the above queries are safe?

A. I and II only

B. I and III only

C. II and III only

D. I, II and III



# 3.23

# Super Key (1)

# 3.23.1 Super Key: GATE CSE 2026 | Set 1 | Question: 55


Consider a relational database schema with a relation $R(A, B, C, D)$ . If $\{A, B\}$ and $\{A, C\}$ are the only two candidate keys of the relation $R$ , then the number of superkeys of relation $R$ is \_\_\_\_. (answer in integer)

gatecse-2026-set1 numerical-answers databases super-key two-marks

Answer key

# 3.24

# Timestamp Ordering (1)

# 3.24.1 Timestamp Ordering: GATE CSE 2017 | Set 1 | Question: 42


In a database system, unique timestamps are assigned to each transaction using Lamport's logical clock. Let $TS(T_{1})$ and $TS(T_{2})$ be the timestamps of transactions $T_{1}$ and $T_{2}$ respectively. Besides, $T_{1}$ holds a lock on the resource R, and $T_{2}$ has requested a conflicting lock on the same resource R. The following algorithm is used to prevent deadlocks in the database system assuming that a killed transaction is restarted with the same timestamp.

$$
\text {if} T S (T _ {2}) <   T S (T _ {1}) \text {then}
$$

$$
T _ {1} \text {is killed}
$$

$$
\text { else } T _ {2} \text { waits. }
$$

Assume any transaction that is not killed terminates eventually. Which of the following is TRUE about the database system that uses the above algorithm to prevent deadlocks?

A. The database system is both deadlock-free and starvation-free.  
B. The database system is deadlock-free, but not starvation-free.  
C. The database system is starvation-free, but not deadlock-free.  
D. The database system is neither deadlock-free nor starvation-free.

gatecse-2017-set1 databases timestamp-ordering normal transaction-and-concurrency

Answer key

# 3.25

# Transaction and Concurrency (27)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (11Q)

# 3.25.1 Transaction and Concurrency: GATE CS Practice : Transaction Concurrency Control (DBMS)


We have a table Orders with a specific predicate range query

Q: SELECT \* FROM Orders WHERE Value > 1000

Transaction $T_{1}$ executes Q and gets 5 rows.

Transaction $T_{2}$ inserts a new row with Value = 1500 and Commits.

Transaction $T_{1}$ executes Q again.

Under which Isolation Level is it guaranteed that $T_{1}$ will still see exactly 5 rows (i.e., prevent the Phantom Read)?

A. Read Committed

B. Repeatable Read

C. Serializable

D. Both B and C

# 3.25.2 Transaction and Concurrency: GATE CSE 1999 | Question: 2.6

For the schedule given below, which of the following is correct:

1 Read A  
2 Read B  
3 Write A  
4 Read A  
5 Write A  
6 Write B  
7 Read B  
8 Write B

A. This schedule is serializable and can occur in a scheme using 2PL protocol  
B. This schedule is serializable but cannot occur in a scheme using 2PL protocol  
C. This schedule is not serializable but can occur in a scheme using 2PL protocol  
D. This schedule is not serializable and cannot occur in a scheme using 2PL protocol

gate1999 databases transaction-and-concurrency normal

Answer key

# 3.25.3 Transaction and Concurrency: GATE CSE 2003 | Question: 29, ISRO2009-73

Which of the following scenarios may lead to an irrecoverable error in a database system?

A. A transaction writes a data item after it is read by an uncommitted transaction  
B. A transaction reads a data item after it is read by an uncommitted transaction  
C. A transaction reads a data item after it is written by a committed transaction  
D. A transaction reads a data item after it is written by an uncommitted transaction

gatecse-2003 databases transaction-and-concurrency easy isro2009

Answer key

# 3.25.4 Transaction and Concurrency: GATE CSE 2003 | Question: 87

Consider three data items D1, D2, and D3, and the following execution schedule of transactions T1, T2, and T3. In the diagram, $R(D)$ and $W(D)$ denote the actions reading and writing the data item D respectively.




<table><tr><td>T1</td><td>T2</td><td>T3</td></tr><tr><td>R(D1);W(D1);R(D2);W(D2);</td><td>R(D3);R(D2);W(D2);R(D1);W(D1);</td><td>R(D2);R(D3);W(D2);W(D3);</td></tr></table>

Which of the following statements is correct?

A. The schedule is serializable as $T2; T3; T1$  
B. The schedule is serializable as $T2; T1; T3$  
C. The schedule is serializable as $T3; T2; T1$  
D. The schedule is not serializable

gatecse-2003 databases transaction-and-concurrency normal

Answer key

# 3.25.5 Transaction and Concurrency: GATE CSE 2006 | Question: 20, ISRO2015-17

Consider the following log sequence of two transactions on a bank account, with initial balance 12000, that transfer 2000 to a mortgage payment and then apply a 5% interest.


1. T1 start  
2. T1 B old = 12000 new = 10000  
3. T1 M old = 0 new = 2000  
4. T1 commit  
5. T2 start  
6. T2 B old = 10000 new = 10500  
7. T2 commit

Suppose the database system crashes just before log record 7 is written. When the system is restarted, which one statement is true of the recovery procedure?

A. We must redo log record 6 to set B to 10500  
B. We must undo log record 6 to set B to 10000 and then redo log records 2 and 3  
C. We need not redo log records 2 and 3 because transaction T1 has committed  
D. We can apply redo and undo operations in arbitrary order because they are idempotent

gatecse-2006 databases transaction-and-concurrency normal isro2015

Answer key

# 3.25.6 Transaction and Concurrency: GATE CSE 2010 | Question: 20

Which of the following concurrency control protocols ensure both conflict serializability and freedom from deadlock?


I. 2-phase locking  
II. Time-stamp ordering

A. I only

B. II only

C. Both I and II

D. Neither I nor II

gatecse-2010 databases transaction-and-concurrency normal

# Answer key

# 3.25.7 Transaction and Concurrency: GATE CSE 2010 | Question: 42

Consider the following schedule for transactions T1, T2 and T3 :

<table><tr><td>T1</td><td>T2</td><td>T3</td></tr><tr><td>Read(X)</td><td></td><td></td></tr><tr><td></td><td>Read(Y)</td><td></td></tr><tr><td></td><td></td><td>Read(Y)</td></tr><tr><td></td><td>Write(Y)</td><td></td></tr><tr><td>Write(X)</td><td></td><td></td></tr><tr><td></td><td></td><td>Write(X)</td></tr><tr><td></td><td>Read(X)</td><td></td></tr><tr><td></td><td>Write(X)</td><td></td></tr></table>

Which one of the schedules below is the correct serialization of the above?

A. $T1 \rightarrow T3 \rightarrow T2$

B. $T2 \rightarrow T1 \rightarrow T3$

C. $T2 \rightarrow T3 \rightarrow T1$

D. $T3 \rightarrow T1 \rightarrow T2$

gatecse-2010 databases transaction-and-concurrency normal

# Answer key

# 3.25.8 Transaction and Concurrency: GATE CSE 2012 | Question: 27

Consider the following transactions with data items P and Q initialized to zero:

<table><tr><td> $T_1$ </td><td>read (P);read (Q);if P = 0 then Q := Q + 1;write (Q)</td></tr><tr><td> $T_2$ </td><td>read (Q);read (P);if Q = 0 then P := P + 1;write (P)</td></tr></table>

Any non-serial interleaving of T1 and T2 for concurrent execution leads to

A. a serializable schedule  
B. a schedule that is not conflict serializable  
C. a conflict serializable schedule  
D. a schedule for which a precedence graph cannot be drawn

gatecse-2012 databases transaction-and-concurrency normal

# Answer key

# 3.25.9 Transaction and Concurrency: GATE CSE 2015 | Set 2 | Question: 1

Consider the following transaction involving two bank accounts x and y.



