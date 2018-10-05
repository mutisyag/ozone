<template>
	<div v-if="info">
		<b-input-group style="margin-bottom:1rem;" prepend="Add file">
			<b-form-file> </b-form-file>
			<b-input-group-append>
				<b-btn variant="primary">Upload</b-btn>
			</b-input-group-append>
		</b-input-group>
		<b-list-group>
			<a style="font-size: 1.5rem"  v-for="attachment in info" :href="attachment.url">
				<b-list-group-item>
					 <i class="fa fa-file-zip-o fa-lg mt-4"></i>  {{attachment.name}}
				</b-list-group-item>
			</a>
		</b-list-group>
	</div>
</template>

<script>
export default {
	props: {
		info: Array,
	},

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
a {
	margin-bottom: 1rem;
}
</style>