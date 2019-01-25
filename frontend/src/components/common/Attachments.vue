<template>
<div class="row">
	<div class="col-12">
		<b-list-group>
			<b-list-group-item>
				<div class="row">
					<div class="col-10">
						$store.getters.can_upload_files - {{$store.getters.can_upload_files}}
						<b-form-file :disabled="loadingInitialFiles || $store.getters.can_upload_files" :multiple="true" ref="filesInput" v-model="selectedFiles" @input="onSelectedFilesChanged" />
					</div>
					<div class="col-2">
						<b-button v-if="attachments.length" variant="danger" class="pull-right" @click="deleteAllAttachments()">
							<i class="fa fa-times" aria-hidden="true"></i>
							<span v-translate>Delete all</span>
						</b-button>
					</div>
				</div>
			</b-list-group-item>
			<b-list-group-item style="font-size: 1.5rem" v-for="attachment in attachments" :key="attachment.name + attachment.updated">
				<div class="row">
					<div class="col-10">
						<div class="spinner" v-show="!attachment.tus_id && !attachment.upload_successful">
							<div class="loader"></div>
						</div>
						<a :href="attachment.file_url">
							<i class="fa fa-file-zip-o fa-lg"></i>
							<span> {{attachment.name}} - {{attachment.updated}}</span>
						</a>
					</div>
					<div class="col-2">
						<b-button variant="danger" class="pull-right" @click="deleteAttachment($event, attachment)">
							<i class="fa fa-times" aria-hidden="true"></i>
							<span v-translate>Delete</span>
						</b-button>
					</div>
				</div>
				<div class="row">
					<div class="col-12" v-show="!attachment.tus_id">
						<b-progress :value="attachment.percentage" :max="100" animated></b-progress>
					</div>
				</div>
				<div class="row">
					<div class="col-12">
						<b-form-textarea placeholder="Description" :value="attachment.description" :rows="3" @input="onDescriptionChange($event, attachment)"></b-form-textarea>
					</div>
				</div>
			</b-list-group-item>
		</b-list-group>
	</div>
</div>
</template>

<script>
import { mapActions, mapMutations } from 'vuex'

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
		}
	},
	methods: {
		...mapActions(['uploadAttachments', 'getAttachmentsWithUploadStatus']),
		...mapMutations(['addTabAttachments', 'updateTabAttachment', 'deleteTabAttachment', 'deleteAllTabAttachments']),
		deleteAllAttachments() {
			this.deleteAllTabAttachments({
				tabName: this.tab.name
			})
			this.$refs.filesInput.reset()
		},
		deleteAttachment(e, attachment) {
			this.deleteTabAttachment({
				tabName: this.tab.name,
				attachment
			})
			this.$refs.filesInput.reset()
		},
		onDescriptionChange(e, attachment) {
			attachment.description = e
			this.updateTabAttachment({
				tabName: this.tab.name,
				attachment
			})
		},
		onProgressCallback(attachment, percentage) {
			attachment.percentage = percentage
			this.updateTabAttachment({
				tabName: this.tab.name,
				attachment
			})
		},
		async onSelectedFilesChanged() {
			if (!this.selectedFiles || !this.selectedFiles.length) {
				return
			}
			const attachments = this.selectedFiles.filter(file => this.allowedExtensions.find(extension => file.name.toLowerCase().trim().endsWith(extension))
				&& !this.attachments.find(attachment => file.name.toLowerCase().trim() === attachment.name.toLowerCase().trim()))

			if (!attachments.length) {
				this.$refs.filesInput.reset()
				return
			}
			const tabName = this.tab.name
			attachments.forEach(attachment => {
				attachment.updated = 'zz' // to appear first in the descending sorted file list while it is uploaded
			})
			this.addTabAttachments({ tabName, attachments })
			await this.uploadAttachments({ attachments, onProgressCallback: this.onProgressCallback })
			attachments.forEach(attachment => {
				this.updateTabAttachment({
					tabName,
					attachment
				})
			})
			this.$refs.filesInput.reset()

			const checkAttachmentsUploadedSuccessfullyInterval = setInterval(async () => {
				if (this.allAttachmentsUploadedSuccessfully) {
					clearInterval(checkAttachmentsUploadedSuccessfullyInterval)
					return
				}
				await this.getAttachmentsWithUploadStatus({ attachments: this.attachments })

				this.attachments.forEach(attachment => {
					this.updateTabAttachment({
						tabName,
						attachment
					})
				})
			}, 1500)
		}
	},
	async created() {
		const existingAttachments = await this.getAttachmentsWithUploadStatus({})
		this.addTabAttachments({ tabName: this.tab.name, attachments: existingAttachments })
		this.loadingInitialFiles = false
	}
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>
