import enum
import math


@enum.unique
class RatificationTypes(enum.Enum):
    """
    General enum of ratification types; should be useful in other models too
    """

    ACCESSION = 'Accession'
    APPROVAL = 'Approval'
    ACCEPTANCE = 'Acceptance'
    RATIFICATION = 'Ratification'
    SUCCESSION = 'Succession'
    SIGNING = 'Signing'


def model_to_dict(instance, fields=None, exclude=None):
    data = instance.__dict__
    attributes = {}
    for key, value in data.items():
        if fields and key not in fields:
            continue
        if exclude and key in exclude:
            continue
        attributes[key] = data[key]
    return attributes


def round_half_up(x, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(x * multiplier + 0.5 * multiplier) / multiplier
