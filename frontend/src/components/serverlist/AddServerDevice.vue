<template>
  <section class="add-device-page" aria-labelledby="add-device-title">
    <header>
      <div>
        <p>SERVER INVENTORY</p>
        <h1 id="add-device-title">新增設備</h1>
      </div>
      <router-link to="/serverlist" class="back-link">
        <i class="fas fa-arrow-left"></i> 返回設備清單
      </router-link>
    </header>

    <form class="device-form" @submit.prevent="submitDevice">
      <div v-if="errorMessage" class="form-alert" role="alert">{{ errorMessage }}</div>

      <label>
        <span>地點 <b>*</b></span>
        <select v-model.number="form.branch_id" required @change="syncLocation">
          <option :value="0" disabled>請選擇地點</option>
          <option v-for="branch in branches" :key="branch.id" :value="branch.id">
            {{ branch.branch_title }} - {{ branch.branch_name }}
          </option>
        </select>
      </label>

      <label><span>設備名稱 <b>*</b></span><input v-model.trim="form.server_name" required maxlength="255"></label>
      <label><span>Server IP <b>*</b></span><input v-model.trim="form.server_ip" required maxlength="255" inputmode="decimal" placeholder="例如 192.168.1.10"></label>
      <label><span>帳號 <b>*</b></span><input v-model.trim="form.server_acc" required maxlength="255" autocomplete="off"></label>
      <label><span>密碼 <b>*</b></span><input v-model="form.server_pass" required maxlength="255" type="password" autocomplete="new-password"></label>
      <label class="full-width"><span>備註</span><textarea v-model.trim="form.server_remark" maxlength="255" rows="4"></textarea></label>

      <footer>
        <router-link to="/serverlist" class="btn btn-outline-secondary">取消</router-link>
        <button class="btn btn-primary" type="submit" :disabled="submitting || loadingBranches">
          <i class="fas fa-save"></i> {{ submitting ? "儲存中…" : "新增設備" }}
        </button>
      </footer>
    </form>
  </section>
</template>

<script>
import { createServerListAPI, getBranchListAPI } from "@/service/apis";

export default {
  name: "AddServerDevice",
  data() {
    return {
      branches: [],
      loadingBranches: false,
      submitting: false,
      errorMessage: "",
      form: {
        branch_id: 0,
        server_location: "",
        server_name: "",
        server_ip: "",
        server_acc: "",
        server_pass: "",
        server_remark: "",
      },
    };
  },
  mounted() {
    this.loadBranches();
  },
  methods: {
    async loadBranches() {
      this.loadingBranches = true;
      try {
        const response = await getBranchListAPI();
        this.branches = response.data;
      } catch {
        this.errorMessage = "無法取得地點清單，請稍後再試。";
      } finally {
        this.loadingBranches = false;
      }
    },
    syncLocation() {
      const branch = this.branches.find((item) => item.id === this.form.branch_id);
      this.form.server_location = branch
        ? `${branch.branch_title} - ${branch.branch_name}`
        : "";
    },
    async submitDevice() {
      if (!this.form.branch_id || !this.form.server_location) {
        this.errorMessage = "請選擇地點。";
        return;
      }
      this.submitting = true;
      this.errorMessage = "";
      try {
        await createServerListAPI(this.form);
        // Re-entering the list route mounts it again and fetches the latest rows.
        await this.$router.push({
          name: "ServerList",
          query: { refresh: Date.now().toString() },
        });
      } catch (error) {
        this.errorMessage = error.response?.data?.detail || "新增設備失敗，請檢查輸入資料。";
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.add-device-page { min-height: 100%; padding: 28px; color: #172033; background: #f3f6fa; }
.add-device-page > header { display: flex; align-items: center; justify-content: space-between; gap: 20px; max-width: 900px; margin: 0 auto 20px; }
.add-device-page header p { margin: 0 0 5px; color: #68809b; font-size: .72rem; font-weight: 800; letter-spacing: .16em; }
.add-device-page h1 { margin: 0; font-size: 2rem; }.back-link { color: #1769e0; text-decoration: none; }
.device-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; max-width: 900px; padding: 26px; margin: auto; border: 1px solid #dce4ee; border-radius: 14px; background: white; box-shadow: 0 10px 30px rgba(30, 48, 75, .06); }
.device-form label { display: flex; flex-direction: column; gap: 7px; }.device-form label > span { font-weight: 700; }.device-form b { color: #d92d20; }
.device-form input, .device-form select, .device-form textarea { width: 100%; padding: 11px 12px; color: #172033; border: 1px solid #cbd5e1; border-radius: 8px; background: white; }
.device-form input:focus, .device-form select:focus, .device-form textarea:focus { outline: 3px solid rgba(23, 105, 224, .14); border-color: #1769e0; }
.full-width, .form-alert, .device-form footer { grid-column: 1 / -1; }.form-alert { padding: 12px 14px; color: #b42318; border-radius: 8px; background: #fff0ef; }
.device-form footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 8px; }
.device-form button i { margin-right: 6px; }
@media (max-width: 650px) { .add-device-page { padding: 18px; }.add-device-page > header { align-items: flex-start; flex-direction: column; }.device-form { grid-template-columns: 1fr; padding: 19px; }.device-form label { grid-column: 1; } }
</style>
