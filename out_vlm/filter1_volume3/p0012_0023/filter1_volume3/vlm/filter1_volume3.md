Machine instructions and Addressing modes. ALU, data-path and control unit. Instruction pipelining. Pipeline hazards, Memory hierarchy: cache, main memory and secondary storage; I/O interface (Interrupt and DMA mode)

Mark Distribution in Previous GATE

<table><tr><td>Year</td><td>2026 - 1</td><td>2026 - 2</td><td>2025 - 1</td><td>2025 - 2</td><td>2024 - 1</td><td>2024 - 2</td><td>2023</td><td>2022</td><td>2021 - 1</td><td>2021 - 2</td><td>Minimum</td></tr><tr><td>1 Mark Count</td><td>3</td><td>1</td><td>2</td><td>1</td><td>2</td><td>2</td><td>2</td><td>3</td><td>1</td><td>2</td><td>1</td></tr><tr><td>2 Marks Count</td><td>4</td><td>5</td><td>3</td><td>4</td><td>3</td><td>3</td><td>4</td><td>2</td><td>2</td><td>2</td><td>2</td></tr><tr><td>Total Marks</td><td>11</td><td>11</td><td>8</td><td>9</td><td>8</td><td>8</td><td>10</td><td>7</td><td>5</td><td>6</td><td>5</td></tr></table>

Welcome to the "Computer Organization & Architecture" chapter of your GATE Computer Science preparation. This crucial subject delves into the fundamental design and operational principles of a computer system, from the lowest-level hardware components to how instructions are executed and data is managed. Understanding COA is vital for any computer scientist as it provides the bedrock knowledge for designing efficient systems, writing optimized code, and comprehending the performance implications of software choices. In the GATE CS exam, COA typically carries a weightage of 8-12 marks, with questions ranging from conceptual understanding of architectural principles (like CISC vs. RISC, control unit types) to numerical problems involving cache memory, pipelining performance, virtual memory, and disk access times. Expect a mix of Multiple Choice Questions (MCQs), Multiple Select Questions (MSQs), and Numerical Answer Type (NAT) questions, often requiring precise calculations and a deep grasp of underlying mechanisms.

# Topic-wise Key Concepts

# Addressing Modes

Addressing modes define how the effective address of an operand is calculated. They specify where the operand is located, whether in a register, memory, or as part of the instruction itself, enabling flexible and efficient memory access.

# Important Formulas & Concepts

- Immediate: Operand is part of the instruction. $EA =$ Operand Value. No memory access for operand.  
- Direct: $EA =$ Address (address field in instruction). One memory access to fetch operand.  
- Indirect: $EA = M[\text{Address}]$ (address field points to memory location containing EA). Two memory accesses (one for EA, one for operand).  
- Register: Operand is in a specified register. $EA = R$ . No memory access.  
- Register Indirect: $EA = [R]$ (register contains EA). One memory access to fetch operand.  
- Relative (PC-relative): $EA = PC + \text{Offset}$ (offset from Program Counter). Used for branch instructions.  
- Indexed: $EA = \text{Base\_Address} + \text{Index\_Register}$ . Used for array access.  
- Base-Register: $EA = \text{Base\_Register} + \text{Offset}$ . Used for relocating programs.

# Key Properties & Identities

- Trade-offs exist between instruction length, execution speed, and flexibility.  
- Used to access data, implement control flow, and manage memory.

# Common Pitfalls

\- Confusing direct and indirect addressing, especially regarding the number of memory accesses.

# Standard Problem-Solving Techniques

\- Trace the instruction execution step-by-step to calculate the effective address for given register/memory contents.

# Average Memory Access Time (AMAT)

AMAT is the average time taken to access memory, considering the presence of a cache and its hit/miss rates. It quantifies the performance of the memory hierarchy.

# Important Formulas & Concepts

\- For a single-level cache:

$$
A M A T = T _ {h i t} + M R \times T _ {m i s s \_ p e n a l t y}
$$

where $T_{hit}$ is cache hit time, MR is miss rate, and $T_{miss\_penalty}$ is the time to fetch data from the next level of memory (main memory).

\- For a two-level cache (L1, L2):

$$
A M A T = T _ {L 1 \_ h i t} + M R _ {L 1} \times \left(T _ {L 2 \_ h i t} + M R _ {L 2} \times T _ {\text {main\_memory}}\right)
$$

where $T_{L1\_hit}$ is L1 hit time, $MR_{L1}$ is L1 miss rate, $T_{L2\_hit}$ is L2 hit time, $MR_{L2}$ is L2 miss rate (local miss rate for L2), and $T_{main\_memory}$ is main memory access time.

# Key Properties & Identities

- Lower AMAT indicates better memory system performance.  
- Affected by cache hit rate, miss penalty, and cache access times.

# Common Pitfalls

- Forgetting to add the hit time to the miss penalty when calculating total miss time.  
- Incorrectly applying local vs. global miss rates for multi-level caches.

# Standard Problem-Solving Techniques

\- Draw the memory hierarchy and clearly identify access times and miss rates for each level.

# Bit Vector

A bit vector (or bit array) is a data structure that efficiently stores a sequence of bits. Each bit typically represents a boolean flag or the presence/absence of an element in a set.

# Important Formulas & Concepts

- Storage: $N$ bits require $\lceil N / 8 \rceil$ bytes of storage.  
- Bitwise operations: AND, OR, XOR, NOT, SHIFT for efficient manipulation.

# Key Properties & Identities

- Space-efficient for large sets of boolean flags.  
- Fast bitwise operations for checking, setting, or clearing flags.

# Common Pitfalls

\- Misinterpreting bit positions or the effect of bitwise operations.

# Standard Problem-Solving Techniques

\- Use bit masks to isolate or modify specific bits.

# CISC RISC Architecture

CISC (Complex Instruction Set Computer) and RISC (Reduced Instruction Set Computer) are two contrasting philosophies for designing instruction sets. They represent different approaches to instruction complexity and hardware implementation.

# Important Formulas & Concepts

• CISC Characteristics:

- Many complex instructions, often performing multiple operations (e.g., memory access and arithmetic).  
- Variable instruction length.  
- Microprogrammed control unit.  
- Fewer general-purpose registers, more memory-to-memory operations.  
- Complex addressing modes.

# • RISC Characteristics:

\- Few, simple, fixed-length instructions, typically one operation per instruction.

\- Hardwired control unit.

\- Many general-purpose registers, load/store architecture (only LOAD/STORE access memory).

\- Simple addressing modes.

\- Optimized for pipelining.

# Key Properties & Identities

- RISC generally achieves higher CPI (Cycles Per Instruction) but lower clock cycle time due to simpler instructions, leading to better performance in many cases.  
- CISC aims for fewer instructions per program but higher CPI.

# Common Pitfalls

\- Assuming one architecture is universally superior; their suitability depends on the application and compiler technology.

# Standard Problem-Solving Techniques

\- Compare and contrast features to identify the type of architecture described in a scenario.

# Cache Memory

Cache memory is a small, fast memory component that stores copies of data from frequently used main memory locations. Its purpose is to reduce the average time to access data, exploiting the principle of locality.

# Important Formulas & Concepts

\- Address Breakdown: For a memory address of $M$ bits, a cache with $B$ bytes per block, and $C$ cache lines (or sets):

- Block Offset bits: $\log_2 B$  
- Number of Blocks in Main Memory: $2^{M} / B$  
- Number of Cache Lines: $C$

\- Direct Mapping:

- Index bits: $\log_2 C$  
- Tag bits: $M - (\log_2 C + \log_2 B)$  
。Cache\_Line\_Index = (Main\_Memory\_Block\_Number) (mod C)

\- Set-Associative Mapping (S-way):

- Number of Sets: $C / S$  
- Index bits: $\log_2(C / S)$  
- Tag bits: $M - (\log_2(C / S) + \log_2 B)$  
。Cache\_Set\_Index = (Main\_Memory\_Block\_Number) (mod (C/S))

• Fully Associative Mapping:

- No Index bits.  
- Tag bits: $M - \log_2 B$  
- Any block can go into any cache line.

\- Hit Rate (HR): $\frac{\text{Number of Cache Hits}}{\text{Total Memory Accesses}}$

\- Miss Rate (MR): 1 - HR

# Key Properties & Identities

- Exploits temporal and spatial locality of reference.  
- Mapping techniques (Direct, Set-Associative, Fully Associative) determine where a block can be placed.  
- Write policies (Write-Through, Write-Back) determine when data is written to main memory.

\- Replacement policies (LRU, FIFO, LFU, Random) determine which block to evict on a miss.

# Common Pitfalls

- Incorrectly calculating the number of bits for Tag, Index, and Offset.  
- Confusing the total cache size with the number of cache lines.

# Standard Problem-Solving Techniques

\- Draw the cache structure and trace memory accesses to determine hits/misses and cache contents.

# Conflict Misses

Conflict misses occur in direct-mapped or set-associative caches when multiple memory blocks map to the same cache line or set, and these blocks are actively used, causing them to evict each other even if other cache lines are empty.

# Important Formulas & Concepts

- These are a type of "capacity miss" specifically due to the mapping function.  
- Increasing associativity reduces conflict misses.

# Key Properties & Identities

- Occur when the cache is not full but the required block is evicted due to mapping constraints.  
- Distinguished from compulsory (first-time access) and capacity (cache too small) misses.

# Common Pitfalls

\- Mistaking a conflict miss for a capacity miss or a compulsory miss.

# Standard Problem-Solving Techniques

\- Analyze the memory access pattern and the cache mapping scheme to identify if multiple active blocks map to the same location.

# Control Unit

The control unit is the part of the CPU that directs the operation of the processor. It interprets instructions and generates control signals to coordinate the activities of other components, such as the ALU, registers, and memory.

# Important Formulas & Concepts

- Hardwired Control: Implemented using combinational logic gates.  
- Faster execution.  
- Complex to design and modify for large instruction sets.  
- Used in RISC processors.

\- Microprogrammed Control: Implemented using a sequence of microinstructions stored in a control memory.

- More flexible and easier to design/modify for complex instruction sets.  
- Slower execution due to memory access for microinstructions.  
- Used in CISC processors.

# Key Properties & Identities

• Determines the sequence of micro-operations for each machine instruction.  
- Generates timing and control signals for the entire system.

# Common Pitfalls

\- Not understanding the trade-offs between hardwired and microprogrammed control in terms of speed, flexibility, and design complexity.

# Standard Problem-Solving Techniques

\- Relate the control unit type to the characteristics of CISC/RISC architectures.

# DMA (Direct Memory Access)

DMA is a hardware feature that allows I/O devices to transfer data directly to and from main memory without involving the CPU. This significantly reduces CPU overhead for data transfers, improving system performance.

# Important Formulas & Concepts

• DMA controller manages the data transfer.  
- Cycle Stealing: DMA controller takes control of the bus for one or more memory cycles to transfer data.  
- Burst Mode: DMA controller takes control of the bus and transfers an entire block of data before releasing the bus.

# Key Properties & Identities

- Frees the CPU to perform other tasks during I/O operations.  
- Requires a DMA controller chip.

# Common Pitfalls

\- Misunderstanding that DMA completely bypasses the CPU; the CPU initiates and configures the DMA transfer.

# Standard Problem-Solving Techniques

\- Analyze scenarios to determine when DMA is most beneficial compared to programmed I/O or interrupt-driven I/O.

# DRAM (Dynamic Random Access Memory)

DRAM is the most common type of main memory used in computers. It stores each bit of data in a separate capacitor within an integrated circuit, requiring periodic refreshing to maintain the charge and thus the data.

# Important Formulas & Concepts

• Data stored as charge in capacitors.  
- Requires refresh cycles to prevent data loss.

# Key Properties & Identities

- Volatile (data is lost when power is removed).  
- Higher density and lower cost per bit compared to SRAM.  
- Slower access times than SRAM due to refresh cycles and capacitor charging/discharging.

# Common Pitfalls

\- Confusing DRAM characteristics with SRAM (Static RAM), which uses latches and does not require refreshing.

# Standard Problem-Solving Techniques

\- Compare and contrast DRAM with SRAM based on cost, speed, density, and power consumption.

# Data Dependency

A data dependency exists between two instructions when the second instruction requires data produced by the first instruction, or when they both access the same memory location, potentially leading to incorrect results if executed out of order.

# Important Formulas & Concepts

- RAW (Read After Write) / True Dependency: Instruction $J$ tries to read a source before instruction $I$ writes to it. $I \rightarrow J$ . This is the most common and critical dependency.  
- WAR (Write After Read) / Anti-dependency: Instruction $J$ tries to write to a destination before instruction $I$ reads from it. $I \leftarrow J$ . Can be resolved by renaming.  
- WAW (Write After Write) / Output Dependency: Instruction $J$ tries to write to a destination before instruction $I$ writes to it. $I \Rightarrow J$ . Can be resolved by renaming.

# Key Properties & Identities

- RAW dependencies are true data dependencies and must be preserved.  
- WAR and WAW are name dependencies and can be eliminated by register renaming.

# Common Pitfalls

\- Incorrectly identifying the type of dependency or missing a dependency.

# Standard Problem-Solving Techniques

\- Analyze the read/write sets of instructions to identify dependencies.

# Data Hazards

Data hazards occur in pipelined processors when an instruction attempts to access data before a preceding instruction has made that data available. These hazards can lead to incorrect program execution if not handled.

# Important Formulas & Concepts

- Caused by RAW, WAR, and WAW dependencies.  
- Solutions:

- Stalling (Bubbles/NOPs): Insert NOP instructions to delay the dependent instruction.  
- Forwarding (Bypassing): Route the result of an instruction directly from an internal pipeline register to the input of a subsequent instruction's functional unit, bypassing the register file.  
- Compiler Scheduling: Reorder instructions at compile time to avoid hazards.

# Key Properties & Identities

- Increase the CPI (Cycles Per Instruction) of a pipeline, reducing ideal speedup.  
• Forwarding is the most common hardware solution to reduce stalls due to RAW hazards.

# Common Pitfalls

• Calculating the number of stalls incorrectly, especially when forwarding is present.  
- Not identifying all data dependencies in a given instruction sequence.

# Standard Problem-Solving Techniques

\- Draw pipeline diagrams to visualize instruction flow and identify where stalls or forwarding are needed.

# Data Path

The data path of a CPU consists of the functional units (like the ALU, registers, and multiplexers) and the buses that connect them, through which data flows during instruction execution. It performs the actual data processing operations.

# Important Formulas & Concepts

\- Key components: Program Counter (PC), Instruction Register (IR), Memory Address Register (MAR), Memory Data Register (MDR), General Purpose Registers (GPRs), Arithmetic Logic Unit (ALU).

# Key Properties & Identities

- The data path is controlled by signals generated by the control unit.  
- Its design impacts the clock cycle time and the number of cycles per instruction.

# Common Pitfalls

\- Not understanding how data moves between components for different instruction types.

# Standard Problem-Solving Techniques

\- Trace the flow of data for a specific instruction (e.g., LOAD, ADD) through the datapath components.

# Direct Mapping

Direct mapping is a cache organization technique where each block from main memory can only be placed into one specific line in the cache. This mapping is determined by a simple modular arithmetic function of the memory block address.

# Important Formulas & Concepts

\- Cache Line Index:
  Cache\_Line\_Index = (Main\_Memory\_Block\_Number) (mod Number\_of\_Cache\_Lines)

\- Address Breakdown: A memory address is divided into three fields: Tag, Index, and Block Offset.

- Block Offset bits: $\log_2$ (Block Size in bytes)  
- Index bits: $\log_2(\text{Number of Cache Lines})$  
- Tag bits: Total Address Bits – Index Bits – Block Offset Bits

# Key Properties & Identities

- Simplest to implement and fastest for cache lookup.  
- Suffers from high conflict misses if frequently accessed blocks map to the same cache line.

# Common Pitfalls

\- Incorrectly calculating the number of bits for the Tag, Index, or Block Offset fields.

# Standard Problem-Solving Techniques

\- Given memory and cache parameters, determine the address breakdown and trace memory accesses to identify hits/misses.

# Dirty Bit

A dirty bit (or modified bit) is a flag associated with a cache line or a virtual memory page table entry. It indicates whether the corresponding data block in the cache/page has been modified since it was loaded from the next lower level of memory (main memory/disk).

# Important Formulas & Concepts

- Set to '1' when data in the cache line or page is written to.  
- Set to '0' when the data is clean (matches the lower level memory).

# Key Properties & Identities

- Crucial for write-back cache policies: if the dirty bit is set, the block must be written back to main memory upon eviction.  
- Used in virtual memory page replacement algorithms to avoid unnecessary writes to disk.

# Common Pitfalls

\- Misunderstanding its role in write-through caches (where it's not typically needed) versus write-back caches.

# Standard Problem-Solving Techniques

\- Analyze cache write operations and page replacement scenarios to determine when the dirty bit is set or checked.

# Disk

A disk (hard disk drive) is a non-volatile secondary storage device that stores data magnetically on rotating platters. It is characterized by its large capacity and persistence, but significantly slower access times compared to RAM.

# Important Formulas & Concepts

\- Disk Access Time:

$$
\text {Access\_Time} = \text {Seek\_Time} + \text {Rotational\_Latency} + \text {Transfer\_Time}
$$

- Seek Time: Time taken for the read/write head to move to the correct track. (Often given as average or calculated based on number of tracks).  
- Rotational Latency: Time taken for the desired sector to rotate under the read/write head.

$$
\text {Average\_Rotational\_Latency} = \frac {1}{2} \times \frac {6 0 \text {seconds}}{\text {RPM}}
$$

(where RPM is revolutions per minute).

\- Transfer Time: Time taken to transfer the actual data once the head is positioned.

$$
\text {Transfer\_Time} = \frac {\text {Number of Sectors to Transfer}}{\text {Sectors per Track}} \times \frac {6 0 \text {seconds}}{\text {RPM}}
$$

$$
\text {or Transfer\_Time} = \frac {\text {Amount of Data}}{\text {Transfer Rate}}.
$$

# Key Properties & Identities

• Non-volatile storage.  
- Mechanical components make it orders of magnitude slower than electronic memory.

# Common Pitfalls

- Incorrectly calculating average rotational latency (using $1/2$ of a full rotation).  
- Mixing units (e.g., milliseconds and seconds).

# Standard Problem-Solving Techniques

\- Break down the access time calculation into its three components and calculate each separately.

# Hazards

Hazards are situations in pipelined processors that prevent the next instruction in the instruction stream from executing in its designated clock cycle. They reduce the ideal speedup of a pipeline.

# Important Formulas & Concepts

- Structural Hazards: Occur when two instructions require the same hardware resource at the same time (e.g., single memory port for both instruction fetch and data access).  
- Data Hazards: Occur when an instruction depends on the result of a previous instruction that has not yet completed (RAW, WAR, WAW).  
- Control Hazards (Branch Hazards): Occur when the pipeline makes a wrong guess about the next instruction to fetch (e.g., after a conditional branch).

# Key Properties & Identities

\- All hazards increase the effective CPI (Cycles Per Instruction) of the pipeline.

\- Solutions include stalling, forwarding, and branch prediction.

# Common Pitfalls

\- Confusing the different types of hazards or misidentifying the cause of a stall.

# Standard Problem-Solving Techniques

\- Analyze the instruction sequence and pipeline stage usage to identify potential conflicts.

# IO Handling

I/O handling refers to the mechanisms by which a CPU communicates and exchanges data with peripheral input/output devices. Efficient I/O handling is crucial for system performance.

# Important Formulas & Concepts

\- Programmed I/O (Polling): CPU continuously checks the status of an I/O device.

\- High CPU overhead, simple to implement.

\- Interrupt-Driven I/O: I/O device signals the CPU via an interrupt when it needs attention.

\- Lower CPU overhead than polling, CPU can do other work.

\- Requires interrupt service routines (ISRs).

\- Direct Memory Access (DMA): I/O device transfers data directly to/from memory without CPU intervention.

\- Lowest CPU overhead for large data transfers.

\- Requires a DMA controller.

# Key Properties & Identities

\- Each method has trade-offs in terms of CPU utilization, response time, and complexity.

\- Interrupts allow for asynchronous event handling.

# Common Pitfalls

\- Not understanding the CPU's involvement (or lack thereof) in data transfer for each method.

# Standard Problem-Solving Techniques

\- Evaluate scenarios to determine the most suitable I/O handling method based on data volume and CPU availability.

# Instruction Execution

Instruction execution is the process by which a CPU carries out a single machine instruction. In a pipelined processor, this process is broken down into several sequential stages, allowing multiple instructions to be processed concurrently.

# Important Formulas & Concepts

• Typical 5-stage pipeline:

1. IF (Instruction Fetch): Fetch instruction from memory.  
2. ID (Instruction Decode): Decode instruction, read registers.  
3. EX (Execute): Perform ALU operation.  
4. MEM (Memory Access): Access data memory (load/store).  
5. WB (Write Back): Write result back to register file.

# Key Properties & Identities

• Each stage ideally takes one clock cycle in a pipelined processor.  
- The slowest stage determines the clock cycle time of the pipeline.

# Common Pitfalls

\- Misunderstanding the specific function of each pipeline stage.

# Standard Problem-Solving Techniques

\- Trace an instruction through each stage of the pipeline to understand its execution flow.

# Instruction Format

The instruction format defines the layout of bits within a machine instruction. It specifies how the opcode, operands, and addressing mode information are encoded, directly impacting the instruction set's flexibility and the CPU's decoding complexity.

# Important Formulas & Concepts

- An instruction typically consists of an opcode (operation code) and one or more operand fields.  
- Operand fields can specify registers, memory addresses, or immediate values.  
- Fixed-length instruction format: All instructions have the same length. Simplifies fetching and decoding, good for pipelining (RISC).  
- Variable-length instruction format: Instructions can have different lengths. Allows for more complex instructions and addressing modes, but complicates fetching and decoding (CISC).

# Key Properties & Identities

- The number of bits for the opcode determines the maximum number of unique operations.  
- The number of bits for operand fields determines the number of registers or the addressable memory range.

# Common Pitfalls

\- Incorrectly calculating the maximum number of opcodes or addressable memory given a fixed instruction length.

# Standard Problem-Solving Techniques

\- Given instruction length and operand requirements, calculate the remaining bits for the opcode or vice-versa.

# Instruction Set Architecture (ISA)

The ISA is the abstract model of a computer that is visible to a programmer or compiler writer. It defines the set of instructions, registers, memory organization, data types, and the I/O model that the hardware supports.

# Important Formulas & Concepts

- Includes the instruction set, register set, memory addressing modes, and interrupt handling mechanisms.  
- Forms the interface between software and hardware.

# Key Properties & Identities

- ISA defines what the processor does, while microarchitecture defines how it does it.  
- CISC and RISC are two major ISA design philosophies.

# Common Pitfalls

\- Confusing ISA (the specification) with microarchitecture (the implementation).

# Standard Problem-Solving Techniques

\- Understand that ISA is the contract that allows software to run on different hardware implementations of the same ISA.

# Interrupts

An interrupt is a signal to the CPU indicating an event that requires immediate attention, causing the CPU to temporarily suspend its current task and execute a special routine (Interrupt Service Routine or ISR) to handle the event.

# Important Formulas & Concepts

- Hardware Interrupts: Generated by I/O devices (e.g., keyboard press, disk completion). Asynchronous.  
- Software Interrupts (Exceptions/Traps): Generated by program execution (e.g., division by zero, page fault, system call). Synchronous.  
- Interrupt Vector Table: A table of addresses for ISRs, indexed by interrupt number.

# Key Properties & Identities

- Enable efficient I/O handling and error management without constant CPU polling.  
- Involve saving CPU state, executing ISR, and restoring CPU state.

# Common Pitfalls

\- Misunderstanding the sequence of events during interrupt handling (saving context, jumping to ISR, restoring context).

# Standard Problem-Solving Techniques

\- Trace the flow of control when an interrupt occurs, considering context saving and ISR execution.

# Machine Instruction

A machine instruction is a command or operation that a CPU can directly understand and execute. It is represented in binary code and forms the lowest-level programming language, specific to a particular processor's Instruction Set Architecture.

# Important Formulas & Concepts

- Composed of an opcode and zero or more operands.  
- Each instruction performs a basic operation (e.g., add, load, store, branch).

# Key Properties & Identities

- Directly executable by the hardware.  
- The fundamental unit of computation for the CPU.

# Common Pitfalls

\- Confusing machine instructions (binary) with assembly language instructions (mnemonic representation).

# Standard Problem-Solving Techniques

\- Understand how an assembly instruction translates into its binary machine code equivalent based on the instruction format.

# Memory Interfacing

Memory interfacing is the process of connecting memory devices (RAM, ROM) to the CPU. It involves designing the necessary address decoding logic, connecting data and address buses, and generating control signals to ensure proper communication and data transfer.

# Important Formulas & Concepts

- Address Decoding: Logic gates (decoders, AND gates) used to select the correct memory chip based on the CPU's address lines.  
- Chip Select (CS): A control signal that enables a specific memory chip.

\- Memory Map: The allocation of address ranges to different memory devices.

# Key Properties & Identities

- Ensures that each memory location has a unique address and that the correct device responds to a CPU request.  
- Bus width (data and address) must match between CPU and memory.

# Common Pitfalls

\- Incorrectly designing address decoding logic, leading to address conflicts or unused address space.

# Standard Problem-Solving Techniques

\- Given CPU address lines and memory chip sizes, determine the address ranges and design the minimal decoding logic.

# Microprogramming

Microprogramming is a technique for implementing the control unit of a CPU by storing a sequence of microinstructions in a special control memory. Each machine instruction is executed by a microprogram, which is a sequence of microinstructions.

# Important Formulas & Concepts

- Microinstruction: A low-level instruction that controls the individual functional units of the CPU (e.g., enable ALU, load register).  
- Control Store (CS): Memory where microprograms are stored.

# Key Properties & Identities

\- Offers flexibility: easier to design complex instruction sets and modify existing ones.

\- Slower than hardwired control due to the overhead of fetching and decoding microinstructions.

• Commonly used in CISC processors.

# Common Pitfalls

\- Confusing microinstructions (internal CPU control) with machine instructions (user-level instructions).

# Standard Problem-Solving Techniques

\- Understand how a machine instruction is broken down into a sequence of micro-operations controlled by microinstructions.

# Pipelining

Pipelining is a technique that allows multiple instructions to be in different stages of execution simultaneously, improving the throughput of a processor. It does not reduce the execution time of a single instruction but increases the rate at which instructions complete.

# Important Formulas & Concepts

- Number of stages: $K$  
• Number of instructions: N  
- Clock cycle time: $T_{cycle}$ (determined by the slowest stage).  
- Execution time for N instructions (non-pipelined): $T_{non-pipeline} = N \times K \times T_{cycle}$  
- Execution time for N instructions (ideal pipelined): $T_{pipeline} = (K + N - 1) \times T_{cycle}$  
- Ideal Speedup (S) for large N: $S = \frac{N \times K \times T_{cycle}}{(K + N - 1) \times T_{cycle}} \approx K$  
- Throughput (ideal): $\frac{1}{T_{cycle}}$ instructions per cycle.  
• CPI (Cycles Per Instruction):