read(x); x:=x-50; write (x); read(y); y:=y+50; write(y)

The constraint that the sum of the accounts $x$ and $y$ should remain constant is that of

A. Atomicity

B. Consistency

C. Isolation

D. Durability

gatecse-2015-set2 databases transaction-and-concurrency easy

# Answer key

# 3.25.10 Transaction and Concurrency: GATE CSE 2015 | Set 2 | Question: 46

Consider a simple checkpointing protocol and the following set of operations in the log.

(start, T4); (write, T4, y, 2, 3); (start, T1); (commit, T4); (write, T1, z, 5, 7);

(checkpoint);

(start, T2); (write, T2, x, 1, 9); (commit, T2); (start, T3); (write, T3, z, 7, 2);

If a crash happens now and the system tries to recover using both undo and redo operations, what are the contents of the undo list and the redo list?

A. Undo: T3, T1; Redo: T2  
C. Undo: none; Redo: T2, T4, T3, T1  
gatecse-2015-set2 databases transaction-and-concurrency normal

B. Undo: T3, T1; Redo: T2, T4

D. Undo: T3, T1, T4; Redo: T2

# Answer key

# 3.25.11 Transaction and Concurrency: GATE CSE 2015 | Set 3 | Question: 29

Consider the partial Schedule S involving two transactions T1 and T2. Only the read and the write operations have been shown. The read operation on data item P is denoted by $\text{read}(P)$ and write operation on data item P is denoted by $\text{write}(P)$ .



<table><tr><td colspan="3">Schedule S</td></tr><tr><td rowspan="2">Time Instance</td><td colspan="2">Transaction ID</td></tr><tr><td>T1</td><td>T2</td></tr><tr><td>1</td><td>read(A)</td><td></td></tr><tr><td>2</td><td>write(A)</td><td></td></tr><tr><td>3</td><td></td><td>read(C)</td></tr><tr><td>4</td><td></td><td>write(C)</td></tr><tr><td>5</td><td></td><td>read(B)</td></tr><tr><td>6</td><td></td><td>write(B)</td></tr><tr><td>7</td><td></td><td>read(A)</td></tr><tr><td>8</td><td></td><td>commit</td></tr><tr><td>9</td><td>read(B)</td><td></td></tr></table>

Suppose that the transaction $T1$ fails immediately after time instance 9. Which of the following statements is correct?

A. $T2$ must be aborted and then both $T1$ and $T2$ must be re-started to ensure transaction atomicity  
B. Schedule S is non-recoverable and cannot ensure transaction atomicity  
C. Only T2 must be aborted and then re-started to ensure transaction atomicity  
D. Schedule $S$ is recoverable and can ensure transaction atomicity and nothing else needs to be done

gatecse-2015-set3 databases transaction-and-concurrency normal

# Answer key

# 3.25.12 Transaction and Concurrency: GATE CSE 2016 | Set 1 | Question: 22

Which one of the following is NOT a part of the ACID properties of database transactions?


A. Atomicity

B. Consistency

C. Isolation

D. Deadlock-freedom

gatecse-2016-set1 databases transaction-and-concurrency easy

# Answer key

# 3.25.13 Transaction and Concurrency: GATE CSE 2016 | Set 1 | Question: 51

Consider the following two phase locking protocol. Suppose a transaction $T$ accesses (for read or write operations), a certain set of objects $\{O_1, \ldots, O_k\}$ . This is done in the following manner:


- Step 1. $T$ acquires exclusive locks to $O_1, \ldots, O_k$ in increasing order of their addresses.  
- Step 2. The required operations are performed.  
- Step 3. All locks are released

This protocol will

A. guarantee serializability and deadlock-freedom  
B. guarantee neither serializability nor deadlock-freedom  
C. guarantee serializability but not deadlock-freedom  
D. guarantee deadlock-freedom but not serializability.

gatecse-2016-set1 databases transaction-and-concurrency normal

# Answer key

# 3.25.14 Transaction and Concurrency: GATE CSE 2016 | Set 2 | Question: 22


Suppose a database schedule $S$ involves transactions $T_1, \ldots, T_n$ . Construct the precedence graph of $S$ with vertices representing the transactions and edges representing the conflicts. If $S$ is serializable, which one of the following orderings of the vertices of the precedence graph is guaranteed to yield a serial schedule?

A. Topological order  
C. Breadth-first order

B. Depth-first order  
D. Ascending order of the transaction indices

gatecse-2016-set2 databases transaction-and-concurrency normal

# Answer key

# 3.25.15 Transaction and Concurrency: GATE CSE 2016 | Set 2 | Question: 51


Consider the following database schedule with two transactions $T_{1}$ and $T_{2}$ .

$$
S = r _ {2} (X); r _ {1} (X); r _ {2} (Y); w _ {1} (X); r _ {1} (Y); w _ {2} (X); a _ {1}; a _ {2}
$$

Where $r_{i}(Z)$ denotes a read operation by transaction $T_{i}$ on a variable Z, $w_{i}(Z)$ denotes a write operation by $T_{i}$ on a variable Z and $a_{i}$ denotes an abort by transaction $T_{i}$ .

Which one of the following statements about the above schedule is TRUE?

A. $S$ is non-recoverable.  
C. $S$ does not have a cascading abort.

B. $S$ is recoverable, but has a cascading abort.  
D. $S$ is strict.

gatecse-2016-set2 databases transaction-and-concurrency normal

# Answer key

# 3.25.16 Transaction and Concurrency: GATE CSE 2019 | Question: 11


Consider the following two statements about database transaction schedules:

I. Strict two-phase locking protocol generates conflict serializable schedules that are also recoverable.  
II. Timestamp-ordering concurrency control protocol with Thomas' Write Rule can generate view serializable schedules that are not conflict serializable

Which of the above statements is/are TRUE?

A. I only

B. II only

C. Both I and II

D. Neither I nor II

# Answer key

# 3.25.17 Transaction and Concurrency: GATE CSE 2021 | Set 1 | Question: 13

Suppose a database system crashes again while recovering from a previous crash. Assume checkpointing is not done by the database either during the transactions or during recovery.

Which of the following statements is/are correct?

A. The same undo and redo list will be used while recovering again  
B. The system cannot recover any further  
C. All the transactions that are already undone and redone will not be recovered again  
D. The database will become inconsistent

gatecse-2021-set1 multiple-selects databases transaction-and-concurrency one-mark

# Answer key

# 3.25.18 Transaction and Concurrency: GATE CSE 2024 | Set 2 | Question: 9

Once the DBMS informs the user that a transaction has been successfully completed, its effect should persist even if the system crashes before all its changes are reflected on disk. This property is called

A. durability

B. atomicity

C. consistency

D. isolation

gatecse-2024-set2 databases transaction-and-concurrency easy one-mark

# Answer key

# 3.25.19 Transaction and Concurrency: GATE CSE 2025 | Set 1 | Question: 5

A schedule of three database transactions $T_{1}, T_{2}$ , and $T_{3}$ is shown. $R_{i}(A)$ and $W_{i}(A)$ denote read and write of data item A by transaction $T_{i}, i = 1, 2, 3$ . The transaction $T_{1}$ aborts at the end. Which other transaction(s) will be required to be rolled back?

$$
R _ {1} (X) W _ {1} (Y) R _ {2} (X) R _ {2} (Y) R _ {3} (Y) \text {ABORT} (T _ {1})
$$

A. Only $T_{2}$

B. Only $T_{3}$

C. Both $T_{2}$ and $T_{3}$

D. Neither $T_{2}$ nor $T_{3}$

gatecse2025-set1 databases transaction-and-concurrency one-mark

# Answer key

# 3.25.20 Transaction and Concurrency: GATE CSE 2025 | Set 2 | Question: 17

An audit of a banking transactions system has found that on an earlier occasion, two joint holders of account A attempted simultaneous transfers of Rs. 10000 each from account A to account B. Both transactions read the same value, Rs. 11000, as the initial balance in A and were allowed to go through. B was credit 10000 twice. A was debited only once and ended up with a balance of Rs. 1000.

Which of the following properties is/are certain to have been violated by the system?

A. Atomicity

B. Consistency

C. Isolation

D. Durability

gatecse2025-set2 databases transaction-and-concurrency multiple-selects one-mark

# Answer key

# 3.25.21 Transaction and Concurrency: GATE CSE 2026 | Set 2 | Question: 10

Consider concurrent execution of two transactions T1 and T2 in a DBMS, both of which access a data object A. For these two transactions to not conflict on A, which one of the following statements must be true?

A. Both $T1$ and $T2$ only read $A$

B. $T1$ reads $A$ and $T2$ writes $A$

C. $T1$ writes $A$ and $T2$ reads $A$

D. Both $T1$ and $T2$ write $A$

gatecse-2026-set2 databases transaction-and-concurrency one-mark






# 3.25.22 Transaction and Concurrency: GATE IT 2004 | Question: 21

Which level of locking provides the highest degree of concurrency in a relational database ?


A. Page  
B. Table  
C. Row  
D. Page, table and row level locking allow the same degree of concurrency

gateit-2004 databases normal transaction-and-concurrency

Answer key

# 3.25.23 Transaction and Concurrency: GATE IT 2004 | Question: 77

Consider the following schedule S of transactions T1 and T2 :


<table><tr><td>T1</td><td>T2</td></tr><tr><td>Read(A)</td><td></td></tr><tr><td>A = A - 10</td><td></td></tr><tr><td></td><td>Read(A)</td></tr><tr><td></td><td>Temp = 0.2*A</td></tr><tr><td></td><td>Write(A)</td></tr><tr><td></td><td>Read(B)</td></tr><tr><td>Write(A)</td><td></td></tr><tr><td>Read(B)</td><td></td></tr><tr><td>B = B + 10</td><td></td></tr><tr><td>Write(B)</td><td></td></tr><tr><td></td><td>B = B + Temp</td></tr><tr><td></td><td>Write(B)</td></tr></table>

Which of the following is TRUE about the schedule S?

A. $S$ is serializable only as $T1, T2$  
B. $S$ is serializable only as $T2, T1$  
C. $S$ is serializable both as $T1, T2$ and $T2, T1$  
D. $S$ is not serializable either as $T1, T2$ or as $T2, T1$

gateit-2004 databases transaction-and-concurrency normal

Answer key

# 3.25.24 Transaction and Concurrency: GATE IT 2005 | Question: 24

Amongst the ACID properties of a transaction, the 'Durability' property requires that the changes made to the database by a successful transaction persist


A. Except in case of an Operating System crash  
B. Except in case of a Disk crash  
C. Except in case of a power failure  
D. Always, even if there is a failure of any kind

gateit-2005 databases transaction-and-concurrency easy

Answer key

A company maintains records of sales made by its salespersons and pays them commission based on each individual's total sales made in a year. This data is maintained in a table with following schema:

salesinfo = (salespersonid, totalsales, commission)

In a certain year, due to better business results, the company decides to further reward its salespersons by enhancing the commission paid to them as per the following formula:

If commission ≤ 50000, enhance it by 2%

If 50000 < commission ≤ 100000, enhance it by 4%

If commission > 100000, enhance it by 6%

The IT staff has written three different SQL scripts to calculate enhancement for each slab, each of these scripts is to run as a separate transaction as follows:

T1

```txt
Update salesinfo
Set commission = commission * 1.02
Where commission <= 50000;
```

T2

```txt
Update salesinfo
Set commission = commission * 1.04
Where commission > 50000 and
commission is <= 100000;
```

T3

```txt
Update salesinfo
Set commission = commission * 1.06
Where commission > 100000;
```

Which of the following options of running these transactions will update the commission of all salespersons correctly

A. Execute T1 followed by T2 followed by T3  
B. Execute T2, followed by T3; T1 running concurrently throughout  
C. Execute T3 followed by T2; T1 running concurrently throughout  
D. Execute T3 followed by T2 followed by T1

gateit-2005

databases

transaction-and-concurrency

normal

Answer key

# 3.25.26 Transaction and Concurrency: GATE IT 2007 | Question: 66

Consider the following two transactions: T1 and T2.

T1: read (A);

read (B);

If $A = 0$ then $B \leftarrow B + 1$ ;

write (B);

T2: read (B);

read (A);

If $B \neq 0$ then $A \leftarrow A - 1$ ;

write (A);


Which of the following schemes, using shared and exclusive locks, satisfy the requirements for strict two phase locking for the above transactions?

<table><tr><td rowspan="10">A.</td><td rowspan="10">S1:</td><td>lock S(A);</td><td rowspan="10">S2:</td><td>lock S(B);</td></tr><tr><td>read (A);</td><td>read (B);</td></tr><tr><td>lock S(B);</td><td>lock S(A);</td></tr><tr><td>read (B);</td><td>read (A);</td></tr><tr><td>If A = 0</td><td>If B ≠ 0</td></tr><tr><td>then B ← B + 1;</td><td>then A ← A - 1;</td></tr><tr><td>write (B);</td><td>write (A);</td></tr><tr><td>commit;</td><td>commit;</td></tr><tr><td>unlock (A);</td><td>unlock (B);</td></tr><tr><td>unlock (B);</td><td>unlock (A);</td></tr><tr><td rowspan="10">B.</td><td rowspan="10">S1:</td><td>lock X(A);</td><td rowspan="10">S2:</td><td>lock X(B);</td></tr><tr><td>read (A);</td><td>read (B);</td></tr><tr><td>lock X(B);</td><td>lock X(A);</td></tr><tr><td>read (B);</td><td>read (A);</td></tr><tr><td>If A = 0</td><td>If B ≠ 0</td></tr><tr><td>then B ← B + 1;</td><td>then A ← A - 1;</td></tr><tr><td>write (B);</td><td>write (A);</td></tr><tr><td>unlock (A);</td><td>unlock (A);</td></tr><tr><td>commit;</td><td>commit;</td></tr><tr><td>unlock (B);</td><td>unlock (A);</td></tr><tr><td rowspan="10">C.</td><td rowspan="10">S1:</td><td>lock S(A);</td><td rowspan="10">S2:</td><td>lock S(B);</td></tr><tr><td>read (A);</td><td>read (B);</td></tr><tr><td>lock X(B);</td><td>lock X(A);</td></tr><tr><td>read (B);</td><td>read (A);</td></tr><tr><td>If A = 0</td><td>If B ≠ 0</td></tr><tr><td>then B ← B + 1;</td><td>then A ← A - 1;</td></tr><tr><td>write (B);</td><td>write(A);</td></tr><tr><td>unlock (A);</td><td>unlock (B);</td></tr><tr><td>commit;</td><td>commit;</td></tr><tr><td>unlock (B);</td><td>unlock (A);</td></tr><tr><td rowspan="10">D.</td><td rowspan="10">S1:</td><td>lock S(A);</td><td rowspan="10">S2:</td><td>lock S(B);</td></tr><tr><td>read (A);</td><td>read (B);</td></tr><tr><td>lock X(B);</td><td>lock X(A);</td></tr><tr><td>read (B);</td><td>read (A);</td></tr><tr><td>If A = 0</td><td>If B ≠ 0</td></tr><tr><td>then B ← B + 1;</td><td>then A ←A - 1;</td></tr><tr><td>write (B);</td><td>write (A);</td></tr><tr><td>unlock (A);</td><td>unlock (A);</td></tr><tr><td>unlock (B);</td><td>unlock (A);</td></tr><tr><td>commit;</td><td>commit;</td></tr></table>

# 3.25.27 Transaction and Concurrency: GATE IT 2008 | Question: 63


Consider the following three schedules of transactions T1, T2 and T3. [Notation: In the following NYO represents the action Y (R for read, W for write) performed by transaction N on object O.]

<table><tr><td>(S1)</td><td>2RA</td><td>2WA</td><td>3RC</td><td>2WB</td><td>3WA</td><td>3WC</td><td>1RA</td><td>1RB</td><td>1WA</td><td>1WB</td></tr><tr><td>(S2)</td><td>3RC</td><td>2RA</td><td>2WA</td><td>2WB</td><td>3WA</td><td>1RA</td><td>1RB</td><td>1WA</td><td>1WB</td><td>3WC</td></tr><tr><td>(S3)</td><td>2RA</td><td>3RC</td><td>3WA</td><td>2WA</td><td>2WB</td><td>3WC</td><td>1RA</td><td>1RB</td><td>1WA</td><td>1WB</td></tr></table>

Which of the following statements is TRUE?

A. S1, S2 and S3 are all conflict equivalent to each other  
B. No two of S1, S2 and S3 are conflict equivalent to each other  
C. S2 is conflict equivalent to S3, but not to S1  
D. S1 is conflict equivalent to S2, but not to S3

gateit-2008 databases transaction-and-concurrency normal

Answer key

# 3.26

# Tuple Relational Calculus (3)

# 3.26.1 Tuple Relational Calculus: GATE CSE 2025 | Set 1 | Question: 29

Consider two relations describing teams and players in a sports league:


- teams(tid, tname): tid, tname are team-id and team-name, respectively  
- players(pid,pname,tid): pid, pname, and tid denote player-id, playername and the team-id of the player, respectively

Which ONE of the following tuple relational calculus queries returns the name of the players who play for the team having tname as 'MI'?

A. $\{p.$ pname $|p\in$ players $\wedge \exists t$ ( $t\in$ teams $\wedge p.tid = t.tid\wedge t.tname = 'MI'\})\}$  
B. $\{p.$ pname $|p\in$ teams $\wedge \exists t$ ( $t\in$ players $\wedge p.tid = t.tid\wedge t.tname = 'MI'\})\}$  
C. $\{p.$ pname $|p\in$ players $\wedge \exists t(t\in$ teams $\wedge t.$ tname $= ^{\prime}MI^{\prime})\}$  
D. $\{p.$ pname $|p\in$ teams $\wedge \exists t(t\in$ players $\wedge t.$ tname $= 'MI'\}$

gatecse2025-set1 databases tuple-relational-calculus two-marks

Answer key

# 3.26.2 Tuple Relational Calculus: GATE CSE 2026 | Set 1 | Question: 33

Consider a relational database schema with two relations $R(P, Q)$ and $S(X, Y)$ .

Let $E = \{\langle u\rangle \mid \exists v\exists w\langle u,v\rangle \in R \land \langle v,w\rangle \in S\}$ be a tuple relational calculus expression.

Which one of the following relational algebraic expressions is equivalent to $E$ ?

A. $\Pi_P(R \bowtie_{R.P=S.X} S)$

C. $\Pi_{P}(R\bowtie_{R.P=S.Y}S)$

B. $\Pi_P(S \bowtie_{S.X = R.Q} R)$

D. $\Pi_{P}(S\bowtie_{S.Y=R.Q}R)$

gatecse-2026-set1 databases two-marks tuple-relational-calculus

Answer key

# 3.26.3 Tuple Relational Calculus: GATE DA 2026 | Question: 49

Let there be two relations $X$ and $Y$ as shown. $X$ has three columns $P, Q$ and $R$ . $Y$ has two columns $P$ and $S$ .



<table><tr><td>P</td><td>Q</td><td>R</td></tr><tr><td>P1</td><td>Q1</td><td>R1</td></tr><tr><td>P2</td><td>Q2</td><td>R2</td></tr><tr><td>P3</td><td>Q3</td><td>R2</td></tr></table>

Y

<table><tr><td>P</td><td>S</td></tr><tr><td>P1</td><td>10</td></tr><tr><td>P1</td><td>15</td></tr><tr><td>P2</td><td>20</td></tr><tr><td>P3</td><td>1</td></tr></table>

Consider that the following tuple relational calculus expression is evaluated.

$$
\{t \mid t \in X \land \exists z \in X (t [ P ] = z [ P ]) \land \exists m \in Y (m [ P ] = t [ P ] \land m [ S ] > 1) \}
$$

The number of tuples that will be returned is \_\_\_\_. (Answer in integer)

gateda-2026 databases tuple-relational-calculus numerical-answers two-marks

Answer key

# 3.27

# Two Phase Locking Protocol (1)

# 3.27.1 Two Phase Locking Protocol: GATE CSE 2024 | Set 2 | Question: 17

Which of the following statements about the Two Phase Locking (2PL) protocol is/are TRUE?


A. 2PL permits only serializable schedules  
B. With 2PL, a transaction always locks the data item being read or written just before every operation and always releases the lock just after the operation  
C. With 2PL, once a lock is released on any data item inside a transaction, no more locks on any data item can be obtained inside that transaction  
D. A deadlock is possible with 2PL

gatecse-2024-set2 databases two-phase-locking-protocol multiple-selects transaction-and-concurrency one-mark

Answer key

# Answer Keys

<table><tr><td>3.1.1</td><td>D</td></tr><tr><td>3.2.5</td><td>B</td></tr><tr><td>3.2.10</td><td>N/A</td></tr><tr><td>3.2.15</td><td>A</td></tr><tr><td>3.2.20</td><td>50</td></tr><tr><td>3.2.25</td><td>B;D</td></tr><tr><td>3.2.30</td><td>C</td></tr><tr><td>3.3.3</td><td>A</td></tr></table>

<table><tr><td>3.2.1</td><td>N/A</td></tr><tr><td>3.2.6</td><td>N/A</td></tr><tr><td>3.2.11</td><td>C</td></tr><tr><td>3.2.16</td><td>C</td></tr><tr><td>3.2.21</td><td>A</td></tr><tr><td>3.2.26</td><td>33:33</td></tr><tr><td>3.2.31</td><td>A</td></tr><tr><td>3.3.4</td><td>8</td></tr></table>

<table><tr><td>3.2.2</td><td>N/A</td></tr><tr><td>3.2.7</td><td>B</td></tr><tr><td>3.2.12</td><td>B</td></tr><tr><td>3.2.17</td><td>C</td></tr><tr><td>3.2.22</td><td>52</td></tr><tr><td>3.2.27</td><td>A</td></tr><tr><td>3.2.32</td><td>A</td></tr><tr><td>3.3.5</td><td>19</td></tr></table>

<table><tr><td>3.2.3</td><td>N/A</td></tr><tr><td>3.2.8</td><td>N/A</td></tr><tr><td>3.2.13</td><td>C</td></tr><tr><td>3.2.18</td><td>B</td></tr><tr><td>3.2.23</td><td>B</td></tr><tr><td>3.2.28</td><td>C</td></tr><tr><td>3.3.1</td><td>N/A</td></tr><tr><td>3.3.6</td><td>B</td></tr></table>

<table><tr><td>3.2.4</td><td>N/A</td></tr><tr><td>3.2.9</td><td>N/A</td></tr><tr><td>3.2.14</td><td>D</td></tr><tr><td>3.2.19</td><td>5</td></tr><tr><td>3.2.24</td><td>A</td></tr><tr><td>3.2.29</td><td>A</td></tr><tr><td>3.3.2</td><td>D</td></tr><tr><td>3.3.7</td><td>A</td></tr></table>

<table><tr><td>3.4.1</td><td>C</td></tr><tr><td>3.4.6</td><td>54</td></tr><tr><td>3.4.11</td><td>B;C;D</td></tr><tr><td>3.6.3</td><td>N/A</td></tr><tr><td>3.6.8</td><td>False</td></tr><tr><td>3.6.13</td><td>B</td></tr><tr><td>3.6.18</td><td>N/A</td></tr><tr><td>3.6.23</td><td>C</td></tr><tr><td>3.6.28</td><td>B</td></tr><tr><td>3.6.33</td><td>B</td></tr><tr><td>3.6.38</td><td>A</td></tr><tr><td>3.6.43</td><td>A;C</td></tr><tr><td>3.6.48</td><td>A;B;D</td></tr><tr><td>3.6.53</td><td>B</td></tr><tr><td>3.8.1</td><td>C</td></tr><tr><td>3.9.5</td><td>4</td></tr><tr><td>3.9.10</td><td>A</td></tr><tr><td>3.10.3</td><td>B;D</td></tr><tr><td>3.11.5</td><td>A</td></tr><tr><td>3.11.10</td><td>4</td></tr><tr><td>3.11.15</td><td>195:195</td></tr><tr><td>3.12.5</td><td>B</td></tr><tr><td>3.14.2</td><td>A</td></tr><tr><td>3.16.3</td><td>3:3</td></tr><tr><td>3.17.5</td><td>D</td></tr><tr><td>3.18.4</td><td>N/A</td></tr><tr><td>3.18.9</td><td>B</td></tr><tr><td>3.18.14</td><td>N/A</td></tr><tr><td>3.18.19</td><td>A</td></tr><tr><td>3.18.24</td><td>1</td></tr><tr><td>3.18.29</td><td>1:1</td></tr><tr><td>3.19.1</td><td>N/A</td></tr><tr><td>3.19.6</td><td>B</td></tr><tr><td>3.19.11</td><td>D</td></tr><tr><td>3.21.1</td><td>N/A</td></tr><tr><td>3.21.6</td><td>N/A</td></tr><tr><td>3.21.11</td><td>A</td></tr><tr><td>3.21.16</td><td>N/A</td></tr><tr><td>3.21.21</td><td>B</td></tr><tr><td>3.21.26</td><td>C</td></tr></table>

<table><tr><td>3.4.2</td><td>B</td></tr><tr><td>3.4.7</td><td>A</td></tr><tr><td>3.4.12</td><td>B</td></tr><tr><td>3.6.4</td><td>N/A</td></tr><tr><td>3.6.9</td><td>N/A</td></tr><tr><td>3.6.14</td><td>D</td></tr><tr><td>3.6.19</td><td>C</td></tr><tr><td>3.6.24</td><td>C</td></tr><tr><td>3.6.29</td><td>A</td></tr><tr><td>3.6.34</td><td>B</td></tr><tr><td>3.6.39</td><td>A</td></tr><tr><td>3.6.44</td><td>B;C;D</td></tr><tr><td>3.6.49</td><td>TBA</td></tr><tr><td>3.6.54</td><td>A</td></tr><tr><td>3.9.1</td><td>B</td></tr><tr><td>3.9.6</td><td>C</td></tr><tr><td>3.9.11</td><td>B</td></tr><tr><td>3.11.1</td><td>N/A</td></tr><tr><td>3.11.6</td><td>C</td></tr><tr><td>3.11.11</td><td>698 : 698</td></tr><tr><td>3.12.1</td><td>A</td></tr><tr><td>3.12.6</td><td>A</td></tr><tr><td>3.14.3</td><td>C</td></tr><tr><td>3.17.1</td><td>B</td></tr><tr><td>3.17.6</td><td>A;B</td></tr><tr><td>3.18.5</td><td>N/A</td></tr><tr><td>3.18.10</td><td>C</td></tr><tr><td>3.18.15</td><td>A</td></tr><tr><td>3.18.20</td><td>D</td></tr><tr><td>3.18.25</td><td>C</td></tr><tr><td>3.18.30</td><td>C</td></tr><tr><td>3.19.2</td><td>D</td></tr><tr><td>3.19.7</td><td>C</td></tr><tr><td>3.19.12</td><td>D</td></tr><tr><td>3.21.2</td><td>N/A</td></tr><tr><td>3.21.7</td><td>N/A</td></tr><tr><td>3.21.12</td><td>C</td></tr><tr><td>3.21.17</td><td>C</td></tr><tr><td>3.21.22</td><td>C</td></tr><tr><td>3.21.27</td><td>A</td></tr></table>

<table><tr><td>3.4.3</td><td>D</td></tr><tr><td>3.4.8</td><td>B</td></tr><tr><td>3.5.1</td><td>False</td></tr><tr><td>3.6.5</td><td>N/A</td></tr><tr><td>3.6.10</td><td>A</td></tr><tr><td>3.6.15</td><td>B</td></tr><tr><td>3.6.20</td><td>C</td></tr><tr><td>3.6.25</td><td>D</td></tr><tr><td>3.6.30</td><td>B</td></tr><tr><td>3.6.35</td><td>A</td></tr><tr><td>3.6.40</td><td>A;C;D</td></tr><tr><td>3.6.45</td><td>50</td></tr><tr><td>3.6.50</td><td>B</td></tr><tr><td>3.6.55</td><td>D</td></tr><tr><td>3.9.2</td><td>B</td></tr><tr><td>3.9.7</td><td>A</td></tr><tr><td>3.9.12</td><td>C</td></tr><tr><td>3.11.2</td><td>N/A</td></tr><tr><td>3.11.7</td><td>C</td></tr><tr><td>3.11.12</td><td>6</td></tr><tr><td>3.12.2</td><td>A</td></tr><tr><td>3.12.7</td><td>A</td></tr><tr><td>3.15.1</td><td>4:4</td></tr><tr><td>3.17.2</td><td>C</td></tr><tr><td>3.18.1</td><td>N/A</td></tr><tr><td>3.18.6</td><td>N/A</td></tr><tr><td>3.18.11</td><td>D</td></tr><tr><td>3.18.16</td><td>D</td></tr><tr><td>3.18.21</td><td>D</td></tr><tr><td>3.18.26</td><td>A;B</td></tr><tr><td>3.18.31</td><td>D</td></tr><tr><td>3.19.3</td><td>C</td></tr><tr><td>3.19.8</td><td>C</td></tr><tr><td>3.19.13</td><td>C</td></tr><tr><td>3.21.3</td><td>N/A</td></tr><tr><td>3.21.8</td><td>D</td></tr><tr><td>3.21.13</td><td>N/A</td></tr><tr><td>3.21.18</td><td>D</td></tr><tr><td>3.21.23</td><td>A</td></tr><tr><td>3.21.28</td><td>C</td></tr></table>

<table><tr><td>3.4.4</td><td>C</td></tr><tr><td>3.4.9</td><td>B</td></tr><tr><td>3.6.1</td><td>True</td></tr><tr><td>3.6.6</td><td>N/A</td></tr><tr><td>3.6.11</td><td>D</td></tr><tr><td>3.6.16</td><td>C</td></tr><tr><td>3.6.21</td><td>D</td></tr><tr><td>3.6.26</td><td>C</td></tr><tr><td>3.6.31</td><td>A</td></tr><tr><td>3.6.36</td><td>B</td></tr><tr><td>3.6.41</td><td>8</td></tr><tr><td>3.6.46</td><td>C;D</td></tr><tr><td>3.6.51</td><td>A</td></tr><tr><td>3.6.56</td><td>C</td></tr><tr><td>3.9.3</td><td>A</td></tr><tr><td>3.9.8</td><td>A</td></tr><tr><td>3.10.1</td><td>B;C</td></tr><tr><td>3.11.3</td><td>3</td></tr><tr><td>3.11.8</td><td>C</td></tr><tr><td>3.11.13</td><td>A;B</td></tr><tr><td>3.12.3</td><td>A</td></tr><tr><td>3.13.1</td><td>C</td></tr><tr><td>3.16.1</td><td>N/A</td></tr><tr><td>3.17.3</td><td>A</td></tr><tr><td>3.18.2</td><td>N/A</td></tr><tr><td>3.18.7</td><td>D</td></tr><tr><td>3.18.12</td><td>C</td></tr><tr><td>3.18.17</td><td>B</td></tr><tr><td>3.18.22</td><td>4</td></tr><tr><td>3.18.27</td><td>2</td></tr><tr><td>3.18.32</td><td>C</td></tr><tr><td>3.19.4</td><td>C</td></tr><tr><td>3.19.9</td><td>A</td></tr><tr><td>3.20.1</td><td>A</td></tr><tr><td>3.21.4</td><td>N/A</td></tr><tr><td>3.21.9</td><td>N/A</td></tr><tr><td>3.21.14</td><td>C</td></tr><tr><td>3.21.19</td><td>D</td></tr><tr><td>3.21.24</td><td>X</td></tr><tr><td>3.21.29</td><td>C</td></tr></table>

<table><tr><td>3.4.5</td><td>A</td></tr><tr><td>3.4.10</td><td>A</td></tr><tr><td>3.6.2</td><td>N/A</td></tr><tr><td>3.6.7</td><td>A;B;D</td></tr><tr><td>3.6.12</td><td>N/A</td></tr><tr><td>3.6.17</td><td>A</td></tr><tr><td>3.6.22</td><td>B</td></tr><tr><td>3.6.27</td><td>C</td></tr><tr><td>3.6.32</td><td>C</td></tr><tr><td>3.6.37</td><td>C</td></tr><tr><td>3.6.42</td><td>A</td></tr><tr><td>3.6.47</td><td>A;B;C</td></tr><tr><td>3.6.52</td><td>B</td></tr><tr><td>3.7.1</td><td>C</td></tr><tr><td>3.9.4</td><td>C</td></tr><tr><td>3.9.9</td><td>D</td></tr><tr><td>3.10.2</td><td>C;D</td></tr><tr><td>3.11.4</td><td>C</td></tr><tr><td>3.11.9</td><td>C</td></tr><tr><td>3.11.14</td><td>A</td></tr><tr><td>3.12.4</td><td>C</td></tr><tr><td>3.14.1</td><td>C</td></tr><tr><td>3.16.2</td><td>A</td></tr><tr><td>3.17.4</td><td>0.00</td></tr><tr><td>3.18.3</td><td>N/A</td></tr><tr><td>3.18.8</td><td>N/A</td></tr><tr><td>3.18.13</td><td>N/A</td></tr><tr><td>3.18.18</td><td>D</td></tr><tr><td>3.18.23</td><td>C</td></tr><tr><td>3.18.28</td><td>B</td></tr><tr><td>3.18.33</td><td>B</td></tr><tr><td>3.19.5</td><td>C</td></tr><tr><td>3.19.10</td><td>A</td></tr><tr><td>3.20.2</td><td>B;C</td></tr><tr><td>3.21.5</td><td>N/A</td></tr><tr><td>3.21.10</td><td>N/A</td></tr><tr><td>3.21.15</td><td>N/A</td></tr><tr><td>3.21.20</td><td>C</td></tr><tr><td>3.21.25</td><td>A</td></tr><tr><td>3.21.30</td><td>B</td></tr></table>

<table><tr><td>3.21.31</td><td>D</td></tr><tr><td>3.21.36</td><td>A</td></tr><tr><td>3.21.41</td><td>5</td></tr><tr><td>3.21.46</td><td>2</td></tr><tr><td>3.21.51</td><td>A;B</td></tr><tr><td>3.21.56</td><td>A</td></tr><tr><td>3.24.1</td><td>A</td></tr><tr><td>3.25.5</td><td>B</td></tr><tr><td>3.25.10</td><td>A</td></tr><tr><td>3.25.15</td><td>C</td></tr><tr><td>3.25.20</td><td>B;C</td></tr><tr><td>3.25.25</td><td>D</td></tr><tr><td>3.26.3</td><td>2</td></tr></table>

<table><tr><td>3.21.32</td><td>B</td></tr><tr><td>3.21.37</td><td>2</td></tr><tr><td>3.21.42</td><td>A</td></tr><tr><td>3.21.47</td><td>26:26</td></tr><tr><td>3.21.52</td><td>D</td></tr><tr><td>3.21.57</td><td>B</td></tr><tr><td>3.25.1</td><td>TBA</td></tr><tr><td>3.25.6</td><td>B</td></tr><tr><td>3.25.11</td><td>B</td></tr><tr><td>3.25.16</td><td>C</td></tr><tr><td>3.25.21</td><td>A</td></tr><tr><td>3.25.26</td><td>C</td></tr><tr><td>3.27.1</td><td>A;C;D</td></tr></table>

<table><tr><td>3.21.33</td><td>C</td></tr><tr><td>3.21.38</td><td>2.6</td></tr><tr><td>3.21.43</td><td>819 : 820 ; 205 : 205</td></tr><tr><td>3.21.48</td><td>A;C;D</td></tr><tr><td>3.21.53</td><td>C</td></tr><tr><td>3.21.58</td><td>D</td></tr><tr><td>3.25.2</td><td>D</td></tr><tr><td>3.25.7</td><td>A</td></tr><tr><td>3.25.12</td><td>D</td></tr><tr><td>3.25.17</td><td>A</td></tr><tr><td>3.25.22</td><td>C</td></tr><tr><td>3.25.27</td><td>D</td></tr></table>

<table><tr><td>3.21.34</td><td>D</td></tr><tr><td>3.21.39</td><td>7</td></tr><tr><td>3.21.44</td><td>B</td></tr><tr><td>3.21.49</td><td>3:3</td></tr><tr><td>3.21.54</td><td>C</td></tr><tr><td>3.22.1</td><td>D</td></tr><tr><td>3.25.3</td><td>D</td></tr><tr><td>3.25.8</td><td>B</td></tr><tr><td>3.25.13</td><td>A</td></tr><tr><td>3.25.18</td><td>A</td></tr><tr><td>3.25.23</td><td>X</td></tr><tr><td>3.26.1</td><td>A</td></tr></table>

<table><tr><td>3.21.35</td><td>2</td></tr><tr><td>3.21.40</td><td>D</td></tr><tr><td>3.21.45</td><td>2</td></tr><tr><td>3.21.50</td><td>3</td></tr><tr><td>3.21.55</td><td>D</td></tr><tr><td>3.23.1</td><td>6 : 6</td></tr><tr><td>3.25.4</td><td>D</td></tr><tr><td>3.25.9</td><td>B</td></tr><tr><td>3.25.14</td><td>A</td></tr><tr><td>3.25.19</td><td>C</td></tr><tr><td>3.25.24</td><td>D</td></tr><tr><td>3.26.2</td><td>B</td></tr></table>

Boolean algebra. Combinational and sequential circuits. Minimization. Number representations and computer arithmetic (fixed and floating point)

Mark Distribution in Previous GATE

<table><tr><td>Year</td><td>2026 - 1</td><td>2026 - 2</td><td>2025 - 1</td><td>2025 - 2</td><td>2024 - 1</td><td>2024 - 2</td><td>2023</td><td>2022</td><td>2021 - 1</td><td>2021 - 2</td><td>Minimum</td></tr><tr><td>1 Mark Count</td><td>2</td><td>3</td><td>2</td><td>3</td><td>2</td><td>2</td><td>2</td><td>1</td><td>2</td><td>3</td><td>1</td></tr><tr><td>2 Marks Count</td><td>3</td><td>2</td><td>2</td><td>3</td><td>2</td><td>2</td><td>2</td><td>2</td><td>2</td><td>2</td><td>2</td></tr><tr><td>Total Marks</td><td>8</td><td>7</td><td>6</td><td>9</td><td>6</td><td>6</td><td>6</td><td>5</td><td>6</td><td>7</td><td>5</td></tr></table>

Welcome to the "Digital Logic" chapter of your GATE Computer Science exam preparation. This foundational subject is the bedrock of computer hardware, providing the essential understanding of how digital circuits process information, store data, and execute instructions. It delves into the fundamental building blocks of modern computing systems, from basic logic gates to complex sequential circuits and memory elements. A strong grasp of Digital Logic is crucial not only for direct questions in the GATE exam but also for understanding related concepts in Computer Architecture, Operating Systems, and even some aspects of programming. Typically, Digital Logic carries a weightage of 8-12 marks in the GATE CS paper, with questions ranging from conceptual understanding and circuit analysis to design problems involving minimization, number representation, and sequential circuit behavior. Questions often include Multiple Choice Questions (MCQs), Multiple Select Questions (MSQs), and Numerical Answer Type (NAT) questions, testing both theoretical knowledge and problem-solving skills.

# Topic-wise Key Concepts

# Adder

An adder is a digital circuit that performs the addition of numbers. It is a fundamental component in Arithmetic Logic Units (ALUs) of processors.

\- Half Adder (HA): Adds two single-bit binary numbers. It produces a sum (S) and a carry-out (Cout).

\- Formulas:

$$
S = A \oplus B
$$

$$
C _ {o u t} = A \cdot B
$$

\- Full Adder (FA): Adds three single-bit binary numbers (two input bits and a carry-in). It produces a sum (S) and a carry-out (Cout).

\- Formulas:

$$
S = A \oplus B \oplus C _ {i n}
$$

$$
C _ {o u t} = (A \cdot B) + (C _ {i n} \cdot (A \oplus B))
$$

$$
C _ {o u t} = (A \cdot B) + (B \cdot C _ {i n}) + (C _ {i n} \cdot A)
$$

\- Ripple Carry Adder: An n-bit adder constructed by cascading n full adders, where the carry-out of one stage becomes the carry-in of the next.

\- Propagation Delay: The total delay is proportional to n, as carry ripples through all stages.

$$
T _ {r i p p l e} = n \times T _ {F A \_ c a r r y}.
$$

\- Carry Look-Ahead Adder (CLA): A faster adder that generates carries in parallel, reducing propagation delay. It uses carry generate (G) and carry propagate (P) signals.

\- Formulas for a single stage i:

$$
P _ {i} = A _ {i} \oplus B _ {i}
$$

$$
G _ {i} = A _ {i} \cdot B _ {i}
$$

$$
S _ {i} = P _ {i} \oplus C _ {i}
$$

$$
C _ {i + 1} = G _ {i} + (P _ {i} \cdot C _ {i})
$$

\- For a 4-bit CLA:

$$
C _ {1} = G _ {0} + P _ {0} C _ {0}
$$

$$
C _ {2} = G _ {1} + P _ {1} C _ {1} = G _ {1} + P _ {1} G _ {0} + P _ {1} P _ {0} C _ {0}
$$

$$
C _ {3} = G _ {2} + P _ {2} C _ {2} = G _ {2} + P _ {2} G _ {1} + P _ {2} P _ {1} G _ {0} + P _ {2} P _ {1} P _ {0} C _ {0}
$$

$$
C _ {4} = G _ {3} + P _ {3} C _ {3} = G _ {3} + P _ {3} G _ {2} + P _ {3} P _ {2} G _ {1} + P _ {3} P _ {2} P _ {1} G _ {0} + P _ {3} P _ {2} P _ {1} P _ {0} C _ {0}
$$

- Common Pitfalls: Confusing half adder and full adder functionality. Incorrectly calculating propagation delay for ripple carry vs. CLA.  
- Problem-solving: Be able to draw and analyze basic adder circuits. Calculate delays for different adder types.

# Array Multiplier

An array multiplier is a combinational circuit that performs multiplication of two binary numbers using an array of full adders and AND gates. It's a direct hardware implementation of the traditional "paper-and-pencil" multiplication method.

- Core Idea: For two n-bit numbers, it requires n rows of partial products. Each partial product is generated by ANDing the multiplicand with one bit of the multiplier. These partial products are then summed using an array of adders (often full adders) in a staggered fashion.  
- Structure: An n x m bit array multiplier typically uses n\*m AND gates to generate partial products and (n-1)\*m full adders (or similar) to sum them.  
- Delay: The delay is proportional to $n + m$ , as carries propagate diagonally across the array.  
- Problem-solving: Understand how partial products are formed and summed. Be able to trace the data flow for small examples.

# Binary Codes

Binary codes are systems used to represent numbers, characters, and instructions in digital systems using binary digits (bits).

\- Weighted Codes: Each bit position has a specific weight.

- BCD (8421): Each decimal digit is represented by its 4-bit binary equivalent. E.g., $(9)_{10} = (1001)_{BCD}$ . $(25)_{10} = (00100101)_{BCD}$ .  
- Excess-3: BCD code with 3 added to each digit. Self-complementing.  
- 2421 Code: Another weighted code.

\- Non-Weighted Codes: Bit positions do not have fixed weights.

\- Gray Code: Only one bit changes between successive numbers. Used to prevent glitches in ADCs and K-maps.

- Binary to Gray: $G_{i} = B_{i} \oplus B_{i+1}$ (for MSB to LSB, $G_{n-1} = B_{n-1}$ , $G_{i} = B_{i} \oplus B_{i+1}$ for $i < n-1$ ). More commonly: $G_{i} = B_{i} \oplus B_{i+1}$ , with $B_{n} = 0$ for the MSB. Correct: $G_{MSB} = B_{MSB}$ , $G_{i} = B_{i} \oplus B_{i+1}$ for $i$ from MSB-1 down to 0. Alternative: $G_{i} = B_{i} \oplus B_{i-1}$ for $i > 0$ , $G_{0} = B_{0}$ . Example: Binary 1011 (11) -> Gray: $G_{3} = 1$ , $G_{2} = 1 \oplus 0 = 1$ , $G_{1} = 0 \oplus 1 = 1$ , $G_{0} = 1 \oplus 1 = 0$ . So 1110.  
- Gray to Binary: $B_{MSB} = G_{MSB}$ , $B_i = G_i \oplus B_{i+1}$ (for MSB to LSB). Correct: $B_i = G_i \oplus B_{i+1}$ for $i$ from MSB-1 down to 0, $B_{MSB} = G_{MSB}$ . Example: Gray 1110 -> Binary: $B_3 = 1, B_2 = 1 \oplus 1 = 0, B_1 = 1 \oplus 0 = 1, B_0 = 0 \oplus 1 = 1$ . So 1011.

\- ASCII: 7-bit or 8-bit code for characters.

\- Error Detection Codes (Parity): Adds an extra bit to detect single-bit errors.

- Even Parity: Total number of 1s (including parity bit) is even.  
- Odd Parity: Total number of 1s (including parity bit) is odd.

- Error Correction Codes (Hamming Code): Can detect and correct multiple-bit errors.  
- Common Pitfalls: Confusing BCD with pure binary. Incorrectly converting between binary and Gray code.  
- Problem-solving: Perform conversions between different binary codes.

# Boolean Algebra

Boolean algebra is a mathematical system for analyzing and simplifying digital circuits. It deals with binary variables and logical operations.

\- Basic Postulates:

1. Closure: $A + B$ and $A \cdot B$ are in $\{0,1\}$ .  
2. Commutative: $A + B = B + A$ , $A \cdot B = B \cdot A$ .  
3. Associative: $A + (B + C) = (A + B) + C$ , $A \cdot (B \cdot C) = (A \cdot B) \cdot C$ .