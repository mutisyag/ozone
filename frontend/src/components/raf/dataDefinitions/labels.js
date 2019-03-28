import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

const getLabels = ($gettext) => {
	const labels = {
		common: getCommonLabels($gettext),
		essencrit: {
			remarks_party: $gettext('Remarks (Secretariat)'),
			remarks_os: $gettext('Remarks (Party)'),
			percent: $gettext('Percentage'),
			essen_crit_type: $gettext('Type of use'),
			essencrit: $gettext('Essential and critical uses'),
			quantity_msac: $gettext('New production for use in multi-split air conditioners	'),
			quantity_sdac: $gettext('New production for use in split ducted air conditioners	'),
			quantity_dcpac: $gettext('New production for use in ducted commercial packaged (self-contained) air conditioners	'),
			hat_production_remarks_secretariat: $gettext('Comments (Secretariat)'),
			hat_production_remarks_party: $gettext('Comments (Party)'),
			group: $gettext('Annex/group'),
			substance: $gettext('Ozone depletig substances'),
			quantity_exempted: $gettext('Amount exempted'),
			quantity_production: $gettext('Amount acquired by production'),
			quantity_import: $gettext('Amount acquired by import & countries of manufacture'),
			quantity_acquired: $gettext('Total acquired'),
			quantity_authorized_not_acquired: $gettext('Authorized but not acquired'),
			on_hand_start_year: $gettext('On hand start of the year'),
			available_for_use: $gettext('Available for use'),
			quantity_used: $gettext('Used'),
			quantity_exported: $gettext('Amount exported'),
			quantity_destroyed: $gettext('Amount destroyed'),
			on_hand_end_year: $gettext('On hand end of year'),
			validation: $gettext('Status')
		}
	}
	return labels
}

export {
	getLabels
}
