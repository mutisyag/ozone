<template>
  <b-dropdown-item @click="logout"><i class="fa fa-lock" /> Logout</b-dropdown-item>
</template>

<script>

import authMixin from '@/components/common/mixins/auth'

export default {
	mixins: [authMixin],
	data: () => ({ itemsCount: 42 })
}
</script>
