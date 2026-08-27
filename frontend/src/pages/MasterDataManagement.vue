<template>
  <section class="master-page">
    <header>
      <div><p>DATABASE ADMINISTRATION</p><h1>基礎資料管理</h1></div>
      <button class="btn btn-primary" type="button" @click="startCreate"><i class="fas fa-plus"></i> 新增{{ current.label }}</button>
    </header>

    <nav class="tabs" aria-label="資料表切換">
      <button v-for="item in tables" :key="item.key" :class="{ active: activeTable === item.key }" type="button" @click="selectTable(item.key)">{{ item.label }} <small>{{ counts[item.key] }}</small></button>
    </nav>

    <div v-if="message" class="notice success">{{ message }}</div>
    <div v-if="errorMessage" class="notice error">{{ errorMessage }}</div>

    <div class="table-card">
      <div class="table-tools"><h2>{{ current.label }}</h2><input v-model.trim="search" type="search" placeholder="搜尋資料"></div>
      <div class="table-scroll">
        <table>
          <thead><tr><th>ID</th><th v-for="field in current.fields" :key="field.key">{{ field.label }}</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.id">
              <td>{{ row.id }}</td><td v-for="field in current.fields" :key="field.key">{{ displayValue(row, field) }}</td>
              <td class="actions"><button class="edit" type="button" @click="startEdit(row)">編輯</button><button class="delete" type="button" @click="remove(row)">刪除</button></td>
            </tr>
            <tr v-if="!loading && filteredRows.length === 0"><td :colspan="current.fields.length + 2" class="empty">沒有符合條件的資料</td></tr>
          </tbody>
        </table>
      </div>
      <div v-if="loading" class="loading">載入中…</div>
    </div>

    <div v-if="editorOpen" class="backdrop" @click.self="closeEditor">
      <form class="editor" @submit.prevent="save">
        <header><h2>{{ editingId ? "編輯" : "新增" }}{{ current.label }}</h2><button type="button" @click="closeEditor">×</button></header>
        <div class="fields">
          <label v-for="field in current.fields" :key="field.key">
            <span>{{ field.label }} <b>*</b></span>
            <select v-if="field.type === 'task'" v-model.number="form[field.key]" required>
              <option :value="0" disabled>請選擇主部門</option>
              <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.id }} - {{ task.fullname || task.taskname }}</option>
            </select>
            <input v-else v-model.trim="form[field.key]" required maxlength="255">
          </label>
        </div>
        <div v-if="editorError" class="notice error">{{ editorError }}</div>
        <footer><button class="btn btn-outline-secondary" type="button" @click="closeEditor">取消</button><button class="btn btn-primary" :disabled="saving">{{ saving ? "儲存中…" : "儲存" }}</button></footer>
      </form>
    </div>
  </section>
</template>

<script>
import {
  createBranchListAPI, createCstShopAPI, createDepartmentAPI,
  deleteBranchListAPI, deleteCstShopAPI, deleteDepartmentAPI,
  getBranchListAPI, getCstShopsAPI, getDepartmentsAPI, getTaskAPI,
  updateBranchListAPI, updateCstShopAPI, updateDepartmentAPI,
} from "@/service/apis";

const TABLES = [
  { key: "branch", label: "據點（branch_list）", fields: [{ key: "branch_title", label: "據點代碼" }, { key: "branch_name", label: "據點名稱" }] },
  { key: "shop", label: "店點（cst_shop）", fields: [{ key: "main_department_id", label: "主部門", type: "task" }, { key: "shop_number", label: "店號" }, { key: "shop_name", label: "店名" }] },
  { key: "department", label: "人員部門（department）", fields: [{ key: "department_name", label: "部門名稱" }] },
];

export default {
  name: "MasterDataManagement",
  data: () => ({ tables: TABLES, activeTable: "branch", rows: { branch: [], shop: [], department: [] }, tasks: [], search: "", loading: false, editorOpen: false, editingId: null, form: {}, saving: false, message: "", errorMessage: "", editorError: "" }),
  computed: {
    current() { return this.tables.find((item) => item.key === this.activeTable); },
    counts() { return { branch: this.rows.branch.length, shop: this.rows.shop.length, department: this.rows.department.length }; },
    filteredRows() { const term = this.search.toLowerCase(); if (!term) return this.rows[this.activeTable]; return this.rows[this.activeTable].filter((row) => Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(term))); },
  },
  mounted() { this.loadAll(); },
  methods: {
    async loadAll() { this.loading = true; this.errorMessage = ""; try { const [branches, shops, departments, tasks] = await Promise.all([getBranchListAPI(), getCstShopsAPI(), getDepartmentsAPI(), getTaskAPI()]); this.rows.branch = branches.data; this.rows.shop = shops.data; this.rows.department = departments.data; this.tasks = tasks.data; } catch (error) { this.errorMessage = error.response?.data?.detail || "無法載入基礎資料。"; } finally { this.loading = false; } },
    selectTable(key) { this.activeTable = key; this.search = ""; this.message = ""; this.errorMessage = ""; },
    emptyForm() { return Object.fromEntries(this.current.fields.map((field) => [field.key, field.type === "task" ? 0 : ""])); },
    startCreate() { this.editingId = null; this.form = this.emptyForm(); this.editorError = ""; this.editorOpen = true; },
    startEdit(row) { this.editingId = row.id; this.form = Object.fromEntries(this.current.fields.map((field) => [field.key, row[field.key] ?? (field.type === "task" ? 0 : "")])); this.editorError = ""; this.editorOpen = true; },
    closeEditor() { this.editorOpen = false; this.editorError = ""; },
    apiSet() { return { branch: { create: createBranchListAPI, update: updateBranchListAPI, remove: deleteBranchListAPI }, shop: { create: createCstShopAPI, update: updateCstShopAPI, remove: deleteCstShopAPI }, department: { create: createDepartmentAPI, update: updateDepartmentAPI, remove: deleteDepartmentAPI } }[this.activeTable]; },
    async save() { this.saving = true; this.editorError = ""; try { const api = this.apiSet(); if (this.editingId) await api.update(this.editingId, this.form); else await api.create(this.form); this.closeEditor(); this.message = `${this.current.label}已儲存。`; await this.loadAll(); } catch (error) { this.editorError = error.response?.data?.detail || "儲存失敗，請檢查輸入資料。"; } finally { this.saving = false; } },
    async remove(row) { if (!window.confirm(`確定刪除 ID ${row.id}？此操作無法復原。`)) return; this.errorMessage = ""; try { await this.apiSet().remove(row.id); this.message = `${this.current.label}已刪除。`; await this.loadAll(); } catch (error) { this.errorMessage = error.response?.status === 409 ? "此資料仍被其他資料使用，無法刪除。" : (error.response?.data?.detail || "刪除失敗。"); } },
    displayValue(row, field) { if (field.type !== "task") return row[field.key] ?? "—"; const task = this.tasks.find((item) => item.id === row[field.key]); return task ? `${task.id} - ${task.fullname || task.taskname}` : row[field.key]; },
  },
};
</script>

<style scoped>
.master-page{min-height:100%;padding:28px;background:#f3f6fa;color:#172033}.master-page>header{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:20px}.master-page header p{margin:0;color:#68809b;font-size:.72rem;font-weight:800;letter-spacing:.16em}.master-page h1{margin:4px 0 0}.tabs{display:flex;gap:8px;margin-bottom:18px;padding:6px;border-radius:12px;background:#e7edf5}.tabs button{flex:1;padding:11px;border:0;border-radius:8px;background:transparent}.tabs button.active{color:#fff;background:#1769e0}.tabs small{margin-left:6px}.notice{margin-bottom:14px;padding:12px 14px;border-radius:8px}.success{color:#067647;background:#ecfdf3}.error{color:#b42318;background:#fff0ef}.table-card{position:relative;border:1px solid #dce4ee;border-radius:14px;background:#fff;box-shadow:0 10px 30px rgba(30,48,75,.06)}.table-tools{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 20px;border-bottom:1px solid #e2e8f0}.table-tools h2{margin:0;font-size:1.2rem}.table-tools input{width:min(320px,50%);padding:9px 11px;border:1px solid #cbd5e1;border-radius:8px}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse}th,td{padding:12px 16px;border-bottom:1px solid #e8edf3;text-align:left;white-space:nowrap}th{color:#607089;background:#f8fafc}.actions{display:flex;gap:7px}.actions button{padding:6px 11px;border-radius:6px;background:#fff}.edit{color:#1769e0;border:1px solid #1769e0}.delete{color:#d92d20;border:1px solid #d92d20}.empty,.loading{text-align:center;color:#718096}.loading{padding:20px}.backdrop{position:fixed;inset:0;z-index:1050;display:grid;place-items:center;padding:20px;background:rgba(15,23,42,.7)}.editor{width:min(620px,100%);border-radius:14px;background:#fff;box-shadow:0 25px 70px rgba(0,0,0,.3)}.editor>header{display:flex;justify-content:space-between;padding:20px 24px;border-bottom:1px solid #e2e8f0}.editor h2{margin:0}.editor header button{border:0;background:transparent;font-size:1.8rem}.fields{display:grid;gap:16px;padding:24px}.fields label{display:flex;flex-direction:column;gap:7px}.fields span{font-weight:700}.fields b{color:#d92d20}.fields input,.fields select{padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px}.editor .notice{margin:0 24px}.editor footer{display:flex;justify-content:flex-end;gap:10px;padding:20px 24px}@media(max-width:700px){.master-page{padding:16px}.master-page>header{align-items:flex-start;flex-direction:column}.tabs{overflow:auto}.tabs button{min-width:180px}}
</style>
