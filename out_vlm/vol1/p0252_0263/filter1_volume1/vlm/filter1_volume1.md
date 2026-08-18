Clock time problems involve calculating angles between clock hands, or determining exact times based on relative speeds of hands.

# - Key Rates:

1. Hour hand: $0.5^{\circ}$ per minute  
2. Minute hand: $6^{\circ}$ per minute  
3. Relative speed: 5.5° per minute (minute hand gains on hour hand)

- Formula for angle between hands at H hours M minutes: $|30H - \frac{11}{2}M|$  
- Technique: Calculate the position of each hand relative to 12, then find the difference.  
- Pitfall: Not considering the hour hand's movement within the hour.

# Combinatory (Permutation and Combination)

Combinatory deals with counting arrangements (permutations) and selections (combinations) of objects.

# - Formulas:

1. Permutation (arrangement of $k$ items from $n$ ): $P(n, k) = \frac{n!}{(n - k)!}$  
2. Combination (selection of $k$ items from $n$ ): $C(n, k) = \frac{n!}{k!(n-k)!}$  
3. $n!=n\times(n-1)\times\cdots\times1,0!=1$

- Key Principle: Permutation is about order, combination is not. "Arrangement" implies permutation, "selection" or "group" implies combination.  
- Pitfall: Confusing permutation with combination.  
- Technique: Determine if order matters. Use multiplication principle for sequential events, addition principle for mutually exclusive events.

# Compound Interest

Compound interest is interest calculated on the initial principal, which also includes all of the accumulated interest from previous periods on a deposit or loan.

# - Formulas:

1. Amount (compounded annually): $A = P\left(1 + \frac{R}{100}\right)^T$  
2. Compound Interest (CI): CI = A - P  
3. Amount (compounded $n$ times a year): $A = P\left(1 + \frac{R}{100n}\right)^{nT}$  
4. Amount (compounded continuously): $A = Pe^{RT / 100}$

- Pitfall: Confusing simple interest with compound interest, or incorrect compounding frequency.  
- Technique: Identify principal (P), rate (R), time (T), and compounding frequency.

# Conditional Probability

Conditional probability is the probability of an event occurring given that another event has already occurred.

- Formula: $P(A|B) = \frac{P(A \cap B)}{P(B)}$ (where $P(B) > 0$ )  
• Key Idea: The sample space is reduced to event B.  
- Pitfall: Misidentifying the intersection event or the conditioning event.  
- Technique: Clearly define events A and B, find their intersection, and the probability of B.

# Cones

A cone is a three-dimensional geometric shape that tapers smoothly from a flat base (usually circular) to a point called the apex or vertex.

# - Formulas:

1. Volume: $V = \frac{1}{3}\pi r^{2}h$  
2. Curved Surface Area (CSA): $CSA = \pi rl$ (where $l$ is slant height, $l = \sqrt{r^2 + h^2}$ )  
3. Total Surface Area (TSA): $TSA = \pi r(l + r)$

- Pitfall: Confusing height $(h)$ with slant height $(l)$ .  
- Technique: Use Pythagorean theorem to find $l$ if $r$ and $h$ are given.

# Contour Plots

Contour plots (or isoline maps) display three-dimensional data on a two-dimensional plane, where lines connect points of equal value.

- Core Idea: Visualize a third variable (e.g., elevation, temperature) over a surface.  
- Technique: Interpret the density and values of contour lines. Closely spaced lines indicate a steep gradient, widely spaced lines indicate a gentle gradient.  
- Pitfall: Misinterpreting the values represented by the lines or the gradient.

# Cost Market Price

These problems involve concepts of cost price (CP), selling price (SP), market price (MP), profit, loss, and discount.

# - Formulas:

1. Profit = SP - CP (if SP > CP)  
2. Loss = CP - SP (if CP > SP)  
3. Profit/Loss $\% = \frac{\text{Profit/Loss}}{\text{CP}} \times 100$  
4. Discount = MP - SP  
5. Discount $\% = \frac{\text{Discount}}{\text{MP}} \times 100$  
6. $\mathrm{SP} = \mathrm{CP} \times (1 \pm \frac{\mathrm{Profit/Loss} \backslash \%}{100})$  
7. $\mathrm{SP} = \mathrm{MP} \times (1 - \frac{\text{Discount} \backslash \%}{100})$

- Pitfall: Calculating profit/loss % on SP instead of CP, or discount % on CP instead of MP.  
- Technique: Clearly identify CP, SP, MP, and the base for percentage calculations.

# Counting

Counting principles involve determining the number of possible outcomes for various events.

# - Principles:

1. Addition Principle: If event A can occur in $m$ ways and event B in $n$ ways, and they are mutually exclusive, then A or B can occur in $m + n$ ways.  
2. Multiplication Principle: If event A can occur in $m$ ways and event B in $n$ ways, then A and B can occur in $m \times n$ ways.  
- Technique: Break down complex counting problems into simpler, sequential or mutually exclusive steps.  
- Pitfall: Overcounting or undercounting by misapplying the principles.

# Cubes

A cube is a three-dimensional solid object bounded by six square faces, facets or sides, with three meeting at each vertex.

# - Formulas:

1. Volume: $V = a^3$ (where $a$ is side length)  
2. Surface Area: $SA = 6a^{2}$  
3. Diagonal of a face: $a\sqrt{2}$  
4. Main Diagonal of the cube: $a\sqrt{3}$  
- Pitfall: Confusing surface area with volume, or face diagonal with main diagonal.  
- Technique: Visualize the cube and its dimensions.

# Currency Notes

Problems involve calculating the total value of currency notes of different denominations or determining the number of notes of each denomination given a total amount.

- Core Idea: Form linear equations based on the value and count of notes.  
- Technique: Assign variables to the number of notes of each denomination and set up equations.  
- Pitfall: Calculation errors with large numbers or multiple denominations.

# Curves

In quantitative aptitude, "curves" generally refer to the graphs of functions, requiring interpretation of their shape, slope, and points of interest.

- Core Idea: Visual representation of relationships between variables.  
- Technique: Analyze the trend (increasing/decreasing), points of maxima/minima, and intersections.  
- Pitfall: Misinterpreting the axes or the units.

# Data Interpretation

Data interpretation involves extracting, analyzing, and drawing conclusions from various forms of data presentation like tables, charts (bar, pie, line, scatter, radar), and graphs.

- Core Idea: Critical analysis of presented data to answer specific questions.  
- Technique: Read titles, labels, scales, and legends carefully. Perform calculations (percentages, ratios, averages) based on the data.  
- Pitfall: Rushing calculations, misreading data points, or making assumptions not supported by the data.

# Digital Image Processing

While a CS topic, in QA it might appear as basic numerical problems related to image size, resolution, or data storage.

- Core Idea: Image represented as a grid of pixels.  
- Key Concepts:  
1. Resolution: Width × Height (in pixels)  
2. Color Depth: Bits per pixel (e.g., 8-bit for 256 colors, 24-bit for true color)  
3. Image Size (uncompressed): Resolution × Color Depth (in bits)  
- Technique: Apply multiplication principles for calculating total bits/bytes.  
- Pitfall: Unit conversions (bits to bytes, KB to MB).

# Factors

Factors (or divisors) of a number are integers that divide the number evenly without leaving a remainder.

- Core Idea: Finding numbers that multiply to give the original number.  
- Properties:  
1. For $N = p_1^{a_1}p_2^{a_2}\ldots p_k^{a_k}$ (prime factorization):  
2. Number of factors: $(a_{1}+1)(a_{2}+1)\ldots(a_{k}+1)$  
3. Sum of factors: $(1 + p_{1} + \cdots + p_{1}^{a_{1}})(1 + p_{2} + \cdots + p_{2}^{a_{2}}) \ldots$  
- Technique: Prime factorization is key to finding number and sum of factors.  
- Pitfall: Missing factors, especially 1 and the number itself.

# Fractions

Fractions represent a part of a whole, expressed as a ratio of two integers (numerator/denominator).

- Operations: Addition, subtraction, multiplication, division.  
- Properties: Equivalent fractions, proper/improper fractions, mixed numbers.  
- Technique: Find common denominators for addition/subtraction. Invert and multiply for division. Simplify fractions.  
- Pitfall: Errors in finding common denominators or simplifying.

# Functions

A function is a relation between a set of inputs and a set of permissible outputs with the property that each input is related to exactly one output.

- Core Idea: Mapping inputs to outputs. $y = f(x)$ .  
- Key Concepts: Domain (set of inputs), Range (set of outputs), types (linear, quadratic, polynomial).  
- Technique: Evaluate functions at given points, understand their graphs, and solve for unknowns.  
- Pitfall: Incorrectly applying function rules or misinterpreting domain/range restrictions.

# Geometry

Geometry deals with the properties and relations of points, lines, surfaces, solids, and higher dimensional analogs.

- Core Idea: Understanding shapes, angles, and spatial relationships.  
- Key Theorems: Pythagorean theorem, properties of parallel lines and transversals, angle sum property of triangles, similar/congruent triangles.  
- Technique: Draw diagrams, identify knowns and unknowns, apply relevant theorems and formulas.  
- Pitfall: Assuming properties not explicitly stated or derivable.

# Graph Coloring

Graph coloring assigns colors to elements of a graph subject to certain constraints. In QA, it's usually simplified to finding the minimum number of colors for a small graph.

- Core Idea: Assign colors to vertices such that no two adjacent vertices share the same color.  
- Technique: Start coloring from a vertex with high degree; systematically assign colors, avoiding conflicts with neighbors.  
- Pitfall: Missing a valid coloring or not finding the minimum.

# Inequality

Inequalities are mathematical statements comparing two expressions using symbols like $<, >, \leq, \geq$ .

# - Properties:

1. Adding/subtracting a number from both sides does not change the inequality direction.  
2. Multiplying/dividing by a positive number does not change the inequality direction.  
3. Multiplying/dividing by a negative number reverses the inequality direction.  
- Technique: Solve like equations, but remember to flip the sign when multiplying/dividing by a negative number. For quadratic inequalities, use sign analysis of factors.  
- Pitfall: Forgetting to reverse the inequality sign.

# LCM HCF

LCM (Least Common Multiple) is the smallest positive integer divisible by each of a given set of integers. HCF (Highest Common Factor) or GCD (Greatest Common Divisor) is the largest positive integer that divides each of a given set of integers.

# - Formulas:

1. For two numbers $a$ and $b$ : $\mathrm{LCM}(a, b) \times \mathrm{HCF}(a, b) = a \times b$  
2. To find LCM/HCF: Use prime factorization method.  
- Technique: Prime factorization is the most reliable method.  
- Pitfall: Confusing LCM with HCF, especially in word problems.

# Line Graph

A line graph displays information as a series of data points connected by straight line segments, showing trends over time or categories.

- Core Idea: Visualizing trends and changes over a continuous variable.  
- Technique: Observe the slope of the lines to understand rates of change, identify peaks and troughs.  
- Pitfall: Misinterpreting the scale or the meaning of the trend.

# Lines

Lines in coordinate geometry are one-dimensional figures with properties like slope, intercepts, and equations.

# - Formulas:

1. Slope (m) of a line through $(x_{1},y_{1})$ and $(x_{2},y_{2})$ : $m = \frac{y_2 - y_1}{x_2 - x_1}$  
2. Equation of a line (slope-intercept form): $y = mx + c$ (where $c$ is y-intercept)  
3. Equation of a line (point-slope form): $y - y_{1} = m(x - x_{1})$  
4. Parallel lines: $m_{1}=m_{2}$  
5. Perpendicular lines: $m_{1}m_{2} = -1$  
- Pitfall: Sign errors in slope calculation, confusing parallel with perpendicular conditions.

\- Technique: Identify slope and a point, then use the appropriate equation form.

# Logarithms

Logarithms are the inverse operation to exponentiation. The logarithm of a number $x$ to the base $b$ is the exponent to which $b$ must be raised to produce $x$ .

- Definition: $\log_b a = c \iff b^c = a$  
- Properties:

1. $\log_b(xy) = \log_b x + \log_b y$  
2. $\log_b(x / y) = \log_b x - \log_b y$  
3. $\log_b x^n = n \log_b x$  
4. $\log_b b = 1, \log_b 1 = 0$  
5. Change of Base: $\log_b a = \frac{\log_c a}{\log_c b}$

- Pitfall: Misapplying properties, especially for addition/subtraction.  
- Technique: Convert between logarithmic and exponential forms, use properties to simplify.

# Maps

Map problems involve interpreting scale, distances, and directions on maps.

- Core Idea: Scale represents the ratio of a distance on the map to the corresponding distance on the ground.  
- Formula: Map Distance = Actual Distance × Scale  
- Technique: Pay close attention to the scale (e.g., 1:100000 or 1 cm = 10 km) and units.  
- Pitfall: Incorrect unit conversions.

# Maxima Minima

Finding the maximum or minimum value of a function or expression.

- Core Idea: Identifying the highest or lowest point a function can reach.  
- For Quadratic Function $f(x) = ax^{2} + bx + c$ :

1. Vertex at $x = -b / (2a)$  
2. If a > 0, minimum value at vertex.  
3. If a < 0, maximum value at vertex.

- General Technique (Calculus-based, if applicable): Find derivative $f'(x)$ , set to zero to find critical points. Use second derivative test for max/min.  
- Pitfall: Confusing local maxima/minima with global maxima/minima.

# Mensuration

Mensuration is the branch of mathematics that deals with the measurement of geometric figures and their parameters like length, area, and volume. This topic consolidates formulas for various 2D and 3D shapes.

- Core Idea: Applying geometric formulas to calculate dimensions, areas, and volumes.  
- Technique: Refer to specific topics like Area, Volume, Cones, Cubes, Circles, Triangles for detailed formulas.  
- Pitfall: Incorrectly applying formulas or unit conversions.

# Modular Arithmetic

Modular arithmetic is a system of arithmetic for integers, where numbers "wrap around" when reaching a certain value —the modulus.

- Definition: $a \equiv b \pmod{m}$ means $a$ and $b$ have the same remainder when divided by $m$ , or $m$ divides $(a - b)$ .  
- Properties:

1. If $a \equiv b \pmod{m}$ and $c \equiv d \pmod{m}$ , then $a + c \equiv b + d \pmod{m}$ and $ac \equiv bd \pmod{m}$ .

2. $(a \times b) (\bmod m) = ((a (\bmod m)) \times (b (\bmod m))) (\bmod m)$

- Technique: Use properties to simplify large numbers before finding remainders. Useful for unit digit problems.  
- Pitfall: Incorrectly handling negative numbers in modulo operations.

# Number Representation

Number representation deals with how numbers are written and interpreted, often involving different bases (e.g., decimal, binary).

- Core Idea: Converting numbers between different bases.  
- Technique: For base-10 to base-B, repeatedly divide by B and collect remainders. For base-B to base-10, use positional notation (sum of digits × base to power of position).  
- Pitfall: Errors in powers of the base or order of remainders.

# Number Series

Number series problems involve identifying the pattern in a sequence of numbers and finding the next term or a missing term.

- Types: Arithmetic, geometric, difference series, squares/cubes, prime numbers, alternating patterns, Fibonacci-like.  
- Technique: Look for common differences, common ratios, differences of differences, squares/cubes, or combinations of operations.  
- Pitfall: Overlooking subtle patterns or assuming a simple pattern too quickly.

# Number System

The number system classifies numbers (natural, whole, integers, rational, irrational, real, complex) and includes concepts like divisibility rules, prime/composite numbers.

- Divisibility Rules: (e.g., by 2, 3, 4, 5, 6, 8, 9, 10, 11).  
- Classification:

1. Natural Numbers: $\{1,2,3,\ldots\}$

2. Whole Numbers: {0, 1, 2, 3, ...}

3. Integers: {...,-2,-1,0,1,2,...}

4. Rational Numbers: $\{p / q \mid p, q$ are integers, $q \neq 0\}$

5. Irrational Numbers: Non-terminating, non-repeating decimals (e.g., $\sqrt{2}, \pi$ )

6. Real Numbers: Rational + Irrational

Technique: Apply divisibility rules, understand properties of number types.

\- Pitfall: Confusing different sets of numbers (e.g., integers vs. whole numbers).

# Number Theory

Number theory is a branch of pure mathematics devoted primarily to the study of integers and integer-valued functions, including primes, divisibility, and modular arithmetic.

- Core Idea: Properties of integers. (Overlaps with Factors, Prime Numbers, Modular Arithmetic).  
• Key Concepts: Prime numbers, composite numbers, factors, multiples, HCF, LCM, divisibility.  
- Technique: Use prime factorization, apply divisibility rules, understand modular arithmetic.  
- Pitfall: Misapplying theorems or properties.

# Numerical Computation

Numerical computation involves performing calculations accurately and efficiently, often with approximations, rounding, and significant figures.

- Core Idea: Precision and accuracy in calculations.  
- Technique: Estimate answers, use approximations (e.g., $\pi \approx 22/7$ or 3.14), understand rules for significant figures and rounding.  
- Pitfall: Rounding too early, leading to accumulated errors.

# Percentage

Percentage is a way of expressing a number or ratio as a fraction of 100. It is often denoted using the percent sign, "%".

\- Formulas:

1. Value = Base × $\frac{Percentage}{100}$  
2. Percentage Change = $\frac{Change}{Original Value} \times 100$

3. Successive Percentage Change: If an item changes by $x\%$ then by $y\%$ , net change is $(x + y + \frac{xy}{100})\%$ .

- Pitfall: Calculating percentage change based on the wrong base value.  
- Technique: Convert percentages to decimals or fractions for calculations.

# Permutation and Combination

Refer to "Combinatory" section for details.

# Pie Chart

A pie chart is a circular statistical graphic, which is divided into slices to illustrate numerical proportion.

- Core Idea: Visualizing parts of a whole as proportions.  
- Properties: The sum of all percentages in a pie chart must be 100%, and the sum of all central angles must be 360°.  
- Technique: Relate percentages to degrees (1% = 3.6°). Calculate proportions and compare sectors.  
- Pitfall: Misinterpreting the size of sectors or the total quantity.

# Polynomials

A polynomial is an expression consisting of variables and coefficients, that involves only the operations of addition, subtraction, multiplication, and non-negative integer exponents of variables.

• Key Concepts: Degree, roots (zeros), factors.  
- Theorems:

1. Remainder Theorem: If a polynomial $P(x)$ is divided by $(x - a)$ , the remainder is $P(a)$ .

2. Factor Theorem: $(x - a)$ is a factor of $P(x)$ if and only if $P(a) = 0$ .

- Technique: Factorization, synthetic division, applying remainder/factor theorems.  
- Pitfall: Errors in algebraic manipulation or sign errors.

# Powers

Powers (or exponents) indicate the number of times a base number is multiplied by itself.

\- Rules of Exponents:

1. $x^{a} \cdot x^{b} = x^{a + b}$  
2. $x^{a} / x^{b} = x^{a - b}$  
3. $(x^{a})^{b} = x^{ab}$  
4. $(xy)^{a} = x^{a}y^{a}$  
5. $(x / y)^{a} = x^{a} / y^{a}$  
6. $x^{0}=1$ (for $x\neq0$ )  
7. $x^{-a} = 1 / x^{a}$  
8. $x^{1 / n} = \sqrt[n]{x}$

- Pitfall: Incorrectly applying rules, especially with negative exponents or fractions.  
- Technique: Simplify expressions using exponent rules, convert to common base if possible.

# Prime Numbers

A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.

\- Properties:

1. 2 is the only even prime number.  
2. Every integer greater than 1 is either prime or can be uniquely expressed as a product of primes (Fundamental Theorem of Arithmetic).

- Technique: To check if $N$ is prime, test divisibility by primes up to $\sqrt{N}$ .  
- Pitfall: Confusing 1 as a prime number (it's not).

# Probability

Probability is the measure of the likelihood that an event will occur.

\- Formula: $P(E) = \frac{\text{Number of Favorable Outcomes}}{\text{Total Number of Possible Outcomes}}$

\- Properties:

1. $0 \leq P(E) \leq 1$  
2. $P(\mathrm{not}E) = 1 - P(E)$  
3. $P(A \cup B) = P(A) + P(B) - P(A \cap B)$  
4. For independent events: $P(A \cap B) = P(A)P(B)$

\- Technique: Clearly define the sample space and the event. Use counting techniques (P&C) to find favorable and total outcomes.

\- Pitfall: Incorrectly identifying sample space or favorable outcomes, or assuming independence when events are dependent.

# Probability Density Function

For continuous random variables, the Probability Density Function (PDF) describes the relative likelihood for the random variable to take on a given value. The probability of the variable falling within a range is given by the integral of the PDF over that range.

\- Core Idea: For continuous variables, $P(a \leq X \leq b) = \int_{a}^{b} f(x) dx$ .

\- Property: $\int_{-\infty}^{\infty} f(x) dx = 1$

\- Technique: Understand that for continuous variables, $P(X = x) = 0$ . Focus on areas under the curve.

\- Pitfall: Treating PDF values directly as probabilities (they are not).

# Profit Loss

Refer to "Cost Market Price" section for details.

# Quadratic Equations

A quadratic equation is a polynomial equation of the second degree, typically written as $ax^2 + bx + c = 0$ .

\- Formulas:

1. Quadratic Formula (roots): $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$  
2. Discriminant: $D = b^{2} - 4ac$

- If $D > 0$ , two distinct real roots.  
- If $D = 0$ , two equal real roots.  
- If $D < 0$ , no real roots (complex roots).

3. Sum of roots: $\alpha + \beta = -b / a$  
4. Product of roots: $\alpha\beta = c/a$

- Technique: Factorization, completing the square, or using the quadratic formula.  
- Pitfall: Sign errors in the quadratic formula or discriminant.

# Radar Chart

A radar chart (or spider chart) displays multivariate data in the form of a two-dimensional chart of three or more quantitative variables represented on axes starting from the same point.

- Core Idea: Comparing multiple attributes of one or more items.  
- Technique: Compare the area covered by different polygons or the values along each axis.  
- Pitfall: Overcrowding with too many variables or items, making comparisons difficult.

# Ratio Proportion

Ratio is a comparison of two quantities by division. Proportion states that two ratios are equal.

\- Formulas:

1. Ratio: $a:b = a / b$  
2. Proportion: $a:b::c:d \implies a/b = c/d \implies ad = bc$ (product of extremes = product of means)  
3. Direct Proportion: $y = kx$  
4. Inverse Proportion: $y = k / x$

- Technique: Simplify ratios, use cross-multiplication for proportions, apply unitary method for direct/inverse proportion problems.  
- Pitfall: Incorrectly setting up ratios or proportions, especially in word problems.

# Scatter Plot

A scatter plot uses Cartesian coordinates to display values for two variables for a set of data. The data is displayed as a collection of points, each having the value of one variable determining the position on the horizontal axis and the value of the other variable determining the position on the vertical axis.

- Core Idea: Visualizing the relationship (correlation) between two variables.  
- Technique: Observe the trend of points (positive, negative, or no correlation), strength of correlation (tightness of points).  
- Pitfall: Inferring causation from correlation.

# Seating Arrangement

Seating arrangement problems involve arranging people or objects in a specific order (linear, circular, etc.) based on given conditions.

- Core Idea: Logical deduction and application of permutation principles.  
- Technique: Draw diagrams, start with fixed positions or most restrictive conditions, use elimination. For circular arrangements, fix one person's position first.  
- Pitfall: Missing a condition, or misinterpreting "left/right" in circular arrangements.

# Sequence Series

A sequence is an ordered list of numbers. A series is the sum of the terms of a sequence. (Refer to Arithmetic Series for specific formulas).

- Core Idea: Identifying patterns and calculating sums.  
- Types: Arithmetic, Geometric, Harmonic, special series (squares, cubes).  
- Geometric Series:  
1. $n$ -th term: $a_{n} = ar^{n-1}$  
2. Sum of $n$ terms: $S_{n} = \frac{a(r^{n} - 1)}{r - 1}$ (for $r \neq 1$ )  
3. Sum to infinity: $S_{\infty} = \frac{a}{1 - r}$ (for $|r| < 1$ )  
- Technique: Determine the type of sequence, find the common difference/ratio, and apply the correct formula.  
- Pitfall: Confusing arithmetic and geometric series formulas.

# Set Theory

Set theory deals with collections of objects (sets) and their properties and operations.

- Key Concepts: Union $(\cup)$ , Intersection $(\cap)$ , Complement $(A'$ or $A^c)$ , Difference $(A - B)$ , Subset $(\subseteq)$ , Cardinality $(|A|)$ .  
- Formulas:  
1. $|A \cup B| = |A| + |B| - |A \cap B|$  
2. $|A \cup B \cup C| = |A| + |B| + |C| - |A \cap B| - |A \cap C| - |B \cap C| + |A \cap B \cap C|$  
- Technique: Use Venn diagrams to visualize and solve problems involving multiple sets.  
- Pitfall: Double-counting or missing elements in set operations.

# Shortest Path

While a CS algorithm topic, in QA, it might involve finding the shortest distance between two points on a simple grid or a small, explicitly given graph.

- Core Idea: Finding the minimum distance or cost to travel between two nodes.  
- Technique: For simple graphs, inspect paths and sum edge weights. For grids, use Manhattan distance or Euclidean distance depending on movement rules.  
- Pitfall: Missing a shorter path or incorrectly calculating path length.

# Speed Time Distance

These problems relate speed, time, and distance, often involving relative motion, trains, or boats.

# - Formulas:

1. Distance = Speed × Time  
2. Average Speed = $\frac{Total Distance}{Total Time}$  
3. Relative Speed (same direction): $|S_{1}-S_{2}|$  
4. Relative Speed (opposite direction): $S_{1} + S_{2}$  
5. Conversion: 1 km/hr = 5/18 m/s

- Technique: Ensure consistent units. For relative speed, determine if objects are moving towards or away from each other.  
- Pitfall: Unit conversion errors, or misapplying relative speed concepts.

# Squares

A square is a regular quadrilateral, which means it has four equal sides and four equal angles ( $90^{\circ}$ each).

# - Formulas:

1. Area: $s^{2}$  
2. Perimeter: 4s  
3. Diagonal: $s\sqrt{2}$

- Properties: All sides equal, all angles $90^{\circ}$ , diagonals bisect each other at $90^{\circ}$ .  
- Technique: Apply formulas directly. Recognize perfect squares.  
- Pitfall: Confusing square properties with other quadrilaterals.

# Statistics

Statistics involves the collection, analysis, interpretation, presentation, and organization of data.

# - Key Measures:

1. Mean: Average of all values.  
2. Median: Middle value when data is ordered.  
3. Mode: Most frequent value.  
4. Range: Max value - Min value.  
5. Standard Deviation: Measure of data dispersion (basic understanding).  
- Technique: Calculate measures of central tendency and dispersion. Interpret basic statistical graphs.  
- Pitfall: Confusing mean, median, and mode.

# System of Equations

A system of equations is a set of two or more equations containing common variables, which are to be solved simultaneously.

- Core Idea: Finding values for variables that satisfy all equations simultaneously.  
1. Substitution: Solve one equation for a variable, substitute into others.  
2. Elimination: Add/subtract equations to eliminate a variable.  
3. Matrix methods: For larger systems (less common in basic QA).  
- Pitfall: Algebraic errors during substitution or elimination.

# - Techniques:

# Tables / Tabular Data

Tables organize data into rows and columns, providing a structured way to present information.

- Core Idea: Extracting specific data points and performing calculations based on row/column totals or individual entries.  
- Technique: Carefully read row and column headers, identify the required data, and perform calculations (sum, average, percentage, ratio).  
- Pitfall: Misreading data from the wrong row/column, or incorrect calculations.

# Triangles

A triangle is a polygon with three edges and three vertices. It is one of the basic shapes in geometry.

# - Properties:

1. Sum of angles = 180°.  
2. Triangle Inequality: Sum of any two sides is greater than the third side.  
3. Types: Equilateral, Isosceles, Scalene, Right-angled, Acute, Obtuse.

# - Formulas:

1. Area: $\frac{1}{2} \times$ base $\times$ height (or Heron's formula)  
2. Pythagorean Theorem (for right triangle): $a^2 + b^2 = c^2$

\- Technique: Draw diagrams, identify triangle type, apply relevant theorems (e.g., Pythagorean, similar triangles).

\- Pitfall: Assuming a triangle is right-angled or isosceles without sufficient information.

# Trigonometry

Trigonometry deals with the relationships between the sides and angles of triangles, particularly right-angled triangles.

# - Ratios (SOH CAH TOA):

1. $\sin \theta = \frac{\text{Opposite}}{\text{Hypotenuse}}$  
2. $\cos \theta = \frac{\text{Adjacent}}{\text{Hypotenuse}}$  
3. $\tan \theta = \frac{\text{Opposite}}{\text{Adjacent}} = \frac{\sin \theta}{\cos \theta}$

# - Identities:

1. $\sin^2\theta +\cos^2\theta = 1$  
2. $\sec^2\theta -\tan^2\theta = 1$  
3. $\csc^2\theta -\cot^2\theta = 1$

- Standard Angles: Memorize values for $0^{\circ}, 30^{\circ}, 45^{\circ}, 60^{\circ}, 90^{\circ}$ .  
- Technique: Draw right triangles, label sides, apply appropriate ratios.  
- Pitfall: Confusing ratios, or incorrect use of identities.

# Unit Digit

Finding the unit digit of large powers or complex expressions.

- Core Idea: The unit digit of powers of a number follows a cycle.  
- Technique: Identify the cyclicity of the unit digit of the base number (e.g., 2: 2,4,8,6; 3: 3,9,7,1; 4: 4,6; 5: 5; 6: 6; 7: 7,9,3,1; 8: 8,4,2,6; 9: 9,1). Divide the exponent by the cycle length and use the remainder.  
- Pitfall: Errors in determining the cycle or using the remainder.

# Venn Diagram

Venn diagrams are graphical representations used to show relationships between sets. (Refer to Set Theory for formulas).

- Core Idea: Visualizing set operations and relationships.  
- Technique: Draw overlapping circles (or other shapes) to represent sets. Fill in the numbers in each region based on the given information, starting from the innermost intersection.  
- Pitfall: Incorrectly placing numbers in regions or misinterpreting the meaning of overlapping areas.

# Volume

Volume is the amount of three-dimensional space occupied by an object or substance.

# - Formulas:

1. Cube: $a^3$  
2. Cuboid: $l \times w \times h$  
3. Cylinder: $\pi r^{2}h$  
4. Cone: $\frac{1}{3}\pi r^{2}h$  
5. Sphere: $\frac{4}{3}\pi r^{3}$

6. Hemisphere: $\frac{2}{3}\pi r^3$

- Technique: Identify the 3D shape, recall the correct formula, ensure consistent units.  
- Pitfall: Confusing volume with surface area, or using incorrect dimensions.

# Work Time

Work-time problems involve calculating the time taken to complete a task by individuals or groups, often working at different rates.

- Core Idea: Work = Rate × Time. Rate is typically "work per unit time".  
- Formulas:

1. If A takes x days, A's 1-day work = 1/x.

2. If A and B work together, their combined 1-day work = 1/x + 1/y.

3. Efficiency $\propto \frac{1}{Time}$

4. Men × Days × Hours/Work = Constant (for multiple workers)

- Technique: Convert all work rates to a common unit (e.g., work per day). Use LCM method for efficiency.  
- Pitfall: Incorrectly adding/subtracting rates, or misinterpreting "together" vs. "alone" work.

# Quick Formula Reference

• Absolute Value: $|x| = a \implies x = \pm a$ ; $(|x|a \implies x<-a \text{ or } x>a)$  
- Algebraic Identities: $(a + b)^2 = a^2 + 2ab + b^2$ , $a^2 - b^2 = (a - b)(a + b)$ , $a^3 + b^3 = (a + b)(a^2 - ab + b^2)$  
- Alligation: $\frac{Q_C}{Q_D} = \frac{P_D - P_M}{P_M - P_C}$  
- Area: Square $s^2$ , Rectangle $lw$ , Circle $\pi r^2$ , Triangle $\frac{1}{2}bh$  
- Arithmetic Series: $a_{n} = a_{1} + (n - 1)d$ , $S_{n} = \frac{n}{2}(a_{1} - a_{n})$  
• Average: $\frac{\sum x}{n}$  
- Bayes Theorem: $P(A|B) = \frac{P(B|A)P(A)}{P(B)}$  
- Cartesian Coordinates: Distance $\sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$ , Midpoint $\left(\frac{x_1 + x_2}{2}, \frac{y_1 + y_2}{2}\right)$  
- Circle: Circumference $2\pi r$ , Area $\pi r^{2}$  
- Clock Angle: $|30H - \frac{11}{2}M|$  
- Combinations: $C(n, k) = \frac{n!}{k!(n - k)!}$  
- Permutations: $P(n, k) = \frac{n!}{(n - k)!}$  
- Compound Interest: $A = P(1 + R / 100)^T$  
- Conditional Probability: $P(A|B) = \frac{P(A \cap B)}{P(B)}$  
- Cone: Volume $\frac{1}{3}\pi r^2 h$ , CSA $\pi rl$ , TSA $\pi r(l + r)$  
- Cost/Profit/Loss: Profit/Loss $\% = \frac{\text{Profit/Loss}}{\text{CP}} \times 100$ , Discount $\% = \frac{\text{Discount}}{\text{MP}} \times 100$  
- Cube: Volume $a^3$ , Surface Area $6a^2$  
- Factors: For $N = p_1^{a_1} \ldots p_k^{a_k}$ , No. of factors $(a_1 + 1) \ldots (a_k + 1)$  
- Geometric Series: $a_{n} = ar^{n - 1}, S_{n} = \frac{a(r^{n} - 1)}{r - 1}$  
- LCM HCF: $\mathrm{LCM}(a, b) \times \mathrm{HCF}(a, b) = a \times b$  
- Lines: Slope $m = \frac{y_2 - y_1}{x_2 - x_1}$ , $y = mx + c$ , Parallel $m_1 = m_2$ , Perpendicular $m_1m_2 = -1$  
- Logarithms: $\log (xy) = \log x + \log y, \log (x / y) = \log x - \log y, \log x^n = n \log x$  
• Percentage: Value = Base × $\frac{Percentage}{100}$  
- Probability: $P(E) = \frac{\text{ Favorable}}{\text{Total}}$  
- Quadratic Equation: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$ , Sum of roots $-b / a$ , Product of roots $c / a$  
- Ratio Proportion: $a:b::c:d \stackrel{2^a}{\Longrightarrow} ad=bc$  
- Set Theory: $|A \cup B| = |A| + |B| - |A \cap B|$  
- Speed Time Distance: $D = S \times T$ , Relative Speed (same) $|S_1 - S_2|$ , (opposite) $S_1 + S_2$  
- Trigonometry: $\sin \theta = O / H, \cos \theta = A / H, \tan \theta = O / A, \sin^2 \theta + \cos^2 \theta = 1$  
- Volume: Cube $a^3$ , Cuboid $lwh$ , Cylinder $\pi r^2 h$ , Cone $\frac{1}{3}\pi r^2 h$ , Sphere $\frac{4}{3}\pi r^3$  
• Work Time: Work = Rate × Time