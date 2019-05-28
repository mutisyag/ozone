<template>
    <div>
        <b-tabs>
            <b-tab :title="$gettext('Send a message')">
                <b-row>
                    <b-col cols="8">
                        <textarea v-model="currentMessage" class="form-control"></textarea>
                    </b-col>
                    <b-col></b-col>
                </b-row>
            </b-tab>
            <b-tab v-if="history" :title="$gettext('Conversation history')">
            </b-tab>
        </b-tabs>
    </div>
</template>
<script>
export default {
  data() {
    return {
      currentMessage: '',
      templates: null,
      history: null
    }
  }
}
</script>
