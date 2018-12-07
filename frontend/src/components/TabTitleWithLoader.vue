<template>
<div class="tab-title">
	{{tab.title}}
	<div v-if="tab.status === 'saving'" class="spinner">
		<div class="loader"></div>
	</div>
	<i v-if="tab.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
	<i v-if="tab.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
	<i v-if="tab.status === 'edited'" class="fa fa-edit fa-lg"></i>
</div>
</template>

<script>

export default {
	props: {
		tab: Object
	}

}
</script>
