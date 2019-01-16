<template>
  <div v-if="field">
    <div v-if="field.type === 'text' || field.type === 'number' || field.type === 'date' || field.type ==='email'">
        <input :id="fieldInfo ? fieldInfo.field : ''" @keyup="validateInput" @change="updateFormField" :disabled="disabled" class="form-control" v-model="currentTyping" :type="field.type ==='number' ? 'text' : field.type">
    </div>
    <b-form-radio-group :id="field.name" @change="updateFormFieldWithTabs" :disabled="disabled" v-else-if="field.type === 'radio'" :checked="field.selected" :options="field.options"></b-form-radio-group>
    <b-form-checkbox :id="id" @change="updateFormFieldWithTabs" :disabled="field.disabled" v-else-if="field.type === 'checkbox'" v-model="currentTyping"></b-form-checkbox>
		<div v-else-if="field.type === 'select'">
			<multiselect
				:multiple="false"
				label="text"
				trackBy="value"
				@input="updateFormField($event)"
				:disabled="disabled"
				v-model="currentTyping"
				:options="fieldOptions" />
		</div>
    <textarea @change="updateFormField"  :disabled="disabled" class="form-control" v-else-if="field.type === 'textarea'"  v-model="currentTyping"></textarea>
  </div>
</template>

<script>
import Multiselect from '@/components/common/ModifiedMultiselect'

export default {

	props: {
		field: Object,
		disabled: { type: Boolean, default: () => false },
		fieldInfo: Object,
		id: String
	},
	components: {
		Multiselect
	},
	created() {
		this.currentTyping = this.field.selected
		if (this.field.type === 'select') {
		// Some numbers can arrive here (usually after prefill) as strings.
		// This issue affects only the select because of the pair (text - value) that needs to match
			this.currentTyping = Number(this.field.selected) || this.field.selected
		}
	},

	data() {
		return {
			currentTyping: null
		}
	},

	computed: {
		fieldOptions() {
			return this.field.options
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

		updateFormField(e) {
			if (this.field.type !== 'select') {
				this.validateInput()
				// empty strings in number field are not accepted in backend, so we need to transform every '' into a null for type === number
				if (this.currentTyping === '' && this.field.type === 'number') {
					console.log('here')
					this.$store.commit('updateFormField', { value: null, fieldInfo: this.fieldInfo })
					return
				}
				this.$store.commit('updateFormField', { value: this.currentTyping, fieldInfo: this.fieldInfo })
			} else {
				this.$store.commit('updateFormField', { value: e, fieldInfo: this.fieldInfo })
			}
		},

		updateFormFieldWithTabs(event) {
			this.$store.commit('updateFormField', { value: event, fieldInfo: this.fieldInfo })
		}

	},
	watch: {
		'field.selected': {
			handler() {
				this.currentTyping = this.field.selected
			}
		}
	}
}
</script>

<style lang="css" scoped>
</style>
