is guaranteed to be same as r, provided.

A. r has no duplicates and s is non-empty  
C. s has no duplicates and r is non-empty

gatecse-2000 databases sql

B. r and s have no duplicates  
D. r and s have the same number of tuples

# Answer key

# 3.21.12 SQL: GATE CSE 2000 | Question: 2.26

In SQL, relations can contain null values, and comparisons with null values are treated as unknown. Suppose all comparisons with a null value are treated as false. Which of the following pairs is not equivalent?

A. $x = 5$ not $(\text{not}(x = 5))$  
B. x = 5 x > 4 and x < 6, where x is an integer  
C. $x\neq 5$ not $(x = 5)$  
D. none of the above

gatecse-2000 databases sql normal

# Answer key

# 3.21.13 SQL: GATE CSE 2000 | Question: 22

Consider a bank database with only one relation

transaction (transno, acctno, date, amount)

The amount attribute value is positive for deposits and negative for withdrawals.

a. Define an SQL view TP containing the information (acctno,T1.date,T2.amount)

for every pair of transaction T1,T2 and such that T1 and T2 are transaction on the same account and the date of T2 is < the date of T1.

b. Using only the above view TP, write a query to find for each account the minimum balance it ever reached (not including the 0 balance when the account is created). Assume there is at most one transaction per day on each account and each account has at least one transaction since it was created. To simplify your query, break it up into 2 steps by defining an intermediate view V.

gatecse-2000 databases sql normal descriptive

# Answer key

# 3.21.14 SQL: GATE CSE 2001 | Question: 2.25

Consider a relation geq which represents "greater than or equal to", that is, $(x, y) \in \text{geq only if } y \geq x$ .

create table geq

(
    ib integer not null,
    ub integer not null,
    primary key ib,
    foreign key (ub) references geq on delete cascade
);




Which of the following is possible if tuple $(x,y)$ is deleted?

A. A tuple $(z,w)$ with z > y is deleted  
C. A tuple $(z,w)$ with w < x is deleted

gatecse-2001 databases sql normal

B. A tuple $(z, w)$ with $z > x$ is deleted  
D. The deletion of $(x,y)$ is prohibited

# Answer key

# 3.21.15 SQL: GATE CSE 2001 | Question: 21-b

Consider a relation examinee (regno, name, score), where regno is the primary key to score is a real


number.

Write an SQL query to list the regno of examinees who have a score greater than the average score.

gatecse-2001 databases sql normal descriptive

Answer key

# 3.21.16 SQL: GATE CSE 2001 | Question: 21-c

Consider a relation examinee (regno, name, score), where regno is the primary key to score is a real number.


Suppose the relation appears (regno, centr\_code) specifies the center where an examinee appears. Write an SQL query to list the centr\_code having an examinee of score greater than 80.

gatecse-2001 databases sql normal descriptive

Answer key

# 3.21.17 SQL: GATE CSE 2003 | Question: 86

Consider the set of relations shown below and the SQL query that follows.

Students: (Roll\_number, Name, Date\_of\_birth)

Courses: (Course\_number, Course\_name, Instructor)

Grades: (Roll\_number, Course\_number, Grade)


```txt
Select distinct Name
from Students, Courses, Grades
where Students.Roll_number=Grades.Roll_number
and Courses.Instructor = 'Korth'
and Courses.Course_number = Grades.Course_number
and Grades.Grade = 'A'
```

Which of the following sets is computed by the above query?

A. Names of students who have got an A grade in all courses taught by Korth  
B. Names of students who have got an A grade in all courses  
C. Names of students who have got an A grade in at least one of the courses taught by Korth  
D. None of the above

gatecse-2003 databases sql easy

Answer key

# 3.21.18 SQL: GATE CSE 2004 | Question: 53

The employee information in a company is stored in the relation


\- Employee (name, sex, salary, deptName)

Consider the following SQL query

```txt
Select deptName
  From Employee
  Where sex = 'M'
  Group by deptName
  Having avg(salary) >
    (select avg (salary) from Employee)
```

It returns the names of the department in which

A. the average salary is more than the average salary in the company  
B. the average salary of male employees is more than the average salary of all male employees in the company  
C. the average salary of male employees is more than the average salary of employees in same the department  
D. the average salary of male employees is more than the average salary in the company


# 3.21.19 SQL: GATE CSE 2005 | Question: 77, ISRO2016-55


The relation book (title, price) contains the titles and prices of different books. Assuming that no two books have the same price, what does the following SQL query list?

```sql
select title
from book as B
where (select count(*)
  from book as T
  where T.price>B.price) < 5
```

A. Titles of the four most expensive books  
B. Title of the fifth most inexpensive book  
C. Title of the fifth most expensive book  
D. Titles of the five most expensive books

gatecse-2005 databases sql easy isro2016

# Answer key

# 3.21.20 SQL: GATE CSE 2006 | Question: 67


Consider the relation account (customer, balance) where the customer is a primary key and there are no null values. We would like to rank customers according to decreasing balance. The customer with the largest balance gets rank 1. Ties are not broke but ranks are skipped: if exactly two customers have the largest balance they each get rank 1 and rank 2 is not assigned.

# Query1:

```txt
select A.customer, count(B.customer)
from account A, account B
where A.balance <=B.balance
group by A.customer
```

# Query2:

```txt
select A.customer, 1+count(B.customer)
from account A, account B
where A.balance < B.balance
group by A.customer
```

Consider these statements about Query1 and Query2.

1. Query1 will produce the same row set as Query2 for some but not all databases.  
2. Both Query1 and Query 2 are a correct implementation of the specification  
3. Query1 is a correct implementation of the specification but Query2 is not  
4. Neither Query1 nor Query2 is a correct implementation of the specification  
5. Assigning rank with a pure relational query takes less time than scanning in decreasing balance order assigning ranks using ODBC.

Which two of the above statements are correct?

A. 2 and 5

B. 1 and 3

C. 1 and 4

D. 3 and 5

gatecse-2006 databases sql normal

# Answer key

# 3.21.21 SQL: GATE CSE 2006 | Question: 68


Consider the relation enrolled (student, course) in which (student, course) is the primary key, and the relation paid (student, amount) where student is the primary key. Assume no null values and no foreign keys or integrity constraints.

Given the following four queries:

Query1:

select student from enrolled where student in (select student from paid)

# Query2:

select student from paid where student in (select student from enrolled)

# Query3:

select E.student from enrolled E, paid P where E.student = P.student

# Query4:

select student from paid where exists
  (select \* from enrolled where enrolled.student = paid.student)

Which one of the following statements is correct?

A. All queries return identical row sets for any database  
B. Query2 and Query4 return identical row sets for all databases but there exist databases for which Query1 and Query2 return different row sets  
C. There exist databases for which Query3 returns strictly fewer rows than Query2  
D. There exist databases for which Query4 will encounter an integrity violation at runtime

gatecse-2006 databases sql normal

# Answer key

# 3.21.22 SQL: GATE CSE 2006 | Question: 69

Consider the relation enrolled (student, course) in which (student, course) is the primary key, and the relation paid (student, amount) where student is the primary key. Assume no null values and no foreign keys or integrity constraints. Assume that amounts 6000, 7000, 8000, 9000 and 10000 were each paid by 20% of the students. Consider these query plans (Plan 1 on left, Plan 2 on right) to “list all courses taken by students who have paid more than x”

![](images/ebe942744fb65d0acfb72c09fdc5634fc01818aa22ebfaa74f0ff62623c5c635.jpg)

A disk seek takes 4ms, disk data transfer bandwidth is 300 MB/s and checking a tuple to see if amount is greater than x takes 10μs. Which of the following statements is correct?

A. Plan 1 and Plan 2 will not output identical row sets for all databases  
B. A course may be listed more than once in the output of Plan 1 for some databases  
C. For x = 5000, Plan 1 executes faster than Plan 2 for all databases  
D. For x = 9000, Plan I executes slower than Plan 2 for all databases

gatecse-2006 databases sql normal

# Answer key

# 3.21.23 SQL: GATE CSE 2007 | Question: 61

Consider the table employee(empld, name, department, salary) and the two queries $Q_{1}, Q_{2}$ below. Assuming that department 5 has more than one employee, and we want to find the employees who get



higher salary than anyone in the department 5, which one of the statements is TRUE for any arbitrary employee table?

Select e.empId

$Q_{1}$ : From employee e
Where not exists

(Select \* From employee s Where s.department = "5" and s.salary >= e.salary)

Select e.empId

$Q_{2}$ : From employee e
Where e.salary > Any

(Select distinct salary From employee s Where s.department = "5")

A. $Q_{1}$ is the correct query  
C. Both $Q_{1}$ and $Q_{2}$ produce the same answer

B. $Q_{2}$ is the correct query

D. Neither $Q_{1}$ nor $Q_{2}$ is the correct query

gatecse-2007 databases sql normal verbal-aptitude

# Answer key

# 3.21.24 SQL: GATE CSE 2009 | Question: 55

Consider the following relational schema:

Suppliers(sid:integer, sname:string, city:string, street:string)

Parts(pid:integer, pname:string, color:string)

Catalog(sid:integer, pid:integer , cost:real)

Consider the following relational query on the above database:

SELECT S.sname

FROM Suppliers S

WHERE S.sid NOT IN (SELECT C.sid

FROM Catalog C

WHERE C.pid NOT IN (SELECT P.pid

FROM Parts P

WHERE P.color<>'blue'))

Assume that relations corresponding to the above schema are not empty. Which one of the following is the correct interpretation of the above query?

A. Find the names of all suppliers who have supplied a non-blue part.  
B. Find the names of all suppliers who have not supplied a non-blue part.  
C. Find the names of all suppliers who have supplied only non-blue part.  
D. Find the names of all suppliers who have not supplied only blue parts.

gatecse-2009 databases sql normal

# Answer key

# 3.21.25 SQL: GATE CSE 2009 | Question: 56

Consider the following relational schema:

- Suppliers(sid:integer, sname:string, city:string, street:string)  
- Parts(pid:integer, pname:string, color:string)  
- Catalog(sid:integer, pid:integer, cost:real)

Assume that, in the suppliers relation above, each supplier and each street within a city has unique name, and (sname, city) forms a candidate key. No other functional dependencies are implied other than those implied by primary and candidate keys. Which one of the following is TRUE about the above schema?



A. The schema is in BCNF

B. The schema is in 3NF but not in BCNF

C. The schema is in 2NF but not in 3NF

D. The schema is not in 2NF

gatecse-2009 databases sql database-normalization normal

# Answer key

# 3.21.26 SQL: GATE CSE 2010 | Question: 19

A relational schema for a train reservation database is given below.

- passenger(pid, pname, age)  
- reservation(pid, class, tid)

Passenger

<table><tr><td>pid</td><td>pname</td><td>Age</td></tr><tr><td>0</td><td>Sachine</td><td>65</td></tr><tr><td>1</td><td>Rahul</td><td>66</td></tr><tr><td>2</td><td>Sourav</td><td>67</td></tr><tr><td>3</td><td>Anil</td><td>69</td></tr></table>

Reservation

<table><tr><td>pid</td><td>class</td><td>tid</td></tr><tr><td>0</td><td>AC</td><td>8200</td></tr><tr><td>1</td><td>AC</td><td>8201</td></tr><tr><td>2</td><td>SC</td><td>8201</td></tr><tr><td>5</td><td>AC</td><td>8203</td></tr><tr><td>1</td><td>SC</td><td>8204</td></tr><tr><td>3</td><td>AC</td><td>8202</td></tr></table>

What pids are returned by the following SQL query for the above instance of the tables?

SELECT pid

FROM Reservation

WHERE class='AC' AND

EXISTS (SELECT \*

FROM Passenger

WHERE age>65 AND

Passenger.pid=Reservation.pid)

A. 1,0

B. 1,2

C. 1,3

D. 1,5

gatecse-2010 databases sql normal

# Answer key

# 3.21.27 SQL: GATE CSE 2011 | Question: 32

Consider a database table T containing two columns X and Y each of type integer. After the creation of the table, one record $(X=1, Y=1)$ is inserted in the table.

Let MX and MY denote the respective maximum values of X and Y among all records in the table at any point in time. Using MX and MY, new records are inserted in the table 128 times with X and Y values being MX+1, 2\*MY+1 respectively. It may be noted that each time after the insertion, values of MX and MY change.

What will be the output of the following SQL query after the steps mentioned above are carried out?

SELECT Y FROM T WHERE X=7;

A. 127

B. 255

C. 129

D. 257

gatecse-2011 databases sql normal

# Answer key

# 3.21.28 SQL: GATE CSE 2011 | Question: 46

Database table by name Loan\_Records is given below.




<table><tr><td>Borrower</td><td>Bank_Manager</td><td>Loan_Amount</td></tr><tr><td>Ramesh</td><td>Sunderajan</td><td>10000.00</td></tr><tr><td>Suresh</td><td>Ramgopal</td><td>5000.00</td></tr><tr><td>Mahesh</td><td>Sunderajan</td><td>7000.00</td></tr></table>

What is the output of the following SQL query?

SELECT count(\*)

FROM (

SELECT Borrower, Bank\_Manager FROM Loan\_Records) AS S

NATURAL JOIN

(SELECT Bank\_Manager, Loan\_Amount FROM Loan\_Records) AS T

A. 3

B. 9

C. 5

D. 6

gatecse-2011 databases sql normal

Answer key

# 3.21.29 SQL: GATE CSE 2012 | Question: 15

Which of the following statements are TRUE about an SQL query?

P : An SQL query can contain a HAVING clause even if it does not have a GROUP BY clause  
Q : An SQL query can contain a HAVING clause only if it has a GROUP BY clause  
R : All attributes used in the GROUP BY clause must appear in the SELECT clause  
S : Not all attributes used in the GROUP BY clause need to appear in the SELECT clause

A. P and R

B. P and S

C. Q and R

D. Q and S

gatecse-2012 databases easy sql ambiguous

Answer key

# 3.21.30 SQL: GATE CSE 2012 | Question: 51

Consider the following relations A, B and C :



A

<table><tr><td>Id</td><td>Name</td><td>Age</td></tr><tr><td>12</td><td>Arun</td><td>60</td></tr><tr><td>15</td><td>Shreya</td><td>24</td></tr><tr><td>99</td><td>Rohit</td><td>11</td></tr></table>

B

<table><tr><td>Id</td><td>Name</td><td>Age</td></tr><tr><td>15</td><td>Shreya</td><td>24</td></tr><tr><td>25</td><td>Hari</td><td>40</td></tr><tr><td>98</td><td>Rohit</td><td>20</td></tr><tr><td>99</td><td>Rohit</td><td>11</td></tr></table>

C

<table><tr><td>Id</td><td>Phone</td><td>Area</td></tr><tr><td>10</td><td>2200</td><td>02</td></tr><tr><td>99</td><td>2100</td><td>01</td></tr></table>

How many tuples does the result of the following SQL query contain?

SELECT A.Id

FROM A

WHERE A.Age > ALL (SELECT B.Age

FROM B

WHERE B.Name = 'Arun')

A. 4

B. 3

C. 0

D. 1

gatecse-2012 databases sql normal

Answer key

# 3.21.31 SQL: GATE CSE 2014 | Set 1 | Question: 22

Given the following statements:

S1: A foreign key declaration can always be replaced by an equivalent check assertion in SQL.


S2: Given the table $R(a, b, c)$ where a and b together form the primary key, the following is a valid table definition.

```sql
CREATE TABLE S (
  a INTEGER,
  d INTEGER,
  e INTEGER,
  PRIMARY KEY (d),
  FOREIGN KEY (a) references R)
```

Which one of the following statements is CORRECT?

A. S1 is TRUE and S2 is FALSE  
C. S1 is FALSE and S2 is TRUE

B. Both S1 and S2 are TRUE  
D. Both S1 and S2 are FALSE

gatecse-2014-set1 databases normal sql

# Answer key

# 3.21.32 SQL: GATE CSE 2014 | Set 1 | Question: 54

Given the following schema:

employees(emp-id, first-name, last-name, hire-date, dept-id, salary)

departments(dept-id, dept-name, manager-id, location-id)

You want to display the last names and hire dates of all latest hires in their respective departments in the location ID 1700. You issue the following query:

SQL>SELECT last-name, hire-date

FROM employees

WHERE (dept-id, hire-date) IN

(SELECT dept-id, MAX(hire-date)

FROM employees JOIN departments USING(dept-id)

WHERE location-id =1700

GROUP BY dept-id);

What is the outcome?

A. It executes but does not give the correct result  
B. It executes and gives the correct result.  
C. It generates an error because of pairwise comparison.  
D. It generates an error because of the GROUP BY clause cannot be used with table joins in a sub-query.

gatecse-2014-set1 databases sql normal

# Answer key

# 3.21.33 SQL: GATE CSE 2014 | Set 2 | Question: 54

SQL allows duplicate tuples in relations, and correspondingly defines the multiplicity of tuples in the result of joins. Which one of the following queries always gives the same answer as the nested query shown below:

select \* from R where a in (select S.a from S)

A. select R.\* from R, S where R.a=S.a  
B. select distinct R.\* from R,S where R.a=S.a  
C. select R.\* from R,(select distinct a from S) as S1 where R.a=S1.a  
D. select R.\* from R,S where R.a=S.a and is unique R

gatecse-2014-set2 databases sql normal

# Answer key

# 3.21.34 SQL: GATE CSE 2014 | Set 3 | Question: 54

Consider the following relational schema:

employee (empId,empName,empDept)

customer (custId,custName,salesRepld,rating)

salesRepld is a foreign key referring to empld of the employee relation. Assume that each employee makes a sale to at least one customer. What does the following query return?




SELECT empName FROM employee E

WHERE NOT EXISTS (SELECT custld

FROM customer C

WHERE C.salesRepld = E.empld

AND C.rating <> 'GOOD');

A. Names of all the employees with at least one of their customers having a 'GOOD' rating.  
B. Names of all the employees with at most one of their customers having a 'GOOD' rating.  
C. Names of all the employees with none of their customers having a 'GOOD' rating.  
D. Names of all the employees with all their customers having a 'GOOD' rating.

gatecse-2014-set3 databases sql easy

# Answer key

# 3.21.35 SQL: GATE CSE 2015 | Set 1 | Question: 27

Consider the following relation:

Student

<table><tr><td>Roll_No</td><td>Student_Name</td></tr><tr><td>1</td><td>Raj</td></tr><tr><td>2</td><td>Rohit</td></tr><tr><td>3</td><td>Raj</td></tr></table>

Performance

<table><tr><td>Roll_No</td><td>Course</td><td>Marks</td></tr><tr><td>1</td><td>Math</td><td>80</td></tr><tr><td>1</td><td>English</td><td>70</td></tr><tr><td>2</td><td>Math</td><td>75</td></tr><tr><td>3</td><td>English</td><td>80</td></tr><tr><td>2</td><td>Physics</td><td>65</td></tr><tr><td>3</td><td>Math</td><td>80</td></tr></table>


Consider the following SQL query.

SELECT S.Student\_Name, Sum(P. Marks)

FROM Student S, Performance P

WHERE S.Roll\_No= P.Roll\_No

GROUP BY S.STUDENT\_Name

The numbers of rows that will be returned by the SQL query is \_\_\_\_.

gatecse-2015-set1 databases sql normal numerical-answers

# Answer key

# 3.21.36 SQL: GATE CSE 2015 | Set 3 | Question: 3

Consider the following relation

Cinema(theater, address, capacity)

Which of the following options will be needed at the end of the SQL query

SELECT P1.address

FROM Cinema P1


such that it always finds the addresses of theaters with maximum capacity?

A. WHERE P1.capacity >= All (select P2.capacity from Cinema P2)

B. WHERE P1.capacity >= Any (select P2.capacity from Cinema P2)

C. WHERE P1.capacity > All (select max(P2.capacity) from Cinema P2)

D. WHERE P1.capacity > Any (select max(P2.capacity) from Cinema P2)

gatecse-2015-set3 databases sql normal

# Answer key

Consider the following database table named water\_schemes:

Water\_schemes

<table><tr><td>scheme_no</td><td>district_name</td><td>capacity</td></tr><tr><td>1</td><td>Ajmer</td><td>20</td></tr><tr><td>1</td><td>Bikaner</td><td>10</td></tr><tr><td>2</td><td>Bikaner</td><td>10</td></tr><tr><td>3</td><td>Bikaner</td><td>20</td></tr><tr><td>1</td><td>Churu</td><td>10</td></tr><tr><td>2</td><td>Churu</td><td>20</td></tr><tr><td>1</td><td>Dungargarh</td><td>10</td></tr></table>

The number of tuples returned by the following SQL query is \_\_\_\_.

```sql
with total (name, capacity) as
  select district_name, sum (capacity)
  from water_schemes
  group by district_name
with total_avg (capacity) as
  select avg (capacity)
  from total
select name
  from total, total_avg
  where total.capacity ≥ total_avg.capacity
```

gatecse-2016-set2 databases sql normal numerical-answers

# Answer key

# 3.21.38 SQL: GATE CSE 2017 | Set 1 | Question: 23

Consider a database that has the relation schema EMP (EmpId, EmpName, and DeptName). An instance of the schema EMP and a SQL query on it are given below:


<table><tr><td colspan="3">EMP</td></tr><tr><td>EmpId</td><td>EmpName</td><td>DeptName</td></tr><tr><td>1</td><td>XYA</td><td>AA</td></tr><tr><td>2</td><td>XYB</td><td>AA</td></tr><tr><td>3</td><td>XYC</td><td>AA</td></tr><tr><td>4</td><td>XYD</td><td>AA</td></tr><tr><td>5</td><td>XYE</td><td>AB</td></tr><tr><td>6</td><td>XYF</td><td>AB</td></tr><tr><td>7</td><td>XYG</td><td>AB</td></tr><tr><td>8</td><td>XYH</td><td>AC</td></tr><tr><td>9</td><td>XYI</td><td>AC</td></tr><tr><td>10</td><td>XYJ</td><td>AC</td></tr><tr><td>11</td><td>XYK</td><td>AD</td></tr><tr><td>12</td><td>XYL</td><td>AD</td></tr><tr><td>13</td><td>XYM</td><td>AE</td></tr></table>

```sql
SELECT AVG(EC.Num)
FROM EC
WHERE (DeptName, Num) IN
    (SELECT DeptName, COUNT(EmpId) AS
        EC(DeptName, Num)
FROM EMP
GROUP BY DeptName)
```

The output of executing the SQL query is \_\_\_\_.

# 3.21.39 SQL: GATE CSE 2017 | Set 2 | Question: 46

Consider the following database table named top\_scorer.


top\_scorer

<table><tr><td>player</td><td>country</td><td>goals</td></tr><tr><td>Klose</td><td>Germany</td><td>16</td></tr><tr><td>Ronaldo</td><td>Brazil</td><td>15</td></tr><tr><td>G Muller</td><td>Germany</td><td>14</td></tr><tr><td>Fontaine</td><td>France</td><td>13</td></tr><tr><td>Pele</td><td>Brazil</td><td>12</td></tr><tr><td>Klinsmann</td><td>Germany</td><td>11</td></tr><tr><td>Kocsis</td><td>Hungary</td><td>11</td></tr><tr><td>Batistuta</td><td>Argentina</td><td>10</td></tr><tr><td>Cubillas</td><td>Peru</td><td>10</td></tr><tr><td>Lato</td><td>Poland</td><td>10</td></tr><tr><td>Lineker</td><td>England</td><td>10</td></tr><tr><td>T Muller</td><td>Germany</td><td>10</td></tr><tr><td>Rahn</td><td>Germany</td><td>10</td></tr></table>

Consider the following SQL query:

```sql
SELECT ta.player FROM top_scorer AS ta
WHERE ta.goals >ALL (SELECT tb.goals
  FROM top_scorer AS tb
  WHERE tb.country = 'Spain')
AND ta.goals > ANY (SELECT tc.goals
  FROM top_scorer AS tc
  WHERE tc.country='Germany')
```

The number of tuples returned by the above SQL query is \_\_\_\_

gatecse-2017-set2 databases sql numerical-answers

# Answer key

# 3.21.40 SQL: GATE CSE 2018 | Question: 12

Consider the following two tables and four queries in SQL.

Book (isbn, bname), Stock(isbn, copies)

Query 1:

SELECT B.isbn, S.copies FROM Book B INNER JOIN Stock S ON B.isbn=S.isbn;

Query 2:

SELECT B.isbn, S.copies FROM Book B LEFT OUTER JOIN Stock S ON B.isbn=S.isbn;

Query 3:

SELECT B.isbn, S,copies FROM Book B RIGHT OUTER JOIN Stock S ON B.isbn=S.isbn

Query 4:

SELECT B.isbn, S.copies FROM Book B FULL OUTER JOIN Stock S ON B.isbn=S.isbn

Which one of the queries above is certain to have an output that is a superset of the outputs of the other three queries?


# Answer key

# 3.21.41 SQL: GATE CSE 2019 | Question: 51

A relational database contains two tables Student and Performance as shown below:


Table: student

<table><tr><td>Roll_no</td><td>Student_name</td></tr><tr><td>1</td><td>Amit</td></tr><tr><td>2</td><td>Priya</td></tr><tr><td>3</td><td>Vinit</td></tr><tr><td>4</td><td>Rohan</td></tr><tr><td>5</td><td>Smita</td></tr></table>

Table: Performance

<table><tr><td>Roll_no</td><td>Subject_code</td><td>Marks</td></tr><tr><td>1</td><td>A</td><td>86</td></tr><tr><td>1</td><td>B</td><td>95</td></tr><tr><td>1</td><td>C</td><td>90</td></tr><tr><td>2</td><td>A</td><td>89</td></tr><tr><td>2</td><td>C</td><td>92</td></tr><tr><td>3</td><td>C</td><td>80</td></tr></table>

The primary key of the Student table is Roll\_no. For the performance table, the columns Roll\_no. and Subject\_code together form the primary key. Consider the SQL query given below:

SELECT S.Student\_name, sum(P.Marks)

FROM Student S, Performance P

WHERE P.Marks >84

GROUP BY S.Student\_name;

The number of rows returned by the above SQL query is \_\_\_\_

gatecse-2019 numerical-answers databases sql two-marks

# Answer key

# 3.21.42 SQL: GATE CSE 2020 | Question: 13

Consider a relational database containing the following schemas.


Catalogue

<table><tr><td>sno</td><td>pno</td><td>cost</td></tr><tr><td>S1</td><td>P1</td><td>150</td></tr><tr><td>S1</td><td>P2</td><td>50</td></tr><tr><td>S1</td><td>P3</td><td>100</td></tr><tr><td>S2</td><td>P4</td><td>200</td></tr><tr><td>S2</td><td>P5</td><td>250</td></tr><tr><td>S3</td><td>P1</td><td>250</td></tr><tr><td>S3</td><td>P2</td><td>150</td></tr><tr><td>S3</td><td>P5</td><td>300</td></tr><tr><td>S3</td><td>P4</td><td>250</td></tr></table>

Suppliers

<table><tr><td>sno</td><td>sname</td><td>location</td></tr><tr><td>S1</td><td>M/s Royal furniture</td><td>Delhi</td></tr><tr><td>S2</td><td>M/s Balaji furniture</td><td>Bangalore</td></tr><tr><td>S3</td><td>M/s Premium furniture</td><td>Chennai</td></tr></table>

Parts

<table><tr><td>$ \underline{\text{pno}} $</td><td>pname</td><td>part_spec</td></tr><tr><td>$ \underline{P1} $</td><td>Table</td><td>Wood</td></tr><tr><td>$ \underline{P2} $</td><td>Chair</td><td>Wood</td></tr><tr><td>$ \underline{P3} $</td><td>Table</td><td>Steel</td></tr><tr><td>$ \underline{P4} $</td><td>Almirah</td><td>Steel</td></tr><tr><td>$ \underline{P5} $</td><td>Almirah</td><td>Wood</td></tr></table>

The primary key of each table is indicated by underlining the constituent fields.

SELECT s.sno, s.sname

FROM Suppliers s, Catalogue c

WHERE s.sno=c.sno AND

cost > (SELECT AVG (cost)

FROM Catalogue

WHERE pno = 'P4'

GROUP BY pno);

The number of rows returned by the above SQL query is

A. 4

B. 5

C. 0

D. 2