""" Vivaldi algorithm """

from coordinate_system import CoordinateSystemPoint
from rtt_provider import RTTSample

def direction(x: CoordinateSystemPoint, y: CoordinateSystemPoint) -> CoordinateSystemPoint:
    """ Returns the unit-vector direction """
    direction_vector = (x-y)

    if direction_vector.norm() == 0:
        return x.random_unit_vector()

    return direction_vector / direction_vector.norm()

def vivaldi(x: CoordinateSystemPoint, rtt_sample: RTTSample, local_error: float, remote_error: float, cc: float, ce: float) -> tuple[CoordinateSystemPoint, float]:
    """ Performs the Vivaldi update algorithm.
        Returns the new x position and the new local error
    """

    y = rtt_sample.point
    rtt = rtt_sample.rtt

    # Sample weight
    w = local_error / (local_error + remote_error)

    # Relative error
    sample_error = ((x - y).norm() - rtt) / rtt

    # Update weighted moving average
    new_local_error = sample_error * ce * w + local_error * (1 - ce * w)

    # Update local coordinates
    delta = cc * w
    new_x = x + delta * (rtt - (x-y).norm()) * direction(x, y)

    return new_x, new_local_error
