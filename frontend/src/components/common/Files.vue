<template>
  <div>
    <div v-if="!files.length">
      <h5 class="ml-2" v-translate>No files uploaded</h5>
    </div>
    <div v-else>
      <b-input-group class="mb-2" v-for="(file, index) in files" :key="index">
        <b-input-group-text
          slot="prepend"
          style="padding: 0;"
        >
          <span>
            <b-btn
              variant="link"
              @click="$store.dispatch('downloadStuff',
						{
							url: file.file_url,
							fileName:file.name
						})"
            v-b-tooltip
            :title="file.upload_succesfull ? 'Download' : ''"
            >
              <i v-if="file.upload_successful" class="fa fa-download" aria-hidden="true"></i>
              <i v-else class="fa fa-upload" aria-hidden="true"></i>
              {{file.name}}
            </b-btn>
            <div v-if="file.upload_successful">
              <small>
              Uploaded at:
                {{formatDate(file.updated)}}
              </small>
            </div>
          </span>
        </b-input-group-text>
        <b-form-input
          class="d-inline"
          placeholder="Optional description"
          :value="file.description"
          style="height: unset"
          @input="onFileDescriptionChanged($event, file)"
        />
        <b-input-group-append>
          <b-button variant="danger" class="pull-right" @click="deleteFile($event, file)">
            <i class="fa fa-trash" aria-hidden="true"></i>
          </b-button>
          <div class="ml-2" style="width:200px" v-if="file.percentage">
            <b-progress :value="file.percentage" :max="100">
              <b-progress-bar :value="file.percentage">
                Uploading: <strong>{{ parseInt(file.percentage) }}%</strong>
              </b-progress-bar>
            </b-progress>
          </div>
        </b-input-group-append>
      </b-input-group>
    </div>
    <hr>
    <div class="row">
      <div class="col-4">
        <b-form-file
          id="choose-files-button"
          :disabled="!$store.getters.can_upload_files || loadingInitialFiles"
          :multiple="true"
          ref="filesInput"
          v-model="selectedFiles"
          :placeholder="placeholder"
          @input="onSelectedFilesChanged"
        />
      </div>
    </div>
    <!-- TODO: there needs to be a method for just saving files. This is a dirty workaround -->
    <div v-if="files.length">
      <hr>
      <b-btn variant="primary" @click="$store.dispatch('triggerSave')" v-translate>Upload files</b-btn>
    </div>
    <small class="ml-2 muted">
      <span v-translate>Allowed files extensions: </span> {{allowedExtensions.join(', ')}}
    </small>
  </div>
</template>

<script>
import FilesMixin from '@/components/common/mixins/FilesMixin'
import { dateFormatToDisplay } from '@/components/common/services/languageService.js'

export default {
  mixins: [FilesMixin],

  props: {
    tabId: Number,
    tabIndex: Number
  },
  data() {
    return {
      selectedFiles: [],
      loadingInitialFiles: true,
      placeholder: this.$gettext('Click to browse files')
    }
  },
  async created() {
    await this.getSubmissionFiles()
    this.loadingInitialFiles = false
  },
  methods: {
    formatDate(date) {
      return dateFormatToDisplay(date)
    },
    async deleteFile(e, file) {
      const confirmed = await this.$store.dispatch('openConfirmModal', { $gettext: this.$gettext })
      if (!confirmed) {
        return
      }
      this.$store.dispatch('deleteTabFile', {	file })
      this.$refs.filesInput.reset()
    },
    onFileDescriptionChanged(description, file) {
      this.$store.commit('updateTabFileDescription', {
        file,
        description
      })
    },
    async onSelectedFilesChanged() {
      if (!this.selectedFiles || !this.selectedFiles.length) {
        return
      }
      const files = this.selectedFiles.filter(file => this.allowedExtensions.find(extension => file.name.toLowerCase().trim().endsWith(extension)))

      files.forEach((file, index) => {
        file.updated = index
      })
      this.$store.commit('addTabFiles', { files })

      this.$refs.filesInput.reset()
    }
  },
  watch: {
    'files': {
      handler() {
        if (parseInt(this.tabId) === this.tabIndex) {
          if (this.$store.state.form.tabs.files !== 'edited') {
            this.$store.commit('setTabStatus', {
              tab: this.$store.state.form.tabs.files.name,
              value: 'edited'
            })
          }
        }
      },
      deep: true
    }
  }
}
</script>

<style lang="css" scoped>
a {
  margin-bottom: 1rem;
}
.progress {
  height: 100%;
}
.btn-link:hover {
  text-decoration: none;
}
</style>
