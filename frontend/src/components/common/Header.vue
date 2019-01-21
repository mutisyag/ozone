<template>
<b-row>
	<HeaderDropdown class="mr-3" right>
		<template slot="header">
			{{$language.available[$language.current]}}
		</template>
		<template slot="dropdown">
			<b-dropdown-item @click="setCurrentLanguage(key)" v-for="(language, key) in $language.available" :key="language.key"><span>{{language}}</span></b-dropdown-item>
		</template>
	</HeaderDropdown>
	<HeaderDropdown class="mr-3" right id="account_options">
		<template v-if="$store.state.currentUser" slot="header">
			{{$store.state.currentUser.username}} <span style="font-size: 1.2rem;" v-if="currentCountryIso" :class="`flag-icon flag-icon-${currentCountryIso}`"></span>
		</template>
		<template slot="dropdown">
			<b-dropdown-header tag="div" class="text-center"><strong><span v-translate>Account</span></strong></b-dropdown-header>
			<b-dropdown-item :href="`${apiBase}/admin/password_change/`"><i class="fa fa-unlock" /> <span v-translate>Reset password</span></b-dropdown-item>
			<b-dropdown-item @click="logout" id="logout_button"><i class="fa fa-lock" /><span v-translate>Logout</span></b-dropdown-item>
		<!-- <b-dropdown-divider /> -->
		</template>
	</HeaderDropdown>
</b-row>
</template>

<script>

import authMixin from '@/components/common/mixins/auth'
import { HeaderDropdown } from '@coreui/vue'
import { apiBase } from '@/components/common/services/api'
import { setLanguage } from '@/components//common/services/languageService'

export default {
	mixins: [authMixin],
	components: {
		HeaderDropdown
	},
	data() {
		return {
			apiBase
		}
	},
	computed: {
		currentCountryIso() {
			return this.$store.getters.currentCountryIso
		}
	},
	methods: {
		setCurrentLanguage(languageKey) {
			setLanguage(languageKey, this)
		}
	}
}
</script>
