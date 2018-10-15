<template>
	  <b-btn @click="submitData" variant="success">
        Submit
      </b-btn>
</template>

<script>
export default {

  name: 'Submit',

  props:{
  	data: Object,
  	submission: Object,
  },

  data () {
    return {

    }
  },
  methods:{
  	submitData(){
  		console.log(this.data,this.submission)
  	}
  }
}
</script>

<style lang="css" scoped>
</style>