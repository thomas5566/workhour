<template>
    <section>
        <form @submit.prevent="onEditIpcamListSubmit">
            <b-container fluid>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-id">shop-id</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.shop_id"
                            placeholder="shop-id"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-name">店別/店名</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.shop_name"
                            placeholder="shop-name"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="ipcam-brand">監視器品牌</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.ipcam_brand"
                            placeholder="ipcam-brand"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="ipcam-ip">IP</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.ipcam_ip"
                            placeholder="ipcam-ip"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="admin-acc">管理者帳號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.admin_acc"
                            placeholder="admin-acc"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="admin-pass">管理者密碼</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.admin_pass"
                            placeholder="admin-pass"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="user-acc">使用者帳號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.user_acc"
                            placeholder="user-acc"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="user-pass">使用者密碼</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.user_pass"
                            placeholder="user-pass"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="phone-port">電話埠號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.phone_port"
                            placeholder="phone-port"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="http-port">HTTP埠號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.http_port"
                            placeholder="http-port"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="tcp-port">HTTP埠號</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.tcp_port"
                            placeholder="tcp-port"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="re-mark">備註</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editIpcamListData.remark"
                            placeholder="re-mark"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <div>
                        <button @click=onEditIpcamListSubmit()>更新</button>
                        <button @click.prevent="$emit('onClose')">取消</button>
                    </div>
                </b-row>
            </b-container>
        </form>
    </section>
</template>
<script>
import { updateIpCamListByIdAPI } from "../../service/apis.js";
export default {
    computed: {},
    components: {},
    props: {
        id: {
            type: Number,
            required: true,
        },
        shopId: {
            type: Number,
            required: true,
        },
        shopName: {
            type: String,
            required: true,
        },
        IpcamBrand: {
            type: String,
            required: true,
        },
        IpcamIp: {
            type: String,
            required: true,
        },
        AdminAcc: {
            type: String,
            required: true,
        },
        AdminPass: {
            type: String,
            required: true,
        },
        UserAcc: {
            type: String,
            required: true,
        },
        UserPass: {
            type: String,
            required: true,
        },
        PhonePort: {
            type: String,
            required: true,
        },
        HttpPort: {
            type: String,
            required: true,
        },
        TcpPort: {
            type: String,
            required: true,
        },
        ReMark: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            editIpcamListID: this.id,
            editIpcamListData: {
                shop_id: this.shopId,
                shop_name: this.shopName,
                ipcam_brand: this.IpcamBrand,
                ipcam_ip: this.IpcamIp,
                admin_acc: this.AdminAcc,
                admin_pass: this.AdminPass,
                user_acc: this.UserAcc,
                user_pass: this.UserPass,
                phone_port: this.PhonePort,
                http_port: this.HttpPort,
                tcp_port: this.TcpPort,
                remark: this.ReMark,
            },
            emits: ["onClose"],
        };
    },
    methods: {
        onEditIpcamListSubmit() {
            updateIpCamListByIdAPI(this.editIpcamListID, this.editIpcamListData)
                .then((response) => {
                    this.$root.$emit("get_ipcamlists");
                    this.editIpcamListID = "";
                    this.editIpcamListData.shop_id = "";
                    this.editIpcamListData.shop_name = "";
                    this.editIpcamListData.ipcam_brand = "";
                    this.editIpcamListData.ipcam_ip = "";
                    this.editIpcamListData.admin_acc = "";
                    this.editIpcamListData.admin_pass = "";
                    this.editIpcamListData.user_acc = "";
                    this.editIpcamListData.user_pass = "";
                    this.editIpcamListData.phone_port = "";
                    this.editIpcamListData.http_port = "";
                    this.editIpcamListData.tcp_port = "";
                    this.editIpcamListData.remark = "";
                    this.$emit('onClose')

                    console.log(response.data);
                    this.message = "The Ipcam List was updated successfully!!";
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
    padding: -2rem;
    margin: 2rem auto;
    max-width: 80rem;
}

form {
    margin: 8rem auto;
    max-width: 40rem;
    height: 40rem auto;
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