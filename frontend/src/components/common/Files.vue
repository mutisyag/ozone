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
			$store.getters.can_upload_files - {{$store.getters.can_upload_files}} - it should be true!
			<b-form-file :disabled="loadingInitialFiles || $store.getters.can_upload_files" :multiple="true" ref="filesInput" v-model="selectedFiles" @input="onSelectedFilesChanged" plain/>
		</div>
	</div>
	<div class="row" v-if="filesNotUploaded.length || filesWithUpdatedDescription.length">
		<div class="col-12">
			<b-button variant="primary" @click="uploadAndSave()">
				<span v-if="filesNotUploaded.length">
					<i class="fa fa-upload" aria-hidden="true"></i>
					&nbsp;
					<span v-translate>Upload</span> &
				</span>
				<span v-translate>Save</span>
			</b-button>
		</div>
	</div>
</div>
</template>

<script>
const ALLOWED_FILE_EXTENSIONS = 'pdf,doc,docx,xls,xlsx,zip,rar,txt,htm,html,odt,ods,eml,ppt,pptx,mdb'

export default {
	props: {
		tab: Object
	},
	data() {
		return {
			selectedFiles: [],
			loadingInitialFiles: true
		}
	},
	async created() {
		const files = await this.$store.dispatch('getSubmissionFiles')
		this.$store.commit('addTabFiles', { tabName: this.tab.name, files })
		this.loadingInitialFiles = false
	},
	computed: {
		files() {
			return this.$store.state.form.tabs[this.tab.name].form_fields.files
		},
		allFilesUploadedSuccessfully() {
			return !this.files.find(file => !file.upload_successful)
		},
		allowedExtensions() {
			return ALLOWED_FILE_EXTENSIONS.split(',').map(x => `.${x}`)
		},
		filesNotUploaded() {
			return this.files.filter(file => !file.tus_id)
		},
		filesWithUpdatedDescription() {
			return this.files.filter(file => file.isDescriptionUpdated).map(file => ({
				id: file.id,
				name: file.name,
				description: file.description
			}))
		}
	},
	methods: {
		deleteFile(e, file) {
			this.$store.dispatch('deleteTabFile', {
				tabName: this.tab.name,
				file
			})
			this.$refs.filesInput.reset()
		},
		onFileDescriptionChanged(newDescription, file) {
			if (file.description === newDescription) {
				return
			}
			this.$store.commit('deleteTabFile', {
				tabName: this.tab.name,
				file
			})
			file.description = newDescription
			file.isDescriptionUpdated = true
			this.$store.commit('addTabFile', {
				tabName: this.tab.name,
				file
			})
			console.log('onFileDescriptionChanged', file)
		},
		onProgressCallback(file, percentage) {
			this.$store.commit('deleteTabFile', {
				tabName: this.tab.name,
				file
			})
			file.percentage = percentage
			this.$store.commit('addTabFile', {
				tabName: this.tab.name,
				file
			})
		},
		async onSelectedFilesChanged() {
			if (!this.selectedFiles || !this.selectedFiles.length) {
				return
			}
			const files = this.selectedFiles.filter(file => this.allowedExtensions.find(extension => file.name.toLowerCase().trim().endsWith(extension)))

			files.forEach((file, index) => {
				file.updated = index
			})
			this.$store.commit('addTabFiles', { tabName: this.tab.name, files })

			this.$refs.filesInput.reset()
		},
		upload() {
			return new Promise(async (resolve, reject) => {
				try {
					await this.$store.dispatch('uploadFiles', { files: this.filesNotUploaded, onProgressCallback: this.onProgressCallback })

					const checkFilesUploadedSuccessfullyInterval = setInterval(async () => {
						if (this.allFilesUploadedSuccessfully) {
							clearInterval(checkFilesUploadedSuccessfullyInterval)
							resolve()
							return
						}
						await this.$store.dispatch('setJustUploadedFilesState', { files: this.files, tabName: this.tab.name })
					}, 1500)
				} catch (error) {
					console.log('error upload', error)
					reject(error)
				}
			})
		},
		async uploadAndSave() {
			await this.upload()
			if (this.filesWithUpdatedDescription.length) {
				await this.$store.dispatch('updateSubmissionFiles', this.filesWithUpdatedDescription)
			}
		}
	}
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>
