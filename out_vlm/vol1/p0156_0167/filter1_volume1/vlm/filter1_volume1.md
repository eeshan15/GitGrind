# - Common Pitfalls:

- Arithmetic errors in Gram-Schmidt, especially with projections.  
- Forgetting to normalize vectors after making them orthogonal.  
- Confusing orthogonal with orthonormal.

# - Problem-Solving Techniques:

- Systematically apply the Gram-Schmidt process, calculating one orthogonal vector at a time.  
- Double-check dot products to ensure orthogonality.  
- Always normalize the final set of orthogonal vectors.

# Rank of Matrix

The rank of a matrix is a fundamental property that measures the "linear independence" present in its rows and columns. It indicates the dimension of the vector space spanned by its rows or columns, and is crucial for understanding the solvability of linear systems.

\- Definition: The maximum number of linearly independent row vectors (row rank) or column vectors (column rank) in a matrix. The row rank is always equal to the column rank.

# • Calculation Methods:

1. Using Row Echelon Form: The rank of a matrix is the number of non-zero rows in its row echelon form.  
2. Using Determinants (Minors): The rank of a matrix $A$ is the largest integer $r$ such that there exists an $r \times r$ submatrix of $A$ with a non-zero determinant.

# • Properties/Theorems:

- For an $m \times n$ matrix $A$ , $\operatorname{rank}(A) \leq \min(m, n)$ .  
- $\operatorname{rank}(A) = 0$ if and only if $A$ is a zero matrix.  
$\circ \mathrm{rank}(A) = \mathrm{rank}(A^T)$ .  
- $\operatorname{rank}(AB) \leq \min(\operatorname{rank}(A), \operatorname{rank}(B))$ .  
- Rank-Nullity Theorem: For an $m \times n$ matrix $A$ , $\text{rank}(A) + \text{nullity}(A) = n$ , where $\text{nullity}(A)$ is the dimension of the null space (kernel) of $A$ .

\- A square matrix $A$ of size $n \times n$ is invertible if and only if $\operatorname{rank}(A) = n$ .

\- For a system $A\mathbf{x} = \mathbf{b}$ :

- Consistent if $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}])$ .  
- Unique solution if $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}]) = n$ (number of variables).  
- Infinitely many solutions if $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}]) < n$ .  
- Inconsistent if $\operatorname{rank}(A) \neq \operatorname{rank}([A|\mathbf{b}])$ .

# - Common Pitfalls:

- Errors in Gaussian elimination leading to incorrect row echelon form.  
- Misinterpreting the number of non-zero rows.  
- Not considering the augmented matrix for system consistency.

# - Problem-Solving Techniques:

- The most reliable method is to reduce the matrix to row echelon form using Gaussian elimination and count the number of non-zero rows.  
- For smaller matrices, checking determinants of submatrices can be faster.  
- Use the Rank-Nullity Theorem to find nullity if rank is known, or vice versa.

# Singular Value Decomposition (SVD)

Singular Value Decomposition is a powerful matrix factorization technique that decomposes any $m \times n$ matrix A into three matrices: $U, \Sigma$ , and $V^{T}$ . It generalizes the concept of eigenvalues and eigenvectors to non-square matrices and has broad applications in data compression, noise reduction, and recommender systems.

\- Definition: Any $m \times n$ matrix $A$ can be factored as $A = U\Sigma V^T$ , where:

- $U$ is an $m \times m$ orthogonal matrix whose columns are the left singular vectors of $A$ .  
- $\Sigma$ is an $m \times n$ diagonal matrix with non-negative real numbers on the diagonal, called singular values $(\sigma_i)$ , arranged in decreasing order. The non-zero singular values are $\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_r > 0$ , where $r = \text{rank}(A)$ .  
$\circ V$ is an $n \times n$ orthogonal matrix whose columns are the right singular vectors of $A$ . $V^{T}$ is its transpose.

# - Relationship to Eigenvalues:

- The singular values $\sigma_{i}$ of $A$ are the square roots of the eigenvalues of $A^{T}A$ (or $AA^{T}$ ).  
- The columns of $V$ are the eigenvectors of $A^T A$ .  
- The columns of $U$ are the eigenvectors of $AA^T$ .

# • Properties/Applications:

- SVD exists for any matrix (square or rectangular).  
- The number of non-zero singular values is equal to the rank of the matrix.  
- Low-rank approximation: By keeping only the largest singular values and corresponding singular vectors, SVD can approximate a matrix with fewer components, useful for data compression.  
- Pseudo-inverse: The SVD can be used to compute the Moore-Penrose pseudo-inverse of a matrix.  
Principal Component Analysis (PCA): SVD is closely related to PCA, where singular vectors correspond to principal components.

# - Common Pitfalls:

- Confusing singular values with eigenvalues.  
- Incorrectly calculating eigenvectors for $A^T A$ or $AA^T$ .  
- Not arranging singular values in decreasing order.

# - Problem-Solving Techniques:

- Calculate $A^T A$ (or $AA^T$ ).  
- Find the eigenvalues of $A^T A$ . The square roots of these eigenvalues are the singular values $\sigma_i$ .  
- Find the eigenvectors of $A^T A$ . These form the columns of $V$ .  
- Find the eigenvectors of $AA^T$ . These form the columns of $U$ .  
• Alternatively, $U_{i} = \frac{1}{\sigma_{i}} AV_{i}$ .

# Statistics

While a broad field, within the context of linear algebra for GATE CS, statistics primarily involves concepts like mean, variance, covariance, and their matrix representations. These are crucial for understanding data analysis techniques like PCA, which heavily rely on linear algebra.

\- Definition (Linear Algebra Context): Focuses on the mathematical tools (vectors, matrices) used to analyze and model data, particularly in multivariate statistics.

# - Key Concepts:

1. Mean: For a vector $\mathbf{x} = [x_1, \ldots, x_n]^T$ , the mean is $\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i$ .  
2. Variance: A measure of how spread out the data is. For a vector $\mathbf{x}$ , $\operatorname{Var}(\mathbf{x}) = \frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2$ .  
3. Covariance: A measure of how two variables change together. For two vectors x and y,  
4. Covariance Matrix: For a dataset with $p$ variables and $n$ observations, the covariance matrix $\Sigma$ is a $p \times p$ symmetric matrix where $\Sigma_{ij} = \mathrm{Cov}(\mathbf{x}_i, \mathbf{x}_j)$ and $\Sigma_{ii} = \mathrm{Var}(\mathbf{x}_i)$ .

$$
\mathrm{Cov} (\mathbf {x}, \mathbf {y}) = \frac {1}{n - 1} \sum_ {i = 1} ^ {n} (x _ {i} - \bar {x}) (y _ {i} - \bar {y}).
$$

$$
\Sigma = \frac {1}{n - 1} X ^ {T} X
$$

where X is the data matrix with columns centered (mean subtracted).

5. Principal Component Analysis (PCA): A dimensionality reduction technique that uses the eigenvectors of the covariance matrix (or SVD of the data matrix) to find orthogonal directions (principal components) of maximum variance in the data.

# - Properties:

- Covariance matrix is always symmetric and positive semi-definite.  
- Eigenvalues of the covariance matrix represent the variance along the principal components.  
- Eigenvectors of the covariance matrix are the principal components.

# - Common Pitfalls:

- Confusing variance with standard deviation.  
- Incorrectly calculating covariance or covariance matrix.  
- Not centering data before calculating covariance matrix for PCA.

# - Problem-Solving Techniques:

- Understand the definitions of mean, variance, and covariance.  
- For PCA, compute the covariance matrix, then find its eigenvalues and eigenvectors.  
- Relate SVD to PCA: SVD of the centered data matrix directly gives principal components and singular values related to variance.

# Subspace

A subspace is a subset of a vector space that itself satisfies the properties of a vector space. It must contain the zero vector, be closed under vector addition, and closed under scalar multiplication. Subspaces are fundamental building

blocks for understanding the structure of vector spaces.

\- Definition: A subset $W$ of a vector space $V$ is a subspace of $V$ if $W$ is itself a vector space under the operations defined on $V$ .

\- Conditions for a Subspace: A non-empty subset $W$ of a vector space $V$ is a subspace if and only if:

1. The zero vector of $V$ is in $W(\mathbf{0} \in W)$ .  
2. $W$ is closed under vector addition: If $\mathbf{u}, \mathbf{v} \in W$ , then $\mathbf{u} + \mathbf{v} \in W$ .  
3. $W$ is closed under scalar multiplication: If $\mathbf{u} \in W$ and $c$ is any scalar, then $\mathbf{c}\mathbf{u} \in W$ .

\- Important Subspaces Associated with a Matrix $A$ :

- Column Space (Col(A)): The span of the column vectors of $A$ . It is a subspace of $\mathbb{R}^m$ (if $A$ is $m \times n$ ). $\dim(\text{Col}(A)) = \text{rank}(A)$ .  
- Row Space (Row(A)): The span of the row vectors of $A$ . It is a subspace of $\mathbb{R}^n$ . $\dim(\text{Row}(A)) = \text{rank}(A)$ .  
- Null Space (Null(A) or Ker(A)): The set of all vectors $\mathbf{x}$ such that $A\mathbf{x} = \mathbf{0}$ . It is a subspace of $\mathbb{R}^n$ . $\dim(\text{Null}(A)) = \text{nullity}(A)$ .  
- Left Null Space (Null( $A^T$ ): The set of all vectors $\mathbf{y}$ such that $A^T\mathbf{y} = \mathbf{0}$ . It is a subspace of $\mathbb{R}^m$ .

\- Properties:

- The intersection of two subspaces is always a subspace.  
- The union of two subspaces is generally not a subspace.  
- The sum of two subspaces $W_{1} + W_{2} = \{\mathbf{w}_{1} + \mathbf{w}_{2} \mid \mathbf{w}_{1} \in W_{1}, \mathbf{w}_{2} \in W_{2}\}$ is a subspace.

\- Common Pitfalls:

- Forgetting to check all three conditions for a subspace (especially the zero vector).  
- Confusing the column space with the null space.  
- Assuming the union of subspaces is a subspace.

\- Problem-Solving Techniques:

- To check if a set is a subspace, verify the three conditions.  
- To find a basis for the column space, identify the pivot columns of the original matrix after reducing to REF.  
To find a basis for the null space, solve $A\mathbf{x} = \mathbf{0}$ and express the solution in terms of free variables.  
- To find a basis for the row space, use the non-zero rows of the REF of the matrix.

# System of Equations

A system of linear equations is a collection of one or more linear equations involving the same set of variables. Linear algebra provides powerful tools to determine the existence and nature of solutions (unique, infinite, or no solution) for such systems.

\- Definition: A set of equations of the form $a_{11}x_1 + \cdots + a_{1n}x_n = b_1, \ldots, a_{m1}x_1 + \cdots + a_{mn}x_n = b_m$ . This can be written in matrix form as $A\mathbf{x} = \mathbf{b}$ , where $A$ is the coefficient matrix, $\mathbf{x}$ is the vector of variables, and $\mathbf{b}$ is the constant vector.

\- Types of Systems:

Homogeneous System: $Ax = 0$ . Always consistent (has at least the trivial solution $\mathbf{x} = \mathbf{0}$ ).  
• Non-homogeneous System: Ax = b where $b \neq 0$ .

\- Consistency and Number of Solutions (using Rank):

1. Consistent System: A system has at least one solution if $\text{rank}(A) = \text{rank}([A|\mathbf{b}])$ .

- Unique Solution: If $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}]) = n$ (number of variables).  
- Infinitely Many Solutions: If $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}]) < n$ . The number of free variables is $n - \operatorname{rank}(A)$ .

2. Inconsistent System: A system has no solution if $\text{rank}(A) \neq \text{rank}([A|\mathbf{b}])$ .

\- Solution Methods:

- Gaussian Elimination/Row Reduction: Transform the augmented matrix $[A|\mathbf{b}]$ into row echelon form to solve by back-substitution.  
- Matrix Inverse Method: If $A$ is square and invertible, $\mathbf{x} = A^{-1}\mathbf{b}$ . (Only for unique solutions).  
- Cramer's Rule: For a square system with a unique solution, $x_{i} = \frac{\det(A_{i})}{\det(A)}$ , where $A_{i}$ is the matrix formed by replacing the $i$ -th column of $A$ with $\mathbf{b}$ . (Computationally expensive for larger systems).

• Properties of Homogeneous Systems:

- Always has the trivial solution $\mathbf{x} = \mathbf{0}$ .  
- Has non-trivial solutions if and only if $\det(A) = 0$ (for square $A$ ) or $\operatorname{rank}(A) < n$ .  
- The set of all solutions forms the null space of $A$ .

\- Common Pitfalls:

- Arithmetic errors during row operations.  
- Incorrectly determining consistency or number of solutions.

\- Applying Cramer's rule or inverse method when not applicable (e.g., non-square matrix, singular matrix).

# - Problem-Solving Techniques:

- Always form the augmented matrix $[A|\mathbf{b}]$ .  
- Use Gaussian elimination to reduce the augmented matrix to row echelon form.  
- Analyze the rank of $A$ and $[A|\mathbf{b}]$ to determine consistency and number of solutions.  
- For homogeneous systems, look for non-trivial solutions if $\det(A) = 0$ or $\operatorname{rank}(A) < n$ .

# Vector Space

A vector space is a fundamental algebraic structure consisting of a set of vectors, along with two operations: vector addition and scalar multiplication, which satisfy a set of ten axioms. It provides a generalized framework for working with vectors beyond simple geometric arrows.

- Definition: A non-empty set $V$ of objects, called vectors, on which two operations are defined: vector addition (denoted by $+$ ) and scalar multiplication (denoted by juxtaposition), subject to ten axioms. The scalars are typically real numbers ( $\mathbb{R}$ ) or complex numbers ( $\mathbb{C}$ ).  
- Axioms of a Vector Space: For all $\mathbf{u}, \mathbf{v}, \mathbf{w} \in V$ and all scalars $c, d$ :

1. $\mathbf{u} + \mathbf{v} \in V$ (Closure under addition)  
2. $\mathbf{u} + \mathbf{v} = \mathbf{v} + \mathbf{u}$ (Commutativity of addition)  
3. $(\mathbf{u} + \mathbf{v}) + \mathbf{w} = \mathbf{u} + (\mathbf{v} + \mathbf{w})$ (Associativity of addition)  
4. There exists a zero vector $\mathbf{0} \in V$ such that $\mathbf{u} + \mathbf{0} = \mathbf{u}$ (Additive identity)  
5. For each $\mathbf{u} \in V$ , there exists an additive inverse $-\mathbf{u} \in V$ such that $\mathbf{u} + (-\mathbf{u}) = \mathbf{0}$ (Additive inverse)  
6. $\mathbf{c}\mathbf{u} \in V$ (Closure under scalar multiplication)  
7. $c(\mathbf{u} + \mathbf{v}) = c\mathbf{u} + c\mathbf{v}$ (Distributivity of scalar over vector addition)  
8. $(c + d)\mathbf{u} = c\mathbf{u} + d\mathbf{u}$ (Distributivity of scalar over scalar addition)  
9. $c(d\mathbf{u}) = (cd)\mathbf{u}$ (Associativity of scalar multiplication)  
10. 1u = u (Multiplicative identity)

# - Key Concepts:

- Span: The set of all possible linear combinations of a set of vectors $\{\mathbf{v}_1, \ldots, \mathbf{v}_k\}$ . Denoted as $\operatorname{span}\{\mathbf{v}_1, \ldots, \mathbf{v}_k\}$ . It is always a subspace.  
- Linear Independence: A set of vectors $\{\mathbf{v}_1, \ldots, \mathbf{v}_k\}$ is linearly independent if the only solution to $c_1\mathbf{v}_1 + \cdots + c_k\mathbf{v}_k = \mathbf{0}$ is $c_1 = \cdots = c_k = 0$ .  
- Basis: A set of vectors in a vector space $V$ that is linearly independent and spans $V$ . The number of vectors in a basis is unique and is called the dimension of the vector space.  
Dimension: The number of vectors in any basis for a vector space $V$ , denoted as $\dim(V)$ .

# • Examples of Vector Spaces:

- $\mathbb{R}^n$ (n-dimensional real coordinate space)  
- The set of all $m \times n$ matrices.  
- The set of all polynomials of degree at most $n$ .  
- The set of all continuous functions on an interval.

# - Common Pitfalls:

- Forgetting to check all axioms when verifying if a set is a vector space.  
- Confusing a vector space with a subspace.  
- Incorrectly determining linear independence or a basis.

# - Problem-Solving Techniques:

- To check if a set is a vector space, verify all ten axioms.  
To check linear independence, set up the equation $c_{1}v_{1}+\cdots+c_{k}v_{k}=0$ and solve the resulting system of linear equations.  
To find a basis, identify a linearly independent set that spans the space. For $\mathbb{R}^n$ , this often involves finding pivot columns of a matrix formed by the vectors.

# Quick Formula Reference

# - Determinant:

$$
\circ 2 \times 2: | A | = a d - b c \text {for} A = \left( \begin{array}{c c} a & b \\ c & d \end{array} \right)
$$

- Properties: $|A^T| = |A|$ , $|AB| = |A||B|$ , $|kA| = k^n |A|$ , $|A^{-1}| = 1 / |A|$  
• Invertible iff |A| ≠ 0

# - Matrix Operations:

\- Matrix Multiplication: $(AB)_{ij} = \sum_{k} A_{ik} B_{kj}$

- Inverse $2 \times 2$ : $A^{-1} = \frac{1}{ad - bc} \left( \begin{array}{cc}d & -b\\ -c & a \end{array} \right)$  
- General Inverse: $A^{-1} = \frac{1}{\det(A)} \operatorname{adj}(A)$  
- Transpose Properties: $(A + \overset{\cdot}{B})^T = A^T + B^T$ , $(AB)^T = B^T A^T$  
- Inverse Properties: $(A^{-1})^{-1} = A, (AB)^{-1} = B^{-1}A^{-1}$

# • Eigenvalues & Eigenvectors:

- Characteristic Equation: $\det(A - \lambda I) = 0$  
- Sum of Eigenvalues: $\sum \lambda_{i} = \text{trace}(A)$  
- Product of Eigenvalues: $\prod \lambda_i = \det(A)$  
- Cayley-Hamilton Theorem: $P(A) = 0$ where $P(\lambda)$ is the characteristic polynomial.  
○ Algebraic Multiplicity (AM): Number of times $\lambda$ is a root.  
- Geometric Multiplicity (GM): $\dim(\text{Null}(A - \lambda I)) = n - \text{rank}(A - \lambda I)$  
- Diagonalizable if $\mathrm{AM}(\lambda) = \mathrm{GM}(\lambda)$ for all $\lambda$ .

# - Rank of Matrix:

- Number of non-zero rows in REF.  
- $\operatorname{rank}(A) \leq \min(m, n)$ for $m \times n$ matrix.  
- Rank-Nullity Theorem: $\operatorname{rank}(A) + \operatorname{nullity}(A) = n$ (number of columns).  
- System $A\mathbf{x} = \mathbf{b}$ consistent if $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}])$ .  
- Unique solution if $\operatorname{rank}(A) = \operatorname{rank}([A|\mathbf{b}]) = n$ .  
• Infinite solutions if $\text{rank}(A) = \text{rank}([A|\mathbf{b}]) < n$ .  
- No solution if $\operatorname{rank}(A) \neq \operatorname{rank}([A|\mathbf{b}])$ .

# - LU Decomposition:

$\circ A = L\bar{U}$ (or $PA = L\bar{U}$ with permutation matrix $P$ )  
- Solve $A\mathbf{x} = \mathbf{b}$ by $L\mathbf{y} = \mathbf{b}$ (forward substitution) then $U\mathbf{x} = \mathbf{y}$ (backward substitution).

# - Orthonormality:

- Orthogonal: $\mathbf{u} \cdot \mathbf{v} = 0$  
- Normalized: ||u|| = 1  
- Orthonormal: $\mathbf{u}_i \cdot \mathbf{u}_j = \delta_{ij}$  
○ Orthogonal Matrix $Q: Q^{T}Q = I \implies Q^{-1} = Q^{T}$ .

# - Singular Value Decomposition (SVD):

$\circ A = U\Sigma V^{T}$  
- Singular values $\sigma_{i}$ are $\sqrt{\lambda_{i}(A^{T}A)}$ .  
- Columns of $V$ are eigenvectors of $A^T A$ .  
- Columns of $U$ are eigenvectors of $AA^T$ .

# - Subspace Conditions:

- Contains zero vector.  
- Closed under addition.  
- Closed under scalar multiplication.

# Important Tips for GATE

1. Master the Basics: Ensure a strong understanding of fundamental definitions (e.g., matrix types, vector space axioms, linear independence). Many conceptual questions test these directly.  
2. Practice Gaussian Elimination: This is a core algorithm. Practice it diligently for solving systems, finding rank, and computing inverses. Accuracy and speed are crucial here.  
3. Understand Eigenvalue/Eigenvector Properties: Don't just memorize formulas. Understand \*why\* the sum of eigenvalues equals the trace and the product equals the determinant. These properties are often used as shortcuts or for verification.  
4. Pay Attention to Matrix Dimensions: Always check if matrix operations (addition, multiplication) are valid based on dimensions. This prevents common errors, especially in matrix multiplication.  
5. Rank-Nullity Theorem is Your Friend: This theorem is incredibly useful for quickly finding the nullity if the rank is known, or vice versa, and for analyzing the nature of solutions to linear systems.  
6. Beware of Calculation Errors: Linear algebra problems often involve extensive calculations. Use the virtual calculator carefully and double-check intermediate steps. Simple arithmetic mistakes are a common reason for losing marks.  
7. Distinguish Between Similar Concepts: Clearly differentiate between algebraic and geometric multiplicity, orthogonal and orthonormal vectors, and the various matrix subspaces (column space, null space, row space).  
8. Practice Previous Year Questions: Solve as many GATE previous year questions as possible. This will familiarize

you with the typical question patterns, difficulty levels, and time constraints. Focus on understanding the solution approach rather than just getting the answer.

# 6.1

# Cartesian Coordinates (1)

# 6.1.1 Cartesian Coordinates: GATE IT 2007 | Question: 80


Let $P_{1}, P_{2}, \ldots, P_{n}$ be n points in the xy-plane such that no three of them are collinear. For every pair of points $P_{i}$ and $P_{j}$ , let $L_{ij}$ be the line passing through them. Let $L_{ab}$ be the line with the steepest gradient amongst all $\frac{n(n-1)}{2}$ lines.

Which one of the following properties should necessarily be satisfied?

A. $P_{a}$ and $P_{b}$ are adjacent to each other with respect to their $x$ -coordinate  
B. Either $P_{a}$ or $P_{b}$ has the largest or the smallest $y$ -coordinate among all the points  
C. The difference between $x$ -coordinates $P_{a}$ and $P_{b}$ is minimum  
D. None of the above

gateit-2007 linear-algebra cartesian-coordinates

Answer key

# 6.2

# Determinant (12)

Practice Tests: Test 1 (15Q) Test 2 (4Q)

# 6.2.1 Determinant: GATE CSE 1997 | Question: 1.3

The determinant of the matrix $\begin{bmatrix} 6 & -8 & 1 & 1 \\ 0 & 2 & 4 & 6 \\ 0 & 0 & 4 & 8 \\ 0 & 0 & 0 & -1 \end{bmatrix}$

A. 11

B. -48

C. 0

D. -24

gate1997 linear-algebra normal determinant

Answer key

# 6.2.2 Determinant: GATE CSE 2000 | Question: 1.3

The determinant of the matrix

$$
\left[ \begin{array}{c c c c} 2 & 0 & 0 & 0 \\ 8 & 1 & 7 & 2 \\ 2 & 0 & 2 & 0 \\ 9 & 0 & 6 & 1 \end{array} \right]
$$

A. 4

B. 0

C. 15

D. 20

gatecse-2000 linear-algebra easy determinant

Answer key

# 6.2.3 Determinant: GATE CSE 2013 | Question: 3

Which one of the following does NOT equal

$$
\left| \begin{array}{ccc} 1 & x & x ^ {2} \\ 1 & y & y ^ {2} \\ 1 & z & z ^ {2} \end{array} \right| \quad ?
$$




$$
\begin{array}{c c c} \text {A.} & \left| \begin{array}{c c c} 1 & x (x + 1) & x + 1 \\ 1 & y (y + 1) & y + 1 \\ 1 & z (z + 1) & z + 1 \end{array} \right| \\ \text {C.} & \left| \begin{array}{c c c} 0 & x - y & x ^ {2} - y ^ {2} \\ 0 & y - z & y ^ {2} - z ^ {2} \\ 1 & z & z ^ {2} \end{array} \right| \end{array}
$$

gatecse-2013 linear-algebra normal determinant

$$
\begin{array}{l} \text {B.} \left| \begin{array}{c c c} 1 & x + 1 & x ^ {2} + 1 \\ 1 & y + 1 & y ^ {2} + 1 \\ 1 & z + 1 & z ^ {2} + 1 \end{array} \right| \\ \text {D.} \left| \begin{array}{c c c} 2 & x + y & x ^ {2} + y ^ {2} \\ 2 & y + z & y ^ {2} + z ^ {2} \\ 1 & z & z ^ {2} \end{array} \right| \\ \end{array}
$$

# Answer key

# 6.2.4 Determinant: GATE CSE 2014 | Set 2 | Question: 4

If the matrix $A$ is such that


$$
A = \left[ \begin{array}{c} 2 \\ - 4 \\ 7 \end{array} \right] \left[ \begin{array}{c c c} 1 & 9 & 5 \end{array} \right]
$$

then the determinant of $A$ is equal to \_\_\_\_.

gatecse-2014-set2 linear-algebra numerical-answers easy determinant

# Answer key

# 6.2.5 Determinant: GATE CSE 2019 | Question: 9

Let $X$ be a square matrix. Consider the following two statements on $X$ .

I. $X$ is invertible  
II. Determinant of $X$ is non-zero

Which one of the following is TRUE?

A. I implies II; II does not imply I  
C. I does not imply II; II does not imply I

B. II implies I; I does not imply II  
D. I and II are equivalent statements

gatecse-2019 engineering-mathematics linear-algebra determinant one-mark

# Answer key

# 6.2.6 Determinant: GATE CSE 2023 | Question: 8

Let


$$
A = \left[ \begin{array}{c c c c} 1 & 2 & 3 & 4 \\ 4 & 1 & 2 & 3 \\ 3 & 4 & 1 & 2 \\ 2 & 3 & 4 & 1 \end{array} \right]
$$

and


$$
B = \left[ \begin{array}{c c c c} 3 & 4 & 1 & 2 \\ 4 & 1 & 2 & 3 \\ 1 & 2 & 3 & 4 \\ 2 & 3 & 4 & 1 \end{array} \right]
$$

Let $\det(A)$ and $\det(B)$ denote the determinants of the matrices $A$ and $B$ , respectively.

Which one of the options given below is TRUE?

A. $\det(A)=\det(B)$

B. $\det(B) = -\det(A)$  
C. $\det(A)=0$  
D. $\det(AB)=\det(A)+\det(B)$

gatecse-2023 linear-algebra determinant one-mark easy

# Answer key

# 6.2.7 Determinant: GATE CSE 2024 | Set 2 | Question: 37

Let $A$ be an $n \times n$ matrix over the set of all real numbers $\mathbb{R}$ . Let $B$ be a matrix obtained from $A$ by swapping two rows. Which of the following statements is/are TRUE?


A. The determinant of B is the negative of the determinant of A  
B. If $A$ is invertible, then $B$ is also invertible  
C. If $A$ is symmetric, then $B$ is also symmetric  
D. If the trace of $A$ is zero, then the trace of $B$ is also zero

gatecse-2024-set2 linear-algebra multiple-selects matrix determinant two-marks

# Answer key

# 6.2.8 Determinant: GATE CSE 2025 | Set 2 | Question: 4

Let $L, M$ , and $N$ be non-singular matrices of order 3 satisfying the equations $L^2 = L^{-1}$ , $M = L^8$ and $N = L^2$ .


Which ONE of the following is the value of the determinant of $(M - N)$ ?

A. 0

B. 1

C. 2

D. 3

gatecse2025-set2 linear-algebra determinant easy one-mark

# Answer key

# 6.2.9 Determinant: GATE CSE 2026 | Set 2 | Question: 52

The determinant of a $4 \times 4$ matrix $A$ is 3. The value of the determinant of $2A$ is \_\_\_\_. (answer in integer)


gatecse-2026-set2 linear-algebra determinant numerical-answers two-marks

# Answer key

# 6.2.10 Determinant: GATE DS&AI 2024 | Question: 25

Consider the $3 \times 3$ matrix $\boldsymbol{M} = \begin{bmatrix} 1 & 2 & 3 \\ 3 & 1 & 3 \\ 4 & 3 & 6 \end{bmatrix}$ .

The determinant of $(M^{2}+12M)$ is \_\_\_\_.

gate-ds-ai-2024 numerical-answers matrix determinant linear-algebra easy one-mark

# Answer key

# 6.2.11 Determinant: GATE IT 2004 | Question: 32

Let $A$ be an $n \times n$ matrix of the following form.



$$
A = \left[ \begin{array}{c c c c c c c c c} 3 & 1 & 0 & 0 & 0 & \dots & 0 & 0 & 0 \\ 1 & 3 & 1 & 0 & 0 & \dots & 0 & 0 & 0 \\ 0 & 1 & 3 & 1 & 0 & \dots & 0 & 0 & 0 \\ 0 & 0 & 1 & 3 & 1 & \dots & 0 & 0 & 0 \\ \dots & & & & & \\ \dots & & & & & \\ 0 & 0 & 0 & 0 & 0 & \dots & 1 & 3 & 1 \\ 0 & 0 & 0 & 0 & 0 & \dots & 0 & 1 & 3 \end{array} \right] _ {n \times n}
$$

What is the value of the determinant of A?

A. $\left(\frac{5 + \sqrt{3}}{2}\right)^{n - 1}\left(\frac{5\sqrt{3} + 7}{2\sqrt{3}}\right) + \left(\frac{5 - \sqrt{3}}{2}\right)^{n - 1}\left(\frac{5\sqrt{3} - 7}{2\sqrt{3}}\right)$  
B. $\left(\frac{7 + \sqrt{5}}{2}\right)^{n - 1}\left(\frac{7\sqrt{5} + 3}{2\sqrt{5}}\right) + \left(\frac{7 - \sqrt{5}}{2}\right)^{n - 1}\left(\frac{7\sqrt{5} - 3}{2\sqrt{5}}\right)$  
C. $\left(\frac{3 + \sqrt{7}}{2}\right)^{n - 1}\left(\frac{3\sqrt{7} + 5}{2\sqrt{7}}\right) + \left(\frac{3 - \sqrt{7}}{2}\right)^{n - 1}\left(\frac{3\sqrt{7} - 5}{2\sqrt{7}}\right)$  
D. $\left(\frac{3 + \sqrt{5}}{2}\right)^{n - 1}\left(\frac{3\sqrt{5} + 7}{2\sqrt{5}}\right) + \left(\frac{3 - \sqrt{5}}{2}\right)^{n - 1}\left(\frac{3\sqrt{5} - 7}{2\sqrt{5}}\right)$

gateit-2004 linear-algebra matrix normal determinant

Answer key

# 6.2.12 Determinant: GATE IT 2005 | Question: 3

The determinant of the matrix given below is

$$
\left[ \begin{array}{c c c c} 0 & 1 & 0 & 2 \\ - 1 & 1 & 1 & 3 \\ 0 & 0 & 0 & 1 \\ 1 & - 2 & 0 & 1 \end{array} \right]
$$

A. -1

B. 0

C. 1

D. 2

gateit-2005 linear-algebra normal determinant

Answer key

6.3

Eigen Value (33)

Practice Tests:

Test 1 (15Q)

Test 2 (15Q)

Test 3 (15Q)

Test 4 (13Q)

# 6.3.1 Eigen Value: GATE CSE 1993 | Question: 01.1

The eigen vector $(s)$ of the matrix

$$
\left[ \begin{array}{c c c} 0 & 0 & \alpha \\ 0 & 0 & 0 \\ 0 & 0 & 0 \end{array} \right], \alpha \neq 0
$$

is (are)

A. $(0,0,\alpha)$

B. $(\alpha,0,0)$

c. $(0,0,1)$

D. $(0,\alpha,0)$

gate1993 eigen-value linear-algebra easy multiple-selects

Answer key



# 6.3.2 Eigen Value: GATE CSE 2002 | Question: 5a

Obtain the eigen values of the matrix

$$
A = \left[ \begin{array}{c c c c} 1 & 2 & 3 4 & 4 9 \\ 0 & 2 & 4 3 & 9 4 \\ 0 & 0 & - 2 & 1 0 4 \\ 0 & 0 & 0 & - 1 \end{array} \right]
$$

gatecse-2002 linear-algebra eigen-value normal descriptive

# Answer key

# 6.3.3 Eigen Value: GATE CSE 2005 | Question: 49

What are the eigenvalues of the following $2 \times 2$ matrix?

$$
\left( \begin{array}{c c} 2 & - 1 \\ - 4 & 5 \end{array} \right)
$$

A. -1 and 1

B. 1 and 6

C. 2 and 5

D. 4 and -1

gatecse-2005 linear-algebra eigen-value easy

# Answer key

# 6.3.4 Eigen Value: GATE CSE 2007 | Question: 25

Let $A$ be a $4 \times 4$ matrix with eigen values -5,-2,1,4. Which of the following is an eigen value of the matrix $\begin{bmatrix} A & I \\ I & A \end{bmatrix}$ , where $I$ is the $4 \times 4$ identity matrix?


A. -5

B. -7

C. 2

D. 1

gatecse-2007 eigen-value linear-algebra difficult

# Answer key

# 6.3.5 Eigen Value: GATE CSE 2008 | Question: 28

How many of the following matrices have an eigenvalue 1?

$$
\left[ \begin{array}{c c} 1 & 0 \\ 0 & 0 \end{array} \right] \left[ \begin{array}{c c} 0 & 1 \\ 0 & 0 \end{array} \right] \left[ \begin{array}{c c} 1 & - 1 \\ 1 & 1 \end{array} \right] \text {and} \left[ \begin{array}{c c} - 1 & 0 \\ 1 & - 1 \end{array} \right]
$$

A. one

B. two

C. three

D. four

gatecse-2008 eigen-value linear-algebra easy

# Answer key

# 6.3.6 Eigen Value: GATE CSE 2010 | Question: 29

Consider the following matrix

$$
A = \left[ \begin{array}{c c} 2 & 3 \\ x & y \end{array} \right]
$$

If the eigenvalues of A are 4 and 8, then

A. x = 4, y = 10

B. $x = 5, y = 8$

C. $x = 3, y = 9$

D. $x = -4, y = 10$

gatecse-2010 linear-algebra eigen-value easy

# Answer key



# 6.3.7 Eigen Value: GATE CSE 2011 | Question: 40

Consider the matrix as given below.


$$
\left[ \begin{array}{c c c} 1 & 2 & 3 \\ 0 & 4 & 7 \\ 0 & 0 & 3 \end{array} \right]
$$

Which one of the following options provides the CORRECT values of the eigenvalues of the matrix?

A. 1,4,3

B. 3,7,3

C. 7,3,2

D. 1,2,3

gatecse-2011 linear-algebra eigen-value easy

# Answer key

# 6.3.8 Eigen Value: GATE CSE 2012 | Question: 11

Let $A$ be the $2 \times 2$ matrix with elements $a_{11} = a_{12} = a_{21} = +1$ and $a_{22} = -1$ . Then the eigenvalues of the matrix $A^{19}$ are


A. 1024 and -1024

B. $1024\sqrt{2}$ and $-1024\sqrt{2}$

C. $4\sqrt{2}$ and $-4\sqrt{2}$

D. $512\sqrt{2}$ and $-512\sqrt{2}$

gatecse-2012 linear-algebra eigen-value easy

# Answer key

# 6.3.9 Eigen Value: GATE CSE 2014 | Set 1 | Question: 5

The value of the dot product of the eigenvectors corresponding to any pair of different eigenvalues of a $4 - by - 4$ symmetric positive definite matrix is \_\_\_\_


gatecse-2014-set1 linear-algebra eigen-value numerical-answers normal

# Answer key

# 6.3.10 Eigen Value: GATE CSE 2014 | Set 2 | Question: 47

The product of the non-zero eigenvalues of the matrix is \_\_\_\_


$$
\left( \begin{array}{c c c c c} 1 & 0 & 0 & 0 & 1 \\ 0 & 1 & 1 & 1 & 0 \\ 0 & 1 & 1 & 1 & 0 \\ 0 & 1 & 1 & 1 & 0 \\ 1 & 0 & 0 & 0 & 1 \end{array} \right)
$$

gatecse-2014-set2 linear-algebra eigen-value normal numerical-answers

# Answer key

# 6.3.11 Eigen Value: GATE CSE 2014 | Set 3 | Question: 4

Which one of the following statements is TRUE about every $n \times n$ matrix with only real eigenvalues?


A. If the trace of the matrix is positive and the determinant of the matrix is negative, at least one of its eigenvalues is negative.  
B. If the trace of the matrix is positive, all its eigenvalues are positive.  
C. If the determinant of the matrix is positive, all its eigenvalues are positive.  
D. If the product of the trace and determinant of the matrix is positive, all its eigenvalues are positive.

gatecse-2014-set3 linear-algebra eigen-value normal

# Answer key

# 6.3.12 Eigen Value: GATE CSE 2015 | Set 1 | Question: 36


Consider the following $2 \times 2$ matrix $A$ where two elements are unknown and are marked by $a$ and $b$ . The eigenvalues of this matrix are -1 and 7. What are the values of $a$ and $b$ ?

$$
A = \left( \begin{array}{c c} 1 & 4 \\ b & a \end{array} \right)
$$

A. $a = 6, b = 4$

B. $a = 4, b = 6$

C. $a = 3, b = 5$

D. $a = 5, b = 3$

gatecse-2015-set1 linear-algebra eigen-value easy

# Answer key

# 6.3.13 Eigen Value: GATE CSE 2015 | Set 2 | Question: 5


The larger of the two eigenvalues of the matrix $\begin{bmatrix}4 & 5 \\ 2 & 1\end{bmatrix}$ is \_\_\_\_.

gatecse-2015-set2 linear-algebra eigen-value easy numerical-answers

# Answer key

# 6.3.14 Eigen Value: GATE CSE 2015 | Set 3 | Question: 15


In the given matrix $\begin{bmatrix}1 & -1 & 2 \\ 0 & 1 & 0 \\ 1 & 2 & 1\end{bmatrix}$ , one of the eigenvalues is 1. The eigenvectors corresponding to the eigenvalue 1 are

A. $\{a(4,2,1) \mid a \neq 0, a \in \mathbb{R}\}$  
B. $\{a(-4,2,1) \mid a \neq 0, a \in \mathbb{R}\}$  
C. $\{a(\sqrt{2},0,1)\mid a\neq 0,a\in \mathbb{R}\}$  
D. $\{a(-\sqrt{2},0,1) \mid a \neq 0, a \in \mathbb{R}\}$

gatecse-2015-set3 linear-algebra eigen-value normal

# Answer key

# 6.3.15 Eigen Value: GATE CSE 2016 | Set 1 | Question: 05


Two eigenvalues of a $3 \times 3$ real matrix $P$ are $(2 + \sqrt{-1})$ and 3. The determinant of $P$ is \_\_\_\_

gatecse-2016-set1 linear-algebra eigen-value numerical-answers normal

# Answer key

# 6.3.16 Eigen Value: GATE CSE 2016 | Set 2 | Question: 06


Suppose that the eigenvalues of matrix $A$ are 1, 2, 4. The determinant of $(A^{-1})^T$ is \_\_\_\_.

gatecse-2016-set2 linear-algebra eigen-value normal numerical-answers

# Answer key

# 6.3.17 Eigen Value: GATE CSE 2017 | Set 1 | Question: 31


Let $A$ be $n \times n$ real valued square symmetric matrix of rank 2 with $\sum_{i=1}^{n} \sum_{j=1}^{n} A_{ij}^{2} = 50$ . Consider the following statements.

I. One eigenvalue must be in $[-5,5]$  
II. The eigenvalue with the largest magnitude must be strictly greater than 5

Which of the above statements about eigenvalues of A is/are necessarily CORRECT?

A. Both I and II

B. I only

C. II only

D. Neither I nor II