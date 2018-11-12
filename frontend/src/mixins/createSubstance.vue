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
  	console.log('substancelist', substanceList)

  	if(substanceList) {
		 for(let substance of substanceList) {
	        let inner_fields = this.getInnerFields(currentSectionName, substance, groupName, country, null, prefillData)
	        var current_fields = currentSection
	        current_fields.push(inner_fields)
	        currentSection = current_fields
	      }
	  } else if(blendList) {
	  	 for(let blend of blendList) {
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
