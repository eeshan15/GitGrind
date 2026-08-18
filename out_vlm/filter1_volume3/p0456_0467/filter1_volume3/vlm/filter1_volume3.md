# 5.31.6 Threads: GATE CSE 2017 | Set 2 | Question: 07

Which of the following is/are shared by all the threads in a process?


I. Program counter  
II. Stack  
III. Address space  
IV. Registers

A. (I) and (II) only

B. (III) only

C. (IV) only

D. (III) and (IV) only

gatecse-2017-set2 operating-system threads

# Answer key

# 5.31.7 Threads: GATE CSE 2021 | Set 2 | Question: 42

Consider the following multi-threaded code segment (in a mix of C and pseudo-code), invoked by two processes $P_{1}$ and $P_{2}$ , and each of the processes spawns two threads $T_{1}$ and $T_{2}$ :


```txt
int x = 0; // global
Lock L1; // global
main () {
    create a thread to execute foo(); // Thread T1
    create a thread to execute foo(); // Thread T2
    wait for the two threads to finish execution;
    print(x);}
foo() {
    int y = 0;
    Acquire L1;
    x = x + 1;
    y = y + 1;
    Release L1;
    print (y);}
```

Which of the following statement(s) is/are correct?

A. Both $P_{1}$ and $P_{2}$ will print the value of x as 2.  
B. At least of $P_{1}$ and $P_{2}$ will print the value of x as 4.  
C. At least one of the threads will print the value of y as 2.  
D. Both $T_{1}$ and $T_{2}$ , in both the processes, will print the value of y as 1.

gatecse-2021-set2 multiple-selects operating-system threads two-marks

# Answer key

# 5.31.8 Threads: GATE CSE 2024 | Set 1 | Question: 14

Which of the following statements about threads is/are TRUE?


A. Threads can only be implemented in kernel space  
B. Each thread has its own file descriptor table for open files  
C. All the threads belonging to a process share a common stack  
D. Threads belonging to a process are by default not protected from each other

gatecse-2024-set1 multiple-selects operating-system threads one-mark

# Answer key

# 5.31.9 Threads: GATE CSE 2024 | Set 1 | Question: 30

Consider the following two threads T1 and T2 that update two shared variables a and b. Assume that initially a = b = 1. Though context switching between threads can happen at any time, each statement of T1 or T2 is executed atomically without interruption.


T1

T2

$$
\mathrm{a} = \mathrm{a} + 1;
$$

$$
\mathrm{b} = 2 * \mathrm{b};
$$

$$
\mathrm{b} = \mathrm{b} + 1;
$$

$$
\mathrm{a} = 2 * a;
$$

Which one of the following options lists all the possible combinations of values of a and b after both T1 and T2 finish execution?

A. $(\mathrm{a} = 4, \mathrm{b} = 4)$ ; $(\mathrm{a} = 3, \mathrm{b} = 3)$ ; $(\mathrm{a} = 4, \mathrm{b} = 3)$  
B. $(\mathrm{a} = 3, \mathrm{b} = 4)$ ; $(\mathrm{a} = 4, \mathrm{b} = 3)$ ; $(\mathrm{a} = 3, \mathrm{b} = 3)$  
C. $(\mathrm{a} = 4, \mathrm{b} = 4)$ ; $(\mathrm{a} = 4, \mathrm{b} = 3)$ ; $(\mathrm{a} = 3, \mathrm{b} = 4)$  
D. $(\mathrm{a} = 2, \mathrm{b} = 2)$ ; $(\mathrm{a} = 2, \mathrm{b} = 3)$ ; $(\mathrm{a} = 3, \mathrm{b} = 4)$

gatecse-2024-set1 operating-system threads two-marks

# Answer key

# 5.31.10 Threads: GATE IT 2004 | Question: 14

Which one of the following is NOT shared by the threads of the same process?

A. Stack  
C. File Descriptor Table  
gateit-2004 operating-system easy threads

# Answer key


# 5.32

# Translation Lookaside Buffer (2)

# 5.32.1 Translation Lookaside Buffer: GATE CSE 2022 | Question: 28

Which one of the following statements is FALSE?


A. The TLB performs an associative search in parallel on all its valid entries using page number of incoming virtual address.  
B. If the virtual address of a word given by CPU has a TLB hit, but the subsequent search for the word results in a cache miss, then the word will always be present in the main memory.  
C. The memory access time using a given inverted page table is always same for all incoming virtual addresses.  
D. In a system that uses hashed page tables, if two distinct virtual addresses V1 and V2 map to the same value while hashing, then the memory access time of these addresses will not be the same.

gatecse-2022 operating-system memory-management translation-lookaside-buffer two-marks

# Answer key

# 5.32.2 Translation Lookaside Buffer: GATE CSE 2026 | Set 2 | Question: 44

A system has a Translation Lookaside Buffer (TLB) that has a reach of 1 MB. TLB reach is defined as the total amount of physical memory that can be accessed through the TLB entries. The paging system uses pages of size 4 KB. The virtual address space is 64 GB and physical address space is 1 GB. If each TLB stores a 4-bit process id, page number, frame number, and a 2-bit control field, then the size of the TLB (in by \_\_\_\_. (answer in integer)


Note: $1\mathrm{K} = 2^{10}, 1\mathrm{M} = 2^{20}, 1\mathrm{G} = 2^{30}$

gatecse-2026-set2 operating-system translation-lookaside-buffer paging numerical-answers two-marks

# Answer key

# 5.33

# Virtual Memory (43)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (15Q)

Test 4 (6Q)

# 5.33.1 Virtual Memory: GATE CSE 1989 | Question: 2-iv

Match the pairs in the following:


<table><tr><td>(A)</td><td>Virtual memory</td><td>(p)</td><td>Temporal Locality</td></tr><tr><td>(B)</td><td>Shared memory</td><td>(q)</td><td>Spatial Locality</td></tr><tr><td>(C)</td><td>Look-ahead buffer</td><td>(r)</td><td>Address Translation</td></tr><tr><td>(D)</td><td>Look-aside buffer</td><td>(s)</td><td>Mutual Exclusion</td></tr></table>

match-the-following gate1989 operating-system virtual-memory

# Answer key

# 5.33.2 Virtual Memory: GATE CSE 1990 | Question: 1-v

Under paged memory management scheme, simple lock and key memory protection arrangement may still be required if the \_\_\_\_ processors do not have address mapping hardware.


gate1990 operating-system virtual-memory fill-in-the-blanks

# Answer key

# 5.33.3 Virtual Memory: GATE CSE 1990 | Question: 7-b

In a two-level virtual memory, the memory access time for main memory, $t_{M} = 10^{-8}$ sec, and the memory access time for the secondary memory, $t_{D} = 10^{-3}$ sec. What must be the hit ratio, H such that the access efficiency is within 80 percent of its maximum value?


gate1990 descriptive operating-system virtual-memory

# Answer key

# 5.33.4 Virtual Memory: GATE CSE 1991 | Question: 03-xi

Indicate all the false statements from the statements given below:


A. The amount of virtual memory available is limited by the availability of the secondary memory  
B. Any implementation of a critical section requires the use of an indivisible machine- instruction, such as test-and-set.  
C. The use of monitors ensure that no dead-locks will be caused.  
D. The LRU page-replacement policy may cause thrashing for some type of programs.  
E. The best fit techniques for memory allocation ensures that memory will never be fragmented.

gate1991 operating-system virtual-memory normal multiple-selects

# Answer key

# 5.33.5 Virtual Memory: GATE CSE 1994 | Question: 1.21

Which one of the following statements is true?


A. Macro definitions cannot appear within other macro definitions in assembly language programs  
B. Overlaying is used to run a program which is longer than the address space of a computer  
C. Virtual memory can be used to accommodate a program which is longer than the address space of a computer  
D. It is not possible to write interrupt service routines in a high level language

gate1994 operating-system normal virtual-memory

# Answer key

# 5.33.6 Virtual Memory: GATE CSE 1995 | Question: 1.7

In a paged segmented scheme of memory management, the segment table itself must have a page table because


A. The segment table is often too large to fit in one page  
B. Each segment is spread over a number of pages

C. Segment tables point to page tables and not to the physical locations of the segment  
D. The processor's description base register points to a page table

gate1995 operating-system virtual-memory normal

# Answer key

# 5.33.7 Virtual Memory: GATE CSE 1995 | Question: 2.16

In a virtual memory system the address space specified by the address lines of the CPU must be \_\_\_\_ than the physical memory size and \_\_\_\_ than the secondary storage size.


A. smaller, smaller  
C. larger, smaller

B. smaller, larger  
D. larger, larger

gate1995 operating-system virtual-memory normal

# Answer key

# 5.33.8 Virtual Memory: GATE CSE 1996 | Question: 7

A demand paged virtual memory system uses 16 bit virtual address, page size of 256 bytes, and has 1 Kbyte of main memory. LRU page replacement is implemented using the list, whose current status (page number is decimal) is


![](images/7bd559bca39066486b0d3925bdcb691f2118c13a02e2bf3e200437f006c5a833.jpg)

For each hexadecimal address in the address sequence given below, 00FF, 010D, 10FF, 11B0

indicate

i. the new status of the list  
ii. page faults, if any, and  
iii. page replacements, if any.

gate1996 operating-system virtual-memory normal descriptive

# Answer key

# 5.33.9 Virtual Memory: GATE CSE 1998 | Question: 2.18, UGCNET-June2012-III: 48

If an instruction takes i microseconds and a page fault takes an additional j microseconds, the effective instruction time if on the average a page fault occurs every k instruction is:


A. $i + \frac{j}{k}$

B. $i + (j \times k)$

C. $\frac{i+j}{k}$

D. $(i + j) \times k$

gate1998 operating-system virtual-memory easy ugcnetcse-june2012-paper3

# Answer key

# 5.33.10 Virtual Memory: GATE CSE 1999 | Question: 19

A certain computer system has the segmented paging architecture for virtual memory. The memory is byte addressable. Both virtual and physical address spaces contain $2^{16}$ bytes each. The virtual address space is divided into 8 non-overlapping equal size segments. The memory management unit (MMU) has a hard segment table, each entry of which contains the physical address of the page table for the segment. Page are stored in the main memory and consists of 2 byte page table entries.


a. What is the minimum page size in bytes so that the page table for a segment requires at most one page to store it? Assume that the page size can only be a power of 2.  
b. Now suppose that the pages size is 512 bytes. It is proposed to provide a TLB (Transaction look-aside buffer) for speeding up address translation. The proposed TLB will be capable of storing page table entries for 16

recently referenced virtual pages, in a fast cache that will use the direct mapping scheme. What is the number of tag bits that will need to be associated with each cache entry?

c. Assume that each page table entry contains (besides other information) 1 valid bit, 3 bits for page protection and 1 dirty bit. How many bits are available in page table entry for storing the aging information for the page? Assume that the page size is 512 bytes.

gate1999 operating-system virtual-memory normal descriptive

# Answer key

# 5.33.11 Virtual Memory: GATE CSE 1999 | Question: 2.10

A multi-user, multi-processing operating system cannot be implemented on hardware that does not support


A. Address translation  
B. DMA for disk transfer  
C. At least two modes of CPU execution (privileged and non-privileged)  
D. Demand paging

gate1999 operating-system normal virtual-memory multiple-selects

# Answer key

# 5.33.12 Virtual Memory: GATE CSE 1999 | Question: 2.11

Which of the following is/are advantage(s) of virtual memory?


A. Faster access to memory on an average.  
B. Processes can be given protected address spaces.  
C. Linker can assign addresses independent of where the program will be loaded in physical memory.  
D. Program larger than the physical memory size can be run.

gate1999 operating-system virtual-memory easy multiple-selects

# Answer key

# 5.33.13 Virtual Memory: GATE CSE 2000 | Question: 2.22

Suppose the time to service a page fault is on the average 10 milliseconds, while a memory access takes 1 microsecond. Then a 99.99% hit ratio results in average memory access time of


A. 1.9999 milliseconds

C. 9.999 microseconds

gatecse-2000 operating-system easy virtual-memory

B. 1 millisecond

D. 1.9999 microseconds

# Answer key

# 5.33.14 Virtual Memory: GATE CSE 2001 | Question: 1.20

Where does the swap space reside?


A. RAM

B. Disk

C. ROM

D. On-chip cache

gatecse-2001 operating-system easy virtual-memory

# Answer key

# 5.33.15 Virtual Memory: GATE CSE 2001 | Question: 1.8

Which of the following statements is false?


A. Virtual memory implements the translation of a program's address space into physical memory address space  
B. Virtual memory allows each program to exceed the size of the primary memory  
C. Virtual memory increases the degree of multiprogramming  
D. Virtual memory reduces the context switching overhead


# 5.33.16 Virtual Memory: GATE CSE 2001 | Question: 2.21


Consider a machine with 64 MB physical memory and a 32-bit virtual address space. If the page size is 4 KB, what is the approximate size of the page table?

A. 16 MB

B. 8 MB

C. 2 MB

D. 24 MB

gatecse-2001 operating-system virtual-memory normal

# Answer key

# 5.33.17 Virtual Memory: GATE CSE 2002 | Question: 19


A computer uses 32 — bit virtual address, and 32 — bit physical address. The physical memory is byte addressable, and the page size is 4 Kbytes. It is decided to use two level page tables to translate from virtual address to physical address. Equal number of bits should be used for indexing first level and second level page table, and the size of each table entry is 4 bytes.

A. Give a diagram showing how a virtual address would be translated to a physical address.  
B. What is the number of page table entries that can be contained in each page?  
C. How many bits are available for storing protection and other information in each page table entry?

gatecse-2002 operating-system virtual-memory normal descriptive

# Answer key

# 5.33.18 Virtual Memory: GATE CSE 2003 | Question: 26


In a system with 32 bit virtual addresses and 1 KB page size, use of one-level page tables for virtual to physical address translation is not practical because of

A. the large amount of internal fragmentation  
B. the large amount of external fragmentation  
C. the large memory overhead in maintaining page tables  
D. the large computation overhead in the translation process

gatecse-2003 operating-system virtual-memory normal

# Answer key

# 5.33.19 Virtual Memory: GATE CSE 2003 | Question: 78


A processor uses 2 — level page tables for virtual to physical address translation. Page tables for both levels are stored in the main memory. Virtual and physical addresses are both 32 bits wide. The memory is byte addressable. For virtual to physical address translation, the 10 most significant bits of the virtual address are used as index into the first level page table while the next 10 bits are used as index into the second level page table. The 12 least significant bits of the virtual address are used as offset within the page. Assume that the page table entries in both levels of page tables are 4 bytes wide. Further, the processor has a translation look-aside buffer (TLB), with a hit rate of 96%. The TLB caches recently used virtual page numbers and the corresponding physical page numbers. The processor also has a physically addressed cache with a hit rate of 90%. Main memory access time is 10 ns, cache access time is 1 ns, and TLB access time is also 1 ns.

Assuming that no page faults occur, the average time taken to access a virtual address is approximately (to the nearest 0.5 ns)

A. 1.5 ns

B. 2 ns

C. 3 ns

D. 4 ns

gatecse-2003 operating-system normal virtual-memory

# Answer key

# 5.33.20 Virtual Memory: GATE CSE 2003 | Question: 79


A processor uses 2-level page tables for virtual to physical address translation. Page tables for both levels are stored in the main memory. Virtual and physical addresses are both 32 bits wide. The memory is byte

addressable. For virtual to physical address translation, the 10 most significant bits of the virtual address are used as index into the first level page table while the next 10 bits are used as index into the second level page table. The 12 least significant bits of the virtual address are used as offset within the page. Assume that the page table entries in both levels of page tables are 4 bytes wide. Further, the processor has a translation look-aside buffer (TLB), with a hit rate of 96%. The TLB caches recently used virtual page numbers and the corresponding physical page numbers. The processor also has a physically addressed cache with a hit rate of 90%. Main memory access time is 10 ns, cache access time is 1 ns, and TLB access time is also 1 ns.

Suppose a process has only the following pages in its virtual address space: two contiguous code pages starting at virtual address 0x00000000, two contiguous data pages starting at virtual address0x00400000, and a stack page starting at virtual address 0xFFFFF000. The amount of memory required for storing the page tables of this process is

A. 8 KB

B. 12 KB

C. 16 KB

D. 20 KB

gatecse-2003 operating-system normal virtual-memory

Answer key

# 5.33.21 Virtual Memory: GATE CSE 2006 | Question: 62, ISRO2016-50


A CPU generates 32-bit virtual addresses. The page size is 4 KB. The processor has a translation look-aside buffer (TLB) which can hold a total of 128 page table entries and is 4-way set associative. The minimum size of the TLB tag is:

A. 11 bits

B. 13 bits

C. 15 bits

D. 20 bits

gatecse-2006 operating-system virtual-memory normal isro2016

Answer key

# 5.33.22 Virtual Memory: GATE CSE 2006 | Question: 63, UGCNET-June2012-III: 45


A computer system supports 32-bit virtual addresses as well as 32-bit physical addresses. Since the virtual address space is of the same size as the physical address space, the operating system designers decide to get rid of the virtual memory entirely. Which one of the following is true?

A. Efficient implementation of multi-user support is no longer possible  
B. The processor cache organization can be made more efficient now  
C. Hardware support for memory management is no longer needed  
D. CPU scheduling can be made more efficient now

gatecse-2006 operating-system virtual-memory normal ugcnetcse-june2012-paper3

Answer key

# 5.33.23 Virtual Memory: GATE CSE 2008 | Question: 67


A processor uses 36 bit physical address and 32 bit virtual addresses, with a page frame size of 4 Kbytes. Each page table entry is of size 4 bytes. A three level page table is used for virtual to physical address translation, where the virtual address is used as follows:

- Bits 30 – 31 are used to index into the first level page table.  
- Bits 21 – 29 are used to index into the 2nd level page table.  
- Bits 12 – 20 are used to index into the 3rd level page table.  
- Bits 0 – 11 are used as offset within the page.

The number of bits required for addressing the next level page table(or page frame) in the page table entry of the first, second and third level page tables are respectively

A. 20,20,20

B. 24,24,24

C. 24,24,20

D. 25,25,24

# 5.33.24 Virtual Memory: GATE CSE 2009 | Question: 10

The essential content(s) in each entry of a page table is / are

A. Virtual page number

B. Page frame number

C. Both virtual page number and page frame number

D. Access right information

gatecse-2009 operating-system virtual-memory easy

# Answer key


# 5.33.25 Virtual Memory: GATE CSE 2009 | Question: 34

A multilevel page table is preferred in comparison to a single level page table for translating virtual address to physical address because


A. It reduces the memory access time to read or write a memory location.  
B. It helps to reduce the size of page table needed to implement the virtual address space of a process  
C. It is required by the translation lookaside buffer.  
D. It helps to reduce the number of page faults in page replacement algorithms.

gatecse-2009 operating-system virtual-memory easy

# Answer key

# 5.33.26 Virtual Memory: GATE CSE 2011 | Question: 20, UGCNET-June2013-II: 48

Let the page fault service time be 10 milliseconds(ms) in a computer with average memory access time being 20 nanoseconds (ns). If one page fault is generated every $10^{6}$ memory accesses, what is the effective access time for memory?


A. 21 ns

B. 30 ns

C. 23 ns

D. 35 ns

gatecse-2011 operating-system virtual-memory normal ugcnetcse-june2013-paper2

# Answer key

# 5.33.27 Virtual Memory: GATE CSE 2013 | Question: 52

A computer uses 46-bit virtual address, 32-bit physical address, and a three-level paged page table organization. The page table base register stores the base address of the first-level table (T1), which occupies exactly one page. Each entry of T1 stores the base address of a page of the second-level table (T2). Each entry of T2 stores the base address of a page of the third-level table (T3). Each entry of T3 stores a page table entry (PTE). The PTE is 32 bits in size. The processor used in the computer has a 1 MB 16 way set associative virtually indexed physically tagged cache. The cache block size is 64 bytes.

What is the size of a page in KB in this computer?

A. 2

B. 4

C. 8

D. 16

gatecse-2013 operating-system virtual-memory normal

# Answer key

# 5.33.28 Virtual Memory: GATE CSE 2013 | Question: 53

A computer uses 46-bit virtual address, 32-bit physical address, and a three-level paged page table organization. The page table base register stores the base address of the first-level table (T1), which occupies exactly one page. Each entry of T1 stores the base address of a page of the second-level table (T2). Each entry of T2 stores the base address of a page of the third-level table (T3). Each entry of T3 stores a page table entry (PTE). The PTE is 32 bits in size. The processor used in the computer has a 1 MB 16 way set associative virtually indexed physically tagged cache. The cache block size is 64 bytes.

What is the minimum number of page colours needed to guarantee that no two synonyms map to different sets in



the processor cache of this computer?

A. 2

B. 4

C. 8

D. 16

gatecse-2013 normal operating-system virtual-memory

Answer key

# 5.33.29 Virtual Memory: GATE CSE 2014 | Set 3 | Question: 33

Consider a paging hardware with a TLB. Assume that the entire page table and all the pages are in the physical memory. It takes 10 milliseconds to search the TLB and 80 milliseconds to access the physical memory. If the TLB hit ratio is 0.6, the effective memory access time (in milliseconds) is \_\_\_\_.

gatecse-2014-set3 operating-system virtual-memory numerical-answers normal

Answer key

# 5.33.30 Virtual Memory: GATE CSE 2015 | Set 1 | Question: 12

Consider a system with byte-addressable memory, 32-bit logical addresses, 4 kilobyte page size and page table entries of 4 bytes each. The size of the page table in the system in megabytes is \_\_\_\_.

gatecse-2015-set1 operating-system virtual-memory easy numerical-answers

Answer key

# 5.33.31 Virtual Memory: GATE CSE 2015 | Set 2 | Question: 25

A computer system implements a 40-bit virtual address, page size of 8 kilobytes, and a 128-entry translation look-aside buffer (TLB) organized into 32 sets each having 4 ways. Assume that the TLB tag does not store any process id. The minimum length of the TLB tag in bits is \_\_\_\_.

gatecse-2015-set2 operating-system virtual-memory easy numerical-answers

Answer key

# 5.33.32 Virtual Memory: GATE CSE 2015 | Set 2 | Question: 47

A computer system implements 8 kilobyte pages and a 32-bit physical address space. Each page table entry contains a valid bit, a dirty bit, three permission bits, and the translation. If the maximum size of the page table of a process is 24 megabytes, the length of the virtual address supported by the system is \_\_\_\_ bits.

gatecse-2015-set2 operating-system virtual-memory normal numerical-answers

Answer key

# 5.33.33 Virtual Memory: GATE CSE 2016 | Set 1 | Question: 47

Consider a computer system with 40-bit virtual addressing and page size of sixteen kilobytes. If the computer system has a one-level page table per process and each page table entry requires 48 bits, then the size of the per-process page table is \_\_\_\_ megabytes.

gatecse-2016-set1 operating-system virtual-memory easy numerical-answers

Answer key

# 5.33.34 Virtual Memory: GATE CSE 2018 | Question: 10

Consider a process executing on an operating system that uses demand paging. The average time for a memory access in the system is $M$ units if the corresponding memory page is available in memory, and $D$ units if the memory access causes a page fault. It has been experimentally measured that the average time taken for a memory access in the process is $X$ units.

Which one of the following is the correct expression for the page fault rate experienced by the process.

A. $(D - M) / (X - M)$

B. $(X - M) / (D - M)$

C. $(D - X) / (D - M)$

D. $(X - M) / (D - X)$

gatecse-2018 operating-system virtual-memory normal one-mark







# 5.33.35 Virtual Memory: GATE CSE 2019 | Question: 33


Assume that in a certain computer, the virtual addresses are 64 bits long and the physical addresses are 48 bits long. The memory is word addressable. The page size is 8 kB and the word size is 4 bytes. The Translation Look-aside Buffer (TLB) in the address translation path has 128 valid entries. At most how many distinct virtual addresses can be translated without any TLB miss?

A. $16 \times 2^{10}$

C. $4 \times 2^{20}$

B. $256 \times 2^{10}$

D. $8 \times 2^{20}$

gatecse-2019 operating-system virtual-memory two-marks

# Answer key

# 5.33.36 Virtual Memory: GATE CSE 2020 | Question: 53


Consider a paging system that uses 1-level page table residing in main memory and a TLB for address translation. Each main memory access takes 100 ns and TLB lookup takes 20 ns. Each page transfer to/from the disk takes 5000 ns. Assume that the TLB hit ratio is 95%, page fault rate is 10%. Assume that for 20% of the total page faults, a dirty page has to be written back to disk before the required page is read from disk. TLB update time is negligible. The average memory access time in ns (round off to 1 decimal places) is

gatecse-2020 numerical-answers operating-system virtual-memory two-marks

# Answer key

# 5.33.37 Virtual Memory: GATE CSE 2023 | Question: 48


Consider a computer system with 57-bit virtual addressing using multi-level tree-structured page tables with L levels for virtual to physical address translation. The page size is $4\mathrm{KB}(1\mathrm{KB}=1024\mathrm{B})$ and a page table entry at any of the levels occupies 8 bytes.

The value of L is \_\_\_\_.

gatecse-2023 operating-system virtual-memory numerical-answers two-marks

# Answer key

# 5.33.38 Virtual Memory: GATE CSE 2024 | Set 1 | Question: 52


Consider a memory management system that uses a page size of 2 KB. Assume that both the physical and virtual addresses start from 0. Assume that the pages 0, 1, 2, and 3 are stored in the page frames 1, 3, 2, and 0, respectively. The physical address (in decimal format) corresponding to the virtual address 2500 (in decimal format) is \_\_\_\_.

gatecse-2024-set1 numerical-answers operating-system virtual-memory two-marks

# Answer key

# 5.33.39 Virtual Memory: GATE CSE 2024 | Set 2 | Question: 14


Which of the following tasks is/are the responsibility/responsibilities of the memory management unit (MMU) in a system with paging-based memory management?

A. Allocate a new page table for a newly created process  
B. Translate a virtual address to a physical address using the page table  
C. Raise a trap when a virtual address is not found in the page table  
D. Raise a trap when a process tries to write to a page marked with read-only permission in the page table

gatecse-2024-set2 operating-system multiple-selects virtual-memory one-mark

# Answer key

# 5.33.40 Virtual Memory: GATE CSE 2024 | Set 2 | Question: 54


Consider a 32-bit system with 4 KB page size and page table entries of size 4 bytes each. Assume $1 KB = 2^{10}$ bytes. The OS uses a 2-level page table for memory management, with the page table

containing an outer page directory and an inner page table. The OS allocates a page for the outer page directory upon process creation. The OS uses demand paging when allocating memory for the inner page table, i.e., a page of the inner page table is allocated only if it contains at least one valid page table entry.

An active process in this system accesses 2000 unique pages during its execution, and none of the pages are swapped out to disk. After it completes the page accesses, let X denote the minimum and Y denote the maximum number of pages across the two levels of the page table of the process.

The value of X+Y is \_\_\_\_.

gatecse-2024-set2

numerical-answers

operating-system

virtual-memory

two-marks

# Answer key

# 5.33.41 Virtual Memory: GATE IT 2004 | Question: 66


In a virtual memory system, size of the virtual address is 32-bit, size of the physical address is 30-bit, page size is 4 Kbyte and size of each page table entry is 32-bit. The main memory is byte addressable. Which one of the following is the maximum number of bits that can be used for storing protection and other information in each page table entry?

A. 2

B. 10

C. 12

D. 14

gateit-2004 operating-system virtual-memory normal

# Answer key

# 5.33.42 Virtual Memory: GATE IT 2008 | Question: 16


A paging scheme uses a Translation Look-aside Buffer (TLB). A TLB-access takes 10 ns and the main memory access takes 50 ns. What is the effective access time(in ns) if the TLB hit ratio is 90% and there is no page-fault?

A. 54

B. 60

C. 65

D. 75

gateit-2008 operating-system virtual-memory normal

# Answer key

# 5.33.43 Virtual Memory: GATE IT 2008 | Question: 56


Match the following flag bits used in the context of virtual memory management on the left side with the different purposes on the right side of the table below.

<table><tr><td colspan="2">Name of the bit</td><td>Purpose</td></tr><tr><td>I.</td><td>Dirty</td><td>a. Page initialization</td></tr><tr><td>II.</td><td>R/W</td><td>b. Write-back policy</td></tr><tr><td>III.</td><td>Reference</td><td>c. Page protection</td></tr><tr><td>IV.</td><td>Valid</td><td>d. Page replacement policy</td></tr></table>

A. I-d, II-a, III-b, IV-c  
C. I-c, II-d, III-a, IV-b

gateit-2008 operating-system virtual-memory easy match-the-following

B. I-b, II-c, III-a, IV-d  
D. I-b, II-c, III-d, IV-a

# Answer key

# Answer Keys

<table><tr><td>5.1.1</td><td>A</td></tr><tr><td>5.3.3</td><td>C</td></tr></table>

<table><tr><td>5.1.2</td><td>A;C</td></tr><tr><td>5.3.4</td><td>A;B</td></tr></table>

<table><tr><td>5.2.1</td><td>3:3</td></tr><tr><td>5.4.1</td><td>800</td></tr></table>

<table><tr><td>5.3.1</td><td>C</td></tr><tr><td>5.5.1</td><td>2</td></tr></table>

<table><tr><td>5.3.2</td><td>B</td></tr><tr><td>5.5.2</td><td>A;B;C</td></tr><tr><td>5.5.3</td><td>06:06</td></tr><tr><td>5.7.1</td><td>N/A</td></tr><tr><td>5.7.6</td><td>9.006</td></tr><tr><td>5.7.11</td><td>D</td></tr><tr><td>5.7.16</td><td>B</td></tr><tr><td>5.7.21</td><td>D</td></tr><tr><td>5.7.26</td><td>30.06</td></tr><tr><td>5.8.1</td><td>N/A</td></tr><tr><td>5.8.6</td><td>A</td></tr><tr><td>5.8.11</td><td>346</td></tr><tr><td>5.8.16</td><td>C</td></tr><tr><td>5.9.5</td><td>A;C</td></tr><tr><td>5.10.3</td><td>C</td></tr><tr><td>5.10.8</td><td>C</td></tr><tr><td>5.11.5</td><td>A</td></tr><tr><td>5.14.1</td><td>90.00</td></tr><tr><td>5.14.6</td><td>D</td></tr><tr><td>5.17.3</td><td>B</td></tr><tr><td>5.17.8</td><td>B</td></tr><tr><td>5.19.3</td><td>B</td></tr><tr><td>5.20.5</td><td>C</td></tr><tr><td>5.20.10</td><td>B</td></tr><tr><td>5.20.15</td><td>C</td></tr><tr><td>5.20.20</td><td>D</td></tr><tr><td>5.20.25</td><td>B</td></tr><tr><td>5.20.30</td><td>A</td></tr><tr><td>5.22.1</td><td>B</td></tr><tr><td>5.23.1</td><td>N/A</td></tr><tr><td>5.23.6</td><td>A</td></tr><tr><td>5.23.11</td><td>B</td></tr><tr><td>5.23.16</td><td>B</td></tr><tr><td>5.23.21</td><td>A</td></tr><tr><td>5.23.26</td><td>5.5</td></tr><tr><td>5.23.31</td><td>8.25</td></tr><tr><td>5.23.36</td><td>5.25:5.26</td></tr><tr><td>5.23.41</td><td>B</td></tr><tr><td>5.23.46</td><td>D</td></tr><tr><td>5.24.2</td><td>N/A</td></tr><tr><td>5.24.7</td><td>N/A</td></tr><tr><td>5.24.12</td><td>N/A</td></tr></table>

<table><tr><td>5.5.4</td><td>A</td></tr><tr><td>5.7.2</td><td>N/A</td></tr><tr><td>5.7.7</td><td>D</td></tr><tr><td>5.7.12</td><td>A</td></tr><tr><td>5.7.17</td><td>C</td></tr><tr><td>5.7.22</td><td>99.55 : 99.65</td></tr><tr><td>5.7.27</td><td>C</td></tr><tr><td>5.8.2</td><td>N/A</td></tr><tr><td>5.8.7</td><td>D</td></tr><tr><td>5.8.12</td><td>85</td></tr><tr><td>5.9.1</td><td>C</td></tr><tr><td>5.9.6</td><td>153</td></tr><tr><td>5.10.4</td><td>31</td></tr><tr><td>5.11.1</td><td>A</td></tr><tr><td>5.11.6</td><td>B</td></tr><tr><td>5.14.2</td><td>D</td></tr><tr><td>5.15.1</td><td>4096</td></tr><tr><td>5.17.4</td><td>B</td></tr><tr><td>5.17.9</td><td>B</td></tr><tr><td>5.20.1</td><td>N/A</td></tr><tr><td>5.20.6</td><td>A</td></tr><tr><td>5.20.11</td><td>A</td></tr><tr><td>5.20.16</td><td>A</td></tr><tr><td>5.20.21</td><td>6</td></tr><tr><td>5.20.26</td><td>A;C</td></tr><tr><td>5.20.31</td><td>B</td></tr><tr><td>5.22.2</td><td>C</td></tr><tr><td>5.23.2</td><td>N/A</td></tr><tr><td>5.23.7</td><td>D</td></tr><tr><td>5.23.12</td><td>D</td></tr><tr><td>5.23.17</td><td>A</td></tr><tr><td>5.23.22</td><td>C</td></tr><tr><td>5.23.27</td><td>12</td></tr><tr><td>5.23.32</td><td>3</td></tr><tr><td>5.23.37</td><td>12 : 12</td></tr><tr><td>5.23.42</td><td>A</td></tr><tr><td>5.23.47</td><td>B</td></tr><tr><td>5.24.3</td><td>N/A</td></tr><tr><td>5.24.8</td><td>N/A</td></tr><tr><td>5.24.13</td><td>D</td></tr></table>

<table><tr><td>5.6.1</td><td>0.6</td></tr><tr><td>5.7.3</td><td>B</td></tr><tr><td>5.7.8</td><td>N/A</td></tr><tr><td>5.7.13</td><td>C</td></tr><tr><td>5.7.18</td><td>C</td></tr><tr><td>5.7.23</td><td>14020</td></tr><tr><td>5.7.28</td><td>D</td></tr><tr><td>5.8.3</td><td>N/A</td></tr><tr><td>5.8.8</td><td>B</td></tr><tr><td>5.8.13</td><td>B</td></tr><tr><td>5.9.2</td><td>D</td></tr><tr><td>5.9.7</td><td>B</td></tr><tr><td>5.10.5</td><td>C;D</td></tr><tr><td>5.11.2</td><td>B</td></tr><tr><td>5.11.7</td><td>C</td></tr><tr><td>5.14.3</td><td>A</td></tr><tr><td>5.16.1</td><td>65468:65468</td></tr><tr><td>5.17.5</td><td>10000</td></tr><tr><td>5.18.1</td><td>11:11</td></tr><tr><td>5.20.2</td><td>B</td></tr><tr><td>5.20.7</td><td>B</td></tr><tr><td>5.20.12</td><td>C</td></tr><tr><td>5.20.17</td><td>A</td></tr><tr><td>5.20.22</td><td>A</td></tr><tr><td>5.20.27</td><td>4108:4108</td></tr><tr><td>5.21.1</td><td>N/A</td></tr><tr><td>5.22.3</td><td>B</td></tr><tr><td>5.23.3</td><td>N/A</td></tr><tr><td>5.23.8</td><td>A</td></tr><tr><td>5.23.13</td><td>A</td></tr><tr><td>5.23.18</td><td>B</td></tr><tr><td>5.23.23</td><td>B</td></tr><tr><td>5.23.28</td><td>D</td></tr><tr><td>5.23.33</td><td>29</td></tr><tr><td>5.23.38</td><td>A;C;D</td></tr><tr><td>5.23.43</td><td>9.5:9.5</td></tr><tr><td>5.23.48</td><td>D</td></tr><tr><td>5.24.4</td><td>N/A</td></tr><tr><td>5.24.9</td><td>N/A</td></tr><tr><td>5.24.14</td><td>N/A</td></tr></table>

<table><tr><td>5.6.2</td><td>A</td></tr><tr><td>5.7.4</td><td>N/A</td></tr><tr><td>5.7.9</td><td>N/A</td></tr><tr><td>5.7.14</td><td>B</td></tr><tr><td>5.7.19</td><td>B</td></tr><tr><td>5.7.24</td><td>6.1 : 6.2</td></tr><tr><td>5.7.29</td><td>B</td></tr><tr><td>5.8.4</td><td>C</td></tr><tr><td>5.8.9</td><td>3</td></tr><tr><td>5.8.14</td><td>C</td></tr><tr><td>5.9.3</td><td>D</td></tr><tr><td>5.10.1</td><td>C</td></tr><tr><td>5.10.6</td><td>14</td></tr><tr><td>5.11.3</td><td>C</td></tr><tr><td>5.12.1</td><td>21:21</td></tr><tr><td>5.14.4</td><td>C</td></tr><tr><td>5.17.1</td><td>3.2</td></tr><tr><td>5.17.6</td><td>A</td></tr><tr><td>5.19.1</td><td>A</td></tr><tr><td>5.20.3</td><td>B</td></tr><tr><td>5.20.8</td><td>C</td></tr><tr><td>5.20.13</td><td>B</td></tr><tr><td>5.20.18</td><td>B</td></tr><tr><td>5.20.23</td><td>1</td></tr><tr><td>5.20.28</td><td>6:6</td></tr><tr><td>5.21.2</td><td>N/A</td></tr><tr><td>5.22.4</td><td>B;C;D</td></tr><tr><td>5.23.4</td><td>C</td></tr><tr><td>5.23.9</td><td>N/A</td></tr><tr><td>5.23.14</td><td>B</td></tr><tr><td>5.23.19</td><td>C</td></tr><tr><td>5.23.24</td><td>7.2</td></tr><tr><td>5.23.29</td><td>C</td></tr><tr><td>5.23.34</td><td>2</td></tr><tr><td>5.23.39</td><td>C;D</td></tr><tr><td>5.23.44</td><td>B</td></tr><tr><td>5.23.49</td><td>C</td></tr><tr><td>5.24.5</td><td>N/A</td></tr><tr><td>5.24.10</td><td>C</td></tr><tr><td>5.24.15</td><td>B</td></tr></table>

<table><tr><td>5.6.3</td><td>D</td></tr><tr><td>5.7.5</td><td>N/A</td></tr><tr><td>5.7.10</td><td>D</td></tr><tr><td>5.7.15</td><td>A</td></tr><tr><td>5.7.20</td><td>B</td></tr><tr><td>5.7.25</td><td>4096</td></tr><tr><td>5.7.30</td><td>D</td></tr><tr><td>5.8.5</td><td>B</td></tr><tr><td>5.8.10</td><td>10</td></tr><tr><td>5.8.15</td><td>B</td></tr><tr><td>5.9.4</td><td>4.0 : 4.1</td></tr><tr><td>5.10.2</td><td>B</td></tr><tr><td>5.10.7</td><td>4 : 4</td></tr><tr><td>5.11.4</td><td>A</td></tr><tr><td>5.13.1</td><td>B</td></tr><tr><td>5.14.5</td><td>C</td></tr><tr><td>5.17.2</td><td>N/A</td></tr><tr><td>5.17.7</td><td>C</td></tr><tr><td>5.19.2</td><td>C</td></tr><tr><td>5.20.4</td><td>C</td></tr><tr><td>5.20.9</td><td>C</td></tr><tr><td>5.20.14</td><td>A</td></tr><tr><td>5.20.19</td><td>7</td></tr><tr><td>5.20.24</td><td>D</td></tr><tr><td>5.20.29</td><td>C</td></tr><tr><td>5.21.3</td><td>N/A</td></tr><tr><td>5.22.5</td><td>B</td></tr><tr><td>5.23.5</td><td>B</td></tr><tr><td>5.23.10</td><td>19</td></tr><tr><td>5.23.15</td><td>A</td></tr><tr><td>5.23.20</td><td>D</td></tr><tr><td>5.23.25</td><td>1000</td></tr><tr><td>5.23.30</td><td>A</td></tr><tr><td>5.23.35</td><td>C</td></tr><tr><td>5.23.40</td><td>B;C</td></tr><tr><td>5.23.45</td><td>D</td></tr><tr><td>5.24.1</td><td>D</td></tr><tr><td>5.24.6</td><td>N/A</td></tr><tr><td>5.24.11</td><td>C</td></tr><tr><td>5.24.16</td><td>N/A</td></tr></table>