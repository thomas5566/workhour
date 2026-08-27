<template>
  <section class="modal-card" role="dialog" aria-modal="true">
    <header><h2>編輯遠傳資料</h2><button type="button" class="close" @click="$emit('onClose')">×</button></header>
    <form @submit.prevent="submit">
      <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
      <label><span>門店</span><select v-model.number="form.branch_id" required><option v-for="branch in branches" :key="branch.id" :value="branch.id">{{ branch.branch_title }} - {{ branch.branch_name }}</option></select></label>
      <label><span>店號</span><input v-model.number="form.shop_id" type="number" min="1" required></label>
      <label><span>店名</span><input v-model.trim="form.shop_name" required maxlength="255"></label><label><span>統編</span><input v-model.trim="form.shop_tax" maxlength="255"></label>
      <label class="wide"><span>安裝地址</span><input v-model.trim="form.shop_location" maxlength="255"></label><label><span>公司名稱</span><input v-model.trim="form.fetnetlist_remark" maxlength="255"></label>
      <label><span>電話／市話</span><input v-model.trim="form.shop_phone_number" maxlength="255"></label><label><span>簡碼</span><input v-model.trim="form.shop_phone_short_code" maxlength="255"></label>
      <label><span>光世代電路號碼</span><input v-model.trim="form.adsl_number" maxlength="255"></label><label><span>市話 NGN 號碼</span><input v-model.trim="form.fetnet_phone_number" maxlength="255"></label><label><span>ADSL 金流附掛</span><input v-model.trim="form.adsl_bank_number" maxlength="255"></label>
      <footer><button type="button" class="btn btn-outline-secondary" @click="$emit('onClose')">取消</button><button class="btn btn-primary" :disabled="submitting">{{ submitting ? "更新中…" : "更新" }}</button></footer>
    </form>
  </section>
</template>
<script>
import { getBranchListAPI, updateFetnetListByIdAPI } from "@/service/apis";
export default {
  name: "EditFetnetListDetail", emits: ["onClose", "updated"],
  props: { id: { type: Number, required: true }, branchId: Number, shopId: Number, shopName: String, shopTax: String, shopLocation: String, shopPhoneNumber: String, shopPhoneShortCode: String, adslNumber: String, fetnetPhoneNumber: String, adslBankNumber: String, fetnetlistRemark: String },
  data() { return { branches: [], submitting: false, errorMessage: "", form: { branch_id: this.branchId, shop_id: this.shopId, shop_name: this.shopName || "", shop_tax: this.shopTax || "", shop_location: this.shopLocation || "", shop_phone_number: this.shopPhoneNumber || "", shop_phone_short_code: this.shopPhoneShortCode || "", adsl_number: this.adslNumber || "", fetnet_phone_number: this.fetnetPhoneNumber || "", adsl_bank_number: this.adslBankNumber || "", fetnetlist_remark: this.fetnetlistRemark || "" } }; },
  async mounted() { try { this.branches = (await getBranchListAPI()).data; } catch { this.errorMessage = "無法取得門店清單。"; } },
  methods: { async submit() { this.submitting = true; this.errorMessage = ""; try { await updateFetnetListByIdAPI(this.id, this.form); this.$emit("updated"); } catch (error) { this.errorMessage = error.response?.data?.detail || "更新失敗，請檢查輸入資料。"; } finally { this.submitting = false; } } },
};
</script>
<style scoped>
.modal-card{position:relative;width:min(900px,calc(100vw - 32px));max-height:calc(100vh - 48px);margin:24px auto;overflow:auto;border-radius:14px;background:#fff}.modal-card>header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid #e2e8f0}.modal-card h2{margin:0}.close{border:0;background:transparent;font-size:2rem}form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding:24px}label{display:flex;flex-direction:column;gap:6px}label span{font-weight:700}input,select{padding:10px;border:1px solid #cbd5e1;border-radius:8px}.wide,.alert,footer{grid-column:1/-1}.alert{padding:12px;color:#b42318;background:#fff0ef}footer{display:flex;justify-content:flex-end;gap:10px}@media(max-width:650px){form{grid-template-columns:1fr}label{grid-column:1}}
</style>
