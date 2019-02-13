<template>
<div>
	<div class="row">
		<div class="col-12 form-inline" v-for="(file, index) in files" :key="index">
			<span>
				<a :href="file.file_url">
					<div class="spinner" v-if="!file.upload_successful">
						<div class="loader"></div>
					</div>
					<i v-if="file.upload_successful" class="fa fa-download" aria-hidden="true"></i>
					&nbsp;
					{{file.name}}
					<span v-if="file.upload_successful">- {{file.updated}}</span>
				</a>
			</span>
			&nbsp;
			<b-form-input class="d-inline" placeholder="Optional description" :value="file.description" @input="onFileDescriptionChanged($event, file)" />
			&nbsp;
			<b-button variant="danger" class="pull-right" @click="deleteFile($event, file)">
				<i class="fa fa-trash" aria-hidden="true"></i>
			</b-button>
			&nbsp;
			<div style="width:200px">
				<b-progress v-show="!file.tus_id" :value="file.percentage" :max="100" animated></b-progress>
			</div>
		</div>
	</div>
	<div class="row">
		<div class="col-12">
			<b-form-file :disabled="!$store.getters.can_upload_files || loadingInitialFiles" :multiple="true" ref="filesInput" v-model="selectedFiles" @input="onSelectedFilesChanged" plain/>
		</div>
	</div>
</div>
</template>

<script>
import FilesMixin from '@/components/common/mixins/FilesMixin'

export default {
	mixins: [FilesMixin],

	props: {
		tabId: Number,
		tabIndex: Number
	},
	data() {
		return {
			selectedFiles: [],
			loadingInitialFiles: true
		}
	},
	async created() {
		await this.getSubmissionFiles()
		this.loadingInitialFiles = false
	},
	methods: {
		deleteFile(e, file) {
			this.$store.dispatch('deleteTabFile', {	file })
			this.$refs.filesInput.reset()
		},
		onFileDescriptionChanged(description, file) {
			this.$store.commit('updateTabFileDescription', {
				file,
				description
			})
		},
		onProgressCallback(file, percentage) {
			this.$store.commit('deleteTabFile', { file })
			file.percentage = percentage
			this.$store.commit('addTabFile', { file })
		},
		async onSelectedFilesChanged() {
			if (!this.selectedFiles || !this.selectedFiles.length) {
				return
			}
			const files = this.selectedFiles.filter(file => this.allowedExtensions.find(extension => file.name.toLowerCase().trim().endsWith(extension)))

			files.forEach((file, index) => {
				file.updated = index
			})
			this.$store.commit('addTabFiles', { files })

			this.$refs.filesInput.reset()
		}
	},
	watch: {
		'files': {
			handler() {
				console.log('here', this.tabId, this.tabIndex)
				if (parseInt(this.tabId) === this.tabIndex) {
					if (this.$store.state.form.tabs.files !== 'edited') {
						this.$store.commit('setTabStatus', {
							tab: this.$store.state.form.tabs.files.name,
							value: 'edited'
						})
					}
				}
			},
			deep: true
		}
	}
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>
