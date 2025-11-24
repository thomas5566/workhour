<template>
    <section>
        <form @submit.prevent="onEditFetnetListSubmit">
            <b-container fluid>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="branch-id">branch-id</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.branch_id"
                            placeholder="branch-id"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-id">shop-id</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_id"
                            placeholder="shop-id"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-name">店別/店名</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_name"
                            placeholder="shop-name"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-tax">統編</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_tax"
                            placeholder="shop-tax"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-location">安裝地址</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_location"
                            placeholder="shop-location"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="fetnetlist-remark">公司名稱</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.fetnetlist_remark"
                            placeholder="fetnetlist-remark"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-phone-number">市話</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_phone_number"
                            placeholder="shop-phone-number"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="shop-phone-short-code">簡碼</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.shop_phone_short_code"
                            placeholder="shop-phone-short-code"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="adsl-number">光世代電路號碼(網路)</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.adsl_number"
                            placeholder="adsl-number"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="fetnet-phone-number">市話NGN號碼(網路電話)</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.fetnet_phone_number"
                            placeholder="fetnet-phone-number"></b-form-input>
                    </b-col>
                </b-row>
                <b-row class="my-1">
                    <b-col class="form-control" sm="3">
                        <label for="adsl-bank-number">ADSL金流附掛(刷卡機網路)</label>
                    </b-col>
                    <b-col>
                        <b-form-input class="form-control" sm="8" v-model="editFetnetListData.adsl_bank_number"
                            placeholder="adsl-bank-number"></b-form-input>
                    </b-col>
                </b-row>

                <b-row class="my-1">
                    <div>
                        <button @click=onEditFetnetListSubmit()>更新</button>
                        <button @click.prevent="$emit('onClose')">取消</button>
                    </div>
                </b-row>
            </b-container>
        </form>
    </section>
</template>
<script>
import { updateFetnetListByIdAPI } from "../../service/apis.js";
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
        shopId: {
            type: Number,
            required: true,
        },
        shopName: {
            type: String,
            required: true,
        },
        shopTax: {
            type: String,
            required: true,
        },
        shopLocation: {
            type: String,
            required: true,
        },
        shopPhoneNumber: {
            type: String,
            required: true,
        },
        shopPhoneShortCode: {
            type: String,
            required: true,
        },
        adslNumber: {
            type: String,
            required: true,
        },
        fetnetPhoneNumber: {
            type: String,
            required: true,
        },
        adslBankNumber: {
            type: String,
            required: true,
        },
        fetnetlistRemark: {
            type: String,
            required: true,
        }
    },
    data() {
        return {
            editFetnetListID: this.id,
            editFetnetListData: {
                branch_id: this.branchId,
                shop_id: this.shopId,
                shop_name: this.shopName,
                shop_tax: this.shopTax,
                shop_location: this.shopLocation,
                shop_phone_number: this.shopPhoneNumber,
                shop_phone_short_code: this.shopPhoneShortCode,
                adsl_number: this.adslNumber,
                fetnet_phone_number: this.fetnetPhoneNumber,
                adsl_bank_number: this.adslBankNumber,
                fetnetlist_remark: this.fetnetlistRemark,
            },
            emits: ["onClose"],
        };
    },
    methods: {
        onEditFetnetListSubmit() {
            updateFetnetListByIdAPI(this.editFetnetListID, this.editFetnetListData)
                .then((response) => {
                    this.$root.$emit("get_fetnetlists");
                    this.editFetnetListID = "";
                    this.editFetnetListData.branch_id = "";
                    this.editFetnetListData.shop_id = "";
                    this.editFetnetListData.shop_name = "";
                    this.editFetnetListData.shop_tax = "";
                    this.editFetnetListData.shop_phone_number = "";
                    this.editFetnetListData.shop_phone_short_code = "";
                    this.editFetnetListData.adsl_number = "";
                    this.editFetnetListData.fetnet_phone_number = "";
                    this.editFetnetListData.adsl_bank_number = "";
                    this.editFetnetListData.fetnetlist_remark = "";
                    this.$emit('onClose')

                    console.log(response.data);
                    this.message = "The Fetnet List was updated successfully!!";
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