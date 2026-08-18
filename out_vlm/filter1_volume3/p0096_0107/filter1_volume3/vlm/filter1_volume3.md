- CRC can detect all single-bit errors, all double-bit errors, any odd number of errors, and all burst errors of length less than or equal to $r$ .  
- It can detect a high percentage of burst errors longer than $r$ .

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Performing binary division incorrectly (modulo-2 arithmetic, no borrows).  
- Technique: Practice modulo-2 polynomial division. Remember to pad the data with $r$ zeros before division.

# CSMA/CD (Carrier Sense Multiple Access with Collision Detection)

CSMA/CD is a MAC protocol used in shared-medium networks like Ethernet. Stations listen before transmitting (carrier sense) and stop transmitting if a collision is detected (collision detection).

# Important Formulas and Results:

\- Slot Time: The maximum time it takes for a collision to be detected by all stations.

$$
\text { Slot   Time } = 2 \times \text { Propagation   Delay }
$$

\- Minimum Frame Size: To ensure a collision is detected before the sender finishes transmitting the frame.

$$
\text {Minimum Frame Size} = \text {Bandwidth} \times \text {Slot Time} = \text {Bandwidth} \times 2 \times \text {Propagation Delay}
$$

# Key Properties and Identities:

- Uses binary exponential backoff algorithm to resolve collisions.  
- Collision domain is the segment where collisions can occur.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing propagation delay with transmission delay. Propagation delay is time for a bit to travel, transmission delay is time to put all bits on wire.  
- Technique: Ensure units are consistent (e.g., convert Mbps to bits/second, km to meters, ms to seconds).

# Channel Utilization

Channel utilization (or efficiency) measures the fraction of time the channel is actively transmitting data, rather than being idle or transmitting overhead. It's a key performance metric for network protocols.

# Important Formulas and Results:

\- General formula:

$$
\text {Utilization} = \frac {\text {Time spent transmitting useful data}}{\text {Total time}}
$$

\- For Stop-and-Wait ARQ:

$$
U = \frac {1}{1 + 2 a}
$$

where $a = \frac{\text{Propagation Delay}}{\text{Transmission Time}} = \frac{T_p}{T_t}$ . This assumes no errors and negligible ACK transmission time.

\- For Sliding Window (Go-Back-N or Selective Repeat) with window size $W$ :

$$
U = \min \left(1, \frac {W}{1 + 2 a}\right)
$$

This assumes no errors. If $W \geq 1 + 2a$ , utilization can be 100%.

\- For Pure Aloha:

$$
S = G \cdot e ^ {- 2 G}
$$

where $S$ is throughput, $G$ is offered load. Max $S \approx 0.184$ at $G = 0.5$ .

\- For Slotted Aloha:

$$
S = G \cdot e ^ {- G}
$$

Max $S \approx 0.368$ at $G = 1$ .

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly calculating $a$ or not considering the full round-trip time.  
- Technique: Clearly identify $T_{t}$ and $T_{p}$ from the problem statement. Remember $T_{p}$ is one-way.

# Communication

Communication in networks refers to the process of exchanging information between two or more entities. It involves various modes and fundamental concepts that define how data travels.

# Key Concepts:

- Simplex: Data flows in one direction only (e.g., radio broadcast).  
- Half-Duplex: Data flows in both directions, but not simultaneously (e.g., walkie-talkie).  
- Full-Duplex: Data flows in both directions simultaneously (e.g., telephone call).  
- Bandwidth: The maximum data transfer rate of a network path, typically measured in bits per second (bps).  
- Latency (Delay): The time it takes for a data packet to travel from one point to another. Comprises transmission, propagation, processing, and queuing delays.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing bandwidth with throughput. Bandwidth is capacity, throughput is actual rate.  
- Technique: Understand the implications of each communication mode on protocol design (e.g., collision detection in half-duplex).

# Congestion Control

Congestion control mechanisms aim to prevent network collapse by regulating the rate at which senders transmit data when the network is overloaded. TCP implements several strategies for this.

# Key Concepts (TCP):

- Slow Start: Exponentially increases congestion window (cwnd) at the beginning of a connection or after a timeout. cwnd starts at 1 MSS (Maximum Segment Size) and doubles every RTT.  
- Congestion Avoidance: After cwnd reaches ssthresh (slow start threshold), cwnd increases linearly (by 1 MSS per RTT).  
- Fast Retransmit: If the sender receives three duplicate ACKs, it retransmits the lost segment without waiting for a timeout.  
- Fast Recovery: After Fast Retransmit, ssthresh is set to half of the current cwnd, and cwnd is set to ssthresh + 3 MSS. It then enters congestion avoidance.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly applying the rules for cwnd and ssthresh changes during slow start, congestion avoidance, and recovery phases.  
- Technique: Draw a graph of cwnd vs. RTT to visualize the changes. Remember the ssthresh value is halved upon a loss.

# Data Communication

Data communication encompasses the processes, technologies, and methods involved in the electronic transmission of information. It covers the physical and logical aspects of moving data between devices.

# Key Concepts:

- Signals: Electrical or electromagnetic waves used to transmit data. Can be analog or digital.  
- Modulation: Converting digital data into analog signals for transmission over analog media.  
- Demodulation: Converting analog signals back into digital data.  
- Multiplexing: Combining multiple data streams into a single stream for transmission (e.g., TDM, FDM, WDM).  
- Switching: Techniques for connecting communication paths (e.g., circuit, packet, message switching).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing modulation with encoding, or different multiplexing techniques.  
- Technique: Understand the purpose and basic mechanism of each concept.

# Distance Vector Routing

Distance Vector Routing is a dynamic routing algorithm where each router maintains a routing table (distance vector) containing the best known distance to each destination and the next hop. Routers exchange their entire routing tables with directly connected neighbors.

# Key Concepts:

\- Bellman-Ford Algorithm: The underlying algorithm for distance vector routing.

$$
D _ {x} (y) = \min _ {v} \{c (x, v) + D _ {v} (y) \}
$$

where $D_x(y)$ is the cost from $x$ to $y$ , $c(x, v)$ is cost from $x$ to neighbor $v$ , and $D_v(y)$ is $v$ 's reported cost to $y$ .

- Count-to-Infinity Problem: A major drawback where routing loops can cause costs to increase indefinitely.  
- Poisoned Reverse: A mechanism to mitigate count-to-infinity by advertising infinite cost for routes learned from a neighbor back to that neighbor.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly updating routing tables or failing to identify routing loops.  
- Technique: Simulate the routing table updates step-by-step for a given network topology and link cost changes.

# Error Detection

Error detection techniques are used to determine if errors have occurred during data transmission. They add redundant bits to the data, allowing the receiver to check for integrity.

# Key Concepts:

- Parity Check: Adds a single parity bit to make the total number of 1s even (even parity) or odd (odd parity). Detects single-bit errors.  
- Checksum: Divides data into segments, sums them (using one's complement arithmetic), and takes the one's complement of the sum as the checksum. Detects most errors, but not as robust as CRC.  
- CRC (Cyclic Redundancy Check): Most powerful error detection technique, uses polynomial division. (See CRC Polynomial topic).

# Important Formulas and Results:

\- Internet Checksum: Sum all 16-bit words (or specified size) of the data. If sum exceeds 16 bits, wrap around the carry. Take one's complement of the final sum.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Forgetting one's complement arithmetic for checksum calculations.  
- Technique: Practice checksum calculations, especially with carry bits.

# Ethernet

Ethernet is the most widely used LAN technology, standardized by IEEE 802.3. It defines the physical and Data Link Layer specifications for wired networks, primarily using CSMA/CD.

# Key Concepts:

- MAC Address: A 48-bit (6-byte) unique hardware identifier assigned to each network interface card (NIC).  
- Ethernet Frame Format: Includes Preamble, SFD (Start Frame Delimiter), Destination MAC, Source MAC, Type/Length, Data, and FCS (Frame Check Sequence/CRC).  
- Minimum/Maximum Frame Size: Standard Ethernet has a minimum frame size of 64 bytes (including header and FCS) and a maximum of 1518 bytes.  
- CSMA/CD: The access method used for shared Ethernet segments.

# Important Formulas and Results:

\- Minimum Data Size: 46 bytes (to ensure minimum frame size of 64 bytes, considering 18 bytes of header/trailer).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing the total frame size with the data payload size.  
- Technique: Memorize the Ethernet frame structure and minimum/maximum sizes.

# Fragmentation

Fragmentation is the process at the Network Layer (IP) where a large IP packet is divided into smaller fragments to traverse a network link with a smaller Maximum Transmission Unit (MTU).

# Important Formulas and Results:

\- Offset Field: In the IP header, indicates the position of the fragment's data relative to the original datagram's data, in units of 8 bytes.

$$
\text {New Offset} = \frac {\text {Original Offset} \times 8 + \text {Data Length of Fragment}}{8}
$$

- Total Length Field: In the IP header, indicates the total length of the current fragment (header + data).  
- More Fragments (MF) Flag: Set to 1 for all fragments except the last one.

# Key Properties and Identities:

- Fragmentation can occur at any router along the path.  
- Reassembly typically occurs only at the destination host.  
- The data payload of each fragment (except possibly the last) must be a multiple of 8 bytes.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly calculating the offset field or the data length of fragments, especially when the original packet's data length is not a multiple of 8.  
- Technique: Work through fragmentation problems step-by-step, ensuring each fragment's data length is a multiple of 8 (except the last) and updating the offset correctly.

# Hamming Code

Hamming code is an error-correcting code capable of detecting and correcting single-bit errors. It adds redundant parity bits at specific positions within the data.

# Important Formulas and Results:

\- Number of Parity Bits $(p)$ : To correct single-bit errors in a message of $m$ data bits, the number of parity bits $p$ must satisfy:

$$
2 ^ {p} \geq m + p + 1
$$

- Parity Bit Positions: Parity bits are placed at positions that are powers of 2 (1, 2, 4, 8, ...).  
- Parity Check: Each parity bit checks specific data bit positions. For example, parity bit at position $2^{k}$ checks all positions whose binary representation has the $k$ -th bit set.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly assigning parity bit positions or calculating parity values.  
- Technique: Systematically determine parity bit positions, then calculate parity values based on the data bits they cover. For error detection/correction, calculate syndrome bits.

# IP Addressing

IP addressing (IPv4 and IPv6) is a fundamental concept in the Network Layer, providing unique logical addresses for devices on a network. IPv4 uses 32-bit addresses, while IPv6 uses 128-bit addresses.

# Important Formulas and Results (IPv4):

- Number of Hosts: For a given subnet mask, if $h$ bits are available for host IDs, then the number of usable hosts is $2^h - 2$ (subtracting network and broadcast addresses).  
- Number of Subnets: If $s$ bits are borrowed from the host portion for subnetting, the number of subnets created is $2^s$ .  
- CIDR (Classless Inter-Domain Routing): Uses a prefix length (e.g., /24) to specify the network portion of an IP address, replacing class-based addressing.

# Key Properties and Identities:

• Network ID: All host bits are 0.  
- Broadcast ID: All host bits are 1.  
- Private IP Ranges: Reserved for private networks (e.g., 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly calculating subnet masks, network IDs, or broadcast IDs, especially with CIDR notation.  
- Technique: Convert IP addresses and subnet masks to binary for clear visualization. Practice subnetting problems extensively.

# IP Packet

An IP packet (or datagram) is the fundamental unit of data transfer in the Internet Protocol. It consists of an IP header and a data payload.

# Key Concepts (IPv4 Header Fields):

- Version (4 bits): Indicates IPv4 or IPv6.  
- Header Length (IHL, 4 bits): Length of the IP header in 32-bit words. Minimum 5 (20 bytes), maximum 15 (60 bytes).  
- Total Length (16 bits): Total length of the IP datagram (header + data) in bytes. Max 65535 bytes.  
- Identification (16 bits): Used for reassembling fragmented datagrams.  
- Flags (3 bits): Includes DF (Don't Fragment) and MF (More Fragments).  
- Fragment Offset (13 bits): Position of the fragment in the original datagram (in 8-byte units).  
- Time To Live (TTL, 8 bits): Decremented by each router; packet is discarded if TTL reaches 0. Prevents infinite loops.  
- Protocol (8 bits): Indicates the next-level protocol (e.g., 6 for TCP, 17 for UDP, 1 for ICMP).  
- Header Checksum (16 bits): Used for error detection only on the header. Recalculated at each hop.  
- Source IP Address (32 bits): Sender's IP address.  
- Destination IP Address (32 bits): Receiver's IP address.

# Common Pitfalls and Problem-Solving Techniques:

\- Pitfall: Confusing header length (in 32-bit words) with total length (in bytes).

\- Technique: Memorize the key fields and their sizes. Practice calculating header checksums.

# ICMP (Internet Control Message Protocol)

ICMP is a Network Layer protocol used by network devices, like routers, to send error messages and operational information indicating, for example, that a requested service is not available or that a host or router could not be reached.

# Key Concepts:

- Error Reporting: Reports errors such as "Destination Unreachable," "Time Exceeded," "Parameter Problem."  
- Query Messages: Used for diagnostic purposes (e.g., Echo Request/Reply for ping, Timestamp Request/Reply).  
- Traceroute: Uses ICMP Time Exceeded messages to map the path to a destination.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing ICMP's role with routing protocols or transport layer protocols. ICMP is for network diagnostics and error reporting.  
- Technique: Understand the common ICMP message types and their uses (e.g., ping uses type 8/0, traceroute uses type 11).

# LAN Technologies

LAN (Local Area Network) technologies define the standards and methods for connecting devices within a limited geographical area. Ethernet is the dominant LAN technology.

# Key Concepts:

- Ethernet (IEEE 802.3): Dominant wired LAN technology, uses CSMA/CD (for shared media) or full-duplex switching. Various speeds (10 Mbps, 100 Mbps, 1 Gbps, 10 Gbps, etc.).  
- Token Ring (IEEE 802.5): Older LAN technology, uses a token-passing mechanism for media access. Devices form a logical ring.  
- FDDI (Fiber Distributed Data Interface): High-speed token-passing LAN over fiber optics, uses dual rings for redundancy.  
- Wi-Fi (IEEE 802.11): Wireless LAN technology, uses CSMA/CA (Collision Avoidance).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing the MAC access methods (CSMA/CD vs. Token Passing vs. CSMA/CA).  
- Technique: Compare and contrast the characteristics, advantages, and disadvantages of different LAN technologies.

# MAC Protocol (Medium Access Control)

MAC protocols define how multiple stations share a common transmission medium to avoid collisions and ensure fair access. They are part of the Data Link Layer.

# Key Concepts:

- Channel Partitioning Protocols: Divide the channel into smaller, independent channels (e.g., TDMA, FDMA, CDMA).  
- Random Access Protocols: Allow stations to transmit whenever they have data, resolving collisions if they occur (e.g., Aloha, CSMA, CSMA/CD, CSMA/CA).  
- Taking-Turns Protocols: Stations take turns accessing the channel (e.g., Token Ring, Polling).

# Important Formulas and Results:

\- (See Pure Aloha, Slotted Aloha, CSMA/CD for specific formulas).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Misidentifying the type of MAC protocol or its collision resolution mechanism.  
- Technique: Understand the trade-offs between different MAC protocols (efficiency, fairness, complexity).

# Network Flow

Network flow is a concept in graph theory used to model the movement of resources through a network. In computer networks, it can represent data traffic.

# Key Concepts:

- Flow Network: A directed graph where each edge has a capacity and a flow.  
- Source and Sink: Special nodes representing the origin and destination of the flow.  
- Max-Flow Min-Cut Theorem: States that the maximum amount of flow passing from a source to a sink in a flow network is equal to the total capacity of the minimum cut.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: While Max-Flow Min-Cut is a core concept, GATE CS typically tests its conceptual understanding rather than complex numerical algorithms like Edmonds-Karp or Dinic.  
- Technique: Focus on understanding the theorem and identifying cuts in simple networks.

# Network Layer

The Network Layer (Layer 3 of the OSI model) is responsible for logical addressing, routing, and forwarding packets across different networks. IP is the primary protocol at this layer.

# Key Concepts:

- Logical Addressing: IP addresses provide unique identification for devices across the internet.  
- Routing: Determining the best path for packets to travel from source to destination.  
- Forwarding: Moving a packet from an incoming interface to an outgoing interface on a router.  
- Protocols: IP, ICMP, IGMP, Routing Protocols (RIP, OSPF, BGP).

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing Network Layer functions with Data Link Layer (MAC addressing, framing) or Transport Layer (port numbers, reliability).  
- Technique: Clearly distinguish the responsibilities of each layer in the OSI/TCP-IP model.

# Network Protocols

Network protocols are formal rules and standards that govern how devices communicate and exchange data over a network. They define the format, timing, sequencing, and error control of data transmission.

# Key Concepts:

- TCP/IP Suite: The most widely used set of protocols, forming the basis of the internet. Includes TCP, UDP, IP, HTTP, FTP, etc.  
- Layered Architecture: Protocols are organized into layers (e.g., OSI model, TCP/IP model), with each layer providing services to the layer above it.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Not knowing which protocols operate at which layer or their specific functions.  
- Technique: Create a mental map or table of protocols and their corresponding layers/functions.

# Network Switching

Network switching refers to the mechanisms used to establish connections between communicating devices in a network. Different switching techniques have varying characteristics regarding resource allocation and delay.

# Key Concepts:

- Circuit Switching: A dedicated end-to-end communication path (circuit) is established before data transfer and maintained for the duration of the communication (e.g., traditional telephone networks). Guarantees bandwidth.  
- Packet Switching: Data is broken into small, independent packets, each routed individually through the network. No dedicated path. More efficient use of bandwidth, but variable delay (e.g., Internet).  
- Message Switching: Entire messages are stored and forwarded at each intermediate node. No dedicated path. High delay.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing the characteristics of circuit vs. packet switching, especially regarding setup time, resource reservation, and delay.  
- Technique: Understand the trade-offs: Circuit switching for guaranteed QoS, Packet switching for efficiency and flexibility.

# OSI Model

The OSI (Open Systems Interconnection) model is a conceptual framework that standardizes the functions of a telecommunication or computing system into seven distinct layers. It helps in understanding network architecture and troubleshooting.

# Key Concepts:

1. Physical Layer (Layer 1): Deals with the physical transmission of raw bits over a medium (cables, connectors, voltage levels). PDU: Bit.  
2. Data Link Layer (Layer 2): Provides reliable data transfer between adjacent nodes, framing, MAC addressing, error detection/correction. PDU: Frame.  
3. Network Layer (Layer 3): Handles logical addressing (IP), routing, and forwarding packets across networks. PDU: Packet/Datagram.  
4. Transport Layer (Layer 4): Provides end-to-end communication, reliability (TCP), flow control, congestion control, port addressing. PDU: Segment (TCP), Datagram (UDP).  
5. Session Layer (Layer 5): Manages communication sessions, synchronization, dialog control.  
6. Presentation Layer (Layer 6): Handles data representation, encryption, decryption, compression.  
7. Application Layer (Layer 7): Provides network services directly to user applications (HTTP, FTP, DNS). PDU: Data/Message.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Forgetting the order of layers or the primary function/PDU of each layer.  
- Technique: Use mnemonics (e.g., "Please Do Not Throw Sausage Pizza Away") to remember the order. Focus on the first four layers, as they are most frequently tested.

# Probability

Probability theory is used in computer networks to model and analyze the performance of random access protocols (like Aloha) and to evaluate network reliability and queueing behavior.

# Key Concepts:

- Poisson Distribution: Often used to model arrival rates of packets or frames in random access protocols.  
- Throughput: The rate at which successful transmissions occur.  
- Offered Load (G): The total number of frames generated per unit of time, including retransmissions.

# Important Formulas and Results:

\- (See Pure Aloha, Slotted Aloha for specific probability-based throughput formulas).

# Common Pitfalls and Problem-Solving Techniques:

\- Pitfall: Misinterpreting the meaning of offered load (G) vs. throughput (S).

\- Technique: Understand the assumptions behind probabilistic models (e.g., Poisson arrivals, infinite number of users).

# Pure Aloha

Pure Aloha is a simple random access MAC protocol where stations transmit frames whenever they have data. If a collision occurs, the stations wait a random amount of time and retransmit.

# Important Formulas and Results:

\- Throughput (S): The rate of successful transmissions.

$$
S = G \cdot e ^ {- 2 G}
$$

where G is the offered load (total number of frames generated per frame transmission time, including retransmissions).

• Maximum Throughput ( $S_{max}$ ): Occurs when G = 0.5.

$$
S _ {m a x} = 0. 5 \cdot e ^ {- 2 \cdot 0. 5} = 0. 5 \cdot e ^ {- 1} = \frac {1}{2 e} \approx 0. 1 8 4
$$

# Key Properties and Identities:

- Collision window is $2 \times T_{\text{frame}}$ .  
- Highly inefficient due to frequent collisions.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Forgetting the factor of 2G in the exponent for pure Aloha.  
- Technique: Understand the concept of the vulnerability period for collisions.

# Routing

Routing is the process of selecting paths in a network along which to send network traffic. It involves determining the best route for packets from a source to a destination.

# Key Concepts:

- Static Routing: Routes are manually configured by an administrator. Simple for small networks.  
- Dynamic Routing: Routers exchange routing information and update their tables automatically using routing protocols. Adaptable to network changes.  
- Routing Table: A table stored in a router that maps destination network addresses to the next hop router and outgoing interface.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing routing (path selection) with forwarding (packet movement).  
- Technique: Understand how a router uses its routing table to make forwarding decisions.

# Routing Protocols

Routing protocols are the algorithms and rules that routers use to exchange routing information and build their routing tables. They are classified by their operating scope and algorithm type.

# Key Concepts:

- Interior Gateway Protocols (IGPs): Used within an Autonomous System (AS).  
- RIP (Routing Information Protocol): Distance Vector, uses hop count as metric, max 15 hops.  
- OSPF (Open Shortest Path First): Link State, uses Dijkstra's algorithm, builds a complete topology map.  
- Exterior Gateway Protocols (EGPs): Used between Autonomous Systems.  
- BGP (Border Gateway Protocol): Path Vector, used for inter-domain routing on the Internet.

\- Link State vs. Distance Vector:

- Distance Vector: Routers share their entire routing tables with neighbors. (e.g., RIP)  
- Link State: Routers share information about their directly connected links with all other routers in the AS. (e.g., OSPF)

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing RIP with OSPF, or IGPs with EGPs.  
- Technique: Know the key characteristics of each protocol (metric, algorithm type, scope). Practice Dijkstra's algorithm for OSPF-like problems.

# Sliding Window

Sliding Window protocols are flow control mechanisms that allow a sender to transmit multiple frames before receiving an acknowledgment, improving channel utilization. They use a window of sequence numbers.

# Important Formulas and Results:

- Window Size (W): The maximum number of unacknowledged frames a sender can transmit.  
- Sequence Number Bits (n): For a window size $W$ , the minimum number of bits required for sequence numbers depends on the protocol.  
- Go-Back-N: Sender window $W_S$ , Receiver window $W_R = 1$ . Sequence numbers range from 0 to $2^n - 1$ . $W_S + W_R \leq 2^n \implies W_S \leq 2^n - 1$ .  
- Selective Repeat: Sender window $W_{S}$ , Receiver window $W_{R}$ . $W_{S} = W_{R} = 2^{n - 1}$ .  
- Channel Utilization (U) for Sliding Window:

$$
U = \min \left(1, \frac {W _ {S}}{1 + 2 a}\right)
$$

where $a = T_{p} / T_{t}$ .

# Key Properties and Identities:

- Go-Back-N (GBN): If a frame is lost, the sender retransmits that frame and all subsequent frames already sent. Receiver discards out-of-order frames.  
- Selective Repeat (SR): If a frame is lost, only that specific frame is retransmitted. Receiver buffers out-of-order frames. More efficient but complex.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly determining the maximum window size for Go-Back-N vs. Selective Repeat for a given number of sequence bits.  
- Technique: Memorize the window size rules for GBN and SR. Practice calculating utilization with different window sizes and $a$ values.

# Slotted Aloha

Slotted Aloha is an improvement over Pure Aloha where time is divided into discrete slots. Stations are only allowed to transmit at the beginning of a slot, reducing the collision window.

# Important Formulas and Results:

\- Throughput (S):

$$
S = G \cdot e ^ {- G}
$$

where G is the offered load.

• Maximum Throughput ( $S_{max}$ ): Occurs when G = 1.

$$
S _ {m a x} = 1 \cdot e ^ {- 1} = \frac {1}{e} \approx 0. 3 6 8
$$

# Key Properties and Identities:

- Collision window is $1 \times T_{frame}$ .  
- Requires global time synchronization.

# Common Pitfalls and Problem-Solving Techniques:

\- Pitfall: Confusing the throughput formula with Pure Aloha (exponent is -G, not -2G).

\- Technique: Understand how slotting reduces the vulnerability period for collisions.

# Sockets

Sockets provide an Application Programming Interface (API) for network communication, allowing applications to send and receive data over a network. They are the endpoints of communication.

# Key Concepts:

- Socket Types:  
- Stream Sockets (TCP): Connection-oriented, reliable, ordered data delivery.  
- Datagram Sockets (UDP): Connectionless, unreliable, unordered data delivery.  
- Common Socket Functions (for TCP server): socket(), bind(), listen(), accept(), send(), recv(), close().  
- Common Socket Functions (for TCP client): socket(), connect(), send(), recv(), close().

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing the sequence of system calls for client vs. server, or for TCP vs. UDP.  
- Technique: Memorize the typical sequence of socket calls for both client and server applications.

# Stop and Wait

Stop and Wait is the simplest ARQ (Automatic Repeat Request) protocol for reliable data transfer. The sender transmits one frame and waits for an acknowledgment (ACK) before sending the next.

# Important Formulas and Results:

\- Transmission Time ( $T_t$ ): Time to put the entire frame on the link.

$$
T _ {t} = \frac {\text {Frame Size}}{\text {Bandwidth}}
$$

\- Propagation Delay ( $T_p$ ): Time for the first bit to travel from sender to receiver.

$$
T _ {p} = \frac {\text {Distance}}{\text {Propagation Speed}}
$$

\- Dimensionless Parameter (a): Ratio of propagation delay to transmission time.

$$
a = \frac{T_p}{T_t}
$$

\- Channel Utilization (Efficiency) ( $U$ ):

$$
U = \frac {1}{1 + 2 a}
$$

This assumes no errors and negligible ACK transmission time.

# Key Properties and Identities:

- Sender window size = 1, Receiver window size = 1.  
- Uses 1-bit sequence numbers (0 and 1).  
- Low utilization for high bandwidth-delay product links.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Forgetting to multiply $T_{p}$ by 2 for the round-trip propagation delay in the denominator of the utilization formula.  
- Technique: Always calculate $T_{t}$ and $T_{p}$ first, then $a$ , then $U$ . Pay attention to units.

# Subnetting

Subnetting is the process of dividing a larger IP network into smaller, more manageable subnetworks (subnets). It improves network efficiency, security, and reduces broadcast traffic.

# Important Formulas and Results:

- Number of Subnets: If $s$ bits are borrowed from the host portion of the IP address to create subnets, the number of subnets created is $2^s$ .  
- Number of Usable Hosts per Subnet: If $h$ bits remain for host IDs in a subnet, the number of usable hosts is $2^h - 2$ (excluding the network and broadcast addresses for that subnet).  
- Subnet Mask: A 32-bit number that distinguishes the network portion from the host portion of an IP address. All network/subnet bits are 1, all host bits are 0.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Incorrectly identifying the network ID, broadcast ID, or valid host range for a given IP address and subnet mask.  
- Technique: Convert IP addresses and subnet masks to binary. Draw out the network, subnet, and host portions. Practice finding the first/last usable IP.

# TCP (Transmission Control Protocol)

TCP is a reliable, connection-oriented, byte-stream Transport Layer protocol. It provides error control, flow control, and congestion control, making it suitable for applications requiring high data integrity.

# Key Concepts:

- Connection-Oriented: Establishes a connection using a 3-way handshake before data transfer.  
- Reliable: Uses sequence numbers, acknowledgments (ACKs), and retransmissions to ensure all data arrives correctly.  
- Flow Control: Prevents a fast sender from overwhelming a slow receiver using a receive window (rwnd).  
- Congestion Control: Prevents network congestion (see Congestion Control topic).  
- Full-Duplex: Data can flow in both directions simultaneously.  
- Header Fields: Source/Destination Port, Sequence Number, Acknowledgment Number, Window Size, Checksum, Flags (SYN, ACK, FIN, RST, PSH, URG).

# Important Formulas and Results:

• 3-Way Handshake: SYN -> SYN+ACK -> ACK.  
- 4-Way Handshake (Connection Termination): FIN -> ACK -> FIN -> ACK.

# Common Pitfalls and Problem-Solving Techniques:

- Pitfall: Confusing sequence numbers with acknowledgment numbers, or the purpose of different TCP flags.  
- Technique: Trace the sequence and acknowledgment numbers during a TCP connection setup, data transfer, and termination. Understand the role of the advertised window.

# Token Bucket