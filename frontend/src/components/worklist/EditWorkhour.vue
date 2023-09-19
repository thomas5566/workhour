<template>
    <section>
        <form @submit.prevent="onEditWorkhourSubmit">
            <b-container fluid>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="user-name">部門/門店 名稱:</label>
                    </b-col>
                    <b-col>
                        <label class="form-control" sm="9" id="user-name" name="user-name">
                            {{ editWorkhourData.task_name }} -
                            {{ editWorkhourData.shopDepartmentShopName }}
                            ({{ editWorkhourData.shopDepartmentShopNumber }})
                        </label>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="input-default">叫修日期/時間:</label>
                    </b-col>
                    <b-col sm="9">
                        <b-form-datepicker id="start_date" placeholder="dd-mm-yyyy" v-model="editWorkhourData.start_date"
                            required locale="zh-CN" menu-class="w-100" calendar-width="100%" today-button close-button>
                        </b-form-datepicker>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="input-default">結束日期/時間:</label>
                    </b-col>
                    <b-col sm="9">
                        <b-form-datepicker id="end_date" placeholder="dd-mm-yyyy" v-model="editWorkhourData.end_date"
                            required locale="zh-CN" menu-class="w-100" calendar-width="100%" today-button close-button>
                        </b-form-datepicker>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="department">叫修內容：</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editWorkhourData.description"
                            placeholder="叫修內容..."></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="department">故障原因：</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editWorkhourData.cause_issue"
                            placeholder="故障原因..."></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="department">處理方式：</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editWorkhourData.processing_method"
                            placeholder="處理方式..."></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="department">結案(是/否)：</label>
                    </b-col>
                    <b-col>
                        <b-form-checkbox class="form-control" sm="8" v-model="editWorkhourData.case_close"
                            switch></b-form-checkbox>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="department">備註：</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editWorkhourData.todo"
                            placeholder="備註..."></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <div>
                        <button @click=onEditWorkhourSubmit()>更新</button>
                        <button @click.prevent="$emit('onClose')">取消</button>
                    </div>
                </b-row>
            </b-container>
        </form>
    </section>
</template>
<script>
import { updateWorkhourAPI } from "../../service/apis.js";
export default {
    computed: {},
    components: {},
    props: {
        id: {
            type: Number,
            required: true,
        },
        departmentName: {
            type: String,
            required: true,
        },
        userId: {
            type: Number,
            required: true,
        },
        userName: {
            type: String,
            required: true,
        },
        caseClose: {
            type: Boolean,
            required: true,
        },
        causeIssue: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        endDate: {
            type: String,
            required: true,
        },
        processingMethod: {
            type: String,
            required: true,
        },
        shopId: {
            type: Number,
            required: true,
        },
        shopDepartmentId: {
            type: Number,
            required: true,
        },
        shopDepartmentShopName: {
            type: String,
            required: true,
        },
        shopDepartmentShopNumber: {
            type: String,
            required: true,
        },
        startDate: {
            type: String,
            required: true,
        },
        taskId: {
            type: Number,
            required: true,
        },
        taskTaskname: {
            type: String,
            required: true,
        },
        todo: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            editWorkhourData: {
                id: this.id,
                department_name: this.departmentName,
                user_id: this.userId,
                username: this.userName,
                start_date: this.startDate,
                end_date: this.endDate,
                case_close: this.caseClose,
                cause_issue: this.causeIssue,
                description: this.description,
                processing_method: this.processingMethod,
                shop_id: this.shopId,
                shopDepartmentId: this.shopDepartmentId,
                shopDepartmentShopName: this.shopDepartmentShopName,
                shopDepartmentShopNumber: this.shopDepartmentShopNumber,
                task_id: this.taskId,
                task_name: this.taskTaskname,
                todo: this.todo,
                hour: 0,
                overtime_hour: 0
            },
            emits: ["onClose"],
        };
    },

    methods: {
        onEditWorkhourSubmit() {
            updateWorkhourAPI(this.editWorkhourData.id, this.editWorkhourData)
                .then((response) => {
                    this.$root.$emit("get_workhour");
                    this.editWorkhourId = "";
                    this.editWorkhourData.id = "";
                    this.editWorkhourData.department_name = "";
                    this.editWorkhourData.user_id = "";
                    this.editWorkhourData.username = "";
                    this.editWorkhourData.task_id = "";
                    this.editWorkhourData.task_name = "";
                    this.editWorkhourData.start_date = "";
                    this.editWorkhourData.description = "";
                    this.editWorkhourData.case_close = "";
                    this.editWorkhourData.end_date = "";
                    this.editWorkhourData.todo = "";
                    this.editWorkhourData.cause_issue = "";
                    this.editWorkhourData.processing_method = "";
                    this.editWorkhourData.shop_id = "";
                    this.editWorkhourData.shopDepartmentShopName = "";
                    this.editWorkhourData.shopDepartmentShopNumber = "";
                    this.$emit('onClose')

                    console.log(response.data);
                    this.message = "The Expen was updated successfully!!";
                })
                .catch((e) => {
                    console.log(e);
                });
        },
        /*onWorkhourSubmit() {
            updateWorkhourAPI(this.editWorkhourData.workhourId, this.editWorkhourData)
                .then((response) => {
                    // reflash data list when chiled component update data
                    this.$root.$emit("get_workhour");
                    this.id = "";
                    this.departmentName = "";
                    this.userId = "";
                    this.userName = "";
                    this.startDate = "";
                    this.endDate = "";
                    this.caseClose = "";
                    this.causeIssue = "";
                    this.description = "";
                    this.processingMethod = "";
                    this.shopId = "";
                    this.shopDepartmentId = "";
                    this.shopDepartmentShopName = "";
                    this.shopDepartmentShopNumber = "";
                    this.taskId = "";
                    this.taskTaskname = "";
                    this.todo = "";
                    console.log(response.data);
                    this.message = "The workhour Data was updated successfully!!";
                })
                .catch((e) => {
                    console.log(e);
                });
        },*/
    },
};
</script>
<style scoped>
section {
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    padding: 1rem;
    margin: 2rem auto;
    max-width: 80rem;
}

form {
    margin: 8rem auto;
    max-width: 40rem;
    height: auto;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.26);
    padding: 2rem;
    background-color: #ffffff;
}

.form-control {
    margin: 0.5rem 0;
}

.form-control.invalid input {
    border-color: red;
}

.form-control.invalid label {
    color: red;
}

label {
    font-weight: bold;
}

h2 {
    font-size: 1rem;
    margin: 0.5rem 0;
}

input,
select {
    display: block;
    width: 100%;
    font: inherit;
    margin-top: 0.5rem;
}

select {
    width: auto;
}

input[type="checkbox"],
input[type="radio"] {
    display: inline-block;
    width: auto;
    margin-right: 1rem;
}

input[type="checkbox"]+label,
input[type="radio"]+label {
    font-weight: normal;
}

button {
    font: inherit;
    border: 1px solid #0076bb;
    background-color: #0076bb;
    color: white;
    cursor: pointer;
    padding: 0.75rem 2rem;
    border-radius: 30px;
}

button:hover,
button:active {
    border-color: #002350;
    background-color: #002350;
}

.backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    z-index: 10;
    background-color: rgba(0, 0, 0, 0.75);
}
</style>