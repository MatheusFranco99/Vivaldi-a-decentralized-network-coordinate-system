# Summary (with questions)

## Introduction
- What is the paper contribution?
    - The paper proposes an algorithm that predicts Internet latencies with low error. The algorithm is fully decentralized and adds low overhead.
- Vivaldi uses synthetic coordinates. What are these coordinates and what they are used for?
    - A synthetic coordinate system emulates a real coordinate system by allowing one to predict RTT values.
- What are the key points of Vivaldi’s contribution?
    - A new synthetic coordinate that outperforms previous ones.
    - The algorithm to update such a system is fully decentralized.
    - It adds no extra network communication, relying on the application’s existing communication, making it scalable.
    - It easily adapts to changes in the network condition.
    - It handles nodes with high-error samples.

## The algorithm
- Describe the algorithm’s components.
    - Each node host in the network is assigned to a synthetic coordinate.
    - Then, the algorithm attempts to update the coordinates such that an error function is minimized.
    - Vivaldi’s algorithm is independent from the chosen synthetic coordinate system. The system must only support magnitude, addition, and subtraction operations.
- Vivaldi’s algorithm is similar to a reinforcement learning algorithm. What is the error function?
    - It uses a squared-error function $E = \sum_i\sum_j (L_{ij} - || x_i - x_j || )^2$ where $L_{ij}$ is the actual RTT between i and j, and $||x_i - x_j||$ is the distance between the coordinates of i and j given by the chosen coordinate space.
- Describe the centralized algorithm.
    - Notice that the error function uses something similar to the spring energy. Minimizing the  error function means minimizing the energy of the system, bringing it to its equilibrium state.
    - From Hooke’s law, we have $F_{ij} = (L_{ij} - ||x_i - x_j||)\times u(x_i - x_j)$, where $u$ gives the direction.
    - The net force on node i is: $F_i = \sum_{j\neq i} F_{ij}$
    - To simulate the spring network evolution, we use time intervals and consider $x_i$ to move according to its net force, as $x_i = x_i + F_i\times t$ (notice that $t$ will influence how the point changes in space)
    - The centralized algorithm follows by receiving the matrix with all RTTs, the current position of all nodes and, while the error is above some threshold value, it updates the position for each node as described above.
    - Due to the algorithm’s nature, it’s not guaranteed that it will find the global minimum, i.e. it may come to rest in a local minimum.
- Describe the Vivaldi’s algorithm.
    - For a fully decentralized version, we don’t have all RTTs from the network. We need to suffice ourselves with only a handful of RTTs taken from the applciation.
    - So, whenever a node receives a new RTT, it updates its current coordinates by: $x_i = x_i + \delta \times (RTT - ||x_i - x_j || ) \times u(x_i-x_j)$
    - For default, all nodes start on the same location. To avoid the problem of being stuck on the initial configuration, it defines $u(0)$ to be a random unit-length vector, so that nodes can push themselves apart.
    - Notice that the algorithm is biased to the newest samples. We could avoid it by maintaining a list of samples. But this incurs the issue of the samples being outdated and requiring more memory for larger systems.

## Hyper parameters
- Analyse the $\delta$ hyperparameter.
    - The rate of convergence is dependent on the $\delta$ parameter. Larger $\delta$ causes faster changes, but if it’s too large, it may keep jumping back and forth.
    - A good approach is to vary it according to the certainty of the coordinates.
    - In the beginning, while still learning, it can be larger. Later, smaller values will help refining the position.
    - Thus, an adaptive $\delta$ may be $\delta= c_c \times \text{local error}$, where $c_c<1$ is some constant.
    - The issue is that we don’t take into account the accuracy of the other node. We can account with it by using $\delta = c_c \times \frac{\text{local error}}{\text{local error + remote error}}$
    - This will provide: quick convergence, low oscillation, and resilience against high-error nodes.
- How Vivaldi computes the accuracy of its own (local) estimation and the accuracy of other nodes?
    - To do it, it may maintain a list of RTT samples and compute the relative errors of new samples against a moving average.
    - More It’s a future work to derive a better predictor.

## Evaluation
- Regarding evaluation, what were the best values for $\delta$ and $c_c$ empirically found?
    - For a fixed $\delta$, 0.001 seemed to slow, 1.0 made it jump back and forth, and 0.01 showed the best stable result.
    - Using an adaptive $\delta$, $c_c$ with 0.25 showed the best result iwth quick error reduction and low oscillation.
- How Vivaldi performs against high-error nodes?
    - The paper showed how Vivaldi responded the a new set of nodes.
    - When the fixed $\delta$ is used, the old points quickly de-arrange themselves. This abrupt change also caused the new nodes to take longer to find their places.
    - With the adaptive $\delta$, the old nodes kept their position stable while the new nodes could also find their places faster.
- How Vivaldi deals with bad communication patterns?
    - If, in a network, the nodes keep only communication with its nearest neighbours, global relations start to get worse.
    - This can be fixed by enforcing the node to do some long-range communications. But how much long is necessary?
    - Suppose, at each step, the node communicates with a far away neighbour with probability $p$, and with a close neighbour with probability $1-p$.
    - Higher $p$ are better for faster convergence, but even for a small $p$ of 5% the bad communication effect is already avoided.
- How Vivaldi adapts to network chances?
    - According to the experiments, Vivaldi quickly recovered after a subtle change in the network configuration.
- How Vivaldi improves with the number of neighbours?
    - It seems that collecting samples from nearby nodes improve the prediction accuracy.
    - Also, the number of neighbours also affect the accuracy. The performance improved until 32 neighbours, after which it didn’t improve much.

## Coordinat space system
- Regarding coordinate space systems, why no system can be ideal?
    - Almost any coordinate space one may consider will respect the triangle inequality.
    - But that’s not a rule in practice. It can happen that some nodes violate the inequality.
    - However, because these violations are not the majority of cases, we can still expect that our systems will work fine.
- How the dimension of the Euclidean space influences Vivaldi’s result?
    - The first system we think about is the Euclidian coordinate space.
    - The main question is: how many dimensions are needed?
    - A principal component analysis execution on real data suggested 2 to 3 dimensions (a surprising result given the complexity of the internet)
    - The paper experimented with 2, 3 , and 5 dimensions. No extra gain was obtained by using more than 3 dimensions.
- How spherical coordinates compares to the Euclidean space?
    - Intuitively, spherical coordinate systems would perform better.
    - However, in practice, it behaves similarly to the 2D Euclidean space.
    - This implies that it’s concentrating the points on a small region of the sphere.
    - The underlying reason may be that the Internet doesn’t wraps around the Earth as expected. E.g., few links connect Asia to Europe. Korean packets crosses to oceans to get to Israel. Thus, the model doesn’t take into account that these packets avoid the Asia path.
- Explain the height vector system and its motivation.
    - Height vector consists of Euclidean coordinate systems augmented with a height.
    - The height models the time a packet takes to travel the access link from the node to the core.
    - Notice than, instead of subtracting, the packet must travel the two nodes’ heights. So the heights are added.
    - The height vector system performed better than both 2D and 3D Euclidean coordinates.
- How the height vector deals with dependent regions?
    - The paper showed an example of Brazilian nodes that send their traffic through the United States.
    - With the height vector, these Brazilian nodes ended up in the United States region, but 95ms (the delay from Brazil to the US) above it.

## Related and future work
- What is an important difference between PIC and Vivaldi?
    - Both PIC and Vivaldi are decentralized. But, while Vivaldi is robust to high error nodes, PIC is robust to malicious participants through a test based on the triangle inequality.
    - Also, PIC is built on top of a discovery protocol, and it can use such protocol to get RTT samples.
- What coordinate system is left unstudied but can improve the algorithm?
    - The hyperbolic coordinate system is promising but wasn’t tested in the paper. It’s a future work to compare it to the height vector system.
