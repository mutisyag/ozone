<template>
	<i v-if="item" class="fa fa-check-square-o" aria-hidden="true"></i>
	<i v-else class="fa fa-square-o" aria-hidden="true"></i>
</template>

<script>
export default {
	props: {
		item: [Object, Boolean]
	}
}
</script>
