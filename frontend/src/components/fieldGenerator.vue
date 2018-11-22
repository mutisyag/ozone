<template>
  <div v-if="field">
    <div v-if="field.type === 'text' || field.type === 'number' || field.type === 'date' || field.type ==='email'">
        <input @change="updateFormField" :disabled="disabled" class="form-control"  :min="field.type === 'number' ? 0: false" :step="field.type === 'number' ? 'any' : false"  :value="field.selected" :type="field.type" @blur="field.type === 'number' ? preventTwoDots(field.selected, field) : false"></input>
    </div>
    <b-form-radio-group @change="updateFormFieldWithTabs" :disabled="disabled" v-else-if="field.type === 'radio'" :checked="field.selected" :options="field.options"></b-form-radio-group>
    <!-- <b-form-checkbox-group @change="updateFormField"  :disabled="disabled" v-else-if="field.type === 'checkbox'" :checked="field.selected" :options="field.options"></b-form-checkbox-group> -->
    <b-form-select @change="updateFormField"  :disabled="disabled" v-else-if="field.type === 'select'" :value="field.selected" :options="field.options"></b-form-select>
    <textarea @change="updateFormField"  class="form-control" v-else-if="field.type === 'textarea'" :value="field.selected"></textarea>
  </div>
</template>

<script>
export default {

  name: 'fieldGenerator',
  props: {
    field: Object, 
    disabled: false, 
    fieldInfo: Object,
  },

  
  // mounted(){
    // if(this.tab) {
      // this.$emit('updateTabState', {tab: this.fieldInfo.field, value: this.field.selected})
    // }
  // },

  methods: {

    updateFormField({ type, target }){
      this.$store.commit('updateFormField', {value: target.value, fieldInfo: this.fieldInfo})
    },

    updateFormFieldWithTabs(event){
      this.$store.commit('updateFormField', {value: event, fieldInfo: this.fieldInfo})
    },


    preventTwoDots(value, field) {
      if(isNaN(parseFloat(value)))
        field.selected = null
    },

    preventArrows(e){
      if (e.which === 38 || e.which === 40) {
        e.preventDefault();
      }
    }
  },


}


</script>

<style lang="css" scoped>
</style>