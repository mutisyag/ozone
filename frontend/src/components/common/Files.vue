<template>
  <div class="col-8 files-upload-wrapper">
    <div>
      <div class="row">
        <div class="col-7 mb-2">
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
      <small class="ml-1 muted">
         <span v-translate>Allowed files extensions: </span> {{allowedExtensions.join(', ')}}
      </small>
      <div v-if="tableItemsToUpload.length">
        <h5 class="mt-3 mb-3 ml-1"> {{tableItemsToUpload.length}} <span v-translate>files ready for upload:</span></h5>
      </div>
    </div>
    <b-table
          show-empty
          class="no-header"
          :empty-text="$gettext('Click the Browse button to add files')"
          :items="tableItemsToUpload"
          :fields="tableFieldsUploaded.filter(field => field.key !== 'date')"
    >

      <template slot="description" slot-scope="cell">
        <b-form-input
          class="d-inline"
          placeholder="Optional description"
          :value="cell.value"
          style="height: unset"
          @input="onFileDescriptionChanged($event, cell.item.details)"
        />
      </template>

      <template slot="actions" slot-scope="cell">
        <div class="d-flex">
          <b-button variant="outline-danger" @click="deleteFile($event, cell.item.details)">
            <i class="fa fa-trash" aria-hidden="true"></i>
          </b-button>
          <div class="ml-2" style="min-width:300px" v-if="cell.item.details.percentage">
            <b-progress :value="cell.item.details.percentage" :max="100">
              <b-progress-bar :value="cell.item.details.percentage">
                Uploading: <strong>{{ parseInt(cell.item.details.percentage) }}%</strong>
              </b-progress-bar>
            </b-progress>
          </div>
        </div>
      </template>
    </b-table>
    <b-btn v-if="tableItemsToUpload.length" class="mb-4" variant="primary" @click="$store.dispatch('triggerSave')" v-translate>Start upload</b-btn>

      <!-- TODO: there needs to be a method for just saving files. This is a dirty workaround -->
    <br>
    <div v-if="tableItemsUploaded.length">
      <h5 class="mb-4 ml-1" v-translate>Uploaded files</h5>
      <b-table
            show-empty
            :empty-text="$gettext('No files uploaded')"
            :items="tableItemsUploaded"
            :fields="tableFieldsUploaded"
          >
        <template slot="actions" slot-scope="cell">
          <b-btn
            variant="outline-primary"
            @click="$store.dispatch('downloadStuff', { url: cell.item.details.file_url, fileName: cell.item.details.name })"
            v-b-tooltip
            :title="downloadLabel"
          ><i class="fa fa-download"></i></b-btn>
          <b-button class="ml-2 mr-2" variant="outline-danger" @click="deleteFile($event, cell.item.details)">
            <i class="fa fa-trash" aria-hidden="true"></i>
          </b-button>
        </template>
      </b-table>
    </div>
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
      placeholder: this.$gettext('Click to browse files'),
      uploadLabel: this.$gettext('File not uploaded yet'),
      downloadLabel: this.$gettext('Download'),
      tableFieldsUploaded: [
        { key: 'fileName', label: this.$gettext('File Name') },
        { key: 'description', label: this.$gettext('Description') },
        { key: 'date', label: this.$gettext('Date') },
        { key: 'actions', label: this.$gettext('Actions') }
      ]
    }
  },
  async created() {
    await this.getSubmissionFiles()
    this.loadingInitialFiles = false
  },
  computed: {
    tableItemsUploaded() {
      return this.files.filter(file => file.upload_successful).map(file => ({
        fileName: file.name,
        description: file.description,
        date: this.formatDate(file.updated),
        details: file
      }))
    },
    tableItemsToUpload() {
      return this.files.filter(file => !file.upload_successful).map(file => ({
        fileName: file.name,
        description: file.description,
        details: file
      }))
    }
  },
  methods: {
    formatDate(date) {
      return dateFormatToDisplay(date)
    },
    async deleteFile(e, file) {
      const confirmed = await this.$store.dispatch('openConfirmModal', { title: 'Please confirm', description: 'Are you sure you want to delete the selected file?', $gettext: this.$gettext })
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
.files-upload-wrapper {
}
a {
  margin-bottom: 1rem;
}
.progress {
  height: 100%;
}
.btn-link:hover {
  text-decoration: none;
}
.uploadedFiles {
  display: flex;
}
.card-header {
  background: white;
  padding: 0;
  margin-bottom: 1rem;
}
</style>
