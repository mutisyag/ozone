from .prodcons.prod_imp_exp import ProdImpExpReport
from .hfc_baseline import HFCBaselineReport
from ..art7 import Art7RawdataReport

registry = [
    ProdImpExpReport,
    HFCBaselineReport,
    Art7RawdataReport,
]

by_name = {r.name: r for r in registry}
