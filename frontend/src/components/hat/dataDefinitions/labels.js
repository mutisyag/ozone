import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

const getLabels = ($gettext) => {
	const labels = {
		common: getCommonLabels($gettext),
		has_imports: {
			substance: $gettext('Substances'),
			blend: $gettext('Blend'),
			group: $gettext('Group'),
			percent: $gettext('Percentage'),
			remarks_os: $gettext('Remarks (Secretariat)'),
			remarks_party: $gettext('Remarks (Party)'),
			quantity_msac: $gettext('New imports for use in multi-split air conditioners'),
			quantity_sdac: $gettext('New imports for use in split ducted air conditioners'),
			quantity_dcpac: $gettext('New imports for use in ducted commercial packaged (self-contained) air conditioners'),
			hat_imports_remarks_secretariat: $gettext('Comments (Secretariat)'),
			hat_imports_remarks_party: $gettext('Comments (Party)')
		},
		has_produced: {
			remarks_party: $gettext('Remarks (Secretariat)'),
			remarks_os: $gettext('Remarks (Party)'),
			percent: $gettext('Percentage'),
			substance: $gettext('Substances'),
			quantity_msac: $gettext('New production for use in multi-split air conditioners	'),
			quantity_sdac: $gettext('New production for use in split ducted air conditioners	'),
			quantity_dcpac: $gettext('New production for use in ducted commercial packaged (self-contained) air conditioners	'),
			hat_production_remarks_secretariat: $gettext('Comments (Secretariat)'),
			hat_production_remarks_party: $gettext('Comments (Party)')
		}
	}
	return labels
}

export {
	getLabels
}
