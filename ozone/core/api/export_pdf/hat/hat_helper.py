from ..util import p_c

from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors


TABLE_IMPORTS_HEADER = lambda isBlend, type: (
    (
        p_c(_('Type' if isBlend else 'Annex/group')),
        p_c(_('Blend' if isBlend else 'Substance')),
        p_c(_(f'Quantity of new substances {type}ed for approved subsectors to'
              ' which the high-ambient-temperature exemption applies')),
        '',
        '',
        p_c(_('Remarks (party)')),
        p_c(_('Remarks (secretariat)')),
    ),
    (
        '',
        '',
        p_c(_(f'New {type+"s" if type=="import" else type+"tion"} for use in '
              f'multi-split air conditioners')),
        p_c(_(f'New {type+"s" if type=="import" else type+"tion"} for use in '
              f'split ducted air conditioners')),
        p_c(_(f'New {type+"s" if type=="import" else type+"tion"} for use in '
              f'ducted commercial packaged (self-contained) air conditioners')
            ),
        '',
        ''
    ),
)

TABLE_IMPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (6, 1)),
)

TABLE_ROW_EMPTY_IMP = ((_('No data.'), '', '', '', '', '', ''),)

TABLE_ROW_EMPTY_STYLE_IMP = (
    ('SPAN', (0, 2), (-1, 2)),
    ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
)


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    import pdb; pdb.set_trace()

    return (
        p_c(_(col_1 or '')),
        p_c(_(col_2 or '')),
        p_c(_(str(obj.quantity_msac or ''))),
        p_c(_(str(obj.quantity_sdac or ''))),
        p_c(_(str(obj.quantity_dcpac or ''))),
        p_c(_(obj.remarks_party or '')),
        p_c(_(obj.remarks_os or '')),
    )
