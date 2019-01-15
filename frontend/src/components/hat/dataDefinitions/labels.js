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
			prop1: $gettext('Proprietatea 1 for testing'),
			prop2: $gettext('Proprietatea 2 for testing'),
			prop3: $gettext('Proprietatea 3 for testing')
		},
		has_produced: {
			remarks_party: $gettext('Remarks (Secretariat)'),
			remarks_os: $gettext('Remarks (Party)'),
			percent: $gettext('Percentage'),
			substance: $gettext('Substances'),
			prop1: $gettext('Proprietatea1 for testing'),
			prop2: $gettext('Proprietatea2 for testing'),
			prop3: $gettext('Proprietatea3 for testing')
		}
	}
	return labels
}

export {
	getLabels
}
