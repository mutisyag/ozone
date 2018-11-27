<template>
	<div>
		<b-input-group style="margin-bottom:1rem;" prepend="Add file">
			<b-form-file :multiple="true" accept="/*.*/" ref="fileinput" v-model="selectedFiles" @input="onSelectedFilesChanged" ></b-form-file>
			<b-input-group-append>
				<b-btn variant="primary" @click="saveAttachments" :disabled="isSaveDisabled"><i class="fa fa-floppy-o" aria-hidden="true"></i> Save changes</b-btn>
			</b-input-group-append>
		</b-input-group>		
		<b-list-group>			
				<b-list-group-item style="font-size: 1.5rem" v-for="attachment in $store.state.form.tabs.attachments" :key="attachment.id">
					<b-button variant="danger" class="pull-right" @click="deleteAttachment($event, attachment)">
						<i class="fa fa-times" aria-hidden="true"></i>
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
import { mapGetters, mapActions, mapMutations } from 'vuex'

export default {	
  data () {
    return {
			selectedFiles: [],
			isSaveDisabled: true
    }
  },	
	 methods: {
		...mapActions(['uploadFormAttachments', 'saveFormAttachments']),
		...mapMutations(['updateFormAttachment', 'deleteFormAttachment']),	
		deleteAttachment(e, attachment) {
			this.deleteFormAttachment({
				...attachment,
				description: e
			});
			this.isSaveDisabled = false;
		},	 
		onDescriptionChange(e, attachment) {
			this.updateFormAttachment({
				...attachment,
				description: e
			});
			this.isSaveDisabled = false;
		},	 
    async onSelectedFilesChanged() {
			if(this.selectedFiles.length) {
				await this.uploadFormAttachments(this.selectedFiles);
				this.$refs.fileinput.reset();	
				this.isSaveDisabled = false;
			} 	
    },
		saveAttachments() {
			this.saveFormAttachments();
		}
  }
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>