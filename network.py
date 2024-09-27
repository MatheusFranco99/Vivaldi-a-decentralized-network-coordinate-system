""" Network """

import copy
from basic_types import RTT, NodeID
from coordinate_system import CoordinateSystemPoint
from node import Node
from vivaldi import RTTSample

class Network:
    """ Network """

    def __init__(self, num_nodes: int, initial_point: CoordinateSystemPoint, cc: float, ce: float):
        self.nodes: dict[NodeID, Node] = {i: Node(i, copy.copy(initial_point), cc, ce) for i in range(num_nodes)}

    def update(self, rtt_samples: dict[NodeID, list[RTTSample]]):
        """ Updates by processing all samples """

        for node, samples in rtt_samples.items():
            for sample in samples:
                self.nodes[node].update(sample)

    def get_estimations(self) -> dict[NodeID, dict[NodeID, RTT]]:
        """ Generate estimations """
        estimations: dict[NodeID, dict[NodeID, RTT]] = {node: {} for node in self.nodes}

        for node_id, node in self.nodes.items():
            for other_node_id, other_node in self.nodes.items():
                if node_id == other_node_id:
                    continue
                estimations[node_id][other_node_id] = node.get_estimation(other_node.x)

        return estimations
