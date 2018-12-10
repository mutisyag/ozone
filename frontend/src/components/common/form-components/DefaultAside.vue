<template>
  <div>
    <AsideToggler class="d-none d-lg-block" />
    <b-tabs v-model="tabIndex">
      <b-tab>
        <template slot="title">
          Substances
        </template>
          <add :tabName="tabName"></add>
      </b-tab>
      <b-tab v-if="tabName !== 'has_destroyed'">
        <template slot="title">
          Blends
        </template>
          <AddBlend :tabName="tabName"></AddBlend>
      </b-tab>
      <b-tab>
        <template slot="title">
          Validation
        </template>
        <Validation :hovered="hovered" :tabName="tabName"></Validation>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>

import { AsideToggler } from '@coreui/vue'
import Add from './Add'
import AddBlend from './AddBlend'
import Validation from './Validation'

export default {
	name: 'DefaultAside',
	components: {
		add: Add,
		AddBlend,
		AsideToggler,
		Validation
	},

	data() {
		return {
			tabIndex: 0
		}
	},

	props: {
		hovered: null,
		tabName: String,
		parentTabIndex: Number
	},

	watch: {
		parentTabIndex: {
			handler(new_val) {
				if (new_val !== this.tabIndex) {
					console.log(new_val)
					this.tabIndex = new_val
				}
			}
		},
		tabIndex: {
			handler(new_val) {
				if (new_val !== this.parentTabIndex) {
					this.$emit('update:parentTabIndex', new_val)
				}
			}
		}
	}

}
</script>
