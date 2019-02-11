<script>
const ALLOWED_FILE_EXTENSIONS = 'pdf,doc,docx,xls,xlsx,zip,rar,txt,htm,html,odt,ods,eml,ppt,pptx,mdb'

export default {
	computed: {
		files() {
			return this.$store.state.form.tabs.files.form_fields.files
		},
		allowedExtensions() {
			return ALLOWED_FILE_EXTENSIONS.split(',').map(x => `.${x}`)
		}
	},
	methods: {
		async getSubmissionFiles() {
			const files = await this.$store.dispatch('getSubmissionFiles')
			this.$store.commit('deleteAllTabFiles')
			this.$store.commit('addTabFiles', { files })
		},
		getWereAllFilesUploadedSuccessfully() {
			return !this.files.find(file => !file.upload_successful)
		},
		getFilesWithUpdatedDescription() {
			return this.files.filter(file => file.isDescriptionUpdated)
		},
		getFilesNotUploaded() {
			return this.files.filter(file => !file.tus_id)
		},
		uploadFiles() {
			const files = this.getFilesNotUploaded()
			if (!files.length) {
				return
			}
			return new Promise(async (resolve, reject) => {
				try {
					await this.$store.dispatch('uploadFiles', { files, onProgressCallback: this.onProgressCallback })

					const checkFilesUploadedSuccessfullyInterval = setInterval(async () => {
						if (this.getWereAllFilesUploadedSuccessfully()) {
							clearInterval(checkFilesUploadedSuccessfullyInterval)
							resolve()
							return
						}
						await this.$store.dispatch('setJustUploadedFilesState')
					}, 1500)
				} catch (error) {
					console.log('error upload', error)
					reject(error)
				}
			})
		}
	}
}
</script>
