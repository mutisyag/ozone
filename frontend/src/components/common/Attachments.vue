<template>
<div>
	<div class="row">
		<div class="col-12 form-inline" v-for="(attachment, index) in attachments" :key="index">
			<span>
				<a :href="attachment.file_url">
					<div class="spinner" v-if="!attachment.upload_successful">
						<div class="loader"></div>
					</div>
					<i v-if="attachment.upload_successful" class="fa fa-download" aria-hidden="true"></i>
					&nbsp;
					{{attachment.name}}
					<span v-if="attachment.upload_successful">- {{attachment.updated}}</span>
				</a>
			</span>
			&nbsp;
			<b-form-input class="d-inline" placeholder="Optional description" :value="attachment.description" @input="onDescriptionChange($event, attachment)" />
			&nbsp;
			<b-button variant="danger" class="pull-right" @click="deleteAttachment($event, attachment)">
				<i class="fa fa-trash" aria-hidden="true"></i>
			</b-button>
			&nbsp;
			<div style="width:200px">
				<b-progress v-show="!attachment.tus_id" :value="attachment.percentage" :max="100" animated></b-progress>
			</div>
		</div>
	</div>
	<div class="row">
		<div class="col-12">
			$store.getters.can_upload_files - {{$store.getters.can_upload_files}} - it should be true!
			<b-form-file :disabled="loadingInitialFiles || $store.getters.can_upload_files" :multiple="true" ref="filesInput" v-model="selectedFiles" @input="onSelectedFilesChanged" plain/>
		</div>
	</div>
	<div class="row" v-if="attachmentsNotUploaded.length">
		<div class="col-12">
			<b-button v-if="attachments.length" variant="primary" @click="upload()">
				<i class="fa fa-upload" aria-hidden="true"></i>
				&nbsp;
				<span v-translate>Upload</span>
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
	computed: {
		attachments() {
			return this.$store.state.form.tabs[this.tab.name].form_fields.attachments
		},
		allAttachmentsUploadedSuccessfully() {
			return !this.attachments.find(attachment => !attachment.upload_successful)
		},
		allowedExtensions() {
			return ALLOWED_FILE_EXTENSIONS.split(',').map(x => `.${x}`)
		},
		attachmentsNotUploaded() {
			return this.attachments.filter(attachment => !attachment.tus_id)
		}
	},
	methods: {
		deleteAttachment(e, attachment) {
			this.$store.dispatch('deleteTabAttachment', {
				tabName: this.tab.name,
				attachment
			})
			this.$refs.filesInput.reset()
		},
		onDescriptionChange(e, attachment) {
			attachment.description = e
			this.$store.commit('updateTabAttachment', {
				tabName: this.tab.name,
				attachment
			})
		},
		onProgressCallback(attachment, percentage) {
			attachment.percentage = percentage
			this.$store.commit('updateTabAttachment', {
				tabName: this.tab.name,
				attachment
			})
		},
		async onSelectedFilesChanged() {
			if (!this.selectedFiles || !this.selectedFiles.length) {
				return
			}
			const attachments = this.selectedFiles.filter(file => this.allowedExtensions.find(extension => file.name.toLowerCase().trim().endsWith(extension)))

			attachments.forEach((attachment, index) => {
				attachment.updated = index
			})
			this.$store.commit('addTabAttachments', { tabName: this.tab.name, attachments })

			this.$refs.filesInput.reset()
		},
		async upload() {
			const attachments = this.attachmentsNotUploaded
			const tabName = this.tab.name
			await this.$store.dispatch('uploadAttachments', { attachments, onProgressCallback: this.onProgressCallback })
			attachments.forEach(attachment => {
				this.$store.commit('updateTabAttachment', {
					tabName,
					attachment
				})
			})

			const checkAttachmentsUploadedSuccessfullyInterval = setInterval(async () => {
				if (this.allAttachmentsUploadedSuccessfully) {
					clearInterval(checkAttachmentsUploadedSuccessfullyInterval)
					return
				}
				await this.$store.dispatch('getAttachmentsWithUploadStatus', { attachments: this.attachments })

				this.attachments.forEach(attachment => {
					this.$store.commit('updateTabAttachment', {
						tabName,
						attachment
					})
				})
			}, 1500)
		}
	},
	async created() {
		const existingAttachments = await this.$store.dispatch('getAttachmentsWithUploadStatus', {})
		this.$store.commit('addTabAttachments', { tabName: this.tab.name, attachments: existingAttachments })
		this.loadingInitialFiles = false
	}
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>
