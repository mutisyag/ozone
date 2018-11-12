<template>
</template>

<script>
import fieldsPerTab from '@/mixins/fieldNamesPerTab.vue'

export default {
	mixins:[fieldsPerTab],

  data () {
    return {

    }
  },

  methods: {
  	createSubstance(substanceList, currentSectionName, groupName, currentSection, country, blendList, prefillData){

  	let iterator = substanceList 
  	let substancesHere = (substanceList && substanceList.length) ? substanceList.some( (el) => {return el !== null}) : false
  	let blendsHere = (blendList && blendList.length) ? blendList.some( (el) => {return el !== null}) : false

  	if(substancesHere) {
		 for(let substance of substanceList) {
	        let inner_fields = this.getInnerFields(currentSectionName, substance, groupName, country, null, prefillData)
	        var current_fields = currentSection
	        current_fields.push(inner_fields)
	        currentSection = current_fields
	      }
	  } else if(blendsHere) {
	  	 for(let blend of blendList) {
	  	 	console.log(blend)
	        let inner_fields = this.getInnerFields(currentSectionName, null, groupName, country, blend, prefillData)
	        var current_fields = currentSection
	        current_fields.push(inner_fields)
	        currentSection = current_fields
	      }
	  }

  	}
  },



}
</script>
