<template>
  <div v-if="field">
    <div v-if="field.type === 'text' || field.type === 'number' || field.type === 'date' || field.type ==='email'">
      <p class="control has-icon has-icon-right">
        <input :name="field.label" v-validate="field.validation" :ref="errors.has(field.label) ? 'invalid' : 'none'" :class="{'form-control': true, 'is-invalid': errors.has(field.label) }"  :min="field.type === 'number' ? 0: false" :step="field.type === 'number' ? 'any' : false" :disabled="disabledField"  v-model="field.selected" :type="field.type" @blur="field.type === 'number' ? preventTwoDots(field.selected, field) : false"></input>
      
        <span v-show="errors.has(field.label)" class="invalid-feedback">  <i v-show="errors.has(field.label)" class="fa fa-warning"></i>{{ errors.first(field.label) }}</span>
      </p>
    </div>
    <b-form-radio-group :disabled="disabledField" v-else-if="field.type === 'radio'" v-model="field.selected" @change="selectTabs($event,field)" :created="selectTabs(field.selected, field)" :options="field.options"></b-form-radio-group>
    <b-form-checkbox-group :disabled="disabledField" v-else-if="field.type === 'checkbox'" v-model="field.selected" :options="field.options"></b-form-checkbox-group>
    <b-form-select :disabled="disabledField" v-else-if="field.type === 'select'" v-model="field.selected" :options="field.options"></b-form-select>
    <textarea class="form-control" v-else-if="field.type === 'textarea'" v-model="field.selected"></textarea>
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
    preventTwoDots(value, field) {
      console.log(value)
      if(isNaN(parseFloat(value)))
        field.selected = null
    },

    preventArrows(e){
      console.log('preventing', e)
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