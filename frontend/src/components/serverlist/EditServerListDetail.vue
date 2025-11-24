<template>
    <section>
        <form @submit.prevent="onEditServerListSubmit">
            <b-container fluid>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-location">地點</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_location"
                            placeholder="server_location"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-name">設備名稱</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_name"
                            placeholder="server_name"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-ip">Server IP</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_ip"
                            placeholder="server_ip"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-acc">帳號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_acc"
                            placeholder="server_acc"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-pass">密碼</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_pass"
                            placeholder="server-pass"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="server-remark">備註</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editServerListData.server_remark"
                            placeholder="server-remark"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <div>
                        <button @click=onEditServerListSubmit()>更新</button>
                        <button @click.prevent="$emit('onClose')">取消</button>
                    </div>
                </b-row>
            </b-container>
        </form>
    </section>
</template>
<script>
import { updateServerListByIdAPI } from "../../service/apis.js";
export default {
    computed: {},
    components: {},
    props: {
        id: {
            type: Number,
            required: true,
        },
        branchId: {
            type: Number,
            required: true,
        },
        serverAcc: {
            type: String,
            required: true,
        },
        serverIp: {
            type: String,
            required: true,
        },
        serverLocation: {
            type: String,
            required: true,
        },
        serverName: {
            type: String,
            required: true,
        },
        serverPass: {
            type: String,
            required: true,
        },
        serverRemark: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            editServerListID: this.id,
            editServerListData: {
                server_acc: this.serverAcc,
                server_ip: this.serverIp,
                server_location: this.serverLocation,
                server_name: this.serverName,
                server_pass: this.serverPass,
                server_remark: this.serverRemark,
            },
            emits: ["onClose"],
        };
    },
    methods: {
        onEditServerListSubmit() {
            updateServerListByIdAPI(this.editServerListID, this.editServerListData)
                .then((response) => {
                    this.$root.$emit("get_serverlists");
                    this.editServerListID = "";
                    this.editServerListData.server_acc = "";
                    this.editServerListData.server_ip = "";
                    this.editServerListData.server_location = "";
                    this.editServerListData.server_name = "";
                    this.editServerListData.server_pass = "";
                    this.editServerListData.server_remark = "";
                    this.$emit('onClose')

                    console.log(response.data);
                    this.message = "The Server List was updated successfully!!";
                })
                .catch((e) => {
                    console.log(e);
                });
        }
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