<template>
  <div v-if="tabName">
    <b-row>
      <b-col lg="9">
        <b-input-group
          id="categories_selector"
          class="mb-2 mt-2"
          :prepend="$gettext('Add categories')"
        >
          <multiselect
            :placeholder="$gettext('Select option')"
            :clear-on-select="false"
            :hide-selected="true"
            :close-on-select="false"
            label="text"
            trackBy="value"
            :multiple="true"
            v-model="selected_categories.selected"
            :options="countries"
          />
        </b-input-group>
      </b-col>
      <b-col class="flex-center">
        <b-btn-group>
          <b-btn
            :disabled="!selected_categories.selected.length"
            @click="addEntries"
            variant="primary"
          >
            <span
              v-translate="selected_categories.selected.length ? {length: selected_categories.selected.length} : {length: ''}"
            >Add %{length} categories</span>
          </b-btn>
          <b-btn v-if="selected_categories.selected.length" @click="resetData">
            <span v-translate>Cancel</span>
          </b-btn>
        </b-btn-group>
      </b-col>
    </b-row>
  </div>
</template>

<script>

import Multiselect from '@/components/common/ModifiedMultiselect'

export default {

  props: {
    tabName: String,
    index: Number
  },

  components: {
    Multiselect
  },

  computed: {
    countries() {
      return this.$store.state.initialData.criticalUseCategoryList
    }
  },

  mounted() {
  },

  data() {
    return {
      selected_categories: {
        selected: []
      }
    }
  },

  created() {
  },

  methods: {
    resetData() {
      this.selected_categories.selected = []
    },
    addEntries() {
      this.$store.commit('addCategoryEntry', { tabName: this.tabName, index: this.index, categoryList: this.selected_categories.selected })
      this.resetData()
    }
  }
}
</script>
