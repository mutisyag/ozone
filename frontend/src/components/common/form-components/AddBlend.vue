<template>
	<div>
		<div class="container">
			<div>
				<h5 class="mt-2">Add predefined blends</h5>
				<small>Filter by blend types in order to select one or more blends. A row for each blend will be added in blends table. Blends can be deleted using table controls.</small>
				<b-input-group class="mt-2" prepend="Blend types">
					<multiselect
						:clear-on-select="false"
						:hide-selected="true"
						trackBy="value"
						label="text"
						:close-on-select="false"
						:multiple="true"
						@input="new_blend = null; selected_blends.selected = []"
						v-model="selected_blends.filter"
						placeholder=""
						:options="selected_blends.filters"
					></multiselect>
				</b-input-group>

				<div class="mt-2 mb-2" style="display: flex;">
					<b-input-group class="mt-2" prepend="Blends">
						<multiselect
							trackBy="value"
							:clear-on-select="false"
							:hide-selected="true"
							:close-on-select="false"
							:multiple="true"
							label="text"
							v-model="selected_blends.selected"
							@input="new_blend = null"
							placeholder=""
							:options="filteredBlends"
						></multiselect>
					</b-input-group>

				</div>
			</div>

			<div
				:key="blend.name"
				v-if="selected_blends.selected"
				v-for="blend in selected_blends.selected"
				class="small mb-2"
			>
				<div>Composition of
					<b>{{display.blends[blend].name}}</b>
				</div>
				<b-row
					v-for="(substance, substance_index) in display.blends[blend].components"
					:key="substance_index"
				>
					<b-col>{{substance.component_name}}</b-col>
					<b-col>{{substance.percentage.toLocaleString("en", {style: "percent"})}}</b-col>
				</b-row>
			</div>
			<b-btn-group>
				<b-btn
					v-if="selected_blends.selected.length"
					@click="addSubstance('selected')"
					variant="primary"
				>Add {{selected_blends.selected.length}} rows</b-btn>
				<b-btn 	v-if="selected_blends.selected.length" @click="resetData">Cancel</b-btn>
			</b-btn-group>
			<hr>

			<div v-if="!new_blend">
				<h5>Add custom blend</h5>
				<b-btn variant="primary" @click="addNewBlend">Add new blend</b-btn>
			</div>

			<div v-if="new_blend">
				<h5>Add custom blend</h5>
				<small>If a non-standard blend not listed above please indicate the blend name and the percentage by weight of each constituent controlled substance of the blend. Please pay attention to the percentage values before adding a new blend. For mistakes please contact secretariat to delete the blend.</small>
				<b-input-group class="mt-2" prepend="Blend name">
					<b-form-input type="text" @blur.native="alertIfBlendExists" v-model="new_blend.text"></b-form-input>
					<b-input-group-append>
						<b-btn @click="addSubstanceToBlend">Add substance</b-btn>
					</b-input-group-append>
				</b-input-group>
				<b-input-group
					class="mb-2 mt-2"
					v-for="(substance, substance_index) in new_blend.composition"
					:key="substance_index"
				>
					<b-input-group-prepend>
						<b-btn
							style="z-index:initial;"
							variant="danger"
							@click="removeSubstanceFromBlend(substance)"
						>X</b-btn>
					</b-input-group-prepend>
					<multiselect
						label="text"
						@tag="addTag($event,substance)"
						:taggable="true"
						trackBy="value"
						tag-placeholder="Press enter to use a new substance"
						placeholder="Controlled or new substance"
						v-model="substance.name"
						:options="substances"
					></multiselect>
					<b-input-group-append>
						<b-input-group append="%">
							<b-form-input class="ml-2" type="text" placeholder="" v-model="substance.percent"></b-form-input>
						</b-input-group>
					</b-input-group-append>
				</b-input-group>
			</div>

			<hr>
			<b-btn-group>
				<b-btn
					v-if="new_blend"
					:disabled="!blendIsValid"
					@click="addSubstance('custom')"
					variant="primary"
				>Add row</b-btn>
				<b-btn v-if="new_blend" @click="resetData">Cancel</b-btn>
			</b-btn-group>

		</div>
	</div>
</template>

<script>

import { createBlend } from '@/components/common/services/api'
import Multiselect from '@/components/common/ModifiedMultiselect'

export default {

	props: {
		tabName: String
	},

	computed: {
		substances() {
			return JSON.parse(JSON.stringify(this.$store.state.initialData.substances))
		},
		blends() {
			return this.$store.state.initialData.blends
		},

		display() {
			return this.$store.state.initialData.display
		},

		blendIsValid() {
			return !this.$store.getters.checkIfBlendAlreadyEists(this.new_blend.text) && this.new_blend.composition.every((substance) => substance.name && substance.percent)
		},

		filteredBlends() {
			return this.selected_blends.filter.length
				? this.selected_blends.options.filter(blend => this.selected_blends.filter.includes(blend.type)) : this.selected_blends.options
		}
	},

	components: {
		Multiselect
	},

	mounted() {
		this.prepareBlends()
	},

	data() {
		return {
			new_blend: null,
			submit_blend: {
				components: null,
				blend_id: null,
				type: 'Other'
			},
			selected_substance: {
				selected: null,
				group: null,
				options: []
			},
			selected_blends: {
				selected: [],
				options: [],
				filters: [],
				filter: [],
				substance_options: []
			}
		}
	},

	methods: {
		pushUnique(array, item) {
			if (array.indexOf(item) === -1) {
				array.push(item)
			}
		},

		addTag(newTag, substance) {
			console.log(newTag, substance)
			const tag = {
				text: newTag,
				value: newTag
			}
			this.substances.push(tag)
			substance.name = newTag
		},

		prepareSubstances() {
			this.selected_substance.options = this.substances.map(substance => ({
				value: substance.id,
				text: substance.name,
				group: substance.group
			}))
		},

		alertIfBlendExists() {
			console.log('here')
			if (this.$store.getters.checkIfBlendAlreadyEists(this.new_blend.text)) {
				this.$store.dispatch('setAlert', {
					message: { __all__: [`A blend with the name ${this.new_blend.text} already exists!`] },
					variant: 'danger'
				})
			}
		},

		addNewBlend() {
			this.selected_blends.selected = []
			this.new_blend = {
				text: null,
				value: null,
				composition: [
					{
						name: null,
						percent: null
					},
					{
						name: null,
						percent: null
					},
					{
						name: null,
						percent: null
					}
				]
			}
		},

		removeSubstanceFromBlend(substance) {
			this.new_blend.composition.splice(this.new_blend.composition.indexOf(substance), 1)
		},

		addSubstanceToBlend() {
			this.new_blend.composition.push({ name: null, percent: null })
		},

		prepareBlends() {
			this.selected_blends.filters = []
			this.selected_blends.options = []
			this.blends.forEach(blend => {
				this.selected_blends.options.push({ text: blend.blend_id, value: blend.id, type: blend.type, sort_order: blend.sort_order })
				this.pushUnique(this.selected_blends.filters, blend.type)
			})
			this.selected_blends.filters = this.selected_blends.filters.map(b => ({ text: b, value: b }))
			this.selected_blends.options.sort((a, b) => a.sort_order - b.sort_order)
			this.prepareSubstances()
		},

		addSubstance(type) {
			if (type === 'selected') {
				this.$store.dispatch('createSubstance', {
					substanceList: null,
					currentSectionName: this.tabName,
					groupName: null,
					country: null,
					blendList: this.selected_blends.selected,
					prefillData: null
				})
				this.resetData()
			} else {
				this.submit_blend.blend_id = this.new_blend.text
				this.submit_blend.components = []
				this.submit_blend.party = this.$store.state.current_submission.party
				this.new_blend.composition.forEach(substance => {
					if (typeof (substance.name) === 'string') {
						this.submit_blend.components.push({ component_name: substance.name, substance: null, percentage: substance.percent / 100 })
					} else {
						this.submit_blend.components.push({ component_name: '', substance: substance.name, percentage: substance.percent / 100 })
					}
				})
				createBlend(this.submit_blend).then(response => {
					this.new_blend.value = response.data.id
					this.$store.commit('addCreateBlendToBlendList', response.data)
					this.display.blends[response.data.id] = { name: response.data.blend_id, components: response.data.components }
					this.$store.dispatch('createSubstance', {
						substanceList: null,
						currentSectionName: this.tabName,
						groupName: null,
						country: null,
						blendList: [this.new_blend.value],
						prefillData: null
					})
					this.$store.dispatch('setAlert', {
						message: { __all__: ['Blend created'] },
						variant: 'success' })
					this.resetData()
				}).catch((error) => {
					console.log(error)
					this.$store.dispatch('setAlert', {
						message: { ...error.response.data },
						variant: 'danger' })
				})
			}
		},

		resetData() {
			this.new_blend = null
			this.selected_blends.filter = []
			this.selected_blends.selected = []
			this.selected_blends.options = []
			this.prepareBlends()
		}

	},

	watch: {
		blends: {
			handler() {
				this.prepareBlends()
			}
		}
	}

}
</script>

<style lang="css" scoped>

.add-blend-wrapper {
	white-space: nowrap;
	margin-left: .5rem;
	display: flex;
	justify-content: center;
	align-items: center;
}
</style>
