""" Simulator """


from dataclasses import dataclass
import random
import numpy as np
from basic_types import NodeID
from network import Network
from coordinate_system import CoordinateSystemPoint
from rtt_provider import RTTProvider, RTTSample
import matplotlib.pyplot as plt
import scienceplots

@dataclass
class ModelError:
    """ Represents the model error """
    errors: dict[NodeID, dict[NodeID, float]]
    errors_lst: list[float]

    def __init__(self, errors: dict[NodeID, dict[NodeID, float]]):
        self.errors = errors
        self.errors_lst = []

    def get_errors_list(self) -> list[float]:
        """ Returns the list with errors """
        if len(self.errors_lst) > 0:
            return self.errors_lst
        for node_errors in self.errors.values():
            self.errors_lst += list(node_errors.values())
        return self.errors_lst

    def median(self) -> float:
        """ Returns the median """
        errors_list = self.get_errors_list()
        return np.median(errors_list)

    def max(self) -> float:
        """ Returns the maximum value """
        errors_list = self.get_errors_list()
        return np.max(errors_list)

    def min(self) -> float:
        """ Returns the maximum value """
        errors_list = self.get_errors_list()
        return np.min(errors_list)

class Simulator:
    """ Simulates an experiment """

    def __init__(self, num_nodes: int, initial_point: CoordinateSystemPoint, rtt_provider: RTTProvider, cc: float, ce: float):
        self.rtt_provider = rtt_provider
        self.num_nodes = num_nodes
        self.net = Network(num_nodes, initial_point, cc, ce)
        self.error: list[ModelError] = []

    def run(self, iterations: int, samples_per_node_per_iteration: int) -> None:
        """ Run iterations """

        for _ in range(iterations):

            # Generate samples
            rtt_samples: dict[NodeID, list[RTTSample]] = {}
            for node in range(self.num_nodes):
                rtt_samples[node] = []
                possible_other_nodes = [other_node for other_node in range(self.num_nodes) if other_node != node]
                random.shuffle(possible_other_nodes)
                selected_nodes = possible_other_nodes[:samples_per_node_per_iteration]
                for selected_node in selected_nodes:
                    rtt = self.rtt_provider.sample(node, selected_node)
                    rtt_samples[node].append(RTTSample(selected_node, self.net.nodes[selected_node].x, rtt))

            # Update
            self.net.update(rtt_samples)

            # Compute error
            estimations = self.net.get_estimations()
            for node, node_estimations in estimations.items():
                for other_node, estimation_value in node_estimations.items():
                    estimations[node][other_node] = abs(self.rtt_provider.real_rtt(node, other_node) - estimation_value)

            self.error.append(ModelError(estimations))

    def get_simulation_errors(self) -> tuple[list, list, list]:
        """ Returns the median, max, and min errors through iterations """
        median_values = []
        max_values = []
        min_values = []

        for error in self.error:
            median_values.append(error.median())
            max_values.append(error.max())
            min_values.append(error.min())

        return median_values, max_values, min_values

    def plot_error(self, iterations: int):
        """ Plot errors """

        with plt.style.context(["science"]):
            _, axs = plt.subplots(1, 3, figsize = (20,5))

            x = list(range(iterations))
            median_values, max_values, min_values = self.get_simulation_errors()

            axs[0].set_title("Median")
            axs[0].plot(x, median_values, linestyle = "--", marker = "o")
            axs[0].grid()

            axs[1].set_title("Max")
            axs[1].plot(x, max_values, linestyle = "--", marker = "o")
            axs[1].grid()

            axs[2].set_title("Min")
            axs[2].plot(x, min_values, linestyle = "--", marker = "o")
            axs[2].grid()

            axs[1].set_xlabel("Step")

            plt.show()
