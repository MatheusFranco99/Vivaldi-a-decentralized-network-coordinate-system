""" Node """


from dataclasses import dataclass
from basic_types import RTT, NodeID
from coordinate_system import CoordinateSystemPoint
from vivaldi import RTTSample, vivaldi


@dataclass
class Node:
    """ Implements a network node """
    node_id: NodeID
    x: CoordinateSystemPoint
    local_error: float
    rtt_history: dict[NodeID, list[RTT]]
    cc: float
    ce: float

    def __init__(self, node_id: NodeID, x: CoordinateSystemPoint, cc: float, ce: float):
        self.node_id = node_id
        self.x = x
        self.local_error = 1 # 100%
        self.rtt_history = {}
        self.cc = cc
        self.ce = ce

    def remote_error(self, y: NodeID, new_rtt: RTT) -> float:
        """ Returns the remote error for the node """
        if y not in self.rtt_history:
            return 1 # 100%

        num_samples = len(self.rtt_history[y])

        if num_samples == 0:
            return 1 # 100%

        if num_samples < 5:
            mean_value = sum(self.rtt_history[y]) / num_samples
            return abs(mean_value - new_rtt) / new_rtt

        mean_value = sum(self.rtt_history[y][num_samples-5:]) / 5
        return abs(mean_value - new_rtt) / new_rtt

    def update(self, rtt_sample: RTTSample):
        """ Updates given the new RTT sample """

        y = rtt_sample.node
        rtt = rtt_sample.rtt

        # Get remote error
        remote_error = self.remote_error(y, rtt)

        # Save RTT in history
        if y not in self.rtt_history:
            self.rtt_history[y] = []
        self.rtt_history[y].append(rtt)

        # Update
        new_x, new_remote_error = vivaldi(self.x, rtt_sample, self.local_error, remote_error, self.cc, self.ce)
        self.x = new_x
        self.local_error = new_remote_error

    def get_estimation(self, other: CoordinateSystemPoint) -> RTT:
        """ Estimates RTT """
        return (self.x - other).norm()
