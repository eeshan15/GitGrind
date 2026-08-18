# Answer key

# 5.25.7 Resource Allocation: GATE CSE 1997 | Question: 6.7


An operating system contains 3 user processes each requiring 2 units of resource $R$ . The minimum number of units of $R$ such that no deadlocks will ever arise is

A. 3

B. 5

C. 4

D. 6

gate1997 operating-system resource-allocation normal

# Answer key

# 5.25.8 Resource Allocation: GATE CSE 1997 | Question: 75


An operating system handles requests to resources as follows.

A process (which asks for some resources, uses them for some time and then exits the system) is assigned a unique timestamp are when it starts. The timestamps are monotonically increasing with time. Let us denote the timestamp of a process $P$ by $TS(P)$ .

When a process P requests for a resource the OS does the following:

i. If no other process is currently holding the resource, the $OS$ awards the resource to $P$ .  
ii. If some process $Q$ with $TS(Q) < TS(P)$ is holding the resource, the $OS$ makes $P$ wait for the resources.  
iii. If some process $Q$ with $TS(Q) > TS(P)$ is holding the resource, the $OS$ restarts $Q$ and awards the resources to $P$ . (Restarting means taking back the resources held by a process, killing it and starting it again with the same timestamp)

When a process releases a resource, the process with the smallest timestamp (if any) amongst those waiting for the resource is awarded the resource.

A. Can a deadlock over arise? If yes, show how. If not prove it.  
B. Can a process P ever starve? If yes, show how. If not prove it.

gate1997 operating-system resource-allocation normal descriptive

# Answer key

# 5.25.9 Resource Allocation: GATE CSE 1998 | Question: 1.32


A computer has six tape drives, with n processes competing for them. Each process may need two drives. What is the maximum value of n for the system to be deadlock free?

A. 6

B. 5

C. 4

D. 3

gate1998 operating-system resource-allocation normal

# Answer key

# 5.25.10 Resource Allocation: GATE CSE 2000 | Question: 2.23


Which of the following is not a valid deadlock prevention scheme?

A. Release all resources before requesting a new resource.  
B. Number the resources uniquely and never request a lower numbered resource than the last one requested.  
C. Never request a resource after releasing any resource.  
D. Request and all required resources be allocated before execution.

gatecse-2000 operating-system resource-allocation normal

# Answer key

Two concurrent processes $P1$ and $P2$ want to use resources $R1$ and $R2$ in a mutually exclusive manner. Initially, $R1$ and $R2$ are free. The programs executed by the two processes are given below.

<table><tr><td colspan="2">Program for P1:</td><td colspan="2">Program for P2:</td></tr><tr><td>S1:</td><td>While (R1 is busy) do no-op;</td><td>Q1:</td><td>While (R1 is busy) do no-op;</td></tr><tr><td>S2:</td><td>Set R1 ← busy;</td><td>Q2:</td><td>Set R1 ← busy;</td></tr><tr><td>S3:</td><td>While (R2 is busy) do no-op;</td><td>Q3:</td><td>While (R2 is busy) do no-op;</td></tr><tr><td>S4:</td><td>Set R2 ← busy;</td><td>Q4:</td><td>Set R2 ← busy;</td></tr><tr><td>S5:</td><td>Use R1 and R2;</td><td>Q5:</td><td>Use R1 and R2;</td></tr><tr><td>S6:</td><td>Set R1 ← free;</td><td>Q6:</td><td>Set R2 ← free;</td></tr><tr><td>S7:</td><td>Set R2 ← free;</td><td>Q7:</td><td>Set R1 ← free;</td></tr></table>

A. Is mutual exclusion guaranteed for $R1$ and $R2$ ? If not show a possible interleaving of the statements of $P1$ and $P2$ such mutual exclusion is violated (i.e., both $P1$ and $P2$ use $R1$ and $R2$ at the same time).  
B. Can deadlock occur in the above program? If yes, show a possible interleaving of the statements of $P1$ and $P2$ leading to deadlock.  
C. Exchange the statements Q1 and Q3 and statements Q2 and Q4. Is mutual exclusion guaranteed now? Can deadlock occur?

gatecse-2001 operating-system resource-allocation normal descriptive

Answer key

# 5.25.12 Resource Allocation: GATE CSE 2005 | Question: 71


Suppose n processes, $P_{1}, \ldots, P_{n}$ share m identical resource units, which can be reserved and released one at a time. The maximum resource requirement of process $P_{i}$ is $s_{i}$ , where $s_{i} > 0$ . Which one of the following is a sufficient condition for ensuring that deadlock does not occur?

A. $\forall i, s_i, < m$  
B. $\forall i, s_i < n$  
C. $\sum_{i=1}^{n} s_i < (m+n)$  
D. $\sum_{i=1}^{n} s_i < (m \times n)$

gatecse-2005 operating-system resource-allocation normal

Answer key

# 5.25.13 Resource Allocation: GATE CSE 2006 | Question: 66


Consider the following snapshot of a system running $n$ processes. Process $i$ is holding $x_{i}$ instances of a resource $R$ , $1 \leq i \leq n$ . Currently, all instances of $R$ are occupied. Further, for all $i$ , process $i$ has placed a request for an additional $y_{i}$ instances while holding the $x_{i}$ instances it already has. There are exactly two processes $p$ and $q$ and such that $y_{p} = y_{q} = 0$ . Which one of the following can serve as a necessary condition to guarantee that the system is not approaching a deadlock?

A. $\min (x_p,x_q) <   \max_{k\neq p,q}y_k$  
C. $\max (x_p,x_q) > 1$

B. $x_{p} + x_{q}\geq \min_{k\neq p,q}y_{k}$  
D. $\min(x_{p},x_{q})>1$

gatecse-2006 operating-system resource-allocation normal

Answer key

A single processor system has three resource types X, Y and Z, which are shared by three processes.

There are 5 units of each resource type. Consider the following scenario, where the column alloc denotes the number of units of each resource type allocated to each process, and the column request denotes the number of units of each resource type requested by a process in order to complete execution. Which of these processes will finish LAST?

<table><tr><td></td><td colspan="3">alloc</td><td colspan="3">request</td></tr><tr><td></td><td>X</td><td>Y</td><td>Z</td><td>X</td><td>Y</td><td>Z</td></tr><tr><td>P0</td><td>1</td><td>2</td><td>1</td><td>1</td><td>0</td><td>3</td></tr><tr><td>P1</td><td>2</td><td>0</td><td>1</td><td>0</td><td>1</td><td>2</td></tr><tr><td>P2</td><td>2</td><td>2</td><td>1</td><td>1</td><td>2</td><td>0</td></tr></table>

A. P0  
C. P2

B. P1  
D. None of the above, since the system is in a deadlock

gatecse-2007 operating-system resource-allocation normal

Answer key

# 5.25.15 Resource Allocation: GATE CSE 2008 | Question: 65

Which of the following is NOT true of deadlock prevention and deadlock avoidance schemes?

A. In deadlock prevention, the request for resources is always granted if the resulting state is safe  
B. In deadlock avoidance, the request for resources is always granted if the resulting state is safe  
C. Deadlock avoidance is less restrictive than deadlock prevention  
D. Deadlock avoidance requires knowledge of resource requirements apriori..

gatecse-2008 operating-system easy resource-allocation

Answer key

# 5.25.16 Resource Allocation: GATE CSE 2009 | Question: 30


Consider a system with 4 types of resources R1 (3 units), R2 (2 units), R3 (3 units), R4 (2 units). A non-preemptive resource allocation policy is used. At any given instance, a request is not entertained if it cannot be completely satisfied. Three processes P1, P2, P3 request the resources as follows if executed independently.

<table><tr><td>Process P1:</td><td>Process P2:</td><td>Process P3:</td></tr><tr><td> $t = 0$ :requests 2 units of  $R2$  $t = 1$ :requests 1 unit of  $R3$  $t = 3$ :requests 2 units of  $R1$  $t = 5$ :releases 1 unit of  $R2$  and 1 unit of  $R1$  $t = 7$ :releases 1 unit of  $R3$  $t = 8$ :requests 2 units of  $R4$  $t = 10$ : Finishes</td><td> $t = 0$ :requests 2 units of  $R3$  $t = 2$ :requests 1 unit of  $R4$  $t = 4$ :requests 1 unit of  $R1$  $t = 6$ :releases 1 unit of  $R3$  $t = 8$ : Finishes</td><td> $t = 0$ :requests 1 unit of  $R4$  $t = 2$ :requests 2 units of  $R1$  $t = 5$ :releases 2 units of  $R1$  $t = 7$ :requests 1 unit of  $R2$  $t = 8$ :requests 1 unit of  $R3$  $t = 9$ : Finishes</td></tr></table>

Which one of the following statements is TRUE if all three processes run concurrently starting at time t = 0?

A. All processes will finish without any deadlock

B. Only P1 and P2 will be in deadlock

C. Only $P1$ and $P3$ will be in deadlock

D. All three processes will be in deadlock

gatecse-2009 operating-system resource-allocation normal

Answer key

A system has $n$ resources $R_0, \ldots, R_{n-1}$ , and $k$ processes $P_0, \ldots, P_{k-1}$ . The implementation of the resource request logic of each process $P_i$ is as follows:

<div class="mineru-algorithm" style="white-space: pre-wrap; font-family:monospace;">
if(i%2 == 0){
    if(i &lt; n) request R_i;
    if(i + 2 &lt; n) request R_{i+2}; }
else{
    if(i &lt; n) request R_{n-i};
    if(i + 2 &lt; n) request R_{n-i-2}; }
</div>

In which of the following situations is a deadlock possible?

A. n = 40, k = 26

B. $n = 21, k = 12$

C. $n = 20, k = 10$

D. $n = 41, k = 19$

gatecse-2010 operating-system resource-allocation normal

# Answer key

# 5.25.18 Resource Allocation: GATE CSE 2013 | Question: 16

Three concurrent processes $X, Y$ , and $Z$ execute three different code segments that access and update certain shared variables. Process $X$ executes the $P$ operation (i.e., wait) on semaphores $a, b$ , and $c$ ;

process Y executes the P operation on semaphores b, c, and d; process Z executes the P operation on semaphores c, d, and a before entering the respective code segments. After completing the execution of its code segment, each process invokes the V operation (i.e., signal) on its three semaphores. All semaphores are binary semaphores initialized to one. Which one of the following represents a deadlock-free order of invoking the P operations by the processes?

A. $X: P(a)P(b)P(c)Y: P(b)P(c)P(d)Z: P(c)P(d)P(a)$  
B. $X:P(b)P(a)P(c)Y:P(b)P(c)P(d)Z:P(a)P(c)P(d)$  
C. $X: P(b)P(a)P(c)Y: P(c)P(b)P(d)Z: P(a)P(c)P(d)$  
D. $X: P(a)P(b)P(c)Y: P(c)P(b)P(d)Z: P(c)P(d)P(a)$

gatecse-2013 operating-system resource-allocation normal

# Answer key

# 5.25.19 Resource Allocation: GATE CSE 2014 | Set 1 | Question: 31

An operating system uses the Banker's algorithm for deadlock avoidance when managing the allocation of three resource types $X, Y$ , and $Z$ to three processes $P0, P1$ , and $P2$ . The table given below presents the

current system state. Here, the Allocation matrix shows the current number of resources of each type allocated to each process and the Max matrix shows the maximum number of resources of each type required by each process during its execution.

<table><tr><td colspan="4">Allocation</td><td colspan="3">Max</td></tr><tr><td></td><td>X</td><td>Y</td><td>Z</td><td>X</td><td>Y</td><td>Z</td></tr><tr><td>P0</td><td>0</td><td>0</td><td>1</td><td>8</td><td>4</td><td>3</td></tr><tr><td>P1</td><td>3</td><td>2</td><td>0</td><td>6</td><td>2</td><td>0</td></tr><tr><td>P2</td><td>2</td><td>1</td><td>1</td><td>3</td><td>3</td><td>3</td></tr></table>

There are 3 units of type X, 2 units of type Y and 2 units of type Z still available. The system is currently in a safe state. Consider the following independent requests for additional resources in the current state:

REQ1: P0 requests 0 units of X, 0 units of Y and 2 units of Z

REQ2: P1 requests 2 units of X, 0 units of Y and 0 units of Z

Which one of the following is TRUE?

A. Only REQ1 can be permitted.  
C. Both REQ1 and REQ2 can be

B. Only REQ2 can be permitted.  
D. Neither REQ1 nor REQ2 can be



# 5.25.20 Resource Allocation: GATE CSE 2014 | Set 3 | Question: 31

A system contains three programs and each requires three tape units for its operation. The minimum number of tape units which the system must have such that deadlocks never arise is \_\_\_\_.


gatecse-2014-set3 operating-system resource-allocation numerical-answers easy

# Answer key

# 5.25.21 Resource Allocation: GATE CSE 2015 | Set 2 | Question: 23

A system has 6 identical resources and N processes competing for them. Each process can request at most 2 resources. Which one of the following values of N could lead to a deadlock?


A. 1

B. 2

C. 3

D. 4

gatecse-2015-set2 operating-system resource-allocation easy

# Answer key

# 5.25.22 Resource Allocation: GATE CSE 2015 | Set 3 | Question: 52

Consider the following policies for preventing deadlock in a system with mutually exclusive resources.


I. Process should acquire all their resources at the beginning of execution. If any resource is not available, all resources acquired so far are released.  
II. The resources are numbered uniquely, and processes are allowed to request for resources only in increasing resource numbers  
III. The resources are numbered uniquely, and processes are allowed to request for resources only in decreasing resource numbers  
IV. The resources are numbered uniquely. A processes is allowed to request for resources only for a resource with resource number larger than its currently held resources

Which of the above policies can be used for preventing deadlock?

A. Any one of (I) and (III) but not (II) or (IV)

B. Any one of (I), (III) and (IV) but not (II)

C. Any one of (II) and (III) but not (I) or (IV)

D. Any one of (I), (II), (III) and (IV)

gatecse-2015-set3 operating-system resource-allocation normal

# Answer key

# 5.25.23 Resource Allocation: GATE CSE 2017 | Set 2 | Question: 33

A system shares 9 tape drives. The current allocation and maximum requirement of tape drives for that processes are shown below:


<table><tr><td>Process</td><td>Current Allocation</td><td>Maximum Requirement</td></tr><tr><td>P1</td><td>3</td><td>7</td></tr><tr><td>P2</td><td>1</td><td>6</td></tr><tr><td>P3</td><td>3</td><td>5</td></tr></table>

Which of the following best describes current state of the system?

A. Safe, Deadlocked

B. Safe, Not Deadlocked

C. Not Safe, Deadlocked

D. Not Safe, Not Deadlocked

gatecse-2017-set2 operating-system resource-allocation normal

# Answer key

Consider the following snapshot of a system running $n$ concurrent processes. Process $i$ is holding $X_{i}$ instances of a resource $R$ , $1 \leq i \leq n$ . Assume that all instances of $R$ are currently in use. Further, for all $i$ , process $i$ can place a request for at most $Y_{i}$ additional instances of $R$ while holding the $X_{i}$ instances it already has. Of the $n$ processes, there are exactly two processes $p$ and $q$ such that $Y_{p} = Y_{q} = 0$ . Which one of the following conditions guarantees that no other process apart from $p$ and $q$ can complete execution?

A. $X_{p} + X_{q} < \operatorname{Min}\{Y_{k} \mid 1 \leq k \leq n, k \neq p, k \neq q\}$  
B. $X_{p} + X_{q} < \operatorname{Max}\{Y_{k} \mid 1 \leq k \leq n, k \neq p, k \neq q\}$  
C. $\operatorname{Min}(X_p, X_q) \geq \operatorname{Min}\{Y_k \mid 1 \leq k \leq n, k \neq p, k \neq q\}$  
D. $\operatorname{Min}(X_p, X_q) \leq \operatorname{Max}\{Y_k \mid 1 \leq k \leq n, k \neq p, k \neq q\}$

gatecse-2019 operating-system two-marks resource-allocation

Answer key

# 5.25.25 Resource Allocation: GATE CSE 2022 | Question: 16

Which of the following statements is/are TRUE with respect to deadlocks?


A. Circular wait is a necessary condition for the formation of deadlock.  
B. In a system where each resource has more than one instance, a cycle in its wait-for graph indicates the presence of a deadlock.  
C. If the current allocation of resources to processes leads the system to unsafe state, then deadlock will necessarily occur.  
D. In the resource-allocation graph of a system, if every edge is an assignment edge, then the system is not in deadlock state.

gatecse-2022 operating-system resource-allocation multiple-selects one-mark

Answer key

# 5.25.26 Resource Allocation: GATE IT 2005 | Question: 62


Two shared resources $R_{1}$ and $R_{2}$ are used by processes $P_{1}$ and $P_{2}$ . Each process has a certain priority for accessing each resource. Let $T_{ij}$ denote the priority of $P_{i}$ for accessing $R_{j}$ . A process $P_{i}$ can snatch a resource $R_{k}$ from process $P_{j}$ if $T_{ik}$ is greater than $T_{jk}$ .

Given the following :

1. $T_{11} > T_{21}$  
II. $T_{12} > T_{22}$  
III. $T_{11} < T_{21}$  
IV. $T_{12} <   T_{22}$

Which of the following conditions ensures that $P_{1}$ and $P_{2}$ can never deadlock?

A. (I) and (IV)

B. (II) and (III)

C. (I) and (II)

D. None of the above

gateit-2005 operating-system resource-allocation normal

Answer key

# 5.25.27 Resource Allocation: GATE IT 2008 | Question: 54


An operating system implements a policy that requires a process to release all resources before making a request for another resource. Select the TRUE statement from the following:

A. Both starvation and deadlock can occur  
B. Starvation can occur but deadlock cannot occur  
C. Starvation cannot occur but deadlock can occur  
D. Neither starvation nor deadlock can occur

# 5.26.1 Resource Allocation Graph: GATE CSE 2025 | Set 2 | Question: 38

$P = \{P_{1}, P_{2}, P_{3}, P_{4}\}$ consists of all active processes in an operating system.

$R = \{R_{1}, R_{2}, R_{3}, R_{4}\}$ consists of single instances of distinct types of resources in the system.

The resource allocation graph has the following assignment and claim edges.

Assignment edges: $R_{1} \to P_{1}, R_{2} \to P_{2}, R_{3} \to P_{3}, R_{4} \to P_{4}$ (the assignment edge $R_{1} \to P_{1}$ means resource $R_{1}$ is assigned to process $P_{1}$ , and so on for others)

Claim edges: $P_{1} \rightarrow R_{2}, P_{2} \rightarrow R_{3}, P_{3} \rightarrow R_{1}, P_{2} \rightarrow R_{4}, P_{4} \rightarrow R_{2}$ (the claim edge $P_{1} \rightarrow R_{2}$ means process $P_{1}$ is waiting for resource $R_{2}$ , and so on for others)

Which of the following statement(s) is/are CORRECT?

A. Aborting $P_{1}$ makes the system deadlock free.  
B. Aborting $P_{3}$ makes the system deadlock free.  
C. Aborting $P_{2}$ makes the system deadlock free.  
D. Aborting $P_{1}$ and $P_{4}$ makes the system deadlock free.

gatecse2025-set2 operating-system resource-allocation-graph multiple-selects two-marks

Answer key

# 5.27

# Round Robin Scheduling (1)

# 5.27.1 Round Robin Scheduling: GATE CSE 2022 | Question: 32

Consider four processes P, Q, R, and S scheduled on a CPU as per round robin algorithm with a time quantum of 4 units. The processes arrive in the order P, Q, R, S, all at time t = 0. There is exactly one context switch from S to Q, exactly one context switch from R to Q, and exactly two context switches from Q to R. There is no context switch from S to P. Switching to a ready process after the termination of another process is also considered a context switch. Which one of the following is NOT possible as CPU burst time (in time units) of these processes?

A. $\mathrm{P} = 4, \mathrm{Q} = 10, \mathrm{R} = 6, \mathrm{S} = 2$  
C. P = 4, Q = 12, R = 5, S = 4

B. $P = 2, Q = 9, R = 5, S = 1$  
D. $\mathrm{P} = 3, \mathrm{Q} = 7, \mathrm{R} = 7, \mathrm{S} = 3$

gatecse-2022 operating-system process-scheduling round-robin-scheduling two-marks

Answer key

# 5.28

# Semaphore (11)

Practice Tests: Test 1 (15Q) Test 2 (3Q)

# 5.28.1 Semaphore: GATE CSE 1990 | Question: 1-vii

Semaphore operations are atomic because they are implemented within the OS \_\_\_\_.

gate1990 operating-system semaphore process-synchronization fill-in-the-blanks

Answer key

# 5.28.2 Semaphore: GATE CSE 1992 | Question: 02,x, ISRO2015-35

At a particular time of computation, the value of a counting semaphore is 7. Then $20P$ operations and $15V$ operations were completed on this semaphore. The resulting value of the semaphore is:

A. 42

B. 2

C. 7

D. 12

gate1992 operating-system semaphore easy isro2015 process-synchronization

Answer key





# 5.28.3 Semaphore: GATE CSE 1998 | Question: 1.31


A counting semaphore was initialized to 10. Then $6P$ (wait) operations and $4V$ (signal) operations were completed on this semaphore. The resulting value of the semaphore is

A. 0

B. 8

C. 10

D. 12

gate1998 operating-system process-synchronization semaphore easy

Answer key

# 5.28.4 Semaphore: GATE CSE 2008 | Question: 63

The P and V operations on counting semaphores, where s is a counting semaphore, are defined as follows:


$$
P (s): \begin{array}{l} s = s - 1; \\ \text {If} s <   0 \text {then wait;} \end{array}
$$

$$
V (s): \begin{array}{l} s = s + 1; \\ \text {If} s \leq 0 \text {then wake up process waiting on} s; \end{array}
$$

Assume that $P_{b}$ and $V_{b}$ the wait and signal operations on binary semaphores are provided. Two binary semaphores $x_{b}$ and $y_{b}$ are used to implement the semaphore operations $P(s)$ and $V(s)$ as follows:

$$
P (s): \begin{array}{l} P _ {b} (x _ {b}); \\ s = s - 1; \\ \text {if} (s <   0) \\ \left\{ \begin{array}{c} V _ {b} (x _ {b}); \\ P _ {b} (y _ {b}); \end{array} \right. \\ \left. \begin{array}{l} \} \\ \text {else} V _ {b} (x _ {b}); \end{array} \right. \end{array}
$$

$$
V (s): \quad \begin{array}{l} P _ {b} (x _ {b}); \\ s = s + 1; \\ \text {if} (s \leq 0) V _ {b} (y _ {b}); \\ V _ {b} (x _ {b}); \end{array}
$$

The initial values of $x_{b}$ and $y_{b}$ are respectively

A. 0 and 0

B. 0 and 1

C. 1 and 0

D. 1 and 1

gatecse-2008 operating-system normal semaphore

Answer key

# 5.28.5 Semaphore: GATE CSE 2016 | Set 2 | Question: 49


Consider a non-negative counting semaphore $S$ . The operation $P(S)$ decrements $S$ , and $V(S)$ increments $S$ . During an execution, 20 $P(S)$ operations and 12 $V(S)$ operations are issued in some order. The largest initial value of $S$ for which at least one $P(S)$ operation will remain blocked is \_\_\_\_

gatecse-2016-set2 operating-system semaphore normal numerical-answers

Answer key

# 5.28.6 Semaphore: GATE CSE 2020 | Question: 34

Each of a set of $n$ processes executes the following code using two semaphores $a$ and $b$ initialized to 1 and 0, respectively. Assume that count is a shared variable initialized to 0 and not used in CODE SECTION P.


# CODE SECTION P

wait(a); count=count+1;

if (count==n) signal (b);

signal (a); wait (b); signal (b);

# CODE SECTION Q

What does the code achieve?

A. It ensures that no process executes CODE SECTION Q before every process has finished CODE SECTION P.  
B. It ensures that almost two processes are in CODE SECTION Q at any time.  
C. It ensures that all processes execute CODE SECTION P mutually exclusively.  
D. It ensures that at most n - 1 processes are in CODE SECTION P at any time.

gatecse-2020 operating-system semaphore two-marks

# Answer key

# 5.28.7 Semaphore: GATE CSE 2021 | Set 1 | Question: 46

Consider the following pseudocode, where S is a semaphore initialized to 5 in line #2 and counter is a shared variable initialized to 0 in line #1. Assume that the increment operation in line #7 is not atomic.


```c
int counter = 0;
Semaphore S = init(5);
void parop(void)
{
    wait(S);
    wait(S);
    counter++;
    signal(S);
    signal(S);
}
```

If five threads execute the function parop concurrently, which of the following program behavior(s) is/are possible?

A. The value of counter is 5 after all the threads successfully complete the execution of parop  
B. The value of counter is 1 after all the threads successfully complete the execution of parop  
C. The value of counter is 0 after all the threads successfully complete the execution of parop  
D. There is a deadlock involving all the threads

gatecse-2021-set1 multiple-selects operating-system process-synchronization semaphore two-marks

# Answer key

# 5.28.8 Semaphore: GATE CSE 2022 | Question: 9

Consider the following threads, $T_{1}$ , $T_{2}$ , and $T_{3}$ executing on a single processor, synchronized using three binary semaphore variables, $S_{1}$ , $S_{2}$ , and $S_{3}$ , operated upon using standard wait() and signal(). The threads can be context switched in any order and at any time.

<table><tr><td> $T_1$ </td><td> $T_2$ </td><td> $T_3$ </td></tr><tr><td>while(true){wait( $S_3$ );print(“C”);signal( $S_2$ );}</td><td>while(true){wait( $S_1$ );print(“B”);signal( $S_3$ );}</td><td>while(true){wait( $S_2$ );print(“A”);signal( $S_1$ );}</td></tr></table>


Which initialization of the semaphores would print the sequence BCABCABCA...?

A. $\mathrm{S}_1 = 1; \mathrm{S}_2 = 1; \mathrm{S}_3 = 1$  
C. $S_{1}=1;S_{2}=0;S_{3}=0$

B. $S_{1} = 1; S_{2} = 1; S_{3} = 0$  
D. $S_{1}=0;S_{2}=1;S_{3}=1$

gatecse-2022 operating-system process-synchronization semaphore one-mark

# Answer key

# 5.28.9 Semaphore: GATE CSE 2023 | Question: 28

Consider the two functions incr and decr shown below.


```txt
incr(){        decr(){
        wait(s);        wait(s);
        X = X+1;        X = X-1;
        signal(s);        signal(s);
    }         }
```

There are 5 threads each invoking incr once, and 3 threads each invoking decr once, on the same shared variable X. The initial value of X is 10.

Suppose there are two implementations of the semaphore S, as follows:

I-1: s is a binary semaphore initialized to 1.

I-2: s is a counting semaphore initialized to 2.

Let V1, V2 be the values of X at the end of execution of all the threads with implementations I-1, I-2, respectively.

Which one of the following choices corresponds to the minimum possible values of V1, V2, respectively?

A. 15,7

B. 7,7

C. 12,7

D. 12,8

gatecse-2023 operating-system semaphore two-marks

# Answer key

# 5.28.10 Semaphore: GATE CSE 2026 | Set 2 | Question: 41

Consider three processes P1, P2, and P3 running identical code, as shown in the pseudocode below. A and B are two binary semaphores initialized to 1 and 0, respectively. X is a shared variable initialized to 0. Each line in the pseudocode is executed atomically.


```txt
Pseudocode of P1, P2, and P3
    Wait(A);
    Print(*);
    X = X+1;
    If (X == 2)
    {
        Print($);
        Signal(B);
    }
    Signal(A);
    Wait(B);
    Print(#);
    Signal(B);
```

Assume that any of the three processes can start to execute first and context switching can happen between these processes at any arbitrary time and in any arbitrary order.

Which of the following patterns is/are possible to be generated as an outcome of the execution of these three processes?

<table><tr><td>A.</td><td>B.</td><td>C.</td><td>D.</td><td></td></tr><tr><td></td><td>**$*###</td><td>**$#*##</td><td>**$##*#</td><td>***$###</td></tr></table>

gatecse-2026-set2 operating-system semaphore multiple-selects two-marks

# Answer key

# 5.28.11 Semaphore: GATE IT 2006 | Question: 57

The wait and signal operations of a monitor are implemented using semaphores as follows. In the following,


- $x$ is a condition variable,  
- mutex is a semaphore initialized to 1,  
- $x$ \_sem is a semaphore initialized to 0,  
- $x$ count is the number of processes waiting on semaphore $x$ sem, initially 0,  
- next is a semaphore initialized to 0,  
- next\_count is the number of processes waiting on semaphore next, initially 0.

The body of each procedure that is visible outside the monitor is replaced with the following:

```txt
P(mutex);
...
body of procedure
...
if (next_count > 0)
```

```txt
V(next);
else
    V(mutex);
```

Each occurrence of x.wait is replaced with the following:

```c
x_count = x_count + 1;
if (next_count > 0)
    V(next);
else
    V(mutex);
-------------------------------------------------------------------------- E1;
x_count = x_count - 1;
```

Each occurrence of x.signal is replaced with the following:

```txt
if (x_count > 0)
{
    next_count = next_count + 1;
    ----------------E2;
    P(next);
    next_count = next_count - 1;
}
```

For correct implementation of the monitor, statements E1 and E2 are, respectively,

A. $P(x\_sem), V(next)$ C. $P(next), V(x\_sem)$

B. $V(next), P(x\_sem)$ D. $P(x\_sem), V(x\_sem)$

gateit-2006 operating-system process-synchronization semaphore normal

Answer key

# 5.29

# Srtf (1)

# 5.29.1 Srtf: GATE CSE 2025 | Set 2 | Question: 16

Processes P1, P2, P3, P4 arrive in that order at times 0, 1, 2, and 8 milliseconds respectively, and have execution times of 10, 13, 6, and 9 milliseconds respectively. Shortest Remaining Time First (SRTF) algorithm is used as the CPU scheduling policy. Ignore context switching times.


Which ONE of the following correctly gives the average turnaround time of the four processes in milliseconds?

A. 22

B. 15

C. 37

D. 19

gatecse2025-set2 operating-system srtf process-scheduling average-turnaround-time one-mark

Answer key

# 5.30

# System Calls (1)

# 5.30.1 System Calls: GATE CSE 2021 | Set 1 | Question: 14

Which of the following standard C library functions will always invoke a system call when executed from a single-threaded process in a UNIX/Linux operating system?


A. exit

B. malloc

C. sleep

D. strlen

gatecse-2021-set1 multiple-selects operating-system system-calls one-mark

Answer key

# 5.31

# Threads (10)

Practice Tests:

Test 1 (15Q)

Test 2 (7Q)

# 5.31.1 Threads: GATE CSE 2004 | Question: 11

Consider the following statements with respect to user-level threads and kernel-supported threads

I. context switch is faster with kernel-supported threads  
II. for user-level threads, a system call can block the entire process  
III. Kernel supported threads can be scheduled independently  
IV. User level threads are transparent to the kernel

Which of the above statements are true?

A. (II), (III) and (IV) only  
C. (I) and (III) only  
gatecse-2004 operating-system threads normal

B. (II) and (III) only

# Answer key

# 5.31.2 Threads: GATE CSE 2007 | Question: 17

Consider the following statements about user level threads and kernel level threads. Which one of the following statements is FALSE?

A. Context switch time is longer for kernel level threads than for user level threads.  
B. User level threads do not need any hardware support.  
C. Related kernel level threads can be scheduled on different processors in a multi-processor system.  
D. Blocking one kernel level thread blocks all related threads.

gatecse-2007 operating-system threads normal

# Answer key

# 5.31.3 Threads: GATE CSE 2011 | Question: 16, UGCNET-June2013-III: 65

A thread is usually defined as a "light weight process" because an Operating System (OS) maintains smaller data structure for a thread than for a process. In relation to this, which of the following statement is TRUE?

A. On per-thread basis, the OS maintains only CPU register state.  
B. The OS does not maintain a separate stack for each thread.  
C. On per-thread basis, the OS does not maintain virtual memory state.  
D. On per-thread basis, the OS maintains only scheduling and accounting information.

gatecse-2011 operating-system threads normal ugcnetcse-june2013-paper3

# Answer key

# 5.31.4 Threads: GATE CSE 2014 | Set 1 | Question: 20

Which one of the following is FALSE?

A. User level threads are not scheduled by the kernel.  
B. When a user level thread is blocked, all other threads of its process are blocked.  
C. Context switching between user level threads is faster than context switching between kernel level threads.  
D. Kernel level threads cannot share the code segment.

gatecse-2014-set1 operating-system threads normal

# Answer key

# 5.31.5 Threads: GATE CSE 2017 | Set 1 | Question: 18

Threads of a process share

A. global variables but not heap  
C. neither global variables nor heap

B. heap but not global variables  
D. both heap and global variables





