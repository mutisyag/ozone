<template>
<!--       <b-alert 
      		 :variant="currentAlert.variant"
             dismissible
             style="position: fixed;
                top: 0;
                z-index: 10000;
                width: 100%;
                left: 0;
                right: 0;"
             :show="showCurrentAlert"
             @dismissed="dismissAlert"
             >
             <div v-html="currentAlert.message"></div>
      </b-alert> -->
 
       <b-alert 
       		style="	
       			position: fixed;
			    z-index: 10000;
			    left: 50%;
			    transform: translateX(-50%);
			    width: 50%;
			    top: 1rem;"
         	:show="dismissCountDown"
             dismissible
             :variant="$store.state.currentAlert.variant"
             @dismissed="resetCurrentAlert"
             @dismiss-count-down="countDownChanged">

             <div v-html="$store.state.currentAlert.message"></div>
      <b-progress :variant="$store.state.currentAlert.variant"
                  :max="dismissSecs"
                  :value="dismissCountDown"
                  height="3px">
      </b-progress>
    </b-alert>

</template>

<script>
export default {



  name: 'Alerts',

  data () {
    return {
      dismissSecs: 500,
      dismissCountDown: 0,
      showDismissibleAlert: false
    }
  },

   methods: {
	    countDownChanged (dismissCountDown) {
	      this.dismissCountDown = dismissCountDown
	      if(dismissCountDown === 0){
	    	this.$store.dispatch('resetAlert')
	      }
	    },
	    showAlert () {
	      this.dismissCountDown = this.dismissSecs
	    },
	    resetCurrentAlert() {
	    	this.$store.dispatch('resetAlert')
	    	this.dismissCountDown=0
	    },
  	},


  	watch: {
  		'$store.state.currentAlert.show': {
  			handler(newVal) {
  				if(newVal){
  					this.showAlert()
  				} else {
  					this.countDownChanged(0)
  				}
  			},
  		}
  	}
}
</script>

<style lang="css" scoped>
</style>