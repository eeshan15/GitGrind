- Always consider the graph representation that best suits the problem and its constraints.  
- Practice drawing graphs and tracing algorithms.

# Graph Search

Definition: Algorithms for systematically visiting all vertices and edges in a graph. The two primary methods are Breadth-First Search (BFS) and Depth-First Search (DFS).

# - Properties/Identities:

- BFS: Level-by-level, uses queue, finds shortest path in unweighted graphs.  
- DFS: Explores deeply, uses stack/recursion, useful for cycle detection, topological sort, SCC.

# - Pitfalls/Tricks:

- Forgetting to use a 'visited' array/set to prevent infinite loops in cyclic graphs.  
- Choosing the wrong search algorithm for the problem (e.g., DFS for unweighted shortest path).

# - Techniques/Shortcuts:

- BFS is good for finding "closest" elements.  
- DFS is good for exploring "all paths" or "connectivity".

# Greedy Algorithms

Definition: An algorithmic paradigm that makes the locally optimal choice at each stage with the hope of finding a global optimum. It doesn't always guarantee the globally optimal solution but works for specific problems.

# - Properties/Identities:

- Greedy Choice Property: A globally optimal solution can be reached by making a locally optimal (greedy) choice.  
- Optimal Substructure: An optimal solution to the problem contains optimal solutions to its subproblems.

# - Pitfalls/Tricks:

- Applying greedy approach to problems where it doesn't yield an optimal solution (e.g., general shortest path with negative weights, 0/1 Knapsack).  
- Not proving the greedy choice property and optimal substructure.

# - Techniques/Shortcuts:

Common examples: Dijkstra's, Prim's, Kruskal's, Huffman Coding.  
- Try to prove correctness by contradiction or exchange argument.

# Hashing

Definition: A technique used to map data of arbitrary size to fixed-size values (hash codes), typically used for efficient data retrieval in hash tables. Involves a hash function and collision resolution strategies.

# - Formulas/Theorems:

- Hash Function: $h(k) = k \pmod{M}$ (division method), $h(k) = \lfloor M(kA \pmod{1}) \rfloor$ (multiplication method).  
- Load Factor: $\alpha = N / M$ , where $N$ is number of items, $M$ is table size.

# • Properties/Identities:

- Collision: When two different keys map to the same hash value.  
○ Collision Resolution: Open addressing (linear probing, quadratic probing, double hashing) or Separate chaining.  
○ Average Time Complexity (Search, Insert, Delete): $O(1)$ (with good hash function and low load factor).  
- Worst-case Time Complexity: $O(N)$ (due to collisions).

# - Pitfalls/Tricks:

- Choosing a poor hash function that leads to many collisions (e.g., for string keys, summing ASCII values).  
- Ignoring the impact of load factor on performance.

# - Techniques/Shortcuts:

- For division method, choose $M$ as a prime number not too close to a power of 2 or 10.  
- Understand the trade-offs between different collision resolution techniques.

# Heap Sort

Definition: A comparison-based sorting algorithm that uses a binary heap data structure. It's an in-place algorithm that first builds a max-heap from the input data and then repeatedly extracts the maximum element and rebuilds the heap.

# - Formulas/Theorems:

- Time Complexity: $O(N \log N)$ for all cases (best, average, worst).  
- Space Complexity: $\hat{O}(1)$ (in-place).

# • Properties/Identities:

- Not a stable sorting algorithm.  
- Uses a max-heap.  
- Build-heap step takes $O(N)$ time.  
- $N$ extractions take $N \cdot \dot{O}(\log N)$ time.

# - Pitfalls/Tricks:

- Confusing the heap property (min-heap vs. max-heap) with the sorting order.  
- Incorrectly implementing the \`heapify\` procedure.

# - Techniques/Shortcuts:

- Remember the two phases: build heap, then extract max and heapify.  
- The largest element is always at the root after heapify.

# Huffman Code

Definition: A particular type of optimal prefix code used for lossless data compression. It's a greedy algorithm that builds a binary tree based on the frequencies of characters, assigning shorter codes to more frequent characters.

# - Properties/Identities:

- Prefix Code: No code is a prefix of another code, allowing unambiguous decoding.  
- Optimal: Produces the minimum possible expected code word length for a given set of character frequencies.  
- Uses a min-priority queue to repeatedly combine the two lowest-frequency nodes.  
- Time Complexity: $O(N \log N)$ where $N$ is the number of unique characters.

# - Pitfalls/Tricks:

- Incorrectly building the Huffman tree (e.g., not using a min-priority queue, or incorrect combination logic).  
- Forgetting that it's a greedy algorithm.

# - Techniques/Shortcuts:

- Always combine the two nodes with the smallest frequencies.  
- The path from the root to a leaf defines the code word (e.g., left=0, right=1).

# Identify Function

Definition: In a general mathematical or programming context, an identity function (often denoted id or I) is a function that always returns the same value that was used as its argument. $f(x) = x$ . In algorithms, it might refer to a function used to uniquely identify elements or properties.

# • Properties/Identities:

- For any input $x$ , $f(x) = x$ .  
- It's the neutral element for function composition: $(f \circ id)(x) = f(x)$ and $(id \circ f)(x) = f(x)$ .

# - Pitfalls/Tricks:

\- This term is very generic; in an algorithmic context, it's usually implied or part of a larger concept (e.g., an identity hash function, or an identity matrix).

# Insertion Sort

Definition: A simple sorting algorithm that builds the final sorted array (or list) one item at a time. It iterates through the input elements and removes one element at a time, finds the place where it belongs within the already sorted part, and inserts it there.

# - Formulas/Theorems:

- Worst-case Time Complexity: $O(N^2)$ (e.g., reverse sorted array).  
○ Average-case Time Complexity: $O(N^{2})$ .  
- Best-case Time Complexity: $O(N)$ (already sorted array).  
- Space Complexity: $O(1)$ (in-place).  
○ Number of Swaps (Worst Case): $N(N-1)/2$ .  
○ Number of Comparisons (Worst Case): $N(N - 1)/2$ .

# • Properties/Identities:

- Stable sorting algorithm.  
- Adaptive (efficient for nearly sorted arrays).  
- Good for small datasets.

# - Pitfalls/Tricks:

- Inefficient for large, unsorted arrays.  
- Understanding the "shift" operation correctly.

# - Techniques/Shortcuts:

- Think of it like sorting a hand of playing cards.  
- The first element is considered sorted.

# Inversion

Definition: In an array $A$ , an inversion is a pair of indices $(i, j)$ such that $i < j$ and $A[i] > A[j]$ . It measures how "unsorted" an array is.

# - Formulas/Theorems:

• Maximum number of inversions in an array of size N: $N(N - 1)/2$ (for a reverse-sorted array).  
- Minimum number of inversions: 0 (for a sorted array).

# - Properties/Identities:

\- The number of inversions can be counted efficiently using a modified Merge Sort algorithm in $O(N \log N)$ time.

# - Pitfalls/Tricks:

\- Confusing inversions with just any pair of elements that are out of order; the index order $i < j$ is crucial.

# - Techniques/Shortcuts:

To count inversions, adapt Merge Sort: when merging two sorted halves, if an element from the right half is taken before an element from the left half, it means all remaining elements in the left half form inversions with the taken element.

# Linear Probing

Definition: A collision resolution technique in open addressing hashing where, upon a collision, the algorithm searches for the next available slot sequentially in the hash table (e.g., at $h(k) + 1$ , $h(k) + 2$ , $\ldots$ ).

# - Formulas/Theorems:

○ Probe Sequence: $h(k,i)=(h(k)+i)$ (mod M), where M is table size and i is probe number $(0,1,2,\ldots)$ .

# • Properties/Identities:

- Simple to implement.  
- Suffers from primary clustering: long runs of occupied slots build up, increasing average search time.

# - Pitfalls/Tricks:

- Primary clustering significantly degrades performance, especially at high load factors.  
Deletion is tricky: simply removing an element can break search chains. Often requires "lazy deletion" or re-hashing.

# - Techniques/Shortcuts:

\- Understand that it's the simplest but often least efficient open addressing method.

# Matrix Chain Ordering (Matrix Chain Multiplication)

Definition: A dynamic programming problem that seeks to find the most efficient way to multiply a sequence of matrices. The problem is not about performing the multiplications, but deciding the optimal parenthesization (order) to minimize the total number of scalar multiplications.

# - Formulas/Theorems:

\- Recurrence Relation: Let $M[i, j]$ be the minimum number of scalar multiplications needed to compute the product $A_i A_{i+1} \ldots A_j$ .

$$
M [ i, j ] = \min _ {i \leq k <   j} (M [ i, k ] + M [ k + 1, j ] + p _ {i - 1} p _ {k} p _ {j})
$$

where $A_{i}$ has dimensions $p_{i-1} \times p_{i}$ .

- Base Case: $M[i, i] = 0$ (single matrix requires no multiplications).  
- Time Complexity: $O(N^3)$ for $N$ matrices.  
- Space Complexity: $O(N^2)$ for the DP table.

# • Properties/Identities:

- Exhibits optimal substructure and overlapping subproblems.  
- The order of multiplication matters for efficiency, not for the result.

# - Pitfalls/Tricks:

- Incorrectly setting up the dimensions array $p$ . If there are $N$ matrices $A_1, \ldots, A_N$ , and $A_i$ is $p_{i-1} \times p_i$ , then the array $p$ has $N + 1$ elements.  
- Off-by-one errors in the recurrence relation indices.

# - Techniques/Shortcuts:

\- Fill the DP table diagonally, starting with chain length 2, then 3, and so on.

# Maximum Minimum

Definition: The problem of finding both the maximum and minimum elements in a given array or list. This can be done naively by iterating twice or more efficiently using a divide and conquer approach.

# - Formulas/Theorems:

- Naive Approach (2N-2 comparisons): Iterate once for max, once for min.  
- Divide and Conquer Approach (approx. 3N/2 comparisons):

- If array size is 1, max=min=element.  
- If array size is 2, compare once.  
- Recursively find max/min in two halves, then compare the two maxes and two mins.

# • Properties/Identities:

\- The divide and conquer approach is more efficient in terms of comparisons.

# - Pitfalls/Tricks:

\- Forgetting to handle base cases (array of size 1 or 2) correctly in recursive solutions.

# - Techniques/Shortcuts:

\- Pairwise comparison: process elements in pairs, comparing them. Then compare the smaller of the pair with the current min, and the larger with the current max. This also achieves approx. 3N/2 comparisons.

# Merge Sort

Definition: A divide and conquer sorting algorithm that divides an unsorted list into N sublists, each containing one element (a list of one element is considered sorted), then repeatedly merges sublists to produce new sorted sublists until there is only one sorted list remaining.

# - Formulas/Theorems:

• Recurrence Relation: $T(N) = 2T(N/2) + O(N)$ (for dividing and merging).  
- Time Complexity: $O(N \log N)$ for all cases (best, average, worst).  
- Space Complexity: $O(N)$ (due to auxiliary array for merging).

# • Properties/Identities:

- Stable sorting algorithm.  
- Not an in-place algorithm (requires extra space).  
- Well-suited for external sorting.

# - Pitfalls/Tricks:

- Incorrectly implementing the merging step, which is crucial for correctness and efficiency.  
- Forgetting to copy remaining elements from one half if the other half is exhausted during merge.

# - Techniques/Shortcuts:

- The merge step is the core: combine two sorted arrays into one sorted array.  
- Can be used to count inversions.

# Merging

Definition: The process of combining two or more sorted lists (or arrays) into a single sorted list. This is a fundamental operation in algorithms like Merge Sort.

# - Formulas/Theorems:

- Time Complexity: $O(N + M)$ to merge two sorted lists of sizes $N$ and $M$ .  
- Space Complexity: $O(N + M)$ for the new merged list.

# • Properties/Identities:

- Requires input lists to be sorted.  
- The output list is also sorted.

# - Pitfalls/Tricks:

- Off-by-one errors when handling array boundaries and indices.  
- Not correctly handling the case where one list is exhausted before the other.

# - Techniques/Shortcuts:

\- Use two pointers, one for each input list, and a third pointer for the merged list.

# Minimum Spanning Tree (MST)

Definition: For a connected, undirected, weighted graph, an MST is a subgraph that is a tree, connects all the vertices together, and has the minimum possible total edge weight. Algorithms include Prim's and Kruskal's.

# - Formulas/Theorems:

- Cut Property: For any cut (partition of vertices into two sets), if an edge crosses the cut and has strictly less weight than any other edge crossing the cut, then this edge must be in every MST.  
- Cycle Property: If an edge is the heaviest edge in any cycle of a graph, then it cannot be part of an MST.  
- An MST of a graph with $|V|$ vertices always has $|V| - 1$ edges.

# • Properties/Identities:

- Both Prim's and Kruskal's are greedy algorithms.  
- Prim's: Grows the MST from a starting vertex.  
- Kruskal's: Adds edges in increasing order of weight, avoiding cycles.

# - Pitfalls/Tricks:

- Applying MST algorithms to disconnected graphs (they will find an MST for each connected component, forming a Minimum Spanning Forest).  
- Confusing MST with shortest path problems.

# - Techniques/Shortcuts:

- Prim's uses a min-priority queue.  
- Kruskal's uses a Disjoint Set Union (DSU) data structure.

# Number of Swap

Definition: A metric used to evaluate the efficiency of certain sorting algorithms, particularly comparison sorts. It counts how many times elements are exchanged during the sorting process.

# - Formulas/Theorems:

○ Bubble Sort (Worst Case): $N(N - 1)/2$ .  
- Selection Sort (Worst Case): $N - 1$ .  
- Insertion Sort (Worst Case): $N(N - 1) / 2$ .  
- Quick Sort (Worst Case): $O(N^{2})$ swaps.  
- Heap Sort (Worst Case): $O(N \log N)$ swaps.

# • Properties/Identities:

- A lower number of swaps generally indicates better performance, especially when swap operations are costly.  
- Selection sort performs the minimum number of swaps among simple sorts.

# - Pitfalls/Tricks:

\- Confusing swaps with comparisons. Both are important metrics but measure different aspects.

# - Techniques/Shortcuts:

\- Memorize the worst-case swap counts for common sorting algorithms.

# Prims Algorithm

Definition: A greedy algorithm that finds a Minimum Spanning Tree (MST) for a weighted undirected graph. It starts from an arbitrary vertex and grows the MST by adding the cheapest edge that connects a vertex in the MST to a vertex outside the MST.

# - Formulas/Theorems:

# - Time Complexity:

- With adjacency matrix (simple array scan): $O(|V|^2)$ .  
- With adjacency list and binary min-priority queue: $O(|E| \log |V|)$ or $O(|E| + |V| \log |V|)$ .  
- Space Complexity: $O(|V| + |E|)$ for graph, $O(|V|)$ for distances/parent array.

# • Properties/Identities:

- Greedy algorithm.  
- Builds the MST by adding vertices one by one.  
- Similar structure to Dijkstra's algorithm.

# - Pitfalls/Tricks:

- Forgetting to update edge weights in the priority queue when a shorter path to an unvisited vertex is found.  
- Applying to directed graphs (MST is for undirected graphs).

# - Techniques/Shortcuts:

\- Maintain a set of vertices already in the MST and a min-priority queue of edges connecting to vertices outside

the MST.

# Quick Sort

Definition: A highly efficient, in-place, divide and conquer sorting algorithm. It works by selecting a 'pivot' element from the array and partitioning the other elements into two sub-arrays, according to whether they are less than or greater than the pivot. The sub-arrays are then sorted recursively.

# - Formulas/Theorems:

- Worst-case Time Complexity: $O(N^2)$ (e.g., already sorted array with first/last element as pivot).  
○ Average-case Time Complexity: $O(N \log N)$ .  
- Best-case Time Complexity: $O(N \log N)$ .  
- Space Complexity: $O(\log N)$ (average, for recursion stack) or $O(N)$ (worst-case, for recursion stack).  
• Recurrence Relation (Average Case): $T(N) = T(k) + T(N - k - 1) + O(N)$ , where k is the size of one partition. For balanced partitions, $T(N) = 2T(N/2) + O(N)$ .

# • Properties/Identities:

- Not a stable sorting algorithm.  
- In-place sorting algorithm.  
- Performance heavily depends on pivot selection.

# - Pitfalls/Tricks:

- Poor pivot selection can lead to $O(N^2)$ performance.  
- Incorrect partitioning logic can lead to infinite recursion or incorrect sorting.

# - Techniques/Shortcuts:

- Randomized pivot selection helps achieve average-case performance reliably.  
- Hoare's partition scheme is often more efficient than Lomuto's.

# Recurrence Relation

Definition: An equation that recursively defines a sequence or function, where each term or value is given as a function of preceding terms. Used to describe the time complexity of recursive algorithms.

# - Formulas/Theorems:

\- Master Theorem: For recurrences of the form $T(N) = aT(N / b) + f(N)$ where $a \geq 1, b > 1$ .

1. If $f(N) = O(N^{\log_b a - \epsilon})$ for some $\epsilon > 0$ , then $T(N) = \Theta(N^{\log_b a})$ .  
2. If $f(N) = \Theta(N^{\log_b a})$ , then $T(N) = \Theta(N^{\log_b a} \log N)$ .  
3. If $f(N) = \Omega(N^{\log_b a + \epsilon})$ for some $\epsilon > 0$ , AND $af(N / b) \leq cf(N)$ for some $c < 1$ and large $N$ , then $T(N) = \Theta(f(N))$ .

# • Properties/Identities:

- Describes the growth rate of recursive algorithms.  
- Methods to solve: Substitution, Recursion Tree, Master Theorem.

# - Pitfalls/Tricks:

- Incorrectly applying the Master Theorem (e.g., when $f(N)$ doesn't fit any case or the regularity condition is not met).  
- Algebraic errors in substitution or recursion tree methods.

# - Techniques/Shortcuts:

- Memorize the three cases of the Master Theorem.  
- For simple recurrences, try expanding a few terms to find a pattern.

# Recursion

Definition: A programming technique where a function calls itself directly or indirectly to solve a problem. It involves a base case (stopping condition) and a recursive step (reducing the problem to a smaller instance of itself).

# • Properties/Identities:

- Base Case: A condition that terminates the recursion.  
- Recursive Step: The function calls itself with a modified (smaller) input.  
- Often leads to elegant and concise code for problems with recursive structure.

# - Pitfalls/Tricks:

- Missing or incorrect base case leading to infinite recursion (stack overflow).  
- High space complexity due to recursion stack.  
- Performance overhead compared to iterative solutions due to function call stack management.

# - Techniques/Shortcuts:

- Always identify the base case first.  
- Ensure that each recursive call moves closer to the base case.  
- For some problems, recursion can be converted to iteration using a stack.

# Searching

Definition: The process of finding a specific item (or items) within a collection of items. Common search algorithms include Linear Search and Binary Search.

# - Formulas/Theorems:

○ Linear Search (Worst Case): $O(N)$ comparisons.  
- Binary Search (Worst Case): $O(\log N)$ comparisons.

# • Properties/Identities:

- Linear Search: Works on unsorted or sorted data.  
- Binary Search: Requires sorted data.

# - Pitfalls/Tricks:

- Using Linear Search on a large sorted array when Binary Search is applicable.  
- Errors in Binary Search boundary conditions.

# - Techniques/Shortcuts:

\- Always check if data is sorted before choosing a search algorithm.

# Selection Sort

Definition: A simple sorting algorithm that repeatedly finds the minimum element from the unsorted part of the list and swaps it with the element at the current position. It maintains two subarrays: sorted and unsorted.

# - Formulas/Theorems:

- Worst-case Time Complexity: $O(N^2)$ .  
○ Average-case Time Complexity: $O(N^{2})$ .  
- Best-case Time Complexity: $O(N^2)$ .  
- Space Complexity: $O(1)$ (in-place).  
- Number of Swaps (All Cases): $N - 1$ (minimum possible swaps for any comparison sort).  
○ Number of Comparisons (All Cases): $N(N-1)/2$ .

# • Properties/Identities:

- Not a stable sorting algorithm.  
- Performs the minimum number of swaps among simple sorts.

# - Pitfalls/Tricks:

\- Its performance is consistently $O(N^2)$ regardless of input order, unlike Bubble Sort or Insertion Sort.

# - Techniques/Shortcuts:

\- The key idea is to find the minimum and place it, then find the next minimum and place it, and so on.

# Shortest Path

Definition: The problem of finding a path between two vertices (or from a source to all other vertices) in a graph such that the sum of the weights of its constituent edges is minimized. Algorithms include BFS (unweighted), Dijkstra's (non-negative weights), and Bellman-Ford (negative weights).

# • Properties/Identities:

- Unweighted Graphs: BFS finds shortest path in terms of number of edges.  
- Non-negative Weighted Graphs: Dijkstra's algorithm.  
- Negative Weighted Graphs (no negative cycles): Bellman-Ford algorithm.  
- All-Pairs Shortest Path: Floyd-Warshall algorithm.

# - Pitfalls/Tricks:

- Using the wrong algorithm for the given graph properties (e.g., Dijkstra's on negative weights).  
- Not handling disconnected components or unreachable vertices.

# - Techniques/Shortcuts:

- Always check for negative edge weights and negative cycles.  
- Understand the relaxation principle.

# Sorting

Definition: The process of arranging elements of a list or array in a specific order (e.g., numerical, alphabetical, ascending, descending). It's a fundamental operation in computer science.

# - Formulas/Theorems:

\- Comparison Sort Lower Bound: Any comparison-based sorting algorithm requires $\Omega(N \log N)$ comparisons in the worst case.

# - Properties/Identities:

- Stable Sort: Preserves the relative order of equal elements.  
• In-place Sort: Requires $O(1)$ or $O(\log N)$ auxiliary space.  
- Adaptive Sort: Performance improves for partially sorted input.

# - Pitfalls/Tricks:

- Confusing different sorting algorithm properties (stability, in-place, worst-case vs. average-case).  
- Choosing an inefficient sort for specific data characteristics.

# - Techniques/Shortcuts:

- Know the time and space complexities, stability, and in-place nature of common sorts.  
- For GATE, often questions involve comparing two sorts or analyzing a modified sort.

# Space Complexity

Definition: A measure of the amount of memory an algorithm needs to run to completion. It includes the space required for input, output, and temporary variables, often expressed using asymptotic notation.

# • Properties/Identities:

- Auxiliary Space: The extra space used by the algorithm beyond the input data.  
- In-place Algorithm: An algorithm that transforms input using only a small, constant amount of auxiliary space, typically $O(1)$ or $O(\log N)$ for recursion stack.

# - Pitfalls/Tricks:

- Forgetting to account for the recursion stack space in recursive algorithms.  
- Confusing total space with auxiliary space.

# - Techniques/Shortcuts:

- Identify data structures created by the algorithm (arrays, queues, stacks, hash tables).  
- For recursive calls, the maximum depth of the recursion stack contributes to space complexity.

# Strongly Connected Components (SCC)

Definition: In a directed graph, a strongly connected component (SCC) is a maximal subgraph such that for every pair of vertices u and v in the subgraph, there is a path from u to v and a path from v to u. Algorithms include Kosaraju's and Tarjan's.

# - Properties/Identities:

- SCCs partition the vertices of a directed graph.  
- If we contract each SCC into a single vertex, the resulting graph is a Directed Acyclic Graph (DAG).  
- Kosaraju's Algorithm: Two DFS passes (one on original graph, one on transpose graph).  
- Tarjan's Algorithm: One DFS pass, uses discovery times and low-link values.

# - Formulas/Theorems:

\- Time Complexity (Kosaraju's, Tarjan's): $O(|V| + |E|)$ .

# - Pitfalls/Tricks:

- Confusing SCCs with connected components in undirected graphs.  
- Incorrectly performing DFS on the transpose graph for Kosaraju's.

# - Techniques/Shortcuts:

- Kosaraju's: DFS on G to get finishing times, then DFS on G transpose in decreasing order of finishing times.  
- Tarjan's: Uses a stack and \`disc\` (discovery time) and \`low\` (lowest discovery time reachable) arrays.

# Time Complexity

Definition: A measure of the amount of time an algorithm takes to run as a function of the length of its input. It's typically expressed using asymptotic notations (Big-O, Omega, Theta).

# • Properties/Identities:

- Focuses on the growth rate of operations as input size $N$ increases.  
- Usually refers to worst-case time complexity, but average-case and best-case are also important.  
- Independent of machine specifics (CPU speed, memory access time).

# - Pitfalls/Tricks:

- Confusing constant factors with asymptotic growth.  
- Incorrectly analyzing loops or recursive calls.  
- Assuming best-case performance for general analysis.

# - Techniques/Shortcuts:

- Count dominant operations (comparisons, assignments, arithmetic operations).  
- For nested loops, multiply loop counts.  
- For recursive functions, use recurrence relations and Master Theorem.

# Topological Sort

Definition: A linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every directed edge $(u, v)$ , vertex u comes before vertex v in the ordering. Not unique for all DAGs.

# • Properties/Identities:

- Only possible for DAGs.  
- Can be implemented using DFS or Kahn's algorithm (using in-degrees and a queue).  
- Time Complexity: $O(|V| + |E|)$ .

# - Pitfalls/Tricks:

- Attempting to topologically sort a graph with cycles (it's impossible).  
- Incorrectly handling multiple possible topological sorts.

# - Techniques/Shortcuts:

- DFS-based: Perform DFS, then reverse the order of finishing times.  
- Kahn's Algorithm: Find all nodes with in-degree 0, add to queue. While queue not empty, dequeue, add to sorted list, decrement in-degree of neighbors. If neighbor's in-degree becomes 0, enqueue.

# Tree Traversal

Definition: The process of visiting each node in a tree data structure exactly once. Common methods include Inorder, Preorder, Postorder (for binary trees), and Level-order traversal.

# • Properties/Identities:

- Inorder (Left-Root-Right): For BSTs, gives sorted elements.  
- Preorder (Root-Left-Right): Useful for creating a copy of the tree.  
- Postorder (Left-Right-Root): Useful for deleting a tree.  
- Level-order (BFS-like): Visits nodes level by level, uses a queue.  
- Time Complexity: $O(N)$ for a tree with $N$ nodes.  
- Space Complexity: $\hat{O}(\hat{H})$ for DFS-based (recursion stack, where $H$ is height), $O(W)$ for BFS-based (queue, where $W$ is max width).

# - Pitfalls/Tricks:

- Confusing the order of visits for different traversal types.  
- Incorrectly handling null nodes in recursive traversals.

# - Techniques/Shortcuts:

- Practice drawing the traversal paths on sample trees.  
- Remember the "Root" position in the name (Pre-Root-Order, In-Root-Order, Post-Root-Order).

# Uniform Hashing

Definition: An idealized theoretical model for hashing where each key is equally likely to hash to any slot in the hash table, independent of where other keys hash. It implies a perfectly random distribution of keys.

# • Properties/Identities:

- Assumed for theoretical analysis of hashing algorithms (e.g., average case performance of open addressing).  
- Difficult to achieve in practice with real-world data.  
- Minimizes collisions and maximizes efficiency.

# - Pitfalls/Tricks:

- Assuming practical hash functions achieve uniform hashing, which is rarely true.  
- Not understanding that it's a theoretical ideal, not a practical hash function.

# - Techniques/Shortcuts:

\- When analyzing hashing, remember that uniform hashing is the best-case scenario for collision distribution.

# Quick Formula Reference

# - Asymptotic Notations:

- Big-O: $f(n) = O(g(n)) \implies \exists c, n_0 > 0$ s.t. $0 \leq f(n) \leq c \cdot g(n)$ for $n \geq n_0$ .  
○ Omega: $f(n) = \Omega(g(n)) \implies \exists c, n_{0} > 0$ s.t. $0 \leq c \cdot g(n) \leq f(n)$ for $n \geq n_{0}$ .  
° Theta: $f(n) = \Theta(g(n)) \implies \exists c_1, c_2, n_0 > 0$ s.t. $0 \leq c_1 \cdot g(n) \leq f(n) \leq c_2 \cdot g(n)$ for $n \geq n_0$ .

# - Binary Heap:

- Parent of $i$ (0-indexed): $\lfloor (i - 1) / 2 \rfloor$ .  
- Left child of $i: 2i + 1$ .  
- Right child of $i: 2i + 2$ .  
- Height: $\lfloor \log_2N\rfloor$ .

# - Binary Tree:

- Max nodes at level $i$ : $2^{i}$ .  
- Max nodes in height $h$ : $2^{h+1} - 1$ .  
- Min height with $N$ nodes: $\lceil \log_2(N + 1) \rceil - 1$ .

# - Hashing (Open Addressing):

- Linear Probing: $h(k,i) = (h(k) + i) \pmod{M}$ .  
- Double Hashing: $h(k,i) = (h_1(k) + i \cdot h_2(k)) \pmod{M}$ .  
- Load Factor: $\alpha = N / M$ .

# - Matrix Chain Ordering:

$$
M [ i, j ] = \min _ {i \leq k <   j} (M [ i, k ] + M [ k + 1, j ] + p _ {i - 1} p _ {k} p _ {j})
$$

Base Case: $M[i,i] = 0$ .

# - Recurrence Relation (Master Theorem): $T(N) = aT(N / b) + f(N)$ .

1. If $f(N) = O(N^{\log_b a - \epsilon}), T(N) = \Theta(N^{\log_b a})$ .  
2. If $f(N) = \Theta(N^{\log_b a}), T(N) = \Theta(N^{\log_b a} \log N)$ .  
3. If $f(N) = \Omega(N^{\log_b a + \epsilon})$ and $af(N / b) \leq cf(N), T(N) = \Theta(f(N))$ .

# - Sorting Algorithm Complexities:

<table><tr><td>Algorithm</td><td>Time (Worst)</td><td>Time (Avg)</td><td>Space</td><td>Stable</td><td>In-place</td></tr><tr><td>Bubble Sort</td><td> $O(N^{2})$ </td><td> $O(N^{2})$ </td><td> $O(1)$ </td><td>Yes</td><td>Yes</td></tr><tr><td>Insertion Sort</td><td> $O(N^{2})$ </td><td> $O(N^{2})$ </td><td> $O(1)$ </td><td>Yes</td><td>Yes</td></tr><tr><td>Selection Sort</td><td> $O(N^{2})$ </td><td> $O(N^{2})$ </td><td> $O(1)$ </td><td>No</td><td>Yes</td></tr><tr><td>Merge Sort</td><td> $O(N \log N)$ </td><td> $O(N \log N)$ </td><td> $O(N)$ </td><td>Yes</td><td>No</td></tr><tr><td>Quick Sort</td><td> $O(N^{2})$ </td><td> $O(N \log N)$ </td><td> $O(\log N)$ </td><td>No</td><td>Yes</td></tr><tr><td>Heap Sort</td><td> $O(N \log N)$ </td><td> $O(N \log N)$ </td><td> $O(1)$ </td><td>No</td><td>Yes</td></tr></table>

# - Graph Algorithm Complexities (Adjacency List):

- BFS: $O(|V| + |E|)$  
。DFS: $O(|V| + |E|)$  
- Dijkstra's (Binary Heap): $O(|E|\log |V|)$  
- Bellman-Ford: $O(|V| \cdot |E|)$  
- Prim's (Binary Heap): $O(|\vec{E}|\log |V|)$  
- Kruskal's (DSU): $O(|E|\log |E|)$ or $O(|E|\log |V|)$  
- Topological Sort: $O(|V| + |E|)$  
- SCC (Kosaraju's/Tarjan's): $O(|V| + |E|)$

# Important Tips for GATE

1. Master Asymptotic Notations: A significant portion of algorithm questions revolves around time and space complexity. Understand the definitions of $O, \Omega, \Theta, o, \omega$ thoroughly, and be adept at applying them to various code snippets and recurrence relations, especially using the Master Theorem.  
2. Understand Algorithm Design Paradigms: Don't just memorize algorithms; understand why they work and which paradigm they belong to (Divide and Conquer, Greedy, Dynamic Programming). This helps in identifying the correct approach for new problems.  
3. Practice Recurrence Relations: Solving recurrence relations is a frequently tested skill. Be comfortable with the substitution method, recursion tree method, and especially the Master Theorem. Pay attention to base cases and boundary conditions.  
4. Graph Algorithms are Crucial: BFS, DFS, Dijkstra's, Bellman-Ford, Prim's, Kruskal's, Topological Sort, and SCCs are high-yield topics. Know their complexities, applications, and limitations (e.g., negative weights for

# 1.1.1 Algorithm Design: GATE CSE 1992 | Question: 8


Let $T$ be a Depth First Tree of a undirected graph $G$ . An array $P$ indexed by the vertices of $G$ is given. $P[V]$ is the parent of vertex $V$ , in $T$ . Parent of the root is the root itself.

Give a method for finding and printing the cycle formed if the edge $(u,v)$ of $G$ not in $T$ (i.e., $e \in G - T$ ) is now added to $T$ .

Time taken by your method must be proportional to the length of the cycle.

Describe the algorithm in a PASCAL $(C)$ - like language. Assume that the variables have been suitably declared.

gate1992 algorithms descriptive algorithm-design

Answer key

# 1.1.2 Algorithm Design: GATE CSE 1994 | Question: 7


An array $A$ contains $n$ integers in locations $A[0], A[1], \ldots A[n-1]$ . It is required to shift the elements of the array cyclically to the left by $K$ places, where $1 \leq K \leq n-1$ . An incomplete algorithm for doing this in linear time, without using another array is given below. Complete the algorithm by filling in the blanks. Assume all variables are suitably declared.

```txt
min:=n;
i=0;
while ______ do
begin
    temp:=A[i];
    j:=i;
    while ______ do
    begin
        A[j]:=________;
        j:=(j+K) mod n;
        if j<min then
            min:=j;
        end;
        A[(n+i-K) mod n]:=________;
        i:=________;
    end;
```

gate1994 algorithms normal algorithm-design fill-in-the-blanks

Answer key

# 1.1.3 Algorithm Design: GATE CSE 2006 | Question: 17


An element in an array $X$ is called a leader if it is greater than all elements to the right of it in $X$ . The best algorithm to find all leaders in an array

A. solves it in linear time using a left to right pass of the array  
B. solves it in linear time using a right to left pass of the array  
C. solves it using divide and conquer in time $\Theta(n \log n)$  
D. solves it in time $\Theta(n^{2})$

gatecse-2006 algorithms normal algorithm-design

Answer key

# 1.1.4 Algorithm Design: GATE CSE 2006 | Question: 54


Given two arrays of numbers $a_{1},\ldots,a_{n}$ and $b_{1},\ldots,b_{n}$ where each number is 0 or 1, the fastest algorithm to find the largest span $(i,j)$ such that $a_{i}+a_{i+1}+\cdots+a_{j}=b_{i}+b_{i+1}+\cdots+b_{j}$ or report that there is not such span,

A. Takes $O(3^n)$ and $\Omega(2^n)$ time if hashing is permitted  
B. Takes $O(n^3)$ and $\Omega(n^{2.5})$ time in the key comparison mode  
C. Takes $\Theta(n)$ time and space  
D. Takes $O(\sqrt{n})$ time only if the sum of the $2n$ elements is an even number

gatecse-2006 algorithms normal algorithm-design time-complexity

# Answer key

# 1.1.5 Algorithm Design: GATE CSE 2014 | Set 1 | Question: 37

There are 5 bags labeled 1 to 5. All the coins in a given bag have the same weight. Some bags have coins of weight 10 gm, others have coins of weight 11 gm. I pick 1, 2, 4, 8, 16 coins respectively from bags 1 to 5. Their total weight comes out to 323 gm. Then the product of the labels of the bags having 11 gm coins is \_\_\_\_.


gatecse-2014-set1 algorithms numerical-answers normal algorithm-design

# Answer key

# 1.1.6 Algorithm Design: GATE CSE 2019 | Question: 25

Consider a sequence of 14 elements: $A = [-5, -10, 6, 3, -1, -2, 13, 4, -9, -1, 4, 12, -3, 0]$ . The sequence sum $S(i, j) = \Sigma_{k=i}^{j} A[k]$ . Determine the maximum of $S(i, j)$ , where $0 \leq i \leq j < 14$ . (Divide and conquer approach may be used.)


Answer: \_\_\_\_

gatecse-2019 numerical-answers algorithms algorithm-design one-mark

# Answer key

# 1.1.7 Algorithm Design: GATE CSE 2021 | Set 1 | Question: 40

Define $R_{n}$ to be the maximum amount earned by cutting a rod of length $n$ meters into one or more pieces of integer length and selling them. For $i > 0$ , let $p[i]$ denote the selling price of a rod whose length is $i$ meters. Consider the array of prices:


$$
\mathrm{p} [ 1 ] = 1, \mathrm{p} [ 2 ] = 5, \mathrm{p} [ 3 ] = 8, \mathrm{p} [ 4 ] = 9, \mathrm{p} [ 5 ] = 1 0, \mathrm{p} [ 6 ] = 1 7, \mathrm{p} [ 7 ] = 1 8
$$

Which of the following statements is/are correct about $R_{7}$ ?

A. $R_{7} = 18$  
B. $R_{7}=19$  
C. $R_{7}$ is achieved by three different solutions  
D. $R_{7}$ cannot be achieved by a solution consisting of three pieces

gatecse-2021-set1 multiple-selects algorithms algorithm-design two-marks

# Answer key

# 1.1.8 Algorithm Design: GATE CSE 2024 | Set 2 | Question: 32

Consider an array X that contains n positive integers. A subarray of X is defined to be a sequence of array locations with consecutive indices.


The C code snippet given below has been written to compute the length of the longest subarray of X that contains at most two distinct integers. The code has two missing expressions labelled (P) and (Q).

```txt
int first=0, second=0, len1=0, len2=0, maxlen=0;
for (int i=0; i < n; i++) {
    if (X[i] == first) {
        len2++; len1++;
    } else if (X[i] == second) {
        len2++;
        len1 = ______(P) ______;
    second = first;
```