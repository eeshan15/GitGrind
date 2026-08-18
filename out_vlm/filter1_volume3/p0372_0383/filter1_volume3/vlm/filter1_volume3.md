- Incorrectly using wait() and signal() operations, leading to deadlock or starvation.  
- Not ensuring atomicity of synchronization primitives.  
- Confusing mutexes with counting semaphores.

# - Standard Problem-Solving Techniques:

- Trace the execution flow of multiple processes accessing shared resources, observing the values of semaphores or mutexes.  
- Identify potential race conditions and propose synchronization solutions.  
○ Analyze classic synchronization problems (Producer-Consumer, Readers-Writers, Dining Philosophers).

# Resource Allocation

Resource allocation is the process by which the operating system assigns available resources (CPU, memory, I/O devices, files) to processes. This is a fundamental task of the OS, impacting system performance and stability.

# - Key Properties:

- Resources can be preemptable (e.g., CPU) or non-preemptable (e.g., printer).  
- Proper resource allocation is critical to prevent deadlocks and ensure fairness.  
- Involves policies for granting requests and reclaiming resources.

# Resource Allocation Graph (RAG)

A Resource Allocation Graph is a directed graph used to depict the state of a system regarding resources and processes. It helps in visualizing resource allocation and detecting deadlocks.

# - Key Properties:

- Nodes: Processes (circles) and Resource types (rectangles).  
- Edges:  
- Request Edge: From process to resource type (e.g., $P_i \to R_j$ ), indicating $P_i$ is requesting an instance of $R_j$ .  
- Assignment Edge: From resource type to process (e.g., $R_{j} \rightarrow P_{i}$ ), indicating an instance of $R_{j}$ has been allocated to $P_{i}$ .

\- If the RAG contains a cycle, and each resource type has only one instance, then a deadlock exists.

\- If the RAG contains a cycle, and some resource types have multiple instances, a deadlock may exist (further analysis needed).

# - Common Pitfalls:

- Incorrectly drawing request vs. assignment edges.  
- Assuming a cycle always implies deadlock, especially for multiple-instance resources.  
- Not understanding the difference between RAG and Wait-For Graph.

# - Standard Problem-Solving Techniques:

- Draw the RAG based on the given process and resource states.  
- Identify cycles in the graph.  
- If cycles exist, determine if they lead to deadlock based on resource instance counts.

# Round Robin Scheduling

Round Robin (RR) is a preemptive process scheduling algorithm designed for time-sharing systems. Each process is given a small unit of CPU time, called a time quantum (or time slice). When the quantum expires, the process is preempted and added to the end of the ready queue.

# - Important Formulas/Theorems:

1. Turnaround Time (TAT): CompletionTime - ArrivalTime  
2. Waiting Time (WT): TurnaroundTime - BurstTime  
3. Number of Context Switches: Depends on the number of processes and the time quantum.

# - Key Properties:

- Fair scheduling, as every process gets a chance to run.  
- Good for interactive systems, providing quick response times.  
- Performance heavily depends on the time quantum:  
- Small quantum: High context switch overhead, good response time.  
- Large quantum: Approaches FCFS, lower overhead, potentially poor response time.

# - Common Pitfalls:

- Incorrectly handling the time quantum and preemption points.  
- Mistakes in calculating TAT or WT, especially when processes arrive at different times.

\- Forgetting to account for context switch overhead if specified in the problem.

# - Standard Problem-Solving Techniques:

Draw a Gantt chart, carefully allocating CPU time in quantum chunks and moving processes to the end of the ready queue upon preemption.  
- Keep track of remaining burst times for each process.

# Semaphore

A semaphore is a synchronization primitive, a protected integer variable that can only be accessed and modified by two atomic operations: wait() (also known as P or down) and signal() (also known as V or up).

# - Important Formulas/Theorems:

# 1. wait(S) operation:

```txt
wait(S) {
    while (S <= 0); // busy wait
    S--;
}
(Alternatively, block the process if S ≤ 0).
```

# 2. signal(S) operation:

```txt
signal(S) {
    S++;
}
```

(Alternatively, wake up a blocked process if any).

# - Key Properties:

- Counting Semaphore: Can range over an unrestricted domain. Used to control access to a resource with multiple instances.  
- Binary Semaphore (Mutex): Can only be 0 or 1. Used for mutual exclusion (like a lock).  
- Can be used for both mutual exclusion and process synchronization (ordering of events).  
- Improper use can lead to deadlock or starvation.

# - Common Pitfalls:

- Swapping the order of wait() and signal() operations, leading to incorrect synchronization.  
- Using busy-waiting semaphores in a single-processor system (wastes CPU cycles).  
- Not initializing semaphores correctly.

# - Standard Problem-Solving Techniques:

- Trace the values of semaphores as processes execute wait() and signal() operations.  
- Identify critical sections and shared resources to determine appropriate semaphore usage.  
- Solve classic synchronization problems using semaphores.

# SRTF (Shortest Remaining Time First)

SRTF is a preemptive version of the Shortest Job First (SJF) scheduling algorithm. The CPU is allocated to the process with the smallest remaining burst time. If a new process arrives with a shorter burst time than the currently running process's remaining time, the current process is preempted.

# - Important Formulas/Theorems:

1. Turnaround Time (TAT): CompletionTime - ArrivalTime  
2. Waiting Time (WT): TurnaroundTime - BurstTime

# - Key Properties:

- Optimal for minimizing average waiting time.  
- Requires knowing the remaining burst time of all processes, which is difficult in practice.  
- High overhead due to frequent context switches, especially with many short jobs or frequent arrivals.  
- Can suffer from starvation if a continuous stream of short jobs keeps arriving.

# - Common Pitfalls:

- Incorrectly determining when preemption occurs (at every arrival or when a shorter job becomes ready).  
- Mistakes in calculating remaining burst times.  
- Overlooking processes that arrive later but have very short burst times.

# - Standard Problem-Solving Techniques:

- Create a Gantt chart, carefully tracking the remaining burst time of all ready processes at each time unit.  
- At each time unit, check for new arrivals and select the process with the minimum remaining burst time.

# System Calls

System calls provide an interface between a running program and the operating system. They allow user-level programs to request services from the OS kernel, such as file I/O, process creation, memory allocation, and device access.

# - Key Properties:

- Transition from user mode to kernel mode (privileged mode).  
- Typically invoked through a software interrupt (trap).  
- Provide a controlled and secure way for user programs to access protected resources.  
- Examples: fork(), exec(), read(), write(), open(), close(), wait(), exit().

# - Common Pitfalls:

- Confusing system calls with library calls (library calls are user-level functions that may or may not invoke system calls).  
- Not understanding the mode switch involved.

# Threads

A thread (or lightweight process) is a basic unit of CPU utilization within a process. Multiple threads within the same process share the same code section, data section, and other OS resources (like open files, signals), but each has its own program counter, register set, and stack.

# - Key Properties:

- Faster Context Switching: Switching between threads in the same process is faster than switching between processes.  
• Resource Sharing: Threads within a process share memory and resources, facilitating communication.  
- Concurrency: Multiple threads can execute concurrently, improving application responsiveness and throughput on multi-core systems.  
- User-level Threads: Managed by a user-level library, faster to create/manage, but if one thread blocks, the entire process blocks.  
- Kernel-level Threads: Managed by the OS kernel, slower to create/manage, but if one thread blocks, others can still run.  
- Many-to-One, One-to-One, Many-to-Many models: Different mappings between user and kernel threads.

# - Common Pitfalls:

- Confusing threads with processes (threads share memory, processes do not).  
- Forgetting that synchronization is still required for shared data among threads.  
- Misunderstanding the implications of user-level vs. kernel-level threads.

# Translation Lookaside Buffer (TLB)

The TLB is a small, fast hardware cache that stores recent virtual-to-physical address translations. It is used to speed up memory access in paged virtual memory systems by avoiding multiple memory accesses to the page table.

# - Important Formulas/Theorems:

1. Effective Access Time (EAT) with TLB:

$$
E A T = T L B \_ H i t \_ R a t i o \times (T L B \_ A c c e s s \_ T i m e + M e m o r y \_ A c c e s s \_ T i m e) + (1 - T L B \_ H i t \_ R a t i o)
$$

Where Page\_Table\_Access\_Time is the time to access the page table in main memory. If the page table is also in memory, this is another Memory\_Access\_Time.

# - Key Properties:

- Significantly reduces the average memory access time if the hit ratio is high.  
- A TLB miss requires a page table walk (accessing the page table in main memory).  
- TLB entries are flushed on context switches between processes (though some TLBs support ASIDs to avoid this).

# - Common Pitfalls:

- Incorrectly calculating EAT, especially the components for a TLB miss (TLB access + memory access for page table + memory access for data).  
- Forgetting to include TLB access time even on a hit.

# - Standard Problem-Solving Techniques:

- Carefully plug values into the EAT formula, ensuring all access times are accounted for.  
- Understand how a TLB miss impacts the total access time.

# Virtual Memory

Virtual memory is a memory management technique that provides an application with an illusion of a contiguous, large address space, even if the physical memory is fragmented or smaller than the virtual address space. It separates logical memory from physical memory.

# - Key Properties:

- Allows programs to be larger than physical memory.  
- Enables efficient sharing of memory among multiple processes.  
- Provides memory protection.  
- Commonly implemented using paging (demand paging) and swapping.  
- Introduces the concept of page faults.

# - Important Formulas/Theorems:

1. Effective Access Time (EAT): (See Demand Paging and TLB sections for detailed formulas).

# - Common Pitfalls:

- Confusing virtual memory with physical memory.  
- Not understanding the role of the MMU (Memory Management Unit) in address translation.  
- Misinterpreting the benefits and overheads of virtual memory.

# Quick Formula Reference

# • Banker's Algorithm:

\- Need Matrix: $Need[i][j] = Max[i][j] - Allocation[i][j]$

\- Demand Paging / Virtual Memory EAT (without TLB):

$$
E A T = (1 - p) \times \text {MemoryAccessTime} + p \times (\text {PageFaultOverhead} + \text {MemoryAccessTime})
$$

where p is page fault rate.

# - Disk Access Time:

$$
\text {AccessTime} = \text {SeekTime} + \text {RotationalLatency} + \text {TransferTime}
$$

$$
\text {AverageRotationalLatency} = \frac {1}{2} \times \text {RotationTime}
$$

$$
\text {TransferTime} = \frac {\text {NumberOfSectors}}{\text {SectorsPerTrack}} \times \text {RotationTime}
$$

# - Multilevel Paging EAT (without TLB):

$$
E A T = (N + 1) \times M e m o r y A c c e s s T i m e
$$

for N-level paging, assuming page tables are in memory.

# • Page Replacement:

- Hit Ratio: $\frac{\text{Number of Page Hits}}{\text{Total Page References}}$  
- Miss Ratio (Page Fault Rate): $\frac{\text{Number of Page Faults}}{\text{Total Page References}}$  
- HitRatio + MissRatio = 1

# - Process Scheduling Metrics:

- Turnaround Time (TAT): CompletionTime - ArrivalTime  
- Waiting Time (WT): TurnaroundTime - BurstTime  
- Response Time (RT): FirstResponseTime - ArrivalTime

# - TLB EAT:

$$
E A T = T L B \_ H i t \_ R a t i o \times (T L B \_ A c c e s s \_ T i m e + M e m o r y \_ A c c e s s \_ T i m e) + (1 - T L B \_ H i t \_ R a t i o) \times
$$

# Important Tips for GATE

1. Master Numerical Problems: A significant portion of OS questions in GATE are numerical, especially from Process Scheduling (FCFS, SJF, SRTF, RR), Memory Management (Paging, Page Replacement, TLB EAT), and Disk Scheduling. Practice drawing Gantt charts and calculating metrics meticulously.  
2. Understand Preemption: Pay close attention to whether a scheduling algorithm is preemptive or non-preemptive.

This is a common source of error in Gantt chart construction. For preemptive algorithms, always check for new arrivals at each time unit.

3. Trace Algorithms Systematically: For complex algorithms like Banker's, Page Replacement, or Disk Scheduling, trace the steps methodically. Draw diagrams (RAG, memory maps, Gantt charts) to visualize the state changes.  
4. Differentiate Similar Concepts: Be clear on the distinctions between processes and threads, mutexes and semaphores, internal and external fragmentation, logical and physical addresses, and different deadlock strategies (prevention, avoidance, detection).  
5. Read Questions Carefully: Look for keywords like "average," "minimum," "maximum," "at least," "at most," "preemptive," "non-preemptive," and specific units (ms, ns). A small detail can change the entire answer.  
6. Focus on Trade-offs: Many OS concepts involve trade-offs (e.g., performance vs. fairness in scheduling, memory usage vs. access time in paging). Understand why certain design choices are made and their implications.  
7. Review Formulas Regularly: Keep the key formulas for EAT, scheduling metrics, and disk access time handy and review them frequently. Understand the components of each formula.  
8. Practice with GATE Previous Year Questions: This will help you understand the common question patterns, difficulty levels, and time management strategies specific to the GATE exam.

# 5.1

# Bankers Algorithm (2)

Practice Test: Test 1 (8Q)

# 5.1.1 Bankers Algorithm: GATE CSE 2018 | Question: 39


In a system, there are three types of resources: $E, F$ and $G$ . Four processes $P_0, P_1, P_2$ and $P_3$ execute concurrently. At the outset, the processes have declared their maximum resource requirements using a

matrix named Max as given below. For example, $Max[P_{2}, F]$ is the maximum number of instances of F that $P_{2}$ would require. The number of instances of the resources allocated to the various processes at any given state is given by a matrix named Allocation.

Consider a state of the system with the Allocation matrix as shown below, and in which 3 instances of E and 3 instances of F are only resources available.

<table><tr><td colspan="4">Allocation</td><td colspan="4">Max</td></tr><tr><td></td><td>E</td><td>F</td><td>G</td><td></td><td>E</td><td>F</td><td>G</td></tr><tr><td> $P_0$ </td><td>1</td><td>0</td><td>1</td><td> $P_0$ </td><td>4</td><td>3</td><td>1</td></tr><tr><td> $P_1$ </td><td>1</td><td>1</td><td>2</td><td> $P_1$ </td><td>2</td><td>1</td><td>4</td></tr><tr><td> $P_2$ </td><td>1</td><td>0</td><td>3</td><td> $P_2$ </td><td>1</td><td>3</td><td>3</td></tr><tr><td> $P_3$ </td><td>2</td><td>0</td><td>0</td><td> $P_3$ </td><td>5</td><td>4</td><td>1</td></tr></table>

From the perspective of deadlock avoidance, which one of the following is true?

A. The system is in safe state  
B. The system is not in safe state, but would be safe if one more instance of $E$ were available  
C. The system is not in safe state, but would be safe if one more instance of $F$ were available  
D. The system is not in safe state, but would be safe if one more instance of G were available

gatecse-2018 operating-system deadlock-prevention-avoidance-detection bankers-algorithm normal two-marks

# Answer key

# 5.1.2 Bankers Algorithm: GATE CSE 2026 | Set 1 | Question: 19

With respect to deadlocks in an operating system, which of the following statements is/are FALSE?

A. Banker's algorithm is used to prevent deadlocks  
B. Deadlock formation can be prevented by ensuring that the hold and wait condition is not allowed  
C. An assignment edge in a resource allocation graph is marked from a process to a resource  
D. A safe state guarantees that all processes can finish without formation of a deadlock

gatecse-2026-set1 operating-system deadlock-prevention-avoidance-detection bankers-algorithm multiple-selects one-mark

# Answer key


# 5.2.1 Best Fit: GATE CSE 2026 | Set 2 | Question: 45


Consider contiguous allocation of physical memory to processes using variable partitioning scheme. Suppose there are 8 holes in the memory of sizes 20KB, 4 KB, 25 KB, 18 KB, 7 KB, 9 KB, 15 KB, and 12 KB. Assume that no two holes are adjacent. Two processes P1 of size 16 KB and P2 of size 9 KB arrive in that order, and they are allocated memory using the best-fit technique. After allocating space to P1 and P2, the number of holes of size less than 8 KB is \_\_\_\_. (answer in integer)

Note: $1\mathrm{K} = 2^{10}$

gatecse-2026-set2 operating-system memory-management best-fit numerical-answers two-marks

Answer key

# 5.3

# Context Switch (4)

Practice Test: Test 1 (6Q)

# 5.3.1 Context Switch: GATE CSE 1999 | Question: 2.12


Which of the following actions is/are typically not performed by the operating system when switching context from process A to process B?

A. Saving current register values and restoring saved register values for process B.  
B. Changing address translation tables.  
C. Swapping out the memory image of process A to the disk.  
D. Invalidating the translation look-aside buffer.

gate1999 operating-system context-switch normal

Answer key

# 5.3.2 Context Switch: GATE CSE 2000 | Question: 1.20, ISRO2008-47


Which of the following need not necessarily be saved on a context switch between processes?

A. General purpose registers  
C. Program counter  
gatecse-2000 operating-system easy isro2008 context-switch

B. Translation look-aside buffer  
D. All of the above

Answer key

# 5.3.3 Context Switch: GATE CSE 2011 | Question: 6, UGCNET-June2013-III: 62


Let the time taken to switch from user mode to kernel mode of execution be T1 while time taken to switch between two user processes be T2. Which of the following is correct?

A. $T1 > T2$  
C. T1 < T2

B. $T1 = T2$  
D. Nothing can be said about the relation between T1 and T2

gatecse-2011 operating-system context-switch easy ugcnetcse-june2013-paper3

Answer key

# 5.3.4 Context Switch: GATE CSE 2024 | Set 2 | Question: 15


Consider a process P running on a CPU. Which one or more of the following events will always trigger a context switch by the OS that results in process P moving to a non-running state (e.g., ready, blocked)?

A. P makes a blocking system call to read a block of data from the disk  
B. P tries to access a page that is in the swap space, triggering a page fault  
C. An interrupt is raised by the disk to deliver data requested by some other process  
D. A timer interrupt is raised by the hardware


# 5.4

# DMA (1)

# 5.4.1 DMA: GATE CSE 2001 | Question: 8


Consider a disk with the following specifications: 20 surfaces, 1000 tracks/surface, 16 sectors/track, data density 1 KB/sector, rotation speed 3000 rpm. The operating system initiates the transfer between the disk

and the memory sector-wise. Once the head has been placed on the right track, the disk reads a sector in a single scan. It reads bits from the sector while the head is passing over the sector. The read bits are formed into bytes in a serial-in-parallel-out buffer and each byte is then transferred to memory. The disk writing is exactly a complementary process.

For parts (C) and (D) below, assume memory read-write time = 0.1 microseconds/byte, interrupt driven transfer has an interrupt overhead = 0.4 microseconds, the DMA initialization, and termination overhead is negligible compared to the total sector transfer time. DMA requests are always granted.

A. What is the total capacity of the desk?  
B. What is the data transfer rate?  
C. What is the percentage of time the CPU is required for this disk I/O for byte-wise interrupts driven transfer?  
D. What is the maximum percentage of time the CPU is held up for this disk I/O for cycle-stealing DMA transfer?

gatecse-2001 operating-system disk normal descriptive dma

Answer key

# 5.5

# Deadlock Prevention Avoidance Detection (4)

Practice Test: Test 1 (9Q)

# 5.5.1 Deadlock Prevention Avoidance Detection: GATE CSE 2018 | Question: 24


Consider a system with 3 processes that share 4 instances of the same resource type. Each process can request a maximum of K instances. Resources can be requested and releases only one at a time. The largest value of K that will always avoid deadlock is \_\_\_\_

gatecse-2018 operating-system deadlock-prevention-avoidance-detection easy numerical-answers one-mark

Answer key

# 5.5.2 Deadlock Prevention Avoidance Detection: GATE CSE 2021 | Set 2 | Question: 43


Consider a computer system with multiple shared resource types, with one instance per resource type. Each instance can be owned by only one process at a time. Owning and freeing of resources are done by holding a global lock (L). The following scheme is used to own a resource instance:

```txt
function OWNRESOURCE(Resource R)
    Acquire lock L // a global lock
    if R is available then
        Acquire R
        Release lock L
    else
        if R is owned by another process P then
            Terminate P, after releasing all resources owned by P
        Acquire R
        Restart P
        Release lock L
    end if
end if
end function
```

Which of the following choice(s) about the above scheme is/are correct?

A. The scheme ensures that deadlocks will not occur  
B. The scheme may lead to live-lock  
C. The scheme may lead to starvation  
D. The scheme violates the mutual exclusion property


# Answer key

# 5.5.3 Deadlock Prevention Avoidance Detection: GATE CSE 2026 | Set 1 | Question: 25


Consider a system consisting of $k$ instances of a resource $R$ , being shared by 5 processes. Assume that each process requires a maximum of two instances of resource $R$ and a process can request or release only one instance at a time. Further, a process can request the second instance of the resource only after accounting the first instance.

The minimum value of $k$ for the system to be deadlock-free is \_\_\_\_. (answer in integer)

gatecse-2026-set1 operating-system deadlock-prevention-avoidance-detection numerical-answers one-mark

# Answer key

# 5.5.4 Deadlock Prevention Avoidance Detection: GATE IT 2004 | Question: 63


In a certain operating system, deadlock prevention is attempted using the following scheme. Each process is assigned a unique timestamp, and is restarted with the same timestamp if killed. Let $P_h$ be the process holding a resource $R, P_r$ be a process requesting for the same resource $R$ , and $T(P_h)$ and $T(P_r)$ be their timestamps respectively. The decision to wait or preempt one of the processes is based on the following algorithm.

```txt
if T(Pr) < T(Ph) then
    kill Pr
else wait
```

Which one of the following is TRUE?

A. The scheme is deadlock-free, but not starvation-free  
B. The scheme is not deadlock-free, but starvation-free  
C. The scheme is neither deadlock-free nor starvation-free  
D. The scheme is both deadlock-free and starvation-free

gateit-2004 operating-system normal deadlock-prevention-avoidance-detection

# Answer key

# 5.6

# Demand Paging (3)

# 5.6.1 Demand Paging: GATE CSE 2022 | Question: 54


Consider a demand paging system with four page frames (initially empty) and LRU page replacement policy. For the following page reference string

$$
7, 2, 7, 3, 2, 5, 3, 4, 6, 7, 7, 1, 5, 6, 1
$$

the page fault rate, defined as the ratio of number of page faults to the number of memory accesses (rounded off to one decimal place) is \_\_\_\_.

gatecse-2022 numerical-answers operating-system page-replacement demand-paging two-marks

# Answer key

# 5.6.2 Demand Paging: GATE CSE 2025 | Set 1 | Question: 4


Consider a demand paging memory management system with 32-bit logical address, 20-bit physical address, and page size of 2048 bytes. Assuming that the memory is byte addressable, what is the maximum number of entries in the page table?

A. $2^{21}$

B. $2^{20}$

C. $2^{22}$

D. $2^{24}$

gatecse2025-set1 operating-system demand-paging paging easy one-mark

# Answer key

# 5.6.3 Demand Paging: GATE CSE 2025 | Set 2 | Question: 37

Consider a demand paging system with three frames, and the following page reference string: 1 2 3 4 5 4 1 6 4 5 1 3 2 . The contents of the frames are as follows initially and after each reference (from left to right):

<table><tr><td>initially</td><td colspan="13">after</td></tr><tr><td>-</td><td> $1^{*}$ </td><td> $2^{*}$ </td><td> $3^{*}$ </td><td> $4^{*}$ </td><td> $5^{*}$ </td><td>4</td><td>1</td><td> $6^{*}$ </td><td>4</td><td>5</td><td> $1^{*}$ </td><td> $3^{*}$ </td><td> $2^{*}$ </td></tr><tr><td>-</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>6</td><td>6</td><td>6</td><td>6</td><td>6</td><td>2</td></tr><tr><td>-</td><td>-</td><td>2</td><td>2</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>4</td><td>1</td><td>1</td><td>1</td></tr><tr><td>-</td><td>-</td><td>-</td><td>3</td><td>3</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>5</td><td>3</td><td>3</td></tr></table>

The \*-marked references cause page replacements.

Which one or more of the following could be the page replacement policy/policies in use?

A. Least Recently Used page replacement policy  
B. Least Frequently Used page replacement policy  
C. Most Frequently Used page replacement policy  
D. Optimal page replacement policy

gatecse2025-set2 operating-system page-replacement demand-paging multiple-selects two-marks

Answer key

# 5.7

# Disk (30)

Practice Tests: Test 1 (15Q) Test 2 (15Q) Test 3 (2Q)

# 5.7.1 Disk: GATE CSE 1990 | Question: 7-c

A certain moving arm disk-storage device has the following specifications:

• Number of tracks per surface = 404  
- Track storage capacity = 130030 bytes.  
- Disk speed = 3600 rpm  
• Average seek time = 30 m secs.

Estimate the average latency, the disk storage capacity, and the data transfer rate.

gate1990 operating-system disk descriptive

Answer key

# 5.7.2 Disk: GATE CSE 1993 | Question: 6.7

A certain moving arm disk storage, with one head, has the following specifications:

• Number of tracks/recording surface = 200  
- Disk rotation speed = 2400 rpm  
- Track storage capacity = 62,500 bits

The average latency of this device is P ms and the data transfer rate is Q bits/sec. Write the values of P and Q.

gate1993 operating-system disk normal descriptive

Answer key

# 5.7.3 Disk: GATE CSE 1993 | Question: 7.8

The root directory of a disk should be placed

A. at a fixed address in main memory  
C. anywhere on the disk

B. at a fixed location on the disk  
D. at a fixed location on the system disk




E. anywhere on the system disk

gate1993 operating-system disk normal

Answer key

# 5.7.4 Disk: GATE CSE 1995 | Question: 14

If the overhead for formatting a disk is 96 bytes for a 4000 byte sector,


A. Compute the unformatted capacity of the disk for the following parameters:

- Number of surfaces: 8  
- Outer diameter of the disk: 12 cm  
- Inner diameter of the disk: 4 cm  
- Inner track space: 0.1 mm  
- Number of sectors per track: 20

B. If the disk in (A) is rotating at 360 rpm, determine the effective data transfer rate which is defined as the number of bytes transferred per second between disk and memory.

gate1995 operating-system disk normal descriptive

Answer key

# 5.7.5 Disk: GATE CSE 1996 | Question: 23

A file system with a one-level directory structure is implemented on a disk with disk block size of $4K$ bytes. The disk is used as follows:

<table><tr><td>Disk-block 0</td><td>File Allocation Table, consisting of one 8-bit entry per data block, representing the data block address of the next data block in the file</td></tr><tr><td>Disk-block 1</td><td>Directory, with one 32 bit entry per file:</td></tr><tr><td>Disk-block 2</td><td>Data-block 1;</td></tr><tr><td>Disk-block 3</td><td>Data-block 2; etc.</td></tr></table>


a. What is the maximum possible number of files?  
b. What is the maximum possible file size in blocks

gate1996 operating-system disk normal file-system descriptive

Answer key

# 5.7.6 Disk: GATE CSE 1997 | Question: 74


A program P reads and processes 1000 consecutive records from a sequential file F stored on device D without using any file system facilities. Given the following

- Size of each record = 3200 bytes  
- Access time of $D = 10$ msecs  
- Data transfer rate of $D = 800 \times 10^{3}$ bytes/second  
- CPU time to process each record = 3 msecs

What is the elapsed time of $P$ if

A. F contains unblocked records and P does not use buffering?  
B. $F$ contains unblocked records and $P$ uses one buffer (i.e., it always reads ahead into the buffer)?  
C. records of $F$ are organized using a blocking factor of 2 (i.e., each block on $D$ contains two records of $F$ ) and $P$ uses one buffer?

gate1997 operating-system disk

Answer key

# 5.7.7 Disk: GATE CSE 1998 | Question: 2-9

Formatting for a floppy disk refers to

A. arranging the data on the disk in contiguous fashion  
B. writing the directory  
C. erasing the system data  
D. writing identification information on all tracks and sectors

gate1998 operating-system disk normal

Answer key

# 5.7.8 Disk: GATE CSE 1998 | Question: 25-a

Free disk space can be used to keep track of using a free list or a bit map. Disk addresses require d bits. For a disk with B blocks, F of which are free, state the condition under which the free list uses less space than the bit map.

gate1998 operating-system disk descriptive

Answer key

# 5.7.9 Disk: GATE CSE 1998 | Question: 25b

Consider a disk with $c$ cylinders, $t$ tracks per cylinder, $s$ sectors per track and a sector length $s_l$ . A logical file $d_l$ with fixed record length $r_l$ is stored continuously on this disk starting at location $(c_L, t_L, s_L)$ , where $c_L, t_L$ and $S_L$ are the cylinder, track and sector numbers, respectively. Derive the formula to calculate the disk address (i.e. cylinder, track and sector) of a logical record $n$ assuming that $r_l = s_l$ .

gate1998 operating-system disk descriptive

Answer key

# 5.7.10 Disk: GATE CSE 1999 | Question: 2-18, ISRO2008-46

Raid configurations of the disks are used to provide

A. Fault-tolerance  
B. High speed  
C. High data density  
D. (A) & (B)

gate1999 operating-system disk easy isro2008

Answer key

# 5.7.11 Disk: GATE CSE 2001 | Question: 1.22

Which of the following requires a device driver?

A. Register

B. Cache

C. Main memory

D. Disk

gatecse-2001 operating-system disk easy

Answer key

# 5.7.12 Disk: GATE CSE 2003 | Question: 25, ISRO2009-12

Using a larger block size in a fixed block size file system leads to

A. better disk throughput but poorer disk space utilization  
B. better disk throughput and better disk space utilization  
C. poorer disk throughput but better disk space utilization  
D. poorer disk throughput and poorer disk space utilization

gatecse-2003 operating-system disk normal isro2009

Answer key







# 5.7.13 Disk: GATE CSE 2004 | Question: 49


A unix-style I-nodes has 10 direct pointers and one single, one double and one triple indirect pointers. Disk block size is 1 Kbyte, disk block address is 32 bits, and 48-bit integers are used. What is the maximum possible file size?

A. $2^{24}$ bytes

B. $2^{32}$ bytes

C. $2^{34}$ bytes

D. $2^{48}$ bytes

gatecse-2004 operating-system disk normal

# Answer key

# 5.7.14 Disk: GATE CSE 2005 | Question: 21

What is the swap space in the disk used for?

A. Saving temporary html pages

B. Saving process data

C. Storing the super-block

D. Storing device drivers

gatecse-2005 operating-system disk easy

# Answer key


# 5.7.15 Disk: GATE CSE 2007 | Question: 11, ISRO2009-36, ISRO2016-21

Consider a disk pack with 16 surfaces, 128 tracks per surface and 256 sectors per track. 512 bytes of data are stored in a bit serial manner in a sector. The capacity of the disk pack and the number of bits required to specify a particular sector in the disk are respectively:

A. 256 Mbyte, 19 bits

B. 256 Mbyte, 28 bits

C. 512 Mbyte, 20 bits

D. 64 Gbyte, 28 bits

gatecse-2007 operating-system disk normal isro2016

# Answer key


# 5.7.16 Disk: GATE CSE 2008 | Question: 32

For a magnetic disk with concentric circular tracks, the seek latency is not linearly proportional to the seek distance due to

A. non-uniform distribution of requests  
B. arm starting and stopping inertia  
C. higher capacity of tracks on the periphery of the platter  
D. use of unfair arm scheduling policies

gatecse-2008 operating-system disk normal

# Answer key


# 5.7.17 Disk: GATE CSE 2009 | Question: 51

A hard disk has 63 sectors per track, 10 platters each with 2 recording surfaces and 1000 cylinders. The address of a sector is given as a triple $\langle c, h, s \rangle$ , where c is the cylinder number, h is the surface number and s is the sector number. Thus, the $0^{th}$ sector is addresses as $\langle 0, 0, 0 \rangle$ , the $1^{st}$ sector as $\langle 0, 0, 1 \rangle$ , and so on The address $\langle 400, 16, 29 \rangle$ corresponds to sector number:

A. 505035

B. 505036

C. 505037

D. 505038

gatecse-2009 operating-system disk normal

# Answer key

# 5.7.18 Disk: GATE CSE 2009 | Question: 52

A hard disk has 63 sectors per track, 10 platters each with 2 recording surfaces and 1000 cylinders. The address of a sector is given as a triple $\langle c, h, s \rangle$ , where c is the cylinder number, h is the surface number and s is the sector number. Thus, the $0^{th}$ sector is addresses as $\langle 0, 0, 0 \rangle$ , the $1^{st}$ sector as $\langle 0, 0, 1 \rangle$ , and so on


