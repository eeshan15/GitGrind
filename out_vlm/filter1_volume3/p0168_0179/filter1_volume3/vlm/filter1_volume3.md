# Formulas/Theorems:

\- Precedence Graph (Serialization Graph):

- Nodes represent transactions.  
- An edge $T_{i} \rightarrow T_{j}$ exists if $T_{i}$ performs an operation that conflicts with an operation of $T_{j}$ , and $T_{i}$ 's operation occurs before $T_{j}$ 's.

\- Theorem: A schedule is conflict serializable if and only if its precedence graph contains no cycles.

# Key Properties/Identities:

• Guarantees that the concurrent execution produces the same result as some sequential execution.

\- A weaker condition than view serializability but easier to test.

# Common Pitfalls:

- Incorrectly identifying conflicting operations (e.g., R-R operations do not conflict).  
- Missing cycles in the precedence graph, especially in complex schedules.

# Problem-Solving Techniques:

- Construct the precedence graph by identifying all conflicting pairs of operations and drawing edges accordingly.  
- Use a cycle detection algorithm (e.g., DFS) on the graph to check for serializability.

# Database Design

Database design is the process of creating a detailed data model for a database. It involves translating conceptual requirements into a logical schema, and then into a physical schema, ensuring data integrity, efficiency, and scalability.

# Formulas/Theorems:

\- No direct formulas, but relies on principles of normalization and ER-to-Relational mapping rules.

# Key Properties/Identities:

- Phases: Conceptual (ER Model), Logical (Relational Schema), Physical (Storage details).  
- Goals: Minimize redundancy, maximize integrity, optimize performance.

# Common Pitfalls:

- Poor choice of primary/foreign keys.  
- Not adequately normalizing the schema, leading to update anomalies.  
• Over-normalization, leading to complex queries and performance issues.

# Problem-Solving Techniques:

- Start with an ER diagram to capture requirements.  
- Apply ER-to-Relational mapping rules systematically.  
- Normalize relations to an appropriate normal form (e.g., BCNF or 3NF) using functional dependencies.

# Database Normalization

Database Normalization is a systematic process of restructuring a relational database schema to minimize data redundancy and improve data integrity. It involves decomposing relations into smaller, well-structured relations based on functional dependencies.

# Formulas/Theorems:

- 1NF (First Normal Form): All attributes must be atomic (no multi-valued or composite attributes).  
- 2NF (Second Normal Form): In 1NF and no non-prime attribute is partially dependent on a candidate key.  
- 3NF (Third Normal Form): In 2NF and no non-prime attribute is transitively dependent on a candidate key.

- BCNF (Boyce-Codd Normal Form): For every non-trivial functional dependency $A \rightarrow B$ , $A$ must be a super key.  
• 4NF (Fourth Normal Form): In BCNF and no non-trivial multi-valued dependencies exist.  
- 5NF (Fifth Normal Form): In 4NF and no non-trivial join dependencies exist.

# Key Properties/Identities:

- Hierarchy: $1NF \subset 2NF \subset 3NF \subset BCNF \subset 4NF \subset 5NF$ .  
- Desirable properties of decomposition: Lossless Join and Dependency Preservation. BCNF decomposition is always lossless but not always dependency preserving. 3NF decomposition is always lossless and dependency preserving.

# Common Pitfalls:

- Incorrectly identifying prime and non-prime attributes.  
- Mistaking partial dependency for transitive dependency.  
- Failing to check for both lossless join and dependency preservation after decomposition.

# Problem-Solving Techniques:

- Identify all candidate keys and functional dependencies.  
- Systematically check for violations of each normal form.  
- If a violation exists, decompose the relation into smaller relations.

# Database Schema

A Database Schema is the logical structure or design of the entire database. It defines the tables, attributes, data types, relationships, and constraints that govern the data within the database. It is defined using Data Definition Language (DDL).

# Formulas/Theorems:

\- No specific formulas, but it's the blueprint for the database.

# Key Properties/Identities:

- Internal Schema: Physical storage structure.  
- Conceptual Schema: Logical structure of the entire database.  
- External Schema (View): User-specific views of the database.  
- Schema defines the intension, while data (instance) defines the extension.

# Common Pitfalls:

- Confusing schema (structure) with database instance (actual data).  
• Overlooking important constraints during schema design.

# Problem-Solving Techniques:

- Understand the mapping from ER diagrams to relational schemas.  
- Be familiar with DDL commands like CREATE TABLE, ALTER TABLE, DROP TABLE.

# Decomposition

Decomposition is the process of breaking down a relation (table) into two or more smaller relations. It is primarily used in normalization to eliminate redundancy and anomalies, ensuring that the resulting relations are in a higher normal form.

# Formulas/Theorems:

- Lossless Join Decomposition: A decomposition of $R$ into $R_1$ and $R_2$ is lossless if $R = R_1 \bowtie R_2$ .  
• Condition: $(R_{1} \cap R_{2}) \rightarrow R_{1}$ or $(R_{1} \cap R_{2}) \rightarrow R_{2}$ must hold based on the FDs of R.

\- Dependency Preservation: A decomposition preserves dependencies if the union of FDs on the decomposed

relations is equivalent to the original set of FDs. Formally, if F is the original set of FDs and $F_{i}$ is the set of FDs on $R_{i}$ , then $(F_{1} \cup F_{2} \cup \cdots \cup F_{k})^{+} = F^{+}$ .

# Key Properties/Identities:

- Desirable properties for decomposition are lossless join and dependency preservation.  
- BCNF decomposition is always lossless but not always dependency preserving.  
- 3NF decomposition is always lossless and dependency preserving.

# Common Pitfalls:

- Incorrectly applying the lossless join test.  
- Failing to check for dependency preservation, especially for BCNF.

# Problem-Solving Techniques:

- For lossless join: Check if the common attributes form a super key for at least one of the decomposed relations.  
- For dependency preservation: For each original FD $A \rightarrow B$ , check if it can be derived from the FDs of the decomposed relations.

# ER Diagram

An Entity-Relationship (ER) Diagram is a high-level conceptual data model that represents the entities, attributes, and relationships within a system. It is used during the conceptual design phase of database development.

# Formulas/Theorems:

\- No direct formulas, but specific rules for mapping to relational schema.

# Key Properties/Identities:

- Entities: Represented by rectangles (e.g., Student, Course).  
- Attributes: Represented by ovals (e.g., Name, ID). Key attributes are underlined.  
- Relationships: Represented by diamonds (e.g., Enrolls, Teaches).  
- Cardinality: (1:1, 1:N, M:N) specifies the number of instances of one entity that can be associated with another.  
- Participation: (Total/Partial) specifies whether an entity instance must participate in a relationship.  
- Weak Entity: An entity that cannot be uniquely identified by its own attributes and depends on a strong (owner) entity. Represented by double rectangles.

# Common Pitfalls:

- Incorrectly identifying cardinalities or participation constraints.  
- Confusing strong and weak entities.  
- Errors in mapping complex ER constructs (e.g., ternary relationships, generalization) to relational schema.

# Problem-Solving Techniques:

- Carefully read the problem description to identify entities, attributes, and relationships.  
- Pay close attention to cardinality and participation rules.  
- Practice mapping ER diagrams to relational schemas using standard rules.

# Functional Dependency

A Functional Dependency (FD) $A \rightarrow B$ means that the value of attribute set A uniquely determines the value of attribute set B. If two tuples have the same values for attributes in A, they must also have the same values for attributes in B.

# Formulas/Theorems:

\- Closure of an attribute set $X^{+}$ : The set of all attributes that are functionally determined by $X$ .

○ Algorithm: Start with $X^{+} = X$ . Repeatedly add attributes $Y$ to $X^{+}$ if there is an FD $W \to Y$ such that $W \subset X^{+}$ .

\- Minimal Cover (or Minimal Basis): A set of FDs $F_{m}$ equivalent to $F$ such that:

1. Every FD in $F_{m}$ has a single attribute on the right-hand side.  
2. No FD in $F_{m}$ can be removed without changing $F_{m}^{+}$ .  
3. No attribute can be removed from the left-hand side of any FD in $F_{m}$ without changing $F_{m}^{+}$ .

# Key Properties/Identities:

- Fundamental for database normalization and identifying keys.  
• Armstrong's Axioms are used to infer FDs.

# Common Pitfalls:

- Incorrectly calculating attribute closure.  
- Errors in finding a minimal cover.

# Problem-Solving Techniques:

- Master the algorithm for finding $X^{+}$ .  
- For minimal cover, systematically apply the three conditions: right-hand side single attribute, remove redundant FDs, remove redundant attributes from LHS.

# Indexing

Indexing is a technique used to optimize the performance of database queries by allowing the database server to quickly locate and retrieve specific rows without scanning the entire table. It creates a data structure (like B-tree or hash table) that stores a small, ordered subset of the data.

# Formulas/Theorems:

- Disk I/O for B-tree index: For a search, typically height of tree + 1 (for data block) disk accesses.  
- Disk I/O for hash index: Typically 1-2 disk accesses for exact match, if no collision.

# Key Properties/Identities:

- Primary Index: Index on the primary key, usually clustered.  
- Secondary Index: Index on non-key attributes, usually unclustered.  
- Clustered Index: Data rows are stored physically in the order of the index key. Only one per table.  
- Unclustered Index: Index stores pointers to the data rows, which are not physically ordered by the index key.

# Common Pitfalls:

- Misunderstanding the difference between clustered and unclustered indexes.  
- Incorrectly calculating disk I/Os for different index types and query patterns.

# Problem-Solving Techniques:

- Analyze the query type (equality search, range search) and index type to determine disk I/O.  
- Remember that clustered indexes can retrieve multiple data records with fewer I/Os for range queries.

# Joins

Joins combine rows from two or more tables based on a related column between them. They are fundamental operations in relational algebra and SQL for retrieving data from multiple relations.

# Formulas/Theorems:

\- Cartesian Product (Cross Join): $R \times S$ . Combines every row of $R$ with every row of $S$ . If $R$ has $n$ tuples and $S$

has $m$ tuples, $R \times S$ has $n \times m$ tuples.

- Theta Join: $R \bowtie_{\theta} S = \sigma_{\theta}(R \times S)$ . Combines tuples from $R$ and $S$ where the condition $\theta$ is true.  
- Equijoin: A theta join where $\theta$ is an equality condition (e.g., $R$ . $A = S$ . $B$ ).  
- Natural Join: $R \bowtie S$ . An equijoin on all common attributes, with duplicate common columns removed from the result.  
- Outer Joins (Left, Right, Full): Preserve tuples that do not have a match in the other relation, filling unmatched attributes with NULLs.

# Key Properties/Identities:

- Result schema of a join is the union of attributes from participating relations (with common attributes appearing once in natural join).  
- Join operations are associative and commutative (for inner joins).

# Common Pitfalls:

- Confusing different types of joins, especially natural join vs. equijoin.  
- Misunderstanding how NULL values are handled in outer joins.  
- Incorrectly calculating the number of tuples in the result.

# Problem-Solving Techniques:

- For natural join, identify common attributes and their values.  
- For outer joins, remember to include unmatched tuples from the specified side(s).  
- Trace the operation step-by-step for small example relations.

# Multivalued Dependency 4NF

A Multivalued Dependency (MVD) $A \rightarrow B$ exists in a relation R if, for a given value of A, there is a set of values for B, and this set is independent of the values of other attributes in R. 4NF (Fourth Normal Form) requires that for every non-trivial MVD $A \rightarrow B$ in a relation, A must be a super key.

# Formulas/Theorems:

- Trivial MVD: $A \twoheadrightarrow B$ is trivial if $B \subseteq A$ or $A \cup B = R$ .  
- MVD Inference Rules (some are similar to FDs):

- Reflexivity: If $B \subseteq A$ , then $A \twoheadrightarrow B$ .  
- Augmentation: If $A \twoheadrightarrow B$ , then $AC \twoheadrightarrow BC$ .  
- Transitivity: If $A \twoheadrightarrow B$ and $B \twoheadrightarrow C$ , then $A \twoheadrightarrow (C - B)$ .  
○ Complementation: If $A \twoheadrightarrow B$ , then $A \twoheadrightarrow (R - A - B)$ .  
○ Union: If $A \rightarrow B$ and $A \rightarrow C$ , then $A \rightarrow BC$ .  
- Decomposition: If $A \twoheadrightarrow B$ and $A \twoheadrightarrow C$ , then $A \twoheadrightarrow (B \cap C)$ , $A \twoheadrightarrow (B - C)$ , and $A \twoheadrightarrow (C - B)$ .  
- Replication (FD to MVD): If $A \to B$ , then $A \twoheadrightarrow B$ .

# Key Properties/Identities:

- MVDs address redundancy arising from multi-valued facts that are independent of each other.  
- 4NF eliminates these MVDs by decomposition.

# Common Pitfalls:

- Confusing MVDs with FDs. MVDs imply FDs, but not vice versa.  
- Incorrectly identifying trivial MVDs.

# Problem-Solving Techniques:

- Identify MVDs by looking for independent multi-valued facts.  
- Decompose relations based on non-trivial MVDs to achieve 4NF. For $R(A, B, C)$ with $A \twoheadrightarrow B$ , decompose into $R_1(A, B)$ and $R_2(A, C)$ .

# Natural Join

The Natural Join operation (⊗) combines two relations based on equality of their common attributes. It implicitly creates an equijoin condition for all attributes that share the same name in both relations and projects out the duplicate common attributes.

# Formulas/Theorems:

\- Given relations $R$ and $S$ , let $C = \text{attributes}(R) \cap \text{attributes}(S)$ be the set of common attributes.

$$
R \bowtie S = \pi_ {\text {attributes} (R) \cup \text {attributes} (S)} \left(\sigma_ {R. c _ {1} = S. c _ {1} \wedge \dots \wedge R. c _ {k} = S. c _ {k}} (R \times S)\right)
$$

where $c_{i}\in C$

# Key Properties/Identities:

- The resulting schema contains all attributes from both relations, with common attributes appearing only once.  
- It is a special case of equijoin followed by projection.

# Common Pitfalls:

- Misunderstanding the implicit join condition (all common attributes).  
- Incorrectly determining the schema or number of tuples in the result.

# Problem-Solving Techniques:

- Identify all common attributes between the two relations.  
- For each pair of tuples (one from each relation), check if their values for all common attributes are equal. If so, combine them into a single result tuple, keeping common attributes only once.

# Normal Forms

Normal Forms (1NF, 2NF, 3NF, BCNF, 4NF, 5NF) are a series of guidelines for designing relational database schemas to reduce data redundancy and improve data integrity. Each normal form builds upon the previous one, imposing stricter rules.

# Formulas/Theorems:

• 1NF: All attributes are atomic.  
- 2NF: In 1NF and no non-prime attribute is partially dependent on any candidate key.  
- 3NF: In 2NF and no non-prime attribute is transitively dependent on any candidate key.  
- BCNF: For every non-trivial FD $A \rightarrow B$ , $A$ is a super key.  
• 4NF: In BCNF and no non-trivial MVDs exist.  
- 5NF: In 4NF and no non-trivial join dependencies exist.

# Key Properties/Identities:

- Higher normal forms generally reduce more redundancy but may require more joins for queries.  
- BCNF is generally preferred, but 3NF is often a practical compromise as it guarantees lossless join and dependency preservation.

# Common Pitfalls:

- Incorrectly identifying candidate keys, which is crucial for all normal forms.  
- Confusing partial, transitive, and multi-valued dependencies.

# Problem-Solving Techniques:

- First, find all candidate keys and the closure of all FDs.  
- Then, systematically check the conditions for 1NF, 2NF, 3NF, and BCNF in order.

\- If a relation is not in a desired normal form, decompose it into smaller relations that satisfy the conditions.

# Query

A query is a request for data or information from a database. Queries are typically written using a query language like SQL, Relational Algebra, or Relational Calculus. They specify what data to retrieve, how to filter it, and how to present it.

# Formulas/Theorems:

\- No specific formulas, but relies on the syntax and semantics of query languages.

# Key Properties/Identities:

- Selectivity: The fraction of tuples that satisfy a selection condition.  
- Projection: Selecting specific columns.  
- Join: Combining data from multiple tables.

# Common Pitfalls:

- Syntax errors in SQL.  
- Logical errors leading to incorrect results (e.g., wrong join conditions, incorrect aggregation).  
- Inefficient queries that perform poorly.

# Problem-Solving Techniques:

- Break down complex queries into smaller, manageable parts.  
- Understand the order of operations in SQL (FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY).  
- Practice translating natural language requirements into formal query language expressions.

# Referential Integrity

Referential Integrity is a database concept that ensures that relationships between tables remain consistent. It is enforced using foreign key constraints, which dictate that a foreign key in one table must either match a primary key in another table or be NULL.

# Formulas/Theorems:

\- No specific formulas, but it's a constraint rule.

# Key Properties/Identities:

- Prevents "dangling references" where a foreign key refers to a non-existent primary key.  
- Actions on deletion/update of primary key: CASCADE, SET NULL, SET DEFAULT, RESTRICT (default).

# Common Pitfalls:

- Violating referential integrity constraints during data modification.  
- Misunderstanding the behavior of different ON DELETE/ON UPDATE actions.

# Problem-Solving Techniques:

- Identify primary and foreign keys correctly during schema design.  
- Choose appropriate ON DELETE/ON UPDATE actions based on business rules.  
- Trace data modification operations to check for constraint violations.

# Relational Algebra

Relational Algebra is a procedural query language that takes relations as input and produces relations as output. It consists of a set of fundamental operations (selection, projection, union, set difference, Cartesian product, rename) and

derived operations (join, intersection, division).

# Formulas/Theorems:

- Select: $\sigma_{P}(R)$ (selects tuples satisfying predicate $P$ ).  
- Project: $\pi_A(R)$ (selects attributes $A$ ).  
- Union: $R \cup S$ (combines tuples from $R$ and $S$ ; relations must be union-compatible).  
- Set Difference: $R \setminus S$ (tuples in $R$ but not in $S$ ; union-compatible).  
- Cartesian Product: $R \times S$ (combines every tuple of $R$ with every tuple of $S$ ).  
- Rename: $\rho_{S(A_1,\dots,A_n)}(R)$ (renames relation $R$ to $S$ and its attributes).  
- Intersection: $R \cap S = R \setminus (R \setminus S)$ (derived).  
- Join: $R \bowtie_{P} S = \sigma_{P}(R \times S)$ (derived).

# Key Properties/Identities:

- Closure property: The result of any operation is also a relation.  
- Forms the theoretical basis for SQL.

# Common Pitfalls:

- Incorrectly applying operators, especially for complex queries.  
- Forgetting union compatibility requirements for set operations.  
- Operator precedence issues.

# Problem-Solving Techniques:

- Break down complex queries into a sequence of simpler relational algebra operations.  
- Practice converting SQL queries to relational algebra and vice versa.

# Relational Calculus

Relational Calculus is a non-procedural (declarative) query language that describes what data to retrieve without specifying how to retrieve it. It comes in two forms: Tuple Relational Calculus (TRC) and Domain Relational Calculus (DRC).

# Formulas/Theorems:

- Tuple Relational Calculus (TRC): $\{t \mid P(t)\}$ where $t$ is a tuple variable and $P(t)$ is a formula (predicate) involving $t$ .  
• Example: $\{t \mid t \in \text{Student} \land t. \text{Age} > 20\}$  
- Domain Relational Calculus (DRC): $\{\langle x_1, x_2, \dots, x_n \rangle \mid P(x_1, x_2, \dots, x_n)\}$ where $x_i$ are domain variables and $P$ is a formula.  
• Example: $\{\langle N,A\rangle\mid\exists I(\langle I,N,A\rangle\in Student\land A>20)\}$

# Key Properties/Identities:

- Expressive power equivalent to Relational Algebra (Codd's Theorem).  
- Uses quantifiers ( $\exists$ - existential, $\forall$ - universal).

# Common Pitfalls:

- Incorrectly using quantifiers, especially universal quantification.  
- Formulating predicates that are not "safe" (may yield infinite results).

# Problem-Solving Techniques:

- Translate natural language queries into logical predicates using tuple or domain variables.  
- Pay close attention to the scope of quantifiers.  
- Ensure queries are safe by bounding all variables.

# Relational Model

The Relational Model is a data model based on the concept of relations (tables). Data is organized into two-dimensional tables, where each table represents an entity or a relationship, and rows (tuples) represent records, while columns (attributes) represent fields.

# Formulas/Theorems:

\- No specific formulas, but defines the structure.

# Key Properties/Identities:

- Relation (Table): A set of tuples.  
- Tuple (Row): A record in a relation.  
- Attribute (Column): A named property of a relation.  
- Domain: The set of permissible values for an attribute.  
- Schema: The logical design of the database.  
- Instance: The actual data stored in the database at a particular time.  
- Integrity Constraints: Entity Integrity (Primary Key not NULL), Referential Integrity (Foreign Key rules).

# Common Pitfalls:

- Confusing the formal definitions of relation, tuple, and attribute.  
- Not understanding the role of domains and integrity constraints.

# Problem-Solving Techniques:

- Understand the basic terminology and how data is represented.  
- Be able to identify components of a relational schema.

# SQL

SQL (Structured Query Language) is the standard language for managing and manipulating relational databases. It is used for defining database schemas (DDL), querying data (DML), controlling access (DCL), and managing transactions (TCL).

# Formulas/Theorems:

\- No specific formulas, but adheres to a strict syntax.

# Key Properties/Identities:

- DDL (Data Definition Language): CREATE, ALTER, DROP (for schema objects).  
- DML (Data Manipulation Language): SELECT, INSERT, UPDATE, DELETE (for data).  
- DCL (Data Control Language): GRANT, REVOKE (for permissions).  
- TCL (Transaction Control Language): COMMIT, ROLLBACK, SAVEPOINT.

# Common Pitfalls:

- Complex queries involving subqueries, aggregate functions, GROUP BY, and HAVING clauses.  
- Understanding the order of execution of SQL clauses.  
- Differences in SQL dialects (though GATE usually sticks to standard SQL).

# Problem-Solving Techniques:

- Practice writing queries for various scenarios, including joins, subqueries, and aggregation.  
- Understand the logical processing order of a SELECT statement: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY.

# Safe Query

A query in Relational Calculus is considered "safe" if it produces a finite number of tuples as its result for any valid database instance. Unsafe queries can potentially produce an infinite result set, which is undesirable in practice.

# Formulas/Theorems:

\- No direct formulas, but a conceptual property.

# Key Properties/Identities:

• Every query expressible in Relational Algebra is safe.  
- Safety typically requires that all variables are "bounded" – their values must come from the active domain of the database (values currently present in the tables).

# Common Pitfalls:

- Queries with unbounded variables, especially those using universal quantifiers without proper restrictions.  
- Example of unsafe query: $\{t \mid \neg(t \in R)\}$ (all tuples not in $\mathsf{R}$ , potentially infinite).

# Problem-Solving Techniques:

- Ensure that all variables in a relational calculus query are restricted to range over finite sets (e.g., relations in the database or active domain).  
- For universal quantifiers, ensure they are used in a limited context (e.g., "for all X in Y...").

# Super Key

A Super Key is any set of attributes in a relation that, taken together, uniquely identifies each tuple in that relation. It guarantees uniqueness but does not necessarily imply minimality.

# Formulas/Theorems:

\- A set of attributes $K$ is a Super Key if $K \to R$ (where $R$ is all attributes in the relation).

# Key Properties/Identities:

• Every candidate key is a super key.  
- A super key can contain redundant attributes (i.e., attributes not necessary for uniqueness).

# Common Pitfalls:

- Confusing with Candidate Key (Candidate Key is a minimal super key).  
- Forgetting that adding more attributes to a super key still results in a super key.

# Problem-Solving Techniques:

- To find super keys, start with candidate keys and add any combination of remaining attributes.  
- Alternatively, find the closure of attribute sets. Any set $X$ for which $X^{+}$ contains all attributes of the relation is a super key.

# Timestamp Ordering

Timestamp Ordering is a concurrency control protocol that ensures serializability by assigning a unique timestamp to each transaction. Transactions are executed in the order of their timestamps, and conflicts are resolved by rolling back transactions that violate this order.

# Formulas/Theorems:

- Each transaction $T_{i}$ is assigned a unique timestamp $TS(T_{i})$ .  
- Each data item $X$ has a $R\_TS(X)$ (read timestamp) and a $W\_TS(X)$ (write timestamp).  
- Read Rule: If $TS(T_i) < W\_TS(X)$ , $T_i$ must abort and restart with a new timestamp. Otherwise, read $X$ and set

$$
R _ {-} T S (X) = \max (R _ {-} T S (X), T S (T _ {i})).
$$

\- Write Rule: If $TS(T_i) < R\_TS(X)$ or $TS(T_i) < W\_TS(X)$ , $T_i$ must abort and restart. Otherwise, write $X$ and set $W\_TS(X) = TS(T_i)$ .

# Key Properties/Identities:

• Guarantees conflict serializability.  
- Can lead to cascading rollbacks and starvation.  
- Basic timestamp ordering is prone to aborts.

# Common Pitfalls:

- Incorrectly applying the read/write rules, especially the abort conditions.  
- Tracing complex schedules with multiple transactions.

# Problem-Solving Techniques:

- Assign timestamps to transactions.  
- Maintain $R\_TS(X)$ and $W\_TS(X)$ for each data item.  
- Step through the schedule, applying the read and write rules and determining if any transaction needs to abort.

# Transaction and Concurrency

A Transaction is a logical unit of work that accesses and possibly modifies the contents of a database. Concurrency Control is the management of simultaneous operations on a database to ensure data consistency and integrity, especially when multiple transactions execute concurrently.

# Formulas/Theorems:

\- No direct formulas, but concepts like serializability and isolation levels are key.

# Key Properties/Identities:

• ACID Properties of Transactions:

- Atomicity: All or nothing.  
- Consistency: Transaction takes database from one consistent state to another.  
- Isolation: Concurrent transactions appear to execute serially.  
- Durability: Changes are permanent once committed.

\- Concurrency Anomalies: Dirty Read, Lost Update, Unrepeatable Read, Phantom Read.

\- Isolation Levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable.

# Common Pitfalls:

- Identifying which anomaly occurs in a given schedule.  
- Understanding how different concurrency control mechanisms (locking, timestamping) prevent anomalies.

# Problem-Solving Techniques:

- Analyze schedules to identify potential anomalies.  
- Understand how each ACID property is maintained or violated.  
- Relate isolation levels to the anomalies they prevent.

# Tuple Relational Calculus

Tuple Relational Calculus (TRC) is a non-procedural query language where variables range over tuples. It allows users to specify the properties of the tuples they want in the result without detailing the exact steps to retrieve them.

# Formulas/Theorems:

\- General form: $\{t \mid P(t)\}$ where $t$ is a tuple variable and $P(t)$ is a formula (predicate) that $t$ must satisfy.

\- Predicates can involve:

- Membership: $t \in R$  
- Attribute access: $t$ . $A$  
- Comparison operators: $=, \neq, <, >, \leq, \geq$  
- Logical connectives: $\land$ , $\lor$ , $\neg$  
- Quantifiers: ∃ (exists), ∀ (for all)

# Key Properties/Identities:

• Expressive power equivalent to Relational Algebra.  
- More declarative than Relational Algebra.

# Common Pitfalls:

- Incorrectly formulating complex predicates, especially with multiple tuple variables and quantifiers.  
- Ensuring the query is "safe" (produces a finite result).

# Problem-Solving Techniques:

- Break down the query into smaller logical conditions.  
- Use a separate tuple variable for each relation involved in the query.  
- Carefully use quantifiers, ensuring variables are appropriately bound.

# Two Phase Locking Protocol

The Two-Phase Locking (2PL) protocol is a concurrency control mechanism that ensures serializability by requiring transactions to acquire all necessary locks before releasing any. It divides a transaction's execution into two phases: a growing phase and a shrinking phase.

# Formulas/Theorems:

\- No direct formulas, but a protocol with rules for lock acquisition and release.

# Key Properties/Identities:

- Growing Phase: Transaction can acquire new locks but cannot release any.  
- Shrinking Phase: Transaction can release existing locks but cannot acquire new ones.  
• Guarantees conflict serializability.  
- Can lead to deadlocks.  
- Strict 2PL: All exclusive (write) locks are held until commit/rollback, preventing cascading rollbacks.

# Common Pitfalls:

- Incorrectly identifying the growing and shrinking phases.  
- Detecting deadlocks in schedules using 2PL (e.g., using a wait-for graph).  
- Understanding the difference between basic 2PL and strict 2PL.

# Problem-Solving Techniques:

- Trace transaction execution, noting when locks are acquired and released.  
- Construct a wait-for graph to detect deadlocks: an edge $T_{i} \rightarrow T_{j}$ exists if $T_{i}$ is waiting for a lock held by $T_{j}$ . A cycle indicates a deadlock.

# Quick Formula Reference

\- Armstrong Axioms:

- Reflexivity: If $B \subseteq A$ , then $A \to B$  
○ Augmentation: If $A \to B$ , then $AC \to BC$  
- Transitivity: If $A \to B$ and $B \to C$ , then $A \to C$

\- B-Tree (Order $m$ ):