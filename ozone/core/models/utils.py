import enum
from decimal import Decimal, ROUND_HALF_UP


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
    # First of all create a Decimal representation of x
    d = Decimal.from_float(x)
    # Be aware that at this point, for example, if:
    # d = decimal.Decimal.from_float(9.075)
    # then
    # d is Decimal('9.074999999999999289457264239899814128875732421875').
    #
    # This means that the smart thing to do is to quantize it to decimals + 1
    # to obtain Decimal('9.075') *and then* apply the half-up rounding to the
    # desired number of decimals to obtain 9.08
    # (in the above example, decimals == 2)
    exp1 = Decimal(f'1.{"0" * (decimals + 1)}')
    exp2 = Decimal(f'1.{"0" * (decimals)}') if decimals > 0 else Decimal('1')
    d = d.quantize(exp1 ,ROUND_HALF_UP).quantize(exp2, ROUND_HALF_UP)

    return float(d)
