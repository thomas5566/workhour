<template>
  <div>
    <!-- <b-button v-b-modal.modal-scrollable>Launch scrolling modal</b-button>

    <b-modal id="modal-scrollable" scrollable title="Scrollable Content">
      <p class="my-4" v-for="i in 1" :key="i">
        Cras mattis consectetur purus sit amet fermentum. Cras justo odio, dapibus ac facilisis
        in, egestas eget quam. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.
      </p>
    </b-modal>-->

    <b-button v-b-modal.modal-prevent-closing>Open Modal</b-button>

    <div class="mt-3">
      Submitted Names:
      <div v-if="submittedNames.length === 0">--</div>
      <ul v-else class="mb-0 pl-3">
        <li v-for="name in submittedNames" :key="name.id">{{ name }}</li>
      </ul>
    </div>

    <b-modal
      id="modal-prevent-closing"
      ref="modal"
      title="Submit Your Name"
      @show="resetModal"
      @hidden="resetModal"
      @ok="handleOk"
      scrollable
    >
      <form ref="form" @submit.stop.prevent="handleSubmit">
        <b-form-group
          label="Name"
          label-for="name-input"
          invalid-feedback="Name is required"
          :state="nameState">

          <template v-if="editId == expen.id">
                      <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <!-- <th scope="col">Expen ID</th> -->
                  <th>部門</th>
                  <th>姓名</th>
                  <th>支出項目</th>
                  <th>日期</th>
                  <th>支出說明</th>
                  <th>支出費用</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="expen in pageOfExpens" v-bind:key="expen.id">
                  <template v-if="editId == expen.id">
                    <!-- <td>
                      <input
                        v-model="editExpenData.id"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td> -->
                    <td>
                      <input
                      size="10"
                      v-model="editExpenData.department_name"
                      type="text"
                      :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input
                        v-model="editExpenData.user_id"
                        type="text"
                        :disabled="isDisabled"
                      /> -->
                      <input
                      size="8"
                        v-model="editExpenData.username"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input
                        v-model="editExpenData.expentask_id"
                        type="text"
                        :disabled="isDisabled"
                      /> -->
                      <input
                      size="10"
                        v-model="editExpenData.expentask_name"
                        type="text"
                        :disabled="isDisabled"
                      />
                    </td>
                    <td>
                      <!-- <input v-model="editExpenData.date" type="text" /> -->
                      <th>
                      <div>
                        <b-input-group class="mb-3">
                          <!-- <b-form-input
                            id="example-input"
                            v-model="editExpenData.date"
                            type="text"
                            placeholder="YYYY-MM-DD"
                            autocomplete="off"
                          ></b-form-input> -->
                          <b-input-group-append>
                            <b-form-datepicker
                              v-model="editExpenData.date"
                              button-only
                              size="sm"
                              right
                              locale="zh-CN"
                              aria-controls="example-input"
                              @context="onContext"
                            ></b-form-datepicker>
                          </b-input-group-append>
                        </b-input-group>
                      </div>
                      </th>
                    </td>
                    <td>
                      <input v-model="editExpenData.description" type="text" />
                    </td>
                    <td><input size="5" v-model="editExpenData.price" type="text" /></td>
                    
                    <td>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-success"
                        @click="onEditSubmit(expen.id)"
                      >
                        更新
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-info"
                        @click="onCancel"
                      >
                        取消
                      </button>
                    </td>
                  </template>
                </tr>
              </tbody>
            </table>
            <edit-expen v-if="showEditExpencmp"></edit-expen>
          </div>
          </template>
          <p class="my-4" v-for="i in 5" :key="i">
            Cras mattis consectetur purus sit amet fermentum. Cras justo odio, dapibus ac facilisis
            in, egestas eget quam. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.
          </p>
          <label for>name</label>
          <!-- <b-form-input
              id="name-input"
              v-model="expen.department_name"
              :state="nameState"
              required
          ></b-form-input>-->
          <b-form-input id="name-input" v-model="editExpenData.username" required></b-form-input>
        </b-form-group>
      </form>
    </b-modal>
  </div>
</template>

<script>
import { getExpenAPI, updateExpenAPI } from "../../service/apis.js";
export default {
  data() {
    return {
      name: "",
      nameState: null,
      submittedNames: [],

      expens: [],
      editId: "",
      editExpenData: {
        id: "",
        user_id: "",
        username: "",
        expentask_id: "",
        expentask_name: "",
        date: "",
        description: "",
        price: "",
        department_name: "",
      },
    };
  },
  mounted: function () {
    this.get_expens();
  },
  methods: {
    onEdit(expen) {
      this.editId = expen.id;
      this.editExpenData.id = expen.id;
      this.editExpenData.username = expen.user.username;
      this.editExpenData.expentask_id = expen.expentask.id;
      this.editExpenData.expentask_name = expen.expentask.expentask_name;
      this.editExpenData.date = expen.date;
      this.editExpenData.description = expen.description;
      this.editExpenData.price = expen.price;
      this.editExpenData.user_id = expen.user.id;
      this.editExpenData.department_name =
        expen.user.department.department_name;
    },
    onCancel() {
      this.editId = "";
      this.editExpenData.id = "";
      this.editExpenData.username = "";
      this.editExpenData.expentask_id = "";
      this.editExpenData.expentask_name = "";
      this.editExpenData.date = "";
      this.editExpenData.description = "";
      this.editExpenData.price = "";
      this.editExpenData.user_id = "";
      this.editExpenData.department_name = "";
    },
    onEditSubmit() {
      updateExpenAPI(this.editExpenData.id, this.editExpenData)
        .then((response) => {
          this.get_expen();
          this.editId = "";
          this.editExpenData.id = "";
          this.editExpenData.username = "";
          this.editExpenData.expentask_id = "";
          this.editExpenData.expentask_name = "";
          this.editExpenData.date = "";
          this.editExpenData.description = "";
          this.editExpenData.price = "";
          this.editExpenData.user_id = "";
          this.editExpenData.department_name = "";
          console.log(response.data);
          this.message = "The Expen was updated successfully!!";
        })
        .catch((e) => {
          console.log(e);
        });
    },
    get_expens() {
      getExpenAPI().then((response) => {
        this.expens = response.data;
      });
    },
    checkFormValidity() {
      const valid = this.$refs.form.checkValidity();
      this.nameState = valid;
      return valid;
    },
    resetModal() {
      this.name = "";
      this.nameState = null;
    },
    handleOk(bvModalEvt) {
      // Prevent modal from closing
      bvModalEvt.preventDefault();
      // Trigger submit handler
      this.handleSubmit();
    },
    handleSubmit() {
      // Exit when the form isn't valid
      if (!this.checkFormValidity()) {
        return;
      }
      // Push the name to submitted names
      this.submittedNames.push(this.name);
      // Hide the modal manually
      this.$nextTick(() => {
        this.$bvModal.hide("modal-prevent-closing");
      });
    },
  },
};
</script>