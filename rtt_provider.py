""" RTT Provider """

from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
from basic_types import RTT, NodeID
from coordinate_system import CoordinateSystemPoint

@dataclass
class RTTSample:
    """ Represents a RTT sample """
    node: NodeID
    point: CoordinateSystemPoint
    rtt: RTT

class RTTProvider(ABC):
    """ RTTProvider provides an RTT sample given two nodes """

    @abstractmethod
    def sample(self, x: NodeID, y: NodeID) -> RTT:
        """ Returns an RTT sample """

    @abstractmethod
    def real_rtt(self, x: NodeID, y: NodeID) -> RTT:
        """ Returns the real RTT value """

class CustomRTTProvider(RTTProvider):
    """ The custom RTTProvider receives the already built dictionary of RTT distances """

    def __init__(self, rtts: dict[NodeID, dict[NodeID, RTT]]):
        self.rtts: dict[NodeID, dict[NodeID, RTT]] = rtts

    def sample(self, x: NodeID, y: NodeID) -> RTT:
        return self.rtts[x][y] + random.random()

    def real_rtt(self, x: NodeID, y: NodeID) -> RTT:
        return self.rtts[x][y]

class RandomRTTProvider(RTTProvider):
    """ The Random RTT Provider construct the RTT map by assigning random RTTs """

    def __init__(self, num_nodes: int):
        self.rtts: dict[NodeID, dict[NodeID, RTT]] = {i: {} for i in range(num_nodes)}

        for i in range(num_nodes):
            for j in range(num_nodes):
                rtt = random.random() * 200
                self.rtts[i][j] = rtt
                self.rtts[j][i] = rtt

    def sample(self, x: NodeID, y: NodeID) -> RTT:
        return self.rtts[x][y] + random.random() * 5

    def real_rtt(self, x: NodeID, y: NodeID) -> RTT:
        return self.rtts[x][y]
