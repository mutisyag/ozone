<template>
  <div v-if="info">

    <form class="form-sections">
      <b-card>
        <div class="form-fields" v-for="field in info.form_fields" :key="field.name">
          <div class="field-wrapper">
            <label>{{field.label}}</label>
            <fieldGenerator :fieldInfo="{index:field.name, tabName: info.name, field:field.name}" :disabled="$store.getters.can_edit_data" :field="field" />
          </div>
        </div>
      </b-card>
    </form>

    </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'

export default {

	name: 'Tab1',

	props: {
		info: Object
	},

	created() {
	},

	components: { fieldGenerator },

	data() {
		return {

		}
	}

}
</script>

<style lang="css" scoped>
</style>
