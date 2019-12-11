from .prodcons.prod_imp_exp import ProdImpExpReport
from .hfc_baseline import HFCBaselineReport

registry = [
    ProdImpExpReport,
    HFCBaselineReport,
]

by_name = {r.name: r for r in registry}
