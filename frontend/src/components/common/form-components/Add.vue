<template>
  <div v-if="tabName">
    <div class="container">
      <h3>
        <span v-translate>Add substances</span>
      </h3>
      <small>
        <span
          v-translate
        >Filter annex groups in order to select one or more substances. A row for each substance will be added in substances table. Substances can be deleted using table controls.</span>
      </small>
      <b-input-group id="substance_annex_selector" class="mt-2" :prepend="$gettext('Annex groups')">
        <multiselect
          :placeholder="$gettext('Select option')"
          @input="prepareSubstances"
          :multiple="true"
          label="text"
          trackBy="value"
          v-model="selected_groups.selected"
          :options="selected_groups.options"
        />
      </b-input-group>
      <b-input-group id="substance_selector" class="mb-2 mt-2" :prepend="$gettext('Substances')">
        <multiselect
          :placeholder="$gettext('Select option')"
          :clear-on-select="false"
          :hide-selected="true"
          :close-on-select="false"
          label="text"
          trackBy="value"
          :multiple="true"
          v-model="selected_substance.selected"
          @change="updateGroup($event)"
          :options="selected_substance.options"
        />
      </b-input-group>
      <b-btn-group>
        <b-btn
          id="add-substance-button"
          v-if="selected_substance.selected"
          :disabled="!selected_substance.selected.length"
          @click="addSubstance"
          variant="primary"
        >
          <span
            v-translate="selected_substance.selected.length ? {length: selected_substance.selected.length} : {length: ''}"
          >Add %{length} rows</span>
        </b-btn>
        <b-btn v-if="selected_substance.selected" @click="resetData">
          <span v-translate>Cancel</span>
        </b-btn>
      </b-btn-group>
    </div>
  </div>
</template>

<script>

import Multiselect from '@/components/common/ModifiedMultiselect'
import { getAlerts } from '@/components/common/dataDefinitions/alerts'

export default {

  props: {
    tabName: String
  },

  components: {
    Multiselect
  },

  computed: {
    substances() {
      return this.$store.state.initialData.substances
    }
  },

  mounted() {
    this.prepareGroups()
  },

  data() {
    return {
      selected_substance: {
        selected: null,
        group: null,
        options: [],
        alerts: getAlerts(this.$gettext)
      },

      selected_groups: {
        selected: [],
        options: []
      },

      group_field: {
        label: '',
        name: '',
        substance: null
      }
    }
  },

  created() {
  },

  methods: {

    prepareSubstances() {
      this.selected_substance.options = []
      this.selected_substance.selected = []
      this.substances.forEach(substance => {
        if (this.selected_groups.selected.length) {
          if (this.selected_groups.selected.includes(substance.group.group_id)) {
            this.selected_substance.options.push({ text: substance.text, value: substance.value })
          }
        } else {
          this.selected_substance.options.push({ text: substance.text, value: substance.value })
        }
      })
    },

    pushUnique(array, item) {
      if (array.indexOf(item) === -1) {
        array.push(item)
      }
    },

    prepareGroups() {
      this.substances.forEach(substance => {
        if (!this.selected_groups.options.find(option => option && option.value === substance.group.group_id)) {
          this.selected_groups.options.push({ text: substance.group.group_id, value: substance.group.group_id })
        }
      })
      this.prepareSubstances()
    },

    updateGroup(selected_substance) {
      this.substances.forEach(substance => {
        if (selected_substance.includes(substance.value)) {
          this.group_field.label = substance.group.group_id
          this.group_field.name = substance.group.group_id
        }
      })
    },

    addSubstance() {
      this.updateGroup(this.selected_substance.selected)

      const { default_properties } = this.$store.state.form.tabs[this.tabName]
      const typeOfCountryFields = ['destination_party', 'source_party', 'trade_party']
      let currentTypeOfCountryField = ''
      const willNotAdd = []

      typeOfCountryFields.forEach(type => {
        if (default_properties.hasOwnProperty(type)) currentTypeOfCountryField = type
      })

      for (const subst of this.selected_substance.selected) {
        let fieldExists = false
        for (const existing_field of this.$store.state.form.tabs[this.tabName].form_fields) {
          if (parseInt(existing_field.substance.selected) === subst && (!currentTypeOfCountryField || existing_field[currentTypeOfCountryField].selected === null)) {
            fieldExists = true
            willNotAdd.push(subst)
            break
          }
        }
        // substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
        if (!fieldExists) {
          this.$store.dispatch('createSubstance', {
            $gettext: this.$gettext,
            substanceList: [subst],
            currentSectionName: this.tabName,
            groupName: this.group_field.name,
            country: null,
            blendList: null,
            prefillData: null
          })
        }
      }

      const willNotAddSubstanceNames = []
      willNotAdd.length && willNotAdd.forEach(id => {
        const { text } = this.substances.find(substanceDisplay => substanceDisplay.value === id)
        if (text) {
          willNotAddSubstanceNames.push(text)
        }
      })
      willNotAddSubstanceNames.length && this.$store.dispatch('setAlert', {
        $gettext: this.$gettext,
        message: { __all__: [`${this.alerts.substance_already_exists} : ${willNotAddSubstanceNames.join(', ')}, <br> ${currentTypeOfCountryField ? this.alerts.select_country_before_adding_again : ''}`] },
        variant: 'danger'
      })
      this.resetData()
    },

    resetData() {
      this.selected_substance.selected = []
      this.selected_substance.options = []
      this.selected_groups.selected = []
      this.group_field = {
        label: '',
        name: '',
        substance: null
      }
      this.prepareSubstances()
    },

    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, '')
    }
  },

  watch: {
    substances: {
      handler() {
        this.prepareGroups()
      }
    }
  }

}
</script>
