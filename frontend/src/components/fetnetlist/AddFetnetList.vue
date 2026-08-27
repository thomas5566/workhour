<template>
  <section class="inventory-page">
    <header><div><p>FETNET INVENTORY</p><h1>新增遠傳資料</h1></div><router-link to="/fetnetlist">← 返回遠傳清單</router-link></header>
    <form class="inventory-form" @submit.prevent="submit">
      <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
      <label><span>地點 <b>*</b></span><select v-model.number="selectedShopId" required @change="syncShop"><option :value="0" disabled>請選擇地點</option><option v-for="shop in shops" :key="shop.id" :value="shop.id">{{ shop.shop_number }} - {{ shop.shop_name }}</option></select></label>
      <label><span>店號 <b>*</b></span><input v-model.number="form.shop_id" type="number" min="1" required></label>
      <label><span>店名 <b>*</b></span><input v-model.trim="form.shop_name" required maxlength="255"></label>
      <label><span>統編</span><input v-model.trim="form.shop_tax" maxlength="255"></label>
      <label class="wide"><span>安裝地址</span><input v-model.trim="form.shop_location" maxlength="255"></label>
      <label><span>公司名稱</span><input v-model.trim="form.fetnetlist_remark" maxlength="255"></label>
      <label><span>電話／市話</span><input v-model.trim="form.shop_phone_number" maxlength="255"></label>
      <label><span>簡碼</span><input v-model.trim="form.shop_phone_short_code" maxlength="255"></label>
      <label><span>光世代電路號碼</span><input v-model.trim="form.adsl_number" maxlength="255"></label>
      <label><span>市話 NGN 號碼</span><input v-model.trim="form.fetnet_phone_number" maxlength="255"></label>
      <label><span>ADSL 金流附掛</span><input v-model.trim="form.adsl_bank_number" maxlength="255"></label>
      <footer><router-link class="btn btn-outline-secondary" to="/fetnetlist">取消</router-link><button class="btn btn-primary" :disabled="submitting">{{ submitting ? "儲存中…" : "新增資料" }}</button></footer>
    </form>
  </section>
</template>
<script>
import { createFetnetListAPI, getCstShopsAPI } from "@/service/apis";
export default {
  name: "AddFetnetList",
  data: () => ({ shops: [], selectedShopId: 0, submitting: false, errorMessage: "", form: { shop_id: null, shop_name: "", shop_tax: "", shop_location: "", shop_phone_number: "", shop_phone_short_code: "", adsl_number: "", fetnet_phone_number: "", adsl_bank_number: "", fetnetlist_remark: "" } }),
  async mounted() { try { this.shops = (await getCstShopsAPI(2)).data; } catch { this.errorMessage = "無法取得地點清單。"; } },
  methods: {
    syncShop() { const shop = this.shops.find((item) => item.id === this.selectedShopId); if (!shop) return; this.form.shop_id = Number(shop.shop_number) || shop.id; this.form.shop_name = shop.shop_name || ""; },
    async submit() { this.submitting = true; this.errorMessage = ""; try { await createFetnetListAPI(this.form); await this.$router.push({ name: "FetnetList", query: { refresh: Date.now().toString() } }); } catch (error) { this.errorMessage = error.response?.data?.detail || "新增遠傳資料失敗。"; } finally { this.submitting = false; } },
  },
};
</script>
<style scoped>
.inventory-page{min-height:100%;padding:28px;background:#f3f6fa;color:#172033}.inventory-page>header{display:flex;justify-content:space-between;align-items:center;max-width:960px;margin:0 auto 20px}.inventory-page header p{margin:0;color:#68809b;font-size:.72rem;font-weight:800;letter-spacing:.16em}.inventory-page h1{margin:4px 0 0}.inventory-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;max-width:960px;margin:auto;padding:26px;border:1px solid #dce4ee;border-radius:14px;background:#fff}.inventory-form label{display:flex;flex-direction:column;gap:7px}.inventory-form span{font-weight:700}.inventory-form b{color:#d92d20}.inventory-form input,.inventory-form select{padding:11px 12px;border:1px solid #cbd5e1;border-radius:8px}.wide,.alert,footer{grid-column:1/-1}.alert{padding:12px;color:#b42318;background:#fff0ef}footer{display:flex;justify-content:flex-end;gap:10px}@media(max-width:650px){.inventory-form{grid-template-columns:1fr}.inventory-form label{grid-column:1}}
</style>
