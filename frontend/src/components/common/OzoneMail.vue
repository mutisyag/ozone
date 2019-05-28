<template>
    <div>
      <b-btn class="square-right square-left" @click="getMail()" variant="outline-dark" v-translate>Ozone Mail</b-btn>
      <b-modal id="ozoneMail" size="xl" ref="ozoneMailModal">
        <b-tabs>
          <b-tab :title="$gettext('Send a message')">
            <b-row>
                <b-col cols="8">
                    <textarea style="height: 300px;" v-model="currentMessage" class="form-control mail-input"></textarea>
                    <b-btn variant="primary" class="mt-2">Send message</b-btn>
                </b-col>
                <b-col>
                  <h4>Templates</h4>
                  <b-list-group class="templates">
                    <b-list-group-item @click="currentMessage = template" class="template-item" v-for="(template, template_index) in templates" :key="template_index">
                      {{ template }}
                    </b-list-group-item>
                  </b-list-group>
                </b-col>
            </b-row>
          </b-tab>
          <b-tab v-if="history" :title="$gettext('Conversation history')">
            <div class="mt-4" v-for="(entry, index) in history" :key="index">
                <div><b>From:</b> {{entry.sender}}</div>
                <small><b>Date:</b> 10 May 2019</small>
                <div class="mt-2">{{entry.message}}</div>
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
import { getOzoneMail } from '@/components/common/services/api'

export default {
  props: {
    submission: String
  },
  data() {
    return {
      currentMessage: '',
      templates: [
        'Lorem ipsum dolor sit amet consectetur adipisicing elit. Veritatis eveniet eaque iusto perspiciatis autem ex eum',
        'Halvah apple pie gummi bears apple pie dragée apple pie wafer chocolate. Toffee chupa chups candy donut chocolate cake. Jujubes icing sweet donut oat cake pudding cupcake. Chocolate cake cookie tart chocolate bar gingerbread chocolate bar macaroon icing lollipop. Toffee cake carrot cake wafer carrot cake tart wafer. Jelly wafer biscuit. Candy canes cupcake topping mar',
        'Bear claw lemon drops muffin chupa chups candy wafer marshmallow halvah. Tiramisu gummies sweet roll gummi bears sesame snaps dragée wafer liquorice croissant. Gummies candy lollipop donut cotton candy cotton candy cotton candy halvah jelly. Fruitcake brownie carrot cake muffin sugar plum',
        'Tootsie roll carrot cake dessert soufflé. Brownie apple pie candy canes. Biscuit gingerbread icing jelly beans cupcake soufflé pie sweet roll. Toffee cotton candy croissant soufflé gingerbread danish. Pudding carrot cake muffin lemon drops cake jelly-o gummi bears. Donut toffee tootsie roll',
        'Lorem ipsum dolor, sit amet consectetur adipisicing elit. Commodi tenetur officia labore consequatur quidem necessitatibus, qui nisi. Quisquam dignissimos nemo asperiores veritatis? Sed unde molestias atque eos perspiciatis maxime ipsam.'
      ],
      history: null
    }
  },
  methods: {
    async getMail() {
      const mail = await getOzoneMail(this.submission)
      this.history = mail.data
      this.$refs.ozoneMailModal.show()
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
</style>
