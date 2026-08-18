# 1.24.17 Pipelining: GATE CSE 2014 | Set 3 | Question: 43


An instruction pipeline has five stages, namely, instruction fetch (IF), instruction decode and register fetch (ID/RF), instruction execution (EX), memory access (MEM), and register writeback (WB) with stage latencies 1 ns, 2.2 ns, 2 ns, 1 ns, and 0.75 ns, respectively (ns stands for nanoseconds). To gain in terms of frequency designers have decided to split the ID/RF stage into three stages (ID, RF1, RF2) each of latency 2.2/3 ns, the EX stage is split into two stages (EX1, EX2) each of latency 1 ns. The new design has a total of eight stages. A program has 20% branch instructions which execute in the EX stage and produce the next instruction pointer at the end of the EX stage in the old design and at the end of the EX2 stage in the new design. The IF stalls after fetching a branch instruction until the next instruction pointer is computed. All instructions other than branch instruction have an average CPI of one in both the designs. The execution times of this program on the and the new design are P and Q nanoseconds, respectively. The value of P/Q is \_\_\_\_.

gatecse-2014-set3 co-and-architecture pipelining numerical-answers normal

Answer key

# 1.24.18 Pipelining: GATE CSE 2014 | Set 3 | Question: 9

Consider the following processors (ns stands for nanoseconds). Assume that the pipeline registers have zero latency.

• P1: Four-stage pipeline with stage latencies 1 ns, 2 ns, 2 ns, 1 ns.  
• P2: Four-stage pipeline with stage latencies 1 ns, 1.5 ns, 1.5 ns, 1.5 ns.  
• P3: Five-stage pipeline with stage latencies 0.5 ns, 1 ns, 1 ns, 0.6 ns, 1 ns.  
- P4: Five-stage pipeline with stage latencies 0.5 ns, 0.5 ns, 1 ns, 1 ns, 1.1 ns.

Which processor has the highest peak clock frequency?

A. P1

B. P2

C. P3

D. P4

gatecse-2014-set3 co-and-architecture pipelining normal

Answer key

# 1.24.19 Pipelining: GATE CSE 2015 | Set 1 | Question: 38


Consider a non-pipelined processor with a clock rate of 2.5 gigahertz and average cycles per instruction of four. The same processor is upgraded to a pipelined processor with five stages; but due to the internal pipeline delay, the clock speed is reduced to 2 gigahertz. Assume that there are no stalls in the pipelin speedup achieved in this pipelined processor is \_\_\_\_.

gatecse-2015-set1 co-and-architecture pipelining normal numerical-answers

Answer key

# 1.24.20 Pipelining: GATE CSE 2015 | Set 2 | Question: 44


Consider the sequence of machine instruction given below:

<table><tr><td>MUL</td><td>R5, R0, R1</td></tr><tr><td>DIV</td><td>R6, R2, R3</td></tr><tr><td>ADD</td><td>R7, R5, R6</td></tr><tr><td>SUB</td><td>R8, R7, R4</td></tr></table>


In the above sequence, R0 to R8 are general purpose registers. In the instructions shown, the first register shows the result of the operation performed on the second and the third registers. This sequence of instructions is to be executed in a pipelined instruction processor with the following 4 stages: (1) Instruction Fetch and Decode (IF), (2) Operand Fetch (OF), (3) Perform Operation (PO) and (4) Write back the result (WB). The IF, OF and WB stages take 1 clock cycle each for any instruction. The PO stage takes 1 clock cycle for ADD and SUB instruction, 3 clock cycles for MUL instruction and 5 clock cycles for DIV instruction. The pipelined processor uses

operand forwarding from the PO stage to the OF stage. The number of clock cycles taken for the execution of the above sequence of instruction is \_\_\_\_.

gatecse-2015-set2 co-and-architecture pipelining normal numerical-answers

# Answer key

# 1.24.21 Pipelining: GATE CSE 2015 | Set 3 | Question: 51

Consider the following reservation table for a pipeline having three stages $S_{1}$ , $S_{2}$ and $S_{3}$ .

<table><tr><td>Time →</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td></tr><tr><td> $S_1$ </td><td>X</td><td></td><td></td><td></td><td>X</td></tr><tr><td> $S_2$ </td><td></td><td>X</td><td></td><td>X</td><td></td></tr><tr><td> $S_3$ </td><td></td><td></td><td>X</td><td></td><td></td></tr></table>


The minimum average latency (MAL) is \_\_\_\_

gatecse-2015-set3 co-and-architecture pipelining difficult numerical-answers

# Answer key

# 1.24.22 Pipelining: GATE CSE 2016 | Set 1 | Question: 32

The stage delays in a 4-stage pipeline are 800, 500, 400 and 300 picoseconds. The first stage (with delay 800 picoseconds) is replaced with a functionality equivalent design involving two stages with respective delays 600 and 350 picoseconds. The throughput increase of the pipeline is \_\_\_\_ percent.


gatecse-2016-set1 co-and-architecture pipelining normal numerical-answers

# Answer key

# 1.24.23 Pipelining: GATE CSE 2016 | Set 2 | Question: 33

Consider a 3 GHz (gigahertz) processor with a three stage pipeline and stage latencies $\tau_{1}$ , $\tau_{2}$ and $\tau_{3}$ such that $\tau_{1} = \frac{3\tau_{2}}{4} = 2\tau_{3}$ . If the longest pipeline stage is split into two pipeline stages of equal latency, the new frequency is \_\_\_\_ GHz, ignoring delays in the pipeline registers.


gatecse-2016-set2 co-and-architecture pipelining normal numerical-answers

# Answer key

# 1.24.24 Pipelining: GATE CSE 2017 | Set 1 | Question: 50

Instruction execution in a processor is divided into 5 stages, Instruction Fetch (IF), Instruction

Decode (ID), Operand fetch (OF), Execute (EX), and Write Back (WB). These stages take 5, 4, 20, 10 and 3 nanoseconds (ns) respectively. A pipelined implementation of the processor requires buffering between each pair of consecutive stages with a delay of 2 ns. Two pipelined implementation of the processor are contemplated:

i. a naive pipeline implementation (NP) with 5 stages and  
ii. an efficient pipeline (EP) where the OF stage is divided into stages OF1 and OF2 with execution times of 12 ns and 8 ns respectively.

The speedup (correct to two decimal places) achieved by EP over NP in executing 20 independent instructions with no hazards is \_\_\_\_.

gatecse-2017-set1 co-and-architecture pipelining normal numerical-answers

# Answer key


The instruction pipeline of a RISC processor has the following stages: Instruction Fetch (IF), Instruction Decode (ID), Operand Fetch (OF), Perform Operation (PO) and Writeback (WB), The IF, ID, OF and WB stages take 1 clock cycle each for every instruction. Consider a sequence of 100 instructions. In the stage, 40 instructions take 3 clock cycles each, 35 instructions take 2 clock cycles each, and the remain instructions take 1 clock cycle each. Assume that there are no data hazards and no control hazards.

The number of clock cycles required for completion of execution of the sequence of instruction is \_\_\_\_.

gatecse-2018 co-and-architecture pipelining numerical-answers two-marks

Answer key

# 1.24.26 Pipelining: GATE CSE 2020 | Question: 43


Consider a non-pipelined processor operating at 2.5 GHz. It takes 5 clock cycles to complete an instruction. You are going to make a 5- stage pipeline out of this processor. Overheads associated with pipelining force you to operate the pipelined processor at 2 GHz. In a given program, assume that 30% are memory instructions, 60% are ALU instructions and the rest are branch instructions. 5% of the memory instructions cause stalls of 50 clock cycles each due to cache misses and 50% of the branch instructions cause stalls of 2 cycles each. Assume that there are no stalls associated with the execution of ALU instructions. For this program, the speedup achieved by the pipelined processor over the non-pipelined processor (round off to 2 decimal places) is \_\_\_\_.

gatecse-2020 numerical-answers co-and-architecture pipelining two-marks

Answer key

# 1.24.27 Pipelining: GATE CSE 2021 | Set 1 | Question: 53


A five-stage pipeline has stage delays of 150, 120, 150, 160 and 140 nanoseconds. The registers that are used between the pipeline stages have a delay of 5 nanoseconds each.

The total time to execute 100 independent instructions on this pipeline, assuming there are no pipeline stalls, is \_\_\_\_ nanoseconds.

gatecse-2021-set1 co-and-architecture pipelining numerical-answers two-marks

Answer key

# 1.24.28 Pipelining: GATE CSE 2021 | Set 2 | Question: 53


Consider a pipelined processor with 5 stages, Instruction Fetch(IF), Instruction Decode(ID), Execute (EX), Memory Access (MEM), and Write Back (WB). Each stage of the pipeline, except the

EX stage, takes one cycle. Assume that the ID stage merely decodes the instruction and the register read is performed in the EX stage. The EX stage takes one cycle for ADD instruction and two cycles for MUL instruction. Ignore pipeline register latencies.

Consider the following sequence of 8 instructions:

$$
\text {ADD, MUL, ADD, MUL, ADD, MUL, ADD, MUL}
$$

Assume that every MUL instruction is data-dependent on the ADD instruction just before it and every ADD instruction (except the first ADD) is data-dependent on the MUL instruction just before it. The speedup defined as follows.

$$
S p e e d u p = \frac {\text {Execution time without operand forwarding}}{\text {Execution time with operand forwarding}}
$$

The Speedup achieved in executing the given instruction sequence on the pipelined processor (rounded to 2 decimal places) is \_\_\_\_

gatecse-2021-set2 co-and-architecture pipelining numerical-answers two-marks

Answer key

# 1.24.29 Pipelining: GATE CSE 2023 | Question: 23


Consider a 3-stage pipelined processor having a delay of 10 ns (nanoseconds), 20 ns, and 14 ns, for the first, second, and the third stages, respectively. Assume that there is no other delay and the processor does not suffer from any pipeline hazards. Also assume that one instruction is fetched every cycle.

The total execution time for executing 100 instructions on this processor is \_\_\_\_ ns.

gatecse-2023 co-and-architecture pipelining numerical-answers one-mark

# Answer key

# 1.24.30 Pipelining: GATE CSE 2024 | Set 1 | Question: 20


Consider a 5-stage pipelined processor with Instruction Fetch (IF), Instruction Decode (ID), Execute (EX), Memory Access (MEM), and Register Writeback (WB) stages. Which of the following statements about forwarding is/are CORRECT?

A. In a pipelined execution, forwarding means the result from a source stage of an earlier instruction is passed on to the destination stage of a later instruction  
B. In forwarding, data from the output of the MEM stage can be passed on to the input of the EX stage of the next instruction  
C. Forwarding cannot prevent all pipeline stalls  
D. Forwarding does not require any extra hardware to retrieve the data from the pipeline stages

gatecse-2024-set1 multiple-selects co-and-architecture pipelining one-mark

# Answer key

# 1.24.31 Pipelining: GATE CSE 2024 | Set 2 | Question: 21


An instruction format has the following structure:

Instruction Number: Opcode destination reg, source reg-1, source reg-2

Consider the following sequence of instructions to be executed in a pipelined processor:

I 1: DIV R3, R1, R2  
I 2: SUB R5, R3, R4  
I 3: ADD R3, R5, R6  
I 4: MUL R7, R3, R8

Which of the following statements is/are TRUE?

A. There is a RAW dependency on R 3 between I 1 and I 2  
B. There is a WAR dependency on R 3 between I 1 and I 3  
C. There is a RAW dependency on R 3 between I 2 and I 3  
D. There is a WAW dependency on R 3 between I 3 and I 4

gatecse-2024-set2 co-and-architecture multiple-selects pipelining one-mark

# Answer key

# 1.24.32 Pipelining: GATE CSE 2024 | Set 2 | Question: 48


A non-pipelined instruction execution unit operating at 2GHz takes an average of 6 cycles to execute an instruction of a program P. The unit is then redesigned to operate on a 5 -stage pipeline at 2GHz. Assume

that the ideal throughput of the pipelined unit is 1 instruction per cycle. In the execution of program P, 20% instructions incur an average of 2 cycles stall due to data hazards and 20% instructions incur an average of 3 cycles stall due to control hazards. The speedup (rounded off to one decimal place) obtained by the pipelined design over the non-pipelined design is \_\_\_\_.

gatecse-2024-set2 numerical-answers co-and-architecture pipelining two-marks

# Answer key

# 1.24.33 Pipelining: GATE CSE 2025 | Set 2 | Question: 46


A 5-stage instruction pipeline has stage delays of 180, 250, 150, 170, and 250, respectively, in nanoseconds. The delay of an inter-stage latch is 10 nanoseconds. Assume that there are no pipeline stalls due to branches and other hazards. The time taken to process 1000 instructions in microseconds is \_\_\_\_ (rounded off to two decimal places)

gatecse2025-set2 co-and-architecture pipelining numerical-answers easy two-marks

# Answer key

# 1.24.34 Pipelining: GATE IT 2004 | Question: 47

Consider a pipeline processor with 4 stages S1 to S4. We want to execute the following loop:


$$
\begin{array}{c} \hline \text {for (i = 1; i <   = 1000; i++)} \\ \{\mathrm{I1}, \mathrm{I2}, \mathrm{I3}, \mathrm{I4} \} \end{array}
$$

where the time taken (in ns) by instructions I1 to I4 for stages S1 to S4 are given below:

<table><tr><td></td><td> $S_{1}$ </td><td> $S_{2}$ </td><td> $S_{3}$ </td><td> $S_{4}$ </td></tr><tr><td>I1</td><td>1</td><td>2</td><td>1</td><td>2</td></tr><tr><td>I2</td><td>2</td><td>1</td><td>2</td><td>1</td></tr><tr><td>I3</td><td>1</td><td>1</td><td>2</td><td>1</td></tr><tr><td>I4</td><td>2</td><td>1</td><td>2</td><td>1</td></tr></table>

The output of I1 for i = 2 will be available after

A. 11 ns

B. 12 ns

C. 13 ns

D. 28 ns

gateit-2004 co-and-architecture pipelining normal

# Answer key

# 1.24.35 Pipelining: GATE IT 2005 | Question: 44


We have two designs D1 and D2 for a synchronous pipeline processor. D1 has 5 pipeline stages with execution times of 3 nsec, 2 nsec, 4 nsec, 2 nsec and 3 nsec while the design D2 has 8 pipeline stages each with 2 nsec execution time. How much time can be saved using design D2 over design D1 for executing 100 instructions?

A. 214 nsec

B. 202 nsec

C. 86 nsec

D. -200 nsec

gateit-2005 co-and-architecture pipelining normal

# Answer key

# 1.24.36 Pipelining: GATE IT 2006 | Question: 78


A pipelined processor uses a 4-stage instruction pipeline with the following stages: Instruction fetch (IF), Instruction decode (ID), Execute (EX) and Writeback (WB). The arithmetic operations as well as the load and store operations are carried out in the EX stage. The sequence of instructions corresponding to the statement $X = (S - R * (P + Q)) / T$ is given below. The values of variables $P, Q, R, S$ and $T$ are available in the registers $R0, R1, R2, R3$ and $R4$ respectively, before the execution of the instruction sequence.

$$
\begin{array}{l} \mathrm{ADD} \quad \mathrm{R5}, \mathrm{R0}, \mathrm{R1} \quad ; \mathrm{R5} \leftarrow \mathrm{R0} + \mathrm{R1} \\ \mathrm{MUL} \quad \mathrm{R6}, \mathrm{R2}, \mathrm{R5} \quad ; \mathrm{R6} \leftarrow \mathrm{R2} ^ {*} \mathrm{R5} \\ \mathrm{SUB} \quad \mathrm{R5}, \mathrm{R3}, \mathrm{R6}; \mathrm{R5} \leftarrow \mathrm{R3} - \mathrm{R6} \\ \mathrm{DIV} \quad \mathrm{R6}, \mathrm{R5}, \mathrm{R4} \quad ; \mathrm{R6} \leftarrow \mathrm{R5} / \mathrm{R4} \\ \text {STORE} \quad \mathrm{R6}, \mathrm{X} \quad ; \mathrm{X} \leftarrow \mathrm{R6} \\ \end{array}
$$

The number of Read-After-Write (RAW) dependencies, Write-After-Read(WAR) dependencies, and Write-After-Write (WAW) dependencies in the sequence of instructions are, respectively,

A. 2,2,4

B. 3,2,3

C. 4,2,2

D. 3,3,2

gateit-2006 co-and-architecture pipelining normal

# Answer key

# 1.24.37 Pipelining: GATE IT 2006 | Question: 79

A pipelined processor uses a 4-stage instruction pipeline with the following stages: Instruction fetch (IF), Instruction decode (ID), Execute (EX) and Writeback (WB). The arithmetic operations as well as the load and store operations are carried out in the EX stage. The sequence of instructions corresponding to the statement $X = (S - R * (P + Q)) / T$ is given below. The values of variables $P, Q, R, S$ and $T$ are available in the registers $R0, R1, R2, R3$ and $R4$ respectively, before the execution of the instruction sequence.

<table><tr><td>ADD</td><td>R5,R0,R1</td><td>;R5←R0+R1</td></tr><tr><td>MUL</td><td>R6,R2,R5</td><td>;R6←R2*R5</td></tr><tr><td>SUB</td><td>R5,R3,R6</td><td>;R5←R3-R6</td></tr><tr><td>DIV</td><td>R6,R5,R4</td><td>;R6←R5/R4</td></tr><tr><td>STORE</td><td>R6,X</td><td>;X←R6</td></tr></table>

The IF, ID and WB stages take 1 clock cycle each. The EX stage takes 1 clock cycle each for the ADD, SUB and STORE operations, and 3 clock cycles each for MUL and DIV operations. Operand forwarding from the EX stage to the ID stage is used. The number of clock cycles required to complete the sequence of instructions is

A. 10

B. 12

C. 14

D. 16

gateit-2006 co-and-architecture pipelining normal

# Answer key

# 1.24.38 Pipelining: GATE IT 2007 | Question: 6, ISRO2011-25

A processor takes 12 cycles to complete an instruction I. The corresponding pipelined processor uses 6 stages with the execution times of 3, 2, 5, 4, 6 and 2 cycles respectively. What is the asymptotic speedup assuming that a very large number of instructions are to be executed?

A. 1.83

B. 2

C. 3

D. 6

gateit-2007 co-and-architecture pipelining normal isro2011

# Answer key

# 1.24.39 Pipelining: GATE IT 2008 | Question: 40

A non pipelined single cycle processor operating at 100 MHz is converted into a synchronous pipelined processor with five stages requiring 2.5 nsec, 1.5 nsec, 2 nsec, 1.5 nsec and 2.5 nsec, respectively. The delay of the latches is 0.5 nsec. The speedup of the pipeline processor for a large number of instructions is:

A. 4.5

B. 4.0

C. 3.33

D. 3.0

gateit-2008 co-and-architecture pipelining normal

# Answer key

# 1.25

# Runtime Environment (2)

# 1.25.1 Runtime Environment: GATE CSE 2001 | Question: 1.10, UGCNET-Dec2012-III: 36

Suppose a processor does not have any stack pointer registers, which of the following statements is true?

A. It cannot have subroutine call instruction  
B. It cannot have nested subroutines call  
C. Interrupts are not possible  
D. All subroutine calls and interrupts are possible





# 1.25.2 Runtime Environment: GATE CSE 2008 | Question: 37, ISRO2009-38


The use of multiple register windows with overlap causes a reduction in the number of memory accesses for:

I. Function locals and parameters  
II. Register saves and restores  
III. Instruction fetches

A. I only

B. II only

C. III only

D. I, II and III

gatecse-2008 co-and-architecture normal isro2009 runtime-environment

# Answer key

# 1.26

# Speedup (6)

# Practice Test: Test 1 (11Q)

# 1.26.1 Speedup: GATE CSE 2014 | Set 1 | Question: 43


Consider a 6-stage instruction pipeline, where all stages are perfectly balanced. Assume that there is no cycle-time overhead of pipelining. When an application is executing on this 6-stage pipeline, the speedup achieved with respect to non-pipelined execution if 25% of the instructions incur 2 pipeline stall cycles is

gatecse-2014-set1 co-and-architecture pipelining numerical-answers normal speedup

# Answer key

# 1.26.2 Speedup: GATE CSE 2014 | Set 1 | Question: 55


Consider two processors $P_1$ and $P_2$ executing the same instruction set. Assume that under identical conditions, for the same input, a program running on $P_2$ takes 25% less time but incurs 20% more CPI (clock cycles per instruction) as compared to the program running on $P_1$ . If the clock frequency of $P_1$ is 1GHz, then the clock frequency of $P_2$ (in GHz) is \_\_\_\_.

gatecse-2014-set1 co-and-architecture numerical-answers normal speedup

# Answer key

# 1.26.3 Speedup: GATE CSE 2024 | Set 1 | Question: 45


The baseline execution time of a program on a 2GHz single core machine is 100 nanoseconds (ns). The code corresponding to 90% of the execution time can be fully parallelized. The overhead for using an additional core is 10 ns when running on a multicore system. Assume that all cores in the multicore system run their share of the parallelized code for an equal amount of time.

The number of cores that minimize the execution time of the program is \_\_\_\_.

gatecse-2024-set1 numerical-answers co-and-architecture speedup two-marks

# Answer key

# 1.26.4 Speedup: GATE CSE 2026 | Set 2 | Question: 47


A non-pipelined instruction execution unit that operates at 1.6 GHz clock takes an average of 5 clock cycles to complete the execution of an instruction. To improve the performance, the system was pipelined with a goal of achieving an average throughput of one instruction per clock cycle. However, it could operate only at 1.2 GHz due to pipeline overheads. While executing a program in the pipelined design, 30% of instructions encountered a stall of 2 cycles due to pipeline hazards. The speed-up obtained by the pipelined design over the non-pipelined one for this program is \_\_\_\_ (rounded off to two decimal places)

Note: $1G = 10^{9}$

# 1.26.5 Speedup: GATE IT 2004 | Question: 50


In an enhancement of a design of a CPU, the speed of a floating point unit has been increased by 20% and the speed of a fixed point unit has been increased by 10%. What is the overall speedup achieved if the ratio of the number of floating point operations to the number of fixed point operations is 2:3 and the floating point operation used to take twice the time taken by the fixed point operation in the original design?

A. 1.155

B. 1.185

C. 1.255

D. 1.285

gateit-2004 normal co-and-architecture speedup

# Answer key

# 1.26.6 Speedup: GATE IT 2007 | Question: 36


The floating point unit of a processor using a design $D$ takes $2t$ cycles compared to $t$ cycles taken by the fixed point unit. There are two more design suggestions $D_1$ and $D_2$ . $D_1$ uses $30\%$ more cycles for fixed point unit but $30\%$ less cycles for floating point unit as compared to design $D$ . $D_2$ uses $40\%$ less cycles for fixed point unit but $10\%$ more cycles for floating point unit as compared to design $D$ . For a given program which has $80\%$ fixed point operations and $20\%$ floating point operations, which of the following ordering reflects the relative performances of three designs?

$(D_{i} > D_{j}$ denotes that $D_{i}$ is faster than $D_{j}$ )

A. $D_{1} > D > D_{2}$

B. $D_{2} > D > D_{1}$

C. $D > D_{2} > D_{1}$

D. $D > D_{1} > D_{2}$

gateit-2007 co-and-architecture normal speedup

# Answer key

# 1.27

# Stall (1)

# 1.27.1 Stall: GATE CSE 2022 | Question: 51


A processor $X_{1}$ operating at 2 GHz has a standard 5-stage RISC instruction pipeline having a base CPI (cycles per instruction) of one without any pipeline hazards. For a given program P that has 30% branch instructions, control hazards incur 2 cycles stall for every branch. A new version of the processor $X_{2}$ operating at same clock frequency has an additional branch predictor unit (BPU) that completely eliminates stalls for correctly predicted branches. There is neither any savings nor any additional stalls for wrong predictions. There are no structural hazards and data hazards for $X_{1}$ and $X_{2}$ . If the BPU has a prediction accuracy of 80%, the speed up (rounded off to two decimal places) obtained by $X_{2}$ over $X_{1}$ in executing P is \_\_\_\_.

gatecse-2022 numerical-answers co-and-architecture pipelining stall two-marks

# Answer key

# 1.28

# Virtual Memory (3)

# 1.28.1 Virtual Memory: GATE CSE 1991 | Question: 03,iii


The total size of address space in a virtual memory system is limited by:

A. the length of MAR

B. the available secondary storage

C. the available main memory

D. all of the above

E. none of the above

gate1991 co-and-architecture virtual-memory normal multiple-selects

# Answer key

# 1.28.2 Virtual Memory: GATE CSE 2004 | Question: 47


Consider a system with a two-level paging scheme in which a regular memory access takes 150 nanoseconds, and servicing a page fault takes 8 milliseconds. An average instruction takes 100 nanoseconds of CPU time, and two memory accesses. The TLB hit ratio is 90%, and the page fault rate is one in every 10,000 instructions. What is the effective average instruction execution time?

A. 645 nanoseconds  
C. 1215 nanoseconds

B. 1050 nanoseconds  
D. 1230 nanoseconds

gatecse-2004 co-and-architecture virtual-memory normal

# Answer key

# 1.28.3 Virtual Memory: GATE CSE 2008 | Question: 38

In an instruction execution pipeline, the earliest that the data TLB (Translation Lookaside Buffer) can be accessed is:


A. before effective address calculation has started  
B. during effective address calculation  
C. after effective address calculation has completed  
D. after data cache lookup has completed

gatecse-2008 co-and-architecture virtual-memory normal

# Answer key

Answer Keys

<table><tr><td>1.1.1</td><td>C</td><td>1.1.2</td><td>N/A</td><td>1.1.3</td><td>N/A</td><td>1.1.4</td><td>N/A</td><td>1.1.5</td><td>B</td></tr><tr><td>1.1.6</td><td>D</td><td>1.1.7</td><td>A;B;C;D</td><td>1.1.8</td><td>C</td><td>1.1.9</td><td>A</td><td>1.1.10</td><td>B</td></tr><tr><td>1.1.11</td><td>C</td><td>1.1.12</td><td>B</td><td>1.1.13</td><td>C</td><td>1.1.14</td><td>C</td><td>1.1.15</td><td>D</td></tr><tr><td>1.1.16</td><td>D</td><td>1.1.17</td><td>B</td><td>1.1.18</td><td>D</td><td>1.1.19</td><td>D</td><td>1.2.1</td><td>180</td></tr><tr><td>1.2.2</td><td>11.83:11.87</td><td>1.2.3</td><td>4:4</td><td>1.3.1</td><td>16417</td><td>1.4.1</td><td>A;B;C;D</td><td>1.4.2</td><td>D</td></tr><tr><td>1.5.1</td><td>N/A</td><td>1.5.2</td><td>N/A</td><td>1.5.3</td><td>22</td><td>1.5.4</td><td>N/A</td><td>1.5.5</td><td>D</td></tr><tr><td>1.5.6</td><td>D</td><td>1.5.7</td><td>61.25</td><td>1.5.8</td><td>N/A</td><td>1.5.9</td><td>B</td><td>1.5.10</td><td>B</td></tr><tr><td>1.5.11</td><td>N/A</td><td>1.5.12</td><td>N/A</td><td>1.5.13</td><td>C</td><td>1.5.14</td><td>A</td><td>1.5.15</td><td>A</td></tr><tr><td>1.5.16</td><td>D</td><td>1.5.17</td><td>C</td><td>1.5.18</td><td>B</td><td>1.5.19</td><td>D</td><td>1.5.20</td><td>C</td></tr><tr><td>1.5.21</td><td>A</td><td>1.5.22</td><td>A</td><td>1.5.23</td><td>D</td><td>1.5.24</td><td>B</td><td>1.5.25</td><td>C</td></tr><tr><td>1.5.26</td><td>D</td><td>1.5.27</td><td>C</td><td>1.5.28</td><td>C</td><td>1.5.29</td><td>D</td><td>1.5.30</td><td>C</td></tr><tr><td>1.5.31</td><td>A</td><td>1.5.32</td><td>A</td><td>1.5.33</td><td>A</td><td>1.5.34</td><td>D</td><td>1.5.35</td><td>D</td></tr><tr><td>1.5.36</td><td>20</td><td>1.5.37</td><td>1.68</td><td>1.5.38</td><td>14</td><td>1.5.39</td><td>A</td><td>1.5.40</td><td>24</td></tr><tr><td>1.5.41</td><td>30</td><td>1.5.42</td><td>0.05</td><td>1.5.43</td><td>14</td><td>1.5.44</td><td>A</td><td>1.5.45</td><td>4.7:4.8</td></tr><tr><td>1.5.46</td><td>18</td><td>1.5.47</td><td>B</td><td>1.5.48</td><td>D</td><td>1.5.49</td><td>160</td><td>1.5.50</td><td>13.3:13.3;13.5:13.5</td></tr><tr><td>1.5.51</td><td>B</td><td>1.5.52</td><td>17:17</td><td>1.5.53</td><td>2:2</td><td>1.5.54</td><td>A</td><td>1.5.55</td><td>A;B;D</td></tr><tr><td>1.5.56</td><td>0.85</td><td>1.5.57</td><td>19</td><td>1.5.58</td><td>B;C</td><td>1.5.59</td><td>3</td><td>1.5.60</td><td>A</td></tr><tr><td>1.5.61</td><td>B;C</td><td>1.5.62</td><td>C</td><td>1.5.63</td><td>B</td><td>1.5.64</td><td>C</td><td>1.5.65</td><td>C</td></tr><tr><td>1.5.66</td><td>A</td><td>1.5.67</td><td>B</td><td>1.5.68</td><td>D</td><td>1.5.69</td><td>A</td><td>1.6.1</td><td>76</td></tr><tr><td>1.7.1</td><td>B</td><td>1.8.1</td><td>D</td><td>1.8.2</td><td>B</td><td>1.8.3</td><td>456</td><td>1.8.4</td><td>80000:80000</td></tr><tr><td>1.8.5</td><td>A</td><td>1.8.6</td><td>C</td><td>1.8.7</td><td>C</td><td>1.8.8</td><td>C</td><td>1.9.1</td><td>A</td></tr><tr><td>1.10.1</td><td>A</td><td>1.10.2</td><td>B</td><td>1.10.3</td><td>B</td><td>1.10.4</td><td>B</td><td>1.11.1</td><td>B</td></tr><tr><td>1.12.1</td><td>N/A</td><td>1.12.2</td><td>D</td><td>1.12.3</td><td>B</td><td>1.12.4</td><td>B</td><td>1.12.5</td><td>28</td></tr><tr><td>1.12.6</td><td>C</td><td>1.12.7</td><td>A;B;C</td><td>1.13.1</td><td>A;B;D</td><td>1.13.2</td><td>A</td><td>1.13.3</td><td>A</td></tr><tr><td>1.13.4</td><td>A;B</td><td>1.13.5</td><td>128</td><td>1.14.1</td><td>77.3:77.3</td><td>1.15.1</td><td>95:95</td><td>1.16.1</td><td>True</td></tr><tr><td>1.16.2</td><td>True</td><td>1.16.3</td><td>False</td><td>1.16.4</td><td>A</td><td>1.16.5</td><td>1.4:1.5</td><td>1.16.6</td><td>B</td></tr><tr><td>1.16.7</td><td>B</td><td>1.16.8</td><td>A</td><td>1.17.1</td><td>False</td><td>1.17.2</td><td>N/A</td><td>1.17.3</td><td>C</td></tr><tr><td>1.17.4</td><td>C</td><td>1.17.5</td><td>A</td><td>1.17.6</td><td>-16.0</td><td>1.17.7</td><td>3.0:3.0</td><td>1.18.1</td><td>N/A</td></tr><tr><td>1.18.2</td><td>256</td><td>1.18.3</td><td>True</td><td>1.18.4</td><td>16383</td><td>1.18.5</td><td>500</td><td>1.18.6</td><td>32</td></tr><tr><td>1.18.7</td><td>14</td><td>1.18.8</td><td>32</td><td>1.18.9</td><td>34</td><td>1.18.10</td><td>D</td><td>1.18.11</td><td>B</td></tr><tr><td>1.19.1</td><td>D</td><td>1.20.1</td><td>D</td><td>1.20.2</td><td>B</td><td>1.20.3</td><td>A</td><td>1.20.4</td><td>A</td></tr><tr><td>1.20.5</td><td>B</td><td>1.20.6</td><td>C</td><td>1.20.7</td><td>C</td><td>1.20.8</td><td>10.2</td><td>1.20.9</td><td>A</td></tr><tr><td>1.20.10</td><td>C</td><td>1.21.1</td><td>N/A</td><td>1.21.2</td><td>N/A</td><td>1.21.3</td><td>N/A</td><td>1.21.4</td><td>B</td></tr><tr><td>1.21.5</td><td>A</td><td>1.21.6</td><td>D</td><td>1.21.7</td><td>B</td><td>1.21.8</td><td>C</td><td>1.21.9</td><td>B</td></tr><tr><td>1.21.10</td><td>D</td><td>1.21.11</td><td>A</td><td>1.21.12</td><td>C</td><td>1.21.13</td><td>D</td><td>1.21.14</td><td>D</td></tr><tr><td>1.21.15</td><td>16</td><td>1.21.16</td><td>50:50</td><td>1.21.17</td><td>B</td><td>1.21.18</td><td>B</td><td>1.21.19</td><td>D</td></tr><tr><td>1.21.20</td><td>C</td><td>1.21.21</td><td>A</td><td>1.22.1</td><td>TBA</td><td>1.22.2</td><td>N/A</td><td>1.22.3</td><td>D</td></tr><tr><td>1.22.4</td><td>31</td><td>1.22.5</td><td>59:60</td><td>1.22.6</td><td>C</td><td>1.23.1</td><td>N/A</td><td>1.23.2</td><td>C</td></tr><tr><td>1.23.3</td><td>C</td><td>1.23.4</td><td>B</td><td>1.23.5</td><td>D</td><td>1.23.6</td><td>A</td><td>1.23.7</td><td>D</td></tr><tr><td>1.23.8</td><td>A</td><td>1.23.9</td><td>D</td><td>1.23.10</td><td>B</td><td>1.23.11</td><td>D</td><td>1.23.12</td><td>D</td></tr><tr><td>1.24.1</td><td>15</td><td>1.24.2</td><td>B</td><td>1.24.3</td><td>N/A</td><td>1.24.4</td><td>N/A</td><td>1.24.5</td><td>D</td></tr><tr><td>1.24.6</td><td>D</td><td>1.24.7</td><td>C</td><td>1.24.8</td><td>C</td><td>1.24.9</td><td>B</td><td>1.24.10</td><td>A</td></tr><tr><td>1.24.11</td><td>D</td><td>1.24.12</td><td>B</td><td>1.24.13</td><td>B</td><td>1.24.14</td><td>B</td><td>1.24.15</td><td>C</td></tr><tr><td>1.24.16</td><td>B</td><td>1.24.17</td><td>1.50:1.60</td><td>1.24.18</td><td>C</td><td>1.24.19</td><td>3.2</td><td>1.24.20</td><td>13</td></tr><tr><td>1.24.21</td><td>3</td><td>1.24.22</td><td>33.0:34.0</td><td>1.24.23</td><td>4</td><td>1.24.24</td><td>1.50:1.51</td><td>1.24.25</td><td>219</td></tr><tr><td>1.24.26</td><td>2.15:2.18</td><td>1.24.27</td><td>17160:17160</td><td>1.24.28</td><td>1.87:1.88</td><td>1.24.29</td><td>2040</td><td>1.24.30</td><td>A;B;C</td></tr><tr><td>1.24.31</td><td>A</td><td>1.24.32</td><td>3</td><td>1.24.33</td><td>260.20:261.20</td><td>1.24.34</td><td>C</td><td>1.24.35</td><td>B</td></tr><tr><td>1.24.36</td><td>C</td><td>1.24.37</td><td>B</td><td>1.24.38</td><td>B</td><td>1.24.39</td><td>C</td><td>1.25.1</td><td>X</td></tr><tr><td>1.25.2</td><td>A</td><td>1.26.1</td><td>4</td><td>1.26.2</td><td>1.6</td><td>1.26.3</td><td>3</td><td>1.26.4</td><td>2.30:2.40</td></tr><tr><td>1.26.5</td><td>A</td><td>1.26.6</td><td>B</td><td>1.27.1</td><td>1.42:1.45</td><td>1.28.1</td><td>A;B</td><td>1.28.2</td><td>D</td></tr><tr><td>1.28.3</td><td>C</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr></table>

Concept of layering.OSI and TCP/IP Protocol Stacks; Basics of packet, circuit and virtual circuit-switching; Data link layer: framing, error detection, Medium Access Control, Ethernet bridging; Routing protocols: shortest path, flooding, distance vector and link state routing; Fragmentation and IP addressing, IPv4, CIDR notation, Basics of IP support protocols (ARP, DHCP, ICMP), Network Address Translation (NAT); Transport layer: flow control and congestion control, UDP, TCP, sockets; Application layer protocols: DNS, SMTP, HTTP, FTP, Email.

Mark Distribution in Previous GATE

<table><tr><td>Year</td><td>2026 - 1</td><td>2026 - 2</td><td>2025 - 1</td><td>2025 - 2</td><td>2024 - 1</td><td>2024 - 2</td><td>2023</td><td>2022</td><td>2021 - 1</td><td>2021 - 2</td><td>Minimum</td></tr><tr><td>1 Mark Count</td><td>2</td><td>3</td><td>2</td><td>4</td><td>3</td><td>3</td><td>2</td><td>2</td><td>1</td><td>1</td><td>1</td></tr><tr><td>2 Marks Count</td><td>3</td><td>3</td><td>3</td><td>1</td><td>3</td><td>3</td><td>3</td><td>4</td><td>4</td><td>3</td><td>1</td></tr><tr><td>Total Marks</td><td>8</td><td>9</td><td>8</td><td>6</td><td>9</td><td>9</td><td>8</td><td>10</td><td>9</td><td>7</td><td>6</td></tr></table>

The Computer Networks chapter in GATE Computer Science is a fundamental and high-scoring area, essential for understanding how modern computing systems communicate and interact. It covers everything from the physical transmission of data to high-level application protocols, network architecture, and security principles. Mastery of this subject is crucial not only for the GATE exam but also for a career in software development, system administration, and network engineering. Typically, Computer Networks carries a weightage of 8-12 marks in the GATE CS exam, with questions ranging from conceptual understanding of protocols and layers to numerical problems involving network performance, addressing, and error control. Question patterns often include multiple-choice questions (MCQs), multiple-select questions (MSQs), and numerical answer type (NAT) questions, testing both theoretical knowledge and problem-solving skills.

# Topic-wise Key Concepts

# Application Layer Protocols

These protocols are at the highest layer of the TCP/IP model, providing services directly to user applications. They define how applications on different hosts communicate and exchange data.

# Key Concepts:

- HTTP (Hypertext Transfer Protocol): Used for web browsing, client-server model, stateless. Default port 80.  
- FTP (File Transfer Protocol): Used for file transfer, uses two connections (control and data). Default ports 20 (data) and 21 (control).  
- DNS (Domain Name System): Translates domain names to IP addresses. UDP port 53 for queries, TCP port 53 for zone transfers.  
- SMTP (Simple Mail Transfer Protocol): Used for sending emails. Default port 25.  
- POP3 (Post Office Protocol v3): Used for retrieving emails. Default port 110.  
- IMAP (Internet Message Access Protocol): More advanced email retrieval, allows managing mail on server. Default port 143.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing the functions and default port numbers of different protocols.  
- Technique: Create a table mapping protocol to function and port number for quick recall.

# ARP (Address Resolution Protocol)

ARP is a protocol used to map an IP address (Network Layer) to a physical MAC address (Data Link Layer) on a local network. It is essential for IP packets to be encapsulated into Ethernet frames for local delivery.

# Key Concepts:

- ARP Request: Broadcasts a query to all hosts on the local network asking for the MAC address corresponding to a specific IP.  
- ARP Reply: The host with the matching IP address sends a unicast reply containing its MAC address.  
- ARP Cache: Hosts maintain a cache of IP-to-MAC mappings to reduce ARP traffic.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Assuming ARP works across routers; it's a local network protocol.  
- Technique: Understand the ARP process step-by-step for tracing packet flows.

# Bit Stuffing

Bit stuffing is a technique used in the Data Link Layer to prevent the flag sequence from appearing in the data portion of a frame. It ensures that the receiver correctly identifies the start and end of a frame.

# Key Concepts:

- Flag Sequence: A unique bit pattern (e.g., 01111110) used to mark frame boundaries.  
- Stuffing Rule: Whenever five consecutive 1s appear in the data, an extra 0 bit is inserted (stuffed) by the sender.  
- Destuffing Rule: The receiver removes a 0 bit after five consecutive 1s.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly stuffing/destuffing bits, especially at the end of the data or near the flag sequence.  
- Technique: Practice with examples, carefully counting consecutive 1s.

# Bridges

Bridges are Data Link Layer devices that connect two or more LAN segments. They filter frames based on MAC addresses, forwarding only those frames destined for another segment, thus reducing collision domains and improving network performance.

# Key Concepts:

- MAC Address Filtering: Bridges maintain a forwarding table (MAC address table) to decide whether to forward or filter frames.  
- Learning: Bridges learn MAC addresses by inspecting the source MAC address of incoming frames.  
- Spanning Tree Protocol (STP): Used to prevent loops in bridged networks by disabling redundant paths.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing bridges with routers (Layer 3) or hubs (Layer 1). Bridges operate at Layer 2.  
- Technique: Trace frame paths in a bridged network, applying learning and forwarding rules.

# CRC Polynomial (Cyclic Redundancy Check)

CRC is a powerful error detection technique used in the Data Link Layer. It appends a checksum (FCS - Frame Check Sequence) to the data, calculated using polynomial division.

# Important Formulas and Results:

\- Let $M(x)$ be the data polynomial and $G(x)$ be the generator polynomial of degree $r$ . To find the CRC remainder $R(x)$ :

$$
\frac {x ^ {r} \cdot M (x)}{G (x)} = Q (x) + \frac {R (x)}{G (x)}
$$

where $R(x)$ is the remainder polynomial of degree less than $r$ .

\- The transmitted codeword $T(x)$ is:

$$
T (x) = x ^ {r} \cdot M (x) + R (x)
$$

This means the codeword is exactly divisible by $G(x)$ .

# Key Properties and Identities: