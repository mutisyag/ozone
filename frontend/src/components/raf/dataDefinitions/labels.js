import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

const getLabels = ($gettext) => {
	const labels = {
		common: getCommonLabels($gettext),
		essencrit: {
			remarks_party: $gettext('Remarks (Secretariat)'),
			remarks_os: $gettext('Remarks (Party)'),
			percent: $gettext('Percentage'),
			essencrit: $gettext('Essential and critical uses'),
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
