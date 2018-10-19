import { intro_fields, reporting_party, substanceMaker } from './questionnaire_fields.js';

var form = {
  tabs: {
      sub_info: {
      intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
      title: 'Questionnaire',
      name: 'sub_info',
      isInvalid: false,
      party: {
        label: 'Party',
        name: 'party',
        selected: 'China',
        type: 'text',
        validation: 'required',
        disabled: true,
      },
      reporting_year: {
        label: 'Reporting Period',
        name: 'reporting_year',
        selected: '2016',
        type: 'text',
        validation: 'required',
        disabled: true,
      },
      description: '',
      // used for identification when adding labels
      name: 'form_intro',
      form_fields: reporting_party
    },
    tab_1: {
      intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
      title: 'Questionnaire',
      name: 'questionaire_questions',
      isInvalid: false,
      party: {
        label: 'Party',
        name: 'party',
        selected: 'China',
        type: 'text',
        validation: 'required',
        disabled: true,
      },
      reporting_year: {
        label: 'Reporting Period',
        name: 'reporting_year',
        selected: '2016',
        type: 'text',
        validation: 'required',
        disabled: true,
      },
      description: '',
      // used for identification when adding labels
      form_fields: intro_fields
    },
    tab_3: {
      intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
      title: 'Data on exports',
      name: 'export_question',
      subtitle: 'in metric tonnes (not ODP tonnes)',
      description: 'Annexes A, B, C and E substances',
      isInvalid: false,
      section_subheaders: [
        {
          label: "1",
          name: 'substances',
          sort: 1,
          type: 'string',
        },
        {
          label: "2",
          name: 'destination_party',
          sort: 1,
          type: 'string',
          tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
        },
        {
          label: "New <br> 3",
          name: 'quantity_total_new',
          sort: 1,
          type: 'number',
        },
        {
          label: "Recovered and Reclaimed <br> 4",
          name: 'quantity_total_recovered',
          sort: 1,
          type: 'number',
        },
        {
          label: "<br> 5",
          name: 'quantity_feedstock',
          sort: 1,
          type: 'number',
        },
        {
          label: "Quantity <br> 6",
          name: 'quantity_exempted',
          sort: 1,
          type: 'number',
        },
        {
          label: "Decision / type of use**** or Remark <br> 7",
          name: 'decision',
        },
      ],

      section_headers: [
        {
          label: "Substances",
        },
        {
          label: "Country of Destination of Exports",
          tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
        },
        {
          label: "Total Quantity Exported for All Uses",
          colspan: 2,
        },
        {
          label: "Quantity of New Substances Exported as Feedstock",
          tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).',
        },
        {
          label: "Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses",
          colspan: 2,
          tooltip: 'Against each substance exported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
        }
      ],

      form_fields: [],
 
      comments: [
        {
          name: 'comments_party',
          selected: '',
          type: 'textarea',
          label: 'Party Comments',
        },
        {
          name: 'comments_secretariat',
          selected: '',
          type: 'textarea',
          label: 'Secretariat Comments',
        },
      ],
      footnotes: ['[1] Tonne = Metric ton.'],
    },

    tab_2: {
      intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
      title: 'Data on imports',
      name: 'import_question',
      comments: [
        {
          name: 'comments_party',
          selected: '',
          type: 'textarea',
          label: 'Party Comments',
        },
        {
          name: 'comments_secretariat',
          selected: '',
          type: 'textarea',
          label: 'Secretariat Comments',
        },
      ],
      subtitle: 'in metric tonnes (not ODP tonnes)',
      description: 'Annexes A, B, C and E substances',
      section_subheaders: [
        {
          label: "1",
          name: 'substances',
          sort: 1,
          type: 'string',
        },
        {
          label: "2",
          name: 'destination_party',
          sort: 1,
          type: 'string',
          tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
        },
        {
          label: "New <br> 3",
          name: 'quantity_total_new',
          sort: 1,
          type: 'number',
        },
        {
          label: "Recovered and Reclaimed <br> 4",
          name: 'quantity_total_recovered',
          sort: 1,
          type: 'number',
        },
        {
          label: "<br> 5",
          name: 'quantity_feedstock',
          sort: 1,
          type: 'number',
        },
        {
          label: "Quantity <br> 6",
          name: 'quantity_exempted',
          sort: 1,
          type: 'number',
        },
        {
          label: "Decision / type of use**** or Remark <br> 7",
          name: 'decision',
        },
      ],

      section_headers: [
        {
          label: "Substances",
        },
        {
          label: "Exporting party for quantities reported as imports",
          tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
        },
        {
          label: "Total Quantity Imported for All Uses",
          colspan: 2,
        },
        {
          label: "Quantity of New Substances Imported as Feedstock",
          tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).',
        },
        {
          label: "Quantity of new substance imported for exempted essential, critical, high-ambient-temperature or other uses",
          colspan: 2,
          tooltip: 'Against each substance imported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
        }
      ],

      form_fields: [],
      isInvalid: false,
      footnotes: ['[1] Tonne = Metric ton.'],
    },
    tab_4: {
      intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
      title: 'Data on production',
      name: 'production_question',
      subtitle: 'in metric tonnes (not ODP tonnes)',
      isInvalid: false,
      description: 'Annexes A, B, C and E substances',
      form_fields: [],
      comments: '',
      section_subheaders: [
        {
          label: "1",
          name: 'substances',
          sort: 1,
          type: 'string',
        },
        {
          label: "2",
          name: 'quantity_total_produced',
          sort: 1,
          type: 'number',
        },
        {
          label: "3",
          name: 'quantity_feedstock',
          sort: 1,
          type: 'number',
        },
        {
          label: "4 <br> Quantity",
          name: 'quantity_feedstock',
          sort: 1,
          type: 'number',
        },
        {
          label: "Decision / type of use <br> 5",
          name: 'quantity_exempted',
          sort: 1,
          type: 'string',
        },
        {
          label: "6",
          name: "quantity_article_5",
          sort: 1,
          type: 'number'
        },
      ],

      section_headers: [
        {
          label: "Substances",
        },
        {
          label: "Total production for all uses",
        },
        {
          label: "Production for feedstock uses within your country",
        },
        {
          label: "Production for exempted essential, critical or other uses within your country*",
          colspan: 2,
          tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
        },
        {
          label: "Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5"
        }
      ],
      comments: [
        {
          name: 'comments_party',
          selected: '',
          type: 'textarea',
          label: 'Party Comments',
        },
        {
          name: 'comments_secretariat',
          selected: '',
          type: 'textarea',
          label: 'Secretariat Comments',
        },
      ],
    },
    tab_5: {
      intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
      title: 'Data on destruction',
      name: 'destruction_question',
      subtitle: 'in metric tonnes (not ODP tonnes)',
      description: 'Annexes A, B, C and E substances',
      isInvalid: false,
      // used for identification when adding labels
      form_sections: [{
          title: 'Section 1',
          description: "",
          name: 'imports_table',
          form_fields: null
        },
        // {
        // 	title: 'test form section 2 title',
        // 	description: "test form section 2 description",
        // 	name: 'form_section_2',
        // 	form_fields: [
        // 	]
        // },
      ],
      comments: '',
    },
    tab_6: {
      intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
      title: 'Data on nonparty',
      name: 'nonparty_question',
      subtitle: 'in metric tonnes (not ODP tonnes)',
      description: 'Annexes A, B, C and E substances',
      isInvalid: false,
      // used for identification when adding labels
      form_sections: [{
          title: 'Section 1',
          description: "",
          name: 'imports_table',
          form_fields: null
        },
        // {
        // 	title: 'test form section 2 title',
        // 	description: "test form section 2 description",
        // 	name: 'form_section_2',
        // 	form_fields: [
        // 	]
        // },
      ],
      comments: '',
    },
    attachements: [
      {
        name: 'asd',
        url: 'www.google.com',
        id: 1,
      },
      {
        name: 'asd1',
        url: 'www.google.com',
        id: 2,
      },
      {
        name: 'asd2',
        url: 'www.google.com',
        id: 3,
      },
      {
        name: 'asd3',
        url: 'www.google.com',
        id: 4,
      },
    ],
  },
}
export default form
