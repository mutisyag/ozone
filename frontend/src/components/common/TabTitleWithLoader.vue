<template>
<div class="tab-title">
	<span class="formNumber" v-if="tab.formNumber">({{tab.formNumber}})</span>
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
<style>

.spinner {
    z-index: 1;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    margin-left: 5px;
}
.formNumber {
	margin-right: .3rem;
}
.loader {
  border: 3px solid #f3f3f3;
  border-radius: 50%;
   border-top: 3px solid blue;
   border-right: 3px solid green;
   border-bottom: 3px solid red;
   border-left: 3px solid pink;
  width: 15px;
  height: 15px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}
.tab-title {
  display: flex;
}

.tab-title i {
  margin-left: 5px;
}
/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
