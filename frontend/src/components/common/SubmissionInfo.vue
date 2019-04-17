<template>
  <div v-if="info" class="submission-info-tab">
    <form class="form-sections">
      <b-row>
        <b-col md="7" lg="7">
          <h5>
            <span v-translate>Submission Info</span>
          </h5>
          <b-card>
            <div class="form-fields">
              <b-row
                :id="order"
                v-for="order in info.fields_order"
                class="field-wrapper"
                :key="order"
              >
                <b-col lg="3">
                  <span
                    v-if="info.form_fields[order].tooltip"
                    v-b-tooltip.hover
                    placement="left"
                    :title="info.form_fields[order].tooltip"
                  >
                    <i class="fa fa-info-circle fa-lg"></i>&nbsp;
                    <label>{{labels[order]}}</label>
                  </span>
                  <span v-else>
                    <label>
                      {{labels[order]}}
                      <div
                        class="floating-error"
                        :class="{danger: error_danger}"
                        v-if="info.form_fields[order].validation"
                        variant="danger"
                        v-translate
                      >(required)</div>
                    </label>
                  </span>
                </b-col>
                <b-col>
                  <fieldGenerator
                    :fieldInfo="{index:order, tabName: info.name, field:order}"
                    :disabled="checkUserType(order)"
                    :field="info.form_fields[order]"
                  ></fieldGenerator>
                </b-col>
              </b-row>
              <b-row
                v-if="is_secretariat || (!is_secretariat && info.form_fields['submitted_at'].selected)"
              >
                <b-col lg="3">
                  <label>
                    {{labels.submitted_at}}
                    <div
                      :class="{danger: error_danger}"
                      class="floating-error"
                      v-if="info.form_fields['submitted_at'].validation"
                      variant="danger"
                      v-translate
                    >({{info.form_fields['submitted_at'].validation}})</div>
                  </label>
                </b-col>
                <b-col>
                  <fieldGenerator
                    :fieldInfo="{index:'submitted_at', tabName: info.name, field:'submitted_at'}"
                    :field="info.form_fields.submitted_at"
                    :disabled="!$store.state.current_submission.can_change_submitted_at"
                  ></fieldGenerator>
                </b-col>
              </b-row>
            </div>
          </b-card>
        </b-col>

        <b-col>
          <h5>
            <span v-if="flags_info" v-translate>Flags</span>
          </h5>
          <b-card v-if="flags_info && $store.state.currentUser.is_secretariat" id="flags">
            <b-row class="mb-2">
              <b-col>
                <b-row v-for="order in general_flags" :key="order">
                  <b-col cols="1">
                    <fieldGenerator
                      :fieldInfo="{index:order, tabName: flags_info.name, field:order}"
                      :disabled="$store.getters.transitionState"
                      :field="flags_info.form_fields[order]"
                      :id="order"
                    ></fieldGenerator>
                  </b-col>
                  <b-col>
                    <label :class="{'muted': flags_info.form_fields[order].disabled}" :for="order">
                      <div
                        v-if="flags_info.form_fields[order].tooltip"
                        v-b-tooltip.hover
                        placement="left"
                        :title="flags_info.form_fields[order].tooltip"
                      >
                        {{labels.flags[order]}}
                        <i class="fa fa-info-circle fa-lg"></i>
                      </div>
                      <div v-else>{{labels.flags[order]}}</div>
                    </label>
                  </b-col>
                </b-row>
              </b-col>
              <b-col>
                <b-row v-for="order in blank_flags" :key="order">
                  <b-col cols="1">
                    <fieldGenerator
                      :fieldInfo="{index:order, tabName: flags_info.name, field:order}"
                      :disabled="$store.getters.transitionState"
                      :field="flags_info.form_fields[order]"
                      :id="order"
                    ></fieldGenerator>
                  </b-col>
                  <b-col>
                    <label :class="{'muted': flags_info.form_fields[order].disabled}" :for="order">
                      <div
                        v-if="flags_info.form_fields[order].tooltip"
                        v-b-tooltip.hover
                        placement="left"
                        :title="flags_info.form_fields[order].tooltip"
                      >
                        <i class="fa fa-info-circle fa-lg"></i>
                        {{labels.flags[order]}}
                      </div>
                      <div v-else>{{labels.flags[order]}}</div>
                    </label>
                  </b-col>
                </b-row>
              </b-col>
            </b-row>
          </b-card>

          <b-card v-if="flags_info">
            <h5 class="mb-3" v-translate>Annex group reported in full</h5>
            <div id="annex-flags">
              <div class="flags-row" v-for="column in specific_flags_columns" :key="column">
                <div
                  class="specific-flags-wrapper"
                  v-for="order in specific_flags.filter(o => o.split('_')[3].includes(column))"
                  :key="order"
                >
                  <span cols="1">
                    <fieldGenerator
                      :fieldInfo="{index:order, tabName: flags_info.name, field:order}"
                      :disabled="$store.getters.transitionState"
                      :field="flags_info.form_fields[order]"
                      :id="order"
                    ></fieldGenerator>
                  </span>
                  <span>
                    <label :class="{'muted': flags_info.form_fields[order].disabled}" :for="order">
                      <div
                        v-if="flags_info.form_fields[order].tooltip"
                        v-b-tooltip.hover
                        placement="left"
                        :title="flags_info.form_fields[order].tooltip"
                      >
                        <i class="fa fa-info-circle fa-lg"></i>
                        {{labels.flags[order]}}
                      </div>
                      <div v-else>{{labels.flags[order]}}</div>
                    </label>
                  </span>
                </div>
              </div>
            </div>
          </b-card>

          <h5>
            <span v-translate>Submission status</span>
          </h5>
          <b-card>
            <SubmissionStatus/>
          </b-card>
        </b-col>
      </b-row>
    </form>
  </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'
import SubmissionStatus from '@/components/common/SubmissionStatus'

export default {
  props: {
    info: Object,
    flags_info: Object
  },

  created() {
    this.labels = getCommonLabels(this.$gettext)
    this.setSubmitted_atValidation()
  },

  components: {
    fieldGenerator,
    SubmissionStatus
  },

  computed: {
    error_danger() {
      return this.info.status === false
    },
    general_flags() {
      return ['flag_provisional']
    },
    exclude_flags() {
      return ['flag_superseded', 'flag_valid']
    },
    blank_flags() {
      return Object.keys(this.flags_info.form_fields).filter(f => this.flags_info.fields_order.includes(f) && f !== 'validation' && f.split('_').includes('blanks'))
    },

    specific_flags() {
      return Object.keys(this.flags_info.form_fields).filter(f => this.flags_info.fields_order.includes(f) && ![...this.general_flags, ...this.exclude_flags, ...this.blank_flags, 'validation'].includes(f))
    },

    specific_flags_columns() {
      return [...new Set(this.specific_flags.map(f => f.split('_')[3]).map(f => f.split('')[0]))]
    },

    is_secretariat() {
      return this.$store.state.currentUser.is_secretariat
    },
    is_data_entry() {
      this.info.form_fields.current_state.selected = this.$store.state.current_submission.current_state === 'data_entry'
      return this.$store.state.current_submission.current_state === 'data_entry'
    }
  },

  data() {
    return {
      labels: null
    }
  },

  methods: {
    setSubmitted_atValidation() {
      const { submitted_at } = this.info.form_fields
      if (!this.is_secretariat || submitted_at.selected) {
        submitted_at.validation = null
      } else {
        submitted_at.validation = this.$gettext('Required')
      }
      if (!this.is_data_entry) {
        submitted_at.validation = null
      }
      this.$forceUpdate()
    },
    checkUserType(order) {
      if (order === 'reporting_channel') {
        return !this.$store.getters.can_change_reporting_channel
      }
      if (order === 'submission_format' && !this.$store.state.currentUser.is_secretariat) {
        return true
      }
      return !this.$store.getters.can_edit_data
    }
  },
  watch: {
    '$language.current': {
      handler() {
        this.labels = getCommonLabels(this.$gettext)
      }
    },
    'info.form_fields.submitted_at.selected': {
      handler() {
        this.setSubmitted_atValidation()
      }
    }
  }

}
</script>
