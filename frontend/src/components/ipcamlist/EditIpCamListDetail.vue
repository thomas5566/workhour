<template>
  <section class="modal-card" role="dialog" aria-modal="true">
    <header><h2>編輯監視器資料</h2><button type="button" class="close" @click="$emit('onClose')">×</button></header>
    <form @submit.prevent="submit">
      <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
      <label><span>店號</span><input v-model.number="form.shop_id" type="number" min="1" required></label><label><span>店名</span><input v-model.trim="form.shop_name" required maxlength="255"></label>
      <label><span>監視器品牌</span><input v-model.trim="form.ipcam_brand" maxlength="255"></label><label><span>IP</span><input v-model.trim="form.ipcam_ip" maxlength="255"></label>
      <label><span>管理者帳號</span><input v-model.trim="form.admin_acc" maxlength="255"></label><label><span>管理者新密碼（留空表示不變）</span><input v-model="form.admin_pass" maxlength="255" type="password" autocomplete="new-password"></label>
      <label><span>使用者帳號</span><input v-model.trim="form.user_acc" maxlength="255"></label><label><span>使用者新密碼（留空表示不變）</span><input v-model="form.user_pass" maxlength="255" type="password" autocomplete="new-password"></label>
      <label><span>手機埠號</span><input v-model.trim="form.phone_port" maxlength="255"></label><label><span>HTTP 埠號</span><input v-model.trim="form.http_port" maxlength="255"></label><label><span>TCP 埠號</span><input v-model.trim="form.tcp_port" maxlength="255"></label>
      <label class="wide"><span>備註</span><textarea v-model.trim="form.remark" maxlength="255" rows="3"></textarea></label>
      <footer><button type="button" class="btn btn-outline-secondary" @click="$emit('onClose')">取消</button><button class="btn btn-primary" :disabled="submitting">{{ submitting ? "更新中…" : "更新" }}</button></footer>
    </form>
  </section>
</template>
<script>
import { updateIpCamListByIdAPI } from "@/service/apis";
export default {
  name: "EditIpCamListDetail", emits: ["onClose", "updated"],
  props: { id: { type: Number, required: true }, shopId: Number, shopName: String, ipcamBrand: String, ipcamIp: String, adminAcc: String, userAcc: String, phonePort: String, httpPort: String, tcpPort: String, reMark: String },
  data() { return { submitting: false, errorMessage: "", form: { shop_id: this.shopId, shop_name: this.shopName || "", ipcam_brand: this.ipcamBrand || "", ipcam_ip: this.ipcamIp || "", admin_acc: this.adminAcc || "", admin_pass: "", user_acc: this.userAcc || "", user_pass: "", phone_port: this.phonePort || "", http_port: this.httpPort || "", tcp_port: this.tcpPort || "", remark: this.reMark || "" } }; },
  methods: { async submit() { this.submitting = true; this.errorMessage = ""; try { const payload = { ...this.form }; if (!payload.admin_pass) delete payload.admin_pass; if (!payload.user_pass) delete payload.user_pass; await updateIpCamListByIdAPI(this.id, payload); this.$emit("updated"); } catch (error) { this.errorMessage = error.response?.data?.detail || "更新失敗，請檢查輸入資料。"; } finally { this.submitting = false; } } },
};
</script>
<style scoped>
.modal-card{position:relative;width:min(900px,calc(100vw - 32px));max-height:calc(100vh - 48px);margin:24px auto;overflow:auto;border-radius:14px;background:#fff}.modal-card>header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid #e2e8f0}.modal-card h2{margin:0}.close{border:0;background:transparent;font-size:2rem}form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding:24px}label{display:flex;flex-direction:column;gap:6px}label span{font-weight:700}input,textarea{padding:10px;border:1px solid #cbd5e1;border-radius:8px}.wide,.alert,footer{grid-column:1/-1}.alert{padding:12px;color:#b42318;background:#fff0ef}footer{display:flex;justify-content:flex-end;gap:10px}@media(max-width:650px){form{grid-template-columns:1fr}label{grid-column:1}}
</style>
