<template>
  <section class="inventory-page">
    <header><div><p>CAMERA INVENTORY</p><h1>新增監視器資料</h1></div><router-link to="/ipcamlist">← 返回監視器清單</router-link></header>
    <form class="inventory-form" @submit.prevent="submit">
      <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
      <label class="wide"><span>地點 <b>*</b></span><select v-model.number="selectedShopId" required @change="syncShop"><option :value="0" disabled>請選擇地點</option><option v-for="shop in shops" :key="shop.id" :value="shop.id">{{ shop.shop_number }} - {{ shop.shop_name }}</option></select></label>
      <label><span>店號 <b>*</b></span><input v-model.number="form.shop_id" type="number" min="1" required></label><label><span>店名 <b>*</b></span><input v-model.trim="form.shop_name" required maxlength="255"></label>
      <label><span>監視器品牌</span><input v-model.trim="form.ipcam_brand" maxlength="255"></label><label><span>IP</span><input v-model.trim="form.ipcam_ip" maxlength="255"></label>
      <label><span>管理者帳號</span><input v-model.trim="form.admin_acc" maxlength="255"></label><label><span>管理者密碼</span><input v-model="form.admin_pass" maxlength="255" type="password" autocomplete="new-password"></label>
      <label><span>使用者帳號</span><input v-model.trim="form.user_acc" maxlength="255"></label><label><span>使用者密碼</span><input v-model="form.user_pass" maxlength="255" type="password" autocomplete="new-password"></label>
      <label><span>手機埠號</span><input v-model.trim="form.phone_port" maxlength="255"></label><label><span>HTTP 埠號</span><input v-model.trim="form.http_port" maxlength="255"></label><label><span>TCP 埠號</span><input v-model.trim="form.tcp_port" maxlength="255"></label>
      <label class="wide"><span>備註</span><textarea v-model.trim="form.remark" maxlength="255" rows="3"></textarea></label>
      <footer><router-link class="btn btn-outline-secondary" to="/ipcamlist">取消</router-link><button class="btn btn-primary" :disabled="submitting">{{ submitting ? "儲存中…" : "新增資料" }}</button></footer>
    </form>
  </section>
</template>
<script>
import { createIpcamListAPI, getCstShopsAPI } from "@/service/apis";
export default {
  name: "AddIpCamList",
  data: () => ({ shops: [], selectedShopId: 0, submitting: false, errorMessage: "", form: { shop_id: null, shop_name: "", ipcam_brand: "", ipcam_ip: "", admin_acc: "", admin_pass: "", user_acc: "", user_pass: "", phone_port: "", http_port: "", tcp_port: "", remark: "" } }),
  async mounted() { try { this.shops = (await getCstShopsAPI(2)).data; } catch { this.errorMessage = "無法取得地點清單。"; } },
  methods: {
    syncShop() { const shop = this.shops.find((item) => item.id === this.selectedShopId); if (!shop) return; this.form.shop_id = Number(shop.shop_number) || shop.id; this.form.shop_name = shop.shop_name || ""; },
    async submit() { this.submitting = true; this.errorMessage = ""; try { await createIpcamListAPI(this.form); await this.$router.push({ name: "IpCamList", query: { refresh: Date.now().toString() } }); } catch (error) { this.errorMessage = error.response?.data?.detail || "新增監視器資料失敗。"; } finally { this.submitting = false; } },
  },
};
</script>
<style scoped>
.inventory-page{min-height:100%;padding:28px;background:#f3f6fa;color:#172033}.inventory-page>header{display:flex;justify-content:space-between;align-items:center;max-width:960px;margin:0 auto 20px}.inventory-page header p{margin:0;color:#68809b;font-size:.72rem;font-weight:800;letter-spacing:.16em}.inventory-page h1{margin:4px 0 0}.inventory-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;max-width:960px;margin:auto;padding:26px;border:1px solid #dce4ee;border-radius:14px;background:#fff}.inventory-form label{display:flex;flex-direction:column;gap:7px}.inventory-form span{font-weight:700}.inventory-form b{color:#d92d20}.inventory-form input,.inventory-form select,.inventory-form textarea{padding:11px 12px;border:1px solid #cbd5e1;border-radius:8px}.wide,.alert,footer{grid-column:1/-1}.alert{padding:12px;color:#b42318;background:#fff0ef}footer{display:flex;justify-content:flex-end;gap:10px}@media(max-width:650px){.inventory-form{grid-template-columns:1fr}.inventory-form label{grid-column:1}}
</style>
