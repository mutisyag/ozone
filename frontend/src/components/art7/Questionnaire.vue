<template>
  <div v-if="info">
    <form class="form-sections">
      <b-card>
        <div class="form-fields" v-for="field in info.form_fields" :key="field.name">
          <div class="field-wrapper">
            <label>{{field.label}}</label>
            <fieldGenerator
              :fieldInfo="{index:field.name, tabName: info.name, field:field.name}"
              :disabled="!$store.getters.can_edit_data"
              :field="field"
            />
          </div>
        </div>
      </b-card>
    </form>
    <div id="tab-comments" class="table-wrapper">
      <h4>Comments</h4>
      <hr>
      <div
        v-for="(comment, comment_key) in info.comments"
        :key="comment_key"
        class="comments-input"
      >
        <label>
          <span>{{labels[comment_key]}}</span>
        </label>
        <!-- addComment(state, { data, tab, field }) { -->
        <textarea
          @change="$store.commit('addComment', {data: $event.target.value, tab:info.name, field: comment_key})"
          :disabled="getCommentFieldPermission(comment_key)"
          class="form-control"
          :value="comment.selected"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
  name: 'Tab1',

  props: {
    info: Object
  },

  created() {
  },

  components: { fieldGenerator },

  methods: {
    getCommentFieldPermission(fieldName) {
      let type = fieldName.split('_')
      type = type[type.length - 1]
      if (type === 'party') {
        return !this.$store.getters.can_change_remarks_party
      }
      if (['secretariat', 'os'].includes(type)) {
        return !this.$store.getters.can_change_remarks_secretariat
      }
    }
  },

  data() {
    return {
      labels: getCommonLabels(this.$gettext)
    }
  }

}
</script>
