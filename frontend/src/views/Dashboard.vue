<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="6">
        <b-card>
          <div slot="header">
            <strong>Title </strong> <small>Form</small>
          </div>
          <div>
          	      <router-link
            class="nav-link"
            :to="{ name: 'Form'}"
          >
          form
          </router-link>

          </div>
        </b-card>
      </b-col>
      <b-col sm="6">
        <b-card>
          <div slot="header">
            <strong>Fitle </strong><small>Form</small>
          </div>
          <b-form-group>
            <label for="company">Company</label>
            <b-form-input type="text" id="company" placeholder="Enter your company name"></b-form-input>
          </b-form-group>
        </b-card>
      </b-col>
    </b-row>
    <b-row>
      <b-col md="6">
        <b-card>
          <div slot="header">
            <strong>Basic Form</strong> Elements
          </div>
        </b-card>
        <b-card>
          <div slot="header">
            <strong>Inline</strong> Form
          </div>
          <div slot="footer">
            <b-button type="submit" size="sm" variant="primary"><i class="fa fa-dot-circle-o"></i> Submit</b-button>
            <b-button type="reset" size="sm" variant="danger"><i class="fa fa-ban"></i> Reset</b-button>
          </div>
        </b-card>
      </b-col>
      <b-col md="6">
        <b-card>
          <div slot="header">
            <strong>Horizontal</strong> Form
          </div>
       
        </b-card>
        <b-card>
          <div slot="header">
            <strong>Normal</strong> Form
          </div>
        </b-card>
        <b-card no-body :no-block="true">
          <div slot="header">
            Input <strong>Grid</strong>
          </div>
          <b-card-body>
            asdas
          </b-card-body>
          <div slot="footer">
            <b-button type="submit" size="sm" variant="primary"><i class="fa fa-user"></i> Login</b-button>
            <b-button type="reset" size="sm" variant="danger"><i class="fa fa-ban"></i> Reset</b-button>
          </div>
        </b-card>
        <b-card>
          <div slot="header">
            Input <strong>Sizes</strong>
          </div>
          <div slot="footer">
            <b-button type="submit" size="sm" variant="primary"><i class="fa fa-dot-circle-o"></i> Submit</b-button>
            <b-button type="reset" size="sm" variant="danger"><i class="fa fa-ban"></i> Reset</b-button>
          </div>
        </b-card>
      </b-col>
    </b-row>
    <b-row>
      <b-col sm="12" md="6">
        <b-card no-body :no-block="true">
          <div slot="header">
            <strong>Validation feedback</strong> Form
          </div>
          <b-card-body>
         
          </b-card-body>
        </b-card>
      </b-col>
      <b-col sm="12" md="6">
        <b-card no-body :no-block="true">
          <div slot="header">
            <strong>Validation feedback</strong> Form
          </div>
          <b-card-body>
          </b-card-body>
        </b-card>
      </b-col>
     </b-row>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data () {
    return {
    }
  },
  methods: {
    click () {
      // do nothing
    }
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>