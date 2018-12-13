<template>
	<div>
		<b-input-group style="margin-bottom:1rem;" prepend="Add file">
			<b-form-file :multiple="true" ref="fileinput" v-model="selectedFiles" @input="onSelectedFilesChanged" ></b-form-file>
			<b-input-group-append>
				<b-btn variant="primary" @click="saveAttachments" :disabled="isSaveDisabled"><i class="fa fa-floppy-o" aria-hidden="true"></i> Save changes</b-btn>
			</b-input-group-append>
		</b-input-group>
		<b-list-group>
				<b-list-group-item style="font-size: 1.5rem" v-for="attachment in $store.state.form.tabs[tab.name].form_fields.attachments" :key="attachment.id">
					<b-button variant="danger" class="pull-right" @click="deleteAttachment($event, attachment)">
						<i class="fa fa-times" aria-hidden="true"></i> Delete
					</b-button>
					<a :href="attachment.url">
						<i class="fa fa-file-zip-o fa-lg mt-4"></i>
						{{attachment.name}} {{attachment.size}} - {{attachment.dateUploaded}}
					</a>
					<b-form-textarea :value="attachment.description" @input="onDescriptionChange($event, attachment)"></b-form-textarea>
				</b-list-group-item>
		</b-list-group>
	</div>
</template>

<script>
import { mapActions, mapMutations } from 'vuex'

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
	methods: {
		...mapActions(['uploadFormAttachments']),
		...mapMutations(['addTabAttachment', 'updateTabAttachment', 'deleteTabAttachment']),
		deleteAttachment(e, attachment) {
			this.deleteTabAttachment({
				tabName: this.tab.name,
				attachment
			})
			this.isSaveDisabled = false
		},
		onDescriptionChange(e, attachment) {
			this.updateTabAttachment({
				tabName: this.tab.name,
				attachment: {
					...attachment,
					description: e
				}
			})
			this.isSaveDisabled = false
		},
		async onSelectedFilesChanged() {
			if (this.selectedFiles.length) {
				const uploadFilesResponse = await this.uploadFormAttachments(
					this.selectedFiles.filter(file => file.type
														&& !file.name.endsWith('.exe')
														&& !file.name.endsWith('.js')
														&& !file.name.endsWith('.php'))
				)
				uploadFilesResponse.forEach(attachment => {
					this.addTabAttachment({
						tabName: this.tab.name,
						attachment
					})
				})

				this.$refs.fileinput.reset()
				this.isSaveDisabled = false
			}
		},
		saveAttachments() {
			console.log(`saveAttachments ${this.tab.name}`, this.$store.state.form.tabs[this.tab.name].form_fields.attachments)
		}
	}
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>
