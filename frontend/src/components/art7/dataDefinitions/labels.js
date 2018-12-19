import commonLabels from '@/components/common/dataDefinitions/labels'

const labels = {
	general: commonLabels,
	has_imports: {
		substance: 'Substances',
		blend: 'Blend',
		group: 'Group',
		percent: 'Percentage',
		source_party: 'Exporting party for quantities reported as imports',
		quantity_total_new: 'Total quantity imported for all uses (new)',
		quantity_total_recovered: 'Total quantity imported for all uses (recovered and reclaimed)',
		quantity_feedstock: 'Quantity of new substances imported as feedstock',
		quantity_exempted: 'Quantity of new substance imported for exempted essential, critical, high-ambient-temperature or other uses',
		quantity_essential_uses: 'Essential use, other than L&A',
		decision_essential_uses: 'Essential use, other than L&A',
		quantity_critical_uses: 'Critical use',
		decision_critical_uses: 'Critical use',
		quantity_high_ambient_temperature: 'High ambient temperature',
		decision_high_ambient_temperature: 'High ambient temperature',
		quantity_process_agent_uses: 'Process agent uses',
		decision_process_agent_uses: 'Process agent uses',
		quantity_laboratory_analytical_uses: 'Laboratory and analytical',
		decision_laboratory_analytical_uses: 'Laboratory and analytical',
		quantity_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		decision_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		quantity_other_uses: 'Other/unspecified',
		decision_other_uses: 'Other/unspecified',
		decision: 'Decision',
		quantity: 'Quantity',
		remarks_os: 'Remarks (Secretariat)',
		remarks_party: 'Remarks (Party)',
		comments_party: 'Party',
		comments_secretariat: 'Secretariat'
	},
	has_exports: {
		substance: 'Substances',
		blend: 'Blend',
		percent: 'Percentage',
		group: 'Group',
		destination_party: 'Country of destination of exports',
		quantity_total_new: 'Total quantity imported for all uses (new)',
		quantity_total_recovered: 'Total quantity imported for all uses (recovered and reclaimed)',
		quantity_feedstock: 'Quantity of new substances imported as feedstock',
		quantity_exempted: 'Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses',
		decision_exempted: 'Decision',
		quantity_essential_uses: 'Essential use, other than L&A',
		decision_essential_uses: 'Essential use, other than L&A',
		quantity_critical_uses: 'Critical use',
		decision_critical_uses: 'Critical use',
		quantity_high_ambient_temperature: 'High ambient temperature',
		decision_high_ambient_temperature: 'High ambient temperature',
		quantity_process_agent_uses: 'Process agent uses',
		decision_process_agent_uses: 'Process agent uses',
		quantity_laboratory_analytical_uses: 'Laboratory and analytical',
		decision_laboratory_analytical_uses: 'Laboratory and analytical',
		quantity_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		decision_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		quantity_other_uses: 'Other/unspecified',
		decision_other_uses: 'Other/unspecified',
		decision: 'Decision',
		quantity: 'Quantity',
		remarks_os: 'Remarks (Secretariat)',
		remarks_party: 'Remarks (Party)',
		comments_party: 'Party',
		comments_secretariat: 'Secretariat'
	},
	has_produced: {
		remarks_party: 'Remarks (Secretariat)',
		remarks_os: 'Remarks (Party)',
		percent: 'Percentage',
		quantity_critical_uses: 'Critical use',
		decision_critical_uses: 'Critical use',
		quantity_essential_uses: 'Essential use, other than L&A',
		decision_essential_uses: 'Essential use, other than L&A',
		quantity_high_ambient_temperature: 'High ambient temperature',
		decision_high_ambient_temperature: 'High ambient temperature',
		quantity_process_agent_uses: 'Process agent uses',
		decision_process_agent_uses: 'Process agent uses',
		quantity_laboratory_analytical_uses: 'Laboratory and analytical',
		decision_laboratory_analytical_uses: 'Laboratory and analytical',
		quantity_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		decision_quarantine_pre_shipment: 'Quarantine and pre-shipment applications',
		quantity_other_uses: 'Other/unspecified',
		decision_other_uses: 'Other/unspecified',
		quantity_total_produced: 'Total production for all uses',
		quantity_feedstock: 'Production for feedstock uses within your country',
		quantity_article_5: 'Production for supply to article 5 countries in accordance with articles 2a 2h and 5',
		substance: 'Substances',
		quantity_exempted: 'Production for exempted essential, critical or other uses within your country',
		decision: 'Decision',
		quantity: 'Quantity',
		comments_party: 'Party',
		comments_secretariat: 'Secretariat'
	},
	has_destroyed: {
		remarks_party: 'Remarks (Secretariat)',
		remarks_os: 'Remarks (Party)',
		percent: 'Percentage',
		quantity_destroyed: 'Quantity destroyed',
		substance: 'Substances',
		blend: 'Blend',
		comments_party: 'Party',
		comments_secretariat: 'Secretariat'
	},
	has_nonparty: {
		remarks_party: 'Remarks (Secretariat)',
		remarks_os: 'Remarks (Party)',
		percent: 'Percentage',
		quantity_import_new: 'Quantity of imports from non-parties (new)',
		quantity_import_recovered: 'Quantity of imports from non-parties (recovered)',
		quantity_export_new: 'Quantity of exports to non-parties (new)',
		quantity_export_recovered: 'Quantity of exports to non-parties (recovered)',
		substance: 'Substance',
		blend: 'Blend',
		trade_party: 'Exporting party for quantities reported as imports or country of destination of exports'
	},
	has_emissions: {
		facility_name: 'Facility name or identifier',
		quantity_generated: 'Amount [generated] (tonnes)',
		quantity_feedstock: 'Amount used for feedstock',
		quantity_destroyed: 'Amount destroyed',
		quantity_emitted: 'Amount of emissions',
		remarks_party: 'Remarks (Secretariat)',
		remarks_os: 'Remarks (Party)',
		comments_party: 'Party',
		comments_secretariat: 'Secretariat'
	}
}

export default labels
