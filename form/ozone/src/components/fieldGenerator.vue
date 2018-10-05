<template>
  <div v-if="field">
    <div v-if="field.type === 'text' || field.type === 'number' || field.type === 'date' || field.type ==='email'">
        <b-form-input :disabled="disabledField" @keydown="field.type === 'number' ? preventArrows: null" v-model="field.selected" :type="field.type"></b-form-input>
    </div>
    <b-form-radio-group :disabled="disabledField" v-else-if="field.type === 'radio'" v-model="field.selected" @change="selectTabs($event,field)" :created="selectTabs(field.selected, field)" :options="field.options"></b-form-radio-group>
    <b-form-checkbox-group :disabled="disabledField" v-else-if="field.type === 'checkbox'" v-model="field.selected" :options="field.options"></b-form-checkbox-group>
    <b-form-select :disabled="disabledField" v-else-if="field.type === 'select'" v-model="field.selected" :options="field.options"></b-form-select>
    <textarea v-else-if="field.type === 'textarea'" v-model="field.selected"></textarea>
  </div>
</template>

<script>
export default {

  name: 'fieldGenerator',
  props: {field: Object, tab: Object, disabled: false},

  created(){

  },

  methods: {
    selectTabs(event, field) {
      if(this.tab) {
        if(event === true) {
          this.tab[field.name] = true
        } else {
          this.tab[field.name] = false
        }
      }
    },
    preventArrows(e){
      if (e.which === 38 || e.which === 40) {
        e.preventDefault();
      }
    }
  },

  data () {
    return {
      disabledField: this.disabled
    }
  },



/*  watch: {
    disabled: {
      handler: function(old_val, new_val) {
        this.disabledField = this.disabled
      }, 
    },
    field: {
      handler: function(old_val, new_val) {
        this.disabledField = this.disabled
      }
    },
    deep: true,
    immediate: true
  },
*/
}


</script>

<style lang="css" scoped>
</style>