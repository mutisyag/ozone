<template>
<div class="row">
	<div class="col-12">
		<b-list-group>
			<b-list-group-item>
				<div class="row">
					<div class="col-10">
						<b-form-file :disabled="$store.getters.can_upload_files" :multiple="true" ref="fileinput" v-model="selectedFiles" @input="onSelectedFilesChanged" plain />
					</div>
					<div class="col-2">
						<b-button v-if="attachments.length" variant="danger" class="pull-right" @click="deleteAllAttachments()">
							<i class="fa fa-times" aria-hidden="true"></i>
							<span v-translate>Delete all</span>
						</b-button>
					</div>
				</div>
			</b-list-group-item>
			<b-list-group-item style="font-size: 1.5rem" v-for="attachment in attachments" :key="attachment.id">
				<div class="row">
					<div class="col-10">
						<a :href="attachment.url">
							<i class="fa fa-file-zip-o fa-lg"></i>
							<span> {{attachment.name}} - {{(attachment.size / 1000000).toFixed(2)}} MB - Date uploaded ?</span>
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
					<div class="col-12">
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

const fileExtensionIsValid = (fileNameLowercase) => {
	const validExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.txt', '.htm', '.html', '.odt', '.ods', '.eml', '.ppt', '.pptx', '.mdb']
	for (let i = 0; i < validExtensions.length; i += 1) {
		if (fileNameLowercase.endsWith(validExtensions[i])) {
			return true
		}
	}
	return false
}

export default {
	props: {
		tab: Object
	},
	data() {
		return {
			selectedFiles: [],
			isSaveDisabled: true
		}
	},
	computed: {
		attachments() {
			return this.$store.state.form.tabs[this.tab.name].form_fields.attachments
		}
	},
	methods: {
		...mapActions(['uploadAttachments']),
		...mapMutations(['addTabAttachments', 'updateTabAttachment', 'deleteTabAttachment', 'deleteAllTabAttachments']),
		deleteAllAttachments() {
			this.deleteAllTabAttachments({
				tabName: this.tab.name
			})
			this.isSaveDisabled = false
		},
		deleteAttachment(e, attachment) {
			this.deleteTabAttachment({
				tabName: this.tab.name,
				attachment
			})
			this.isSaveDisabled = false
		},
		onDescriptionChange(e, attachment) {
			attachment.description = e
			this.updateTabAttachment({
				tabName: this.tab.name,
				attachment
			})
			this.isSaveDisabled = false
		},
		onProgressCallback(attachment, percentage) {
			attachment.percentage = percentage
			this.updateTabAttachment({
				tabName: this.tab.name,
				attachment
			})
		},
		async onSelectedFilesChanged() {
			if (this.selectedFiles.length) {
				const tabName = this.tab.name
				let attachments = this.selectedFiles.filter(file => file.type
																	&& fileExtensionIsValid(file.name.toLowerCase()))
				this.addTabAttachments({ tabName, attachments })
				attachments = await this.uploadAttachments({ attachments, onProgressCallback: this.onProgressCallback })
				attachments.forEach(attachment => {
					this.updateTabAttachment({
						tabName: this.tab.name,
						attachment
					})
				})
				console.log(this.attachments)
				this.$refs.fileinput.reset()
				this.isSaveDisabled = false
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
