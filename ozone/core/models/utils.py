import enum
import decimal


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
    # Be aware that some floats are represented with extra decimals, e.g.
    # 9.075 => Decimal('9.074999999999999289457264239899814128875732421875')
    # 1171.545 => Decimal('1171.545000000000072759576141834259033203125')
    # 49.95 => Decimal('49.9500000000000028421709430404007434844970703125')

    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    return float(round(decimal.Decimal(str(x)), decimals))
