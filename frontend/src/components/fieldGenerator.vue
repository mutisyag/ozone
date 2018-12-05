<template>
  <div v-if="field">
    <div v-if="field.type === 'text' || field.type === 'number' || field.type === 'date' || field.type ==='email'">
        <input @keyup="validateInput" @change="updateFormField" :disabled="disabled" class="form-control" v-model="currentTyping" :type="field.type ==='number' ? 'text' : field.type">
    </div>
    <b-form-radio-group @change="updateFormFieldWithTabs" :disabled="disabled" v-else-if="field.type === 'radio'" :checked="field.selected" :options="field.options"></b-form-radio-group>
    <b-form-select @change="updateFormField"  :disabled="disabled" v-else-if="field.type === 'select'" :value="field.selected" :options="field.options"></b-form-select>
    <textarea @change="updateFormField"  class="form-control" v-else-if="field.type === 'textarea'" :value="field.selected"></textarea>
  </div>
</template>

<script>
export default {

	name: 'fieldGenerator',
	props: {
		field: Object,
		disabled: { type: Boolean, default: () => false },
		fieldInfo: Object
	},

	created() {
		this.currentTyping = this.field.selected
	},

	data() {
		return {
			currentTyping: null
		}
	},

	methods: {
		validateInput() {
			if (this.field.type === 'number') {
				const valid = /^-?\d+\.\d*$|^-?[\d]*$/
				const number = /-\d+\.\d*|-[\d]*|[\d]+\.[\d]*|[\d]+/
				if (this.currentTyping && !valid.test(this.currentTyping)) {
					const n = this.currentTyping.match(number)
					this.currentTyping = n ? n[0] : ''
				}
			}
		},

		updateFormField() {
			this.validateInput()
			this.$store.commit('updateFormField', { value: this.currentTyping, fieldInfo: this.fieldInfo })
		},

		updateFormFieldWithTabs(event) {
			this.$store.commit('updateFormField', { value: event, fieldInfo: this.fieldInfo })
		}

	},
	watch:{		
		'field.selected': {
			handler() {
				this.currentTyping = this.field.selected
			},
		}
	}
}

</script>

<style lang="css" scoped>
</style>
