<template>
  <section class="editor-dialog" role="dialog" aria-modal="true" aria-labelledby="edit-server-title">
    <form @submit.prevent="submitUpdate">
      <header>
        <div><p>SERVER INVENTORY</p><h2 id="edit-server-title">編輯設備</h2></div>
        <button type="button" class="close-button" aria-label="關閉" @click="$emit('onClose')">×</button>
      </header>
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
      <label><span>Server IP <b>*</b></span><input v-model.trim="form.server_ip" required maxlength="255"></label>
      <label><span>帳號 <b>*</b></span><input v-model.trim="form.server_acc" required maxlength="255" autocomplete="off"></label>
      <label><span>新密碼（留空表示不變）</span><input v-model="form.server_pass" maxlength="255" type="password" autocomplete="new-password"></label>
      <label><span>備註</span><textarea v-model.trim="form.server_remark" maxlength="255" rows="3"></textarea></label>
      <footer>
        <button type="button" class="btn btn-outline-secondary" @click="$emit('onClose')">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="submitting || loadingBranches">
          {{ submitting ? "更新中…" : "更新" }}
        </button>
      </footer>
    </form>
  </section>
</template>

<script>
import { getBranchListAPI, updateServerListByIdAPI } from "@/service/apis";

export default {
  name: "EditServerListDetail",
  emits: ["onClose", "updated"],
  props: {
    id: { type: Number, required: true },
    branchId: { type: Number, default: 0 },
    serverAcc: { type: String, default: "" },
    serverIp: { type: String, default: "" },
    serverLocation: { type: String, default: "" },
    serverName: { type: String, default: "" },
    serverRemark: { type: String, default: "" },
  },
  data() {
    return {
      branches: [],
      loadingBranches: false,
      submitting: false,
      errorMessage: "",
      form: {
        branch_id: this.branchId || 0,
        server_acc: this.serverAcc || "",
        server_ip: this.serverIp || "",
        server_location: this.serverLocation || "",
        server_name: this.serverName || "",
        server_pass: "",
        server_remark: this.serverRemark || "",
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
        this.errorMessage = "無法取得地點清單。";
      } finally {
        this.loadingBranches = false;
      }
    },
    syncLocation() {
      const branch = this.branches.find((item) => item.id === this.form.branch_id);
      if (branch) this.form.server_location = `${branch.branch_title} - ${branch.branch_name}`;
    },
    async submitUpdate() {
      if (!this.form.branch_id) {
        this.errorMessage = "請選擇地點。";
        return;
      }
      this.submitting = true;
      this.errorMessage = "";
      try {
        const payload = { ...this.form };
        // Never send a placeholder or an empty value that could overwrite the secret.
        if (!payload.server_pass) delete payload.server_pass;
        await updateServerListByIdAPI(this.id, payload);
        this.$emit("updated");
      } catch (error) {
        this.errorMessage = error.response?.data?.detail || "更新失敗，請檢查輸入資料。";
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.editor-dialog { display: grid; min-height: 100vh; padding: 24px; place-items: center; }
form { width: min(720px, 100%); max-height: calc(100vh - 48px); padding: 25px; overflow-y: auto; border-radius: 14px; background: white; box-shadow: 0 18px 50px rgba(0, 0, 0, .28); }
form > header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 18px; }
header p { margin: 0 0 4px; color: #68809b; font-size: .7rem; font-weight: 800; letter-spacing: .15em; }
h2 { margin: 0; }.close-button { padding: 0 8px; color: #667085; border: 0; background: transparent; font-size: 1.8rem; }
label { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }label span { font-weight: 700; }label b { color: #d92d20; }
input, select, textarea { width: 100%; padding: 10px 12px; color: #172033; border: 1px solid #cbd5e1; border-radius: 8px; background: white; }
input:focus, select:focus, textarea:focus { outline: 3px solid rgba(23, 105, 224, .14); border-color: #1769e0; }
.form-alert { padding: 11px 13px; margin-bottom: 14px; color: #b42318; border-radius: 8px; background: #fff0ef; }
footer { display: flex; justify-content: flex-end; gap: 9px; padding-top: 6px; }
</style>
