<template>
    <div v-if="templates && sender">
      <b-btn class="square-right square-left" @click="getMail()" variant="outline-dark" v-translate>E-mail</b-btn>
      <b-modal title="E-mail" id="ozoneMail" size="xl" ref="ozoneMailModal">
        <b-tabs v-model="tabIndex">
          <b-tab :title="$gettext('Send a message')">
            <b-row>
                <b-col cols="8">
                    <b-input-group class="mb-1" prepend="To">
                      <multiselect
                            label="text"
                            @tag="addTagTo($event)"
                            :taggable="true"
                            trackBy="value"
                            :multiple="true"
                            :close-on-select="true"
                            :tag-placeholder="$gettext('Press enter to add an email')"
                            :placeholder="$gettext('Type the recipient address and press enter')"
                            v-model="mail.to"
                            :options="toList"
                            />
                    </b-input-group>
                    <b-input-group class="mb-1" prepend="Cc">
                      <multiselect
                            label="text"
                            @tag="addTag($event)"
                            :taggable="true"
                            trackBy="value"
                            :multiple="true"
                            :close-on-select="true"
                            :tag-placeholder="$gettext('Press enter to add an email')"
                            :placeholder="$gettext('Type the recipient address and press enter')"
                            v-model="mail.cc"
                            :options="ccList"
                            />
                    </b-input-group>
                    <b-input-group class="mb-1" prepend="Subject">
                      <b-input v-model="mail.subject"></b-input>
                    </b-input-group>
                    <textarea style="height: 300px;" v-model="mail.body" class="form-control mail-input"></textarea>
                    <b-btn @click="sendMail" variant="primary" class="mt-2">Send message</b-btn>
                </b-col>
                <b-col>
                  <h4>Templates</h4>
                  <b-list-group class="templates">
                    <b-list-group-item @click="mail.body = template.description; mail.subject = template.subject" class="template-item" v-for="(template, template_index) in templates" :key="template_index">
                      <b>Template {{ template.name }} </b>
                      <br>
                      {{ template.subject }}
                    </b-list-group-item>
                  </b-list-group>
                </b-col>
            </b-row>
          </b-tab>
          <b-tab v-if="history" :title="$gettext('Correspondence')">
            <div class="mb-3" v-for="(entry, index) in history" :key="index">
                <small style="float: right" class="muted">Date: 10 May 2019</small>
                <h4>{{ entry.subject }}</h4>
                <small><b>From:</b> {{entry.from_email}}</small> <br>
                <small><b>To:</b> {{entry.to.join(', ')}} </small><br>
                <small><b>Cc:</b> {{entry.cc.join(', ')}}</small>
                <div class="correspondence-body mt-2">{{entry.body}}</div>
                <hr>
            </div>
          </b-tab>
        </b-tabs>
        <div slot="modal-footer">
          <b-btn @click="$refs.ozoneMailModal.hide()" variant="outline-danger" v-translate>Close</b-btn>
        </div>
      </b-modal>
    </div>
</template>
<script>
import { getEmails, sendEmail } from '@/components/common/services/api'
import Multiselect from '@/components/common/ModifiedMultiselect'

export default {
  props: {
    submission: String
  },
  components: {
    Multiselect
  },
  data() {
    return {
      tabIndex: 0,
      ccList: [],
      toList: [],
      mail: {
        to: [],
        cc: [],
        subject: null,
        body: null
      },
      templates: this.$store.state.emailTemplates,
      history: null
    }
  },
  mounted() {
    if (this.$store.state.form.tabs.sub_info.form_fields.email.selected) {
      this.addTagTo(this.$store.state.form.tabs.sub_info.form_fields.email.selected)
    }
  },
  computed: {
    sender() {
      return this.$store.state.currentUser.email
    }
  },
  methods: {
    async getMail() {
      const mail = await getEmails(this.$store.state.current_submission.id)
      this.history = mail.data
      this.$refs.ozoneMailModal.show()
    },

    addTag(newTag) {
      const tag = {
        text: newTag,
        value: newTag
      }
      this.ccList.push(tag)
      this.mail.cc.push(tag.value)
    },

    addTagTo(newTag) {
      const tag = {
        text: newTag,
        value: newTag
      }
      this.toList.push(tag)
      this.mail.to.push(tag.value)
    },

    async sendMail() {
      const currentMail = this.mail
      currentMail.from_email = this.sender
      await sendEmail(this.$store.state.current_submission.id, currentMail)
      this.$store.dispatch('setAlert', {
        $gettext: this.$gettext,
        message: { __all__: [this.$gettext('Mail sent')] },
        variant: 'success'
      })
      this.mail = {
        to: null,
        cc: [],
        subject: null,
        body: null
      }
      this.getMail().then(() => {
        this.tabIndex = 1
      })
    }
  }
}
</script>
<style>
  .square-left {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .template-item:hover {
    cursor: pointer;
    background: rgba(0,0,0,0.05);
  }
  .templates {
    max-height: 400px;
    overflow: auto;
  }

  .mail-input {
    height: 300px;
  }
  .correspondence-body {
    white-space: pre-wrap;
  }
</style>
