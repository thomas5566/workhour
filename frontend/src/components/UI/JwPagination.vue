<template>
  <nav v-if="pageCount > 1" aria-label="分頁">
    <ul class="pagination justify-content-center">
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <button class="page-link" type="button" @click="selectPage(currentPage - 1)">上一頁</button>
      </li>
      <li v-for="page in visiblePages" :key="page" class="page-item" :class="{ active: page === currentPage }">
        <button class="page-link" type="button" @click="selectPage(page)">{{ page }}</button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage === pageCount }">
        <button class="page-link" type="button" @click="selectPage(currentPage + 1)">下一頁</button>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: "JwPagination",
  props: {
    items: { type: Array, default: () => [] },
    pageSize: { type: Number, default: 10 },
    maxPages: { type: Number, default: 10 },
  },
  emits: ["changePage"],
  data: () => ({ currentPage: 1 }),
  computed: {
    pageCount() { return Math.max(1, Math.ceil(this.items.length / this.pageSize)); },
    visiblePages() {
      const start = Math.max(1, Math.min(this.currentPage - Math.floor(this.maxPages / 2), this.pageCount - this.maxPages + 1));
      return Array.from({ length: Math.min(this.maxPages, this.pageCount) }, (_, index) => start + index);
    },
  },
  watch: {
    items: { immediate: true, handler() { this.selectPage(Math.min(this.currentPage, this.pageCount)); } },
  },
  methods: {
    selectPage(page) {
      this.currentPage = Math.min(Math.max(page, 1), this.pageCount);
      const start = (this.currentPage - 1) * this.pageSize;
      this.$emit("changePage", this.items.slice(start, start + this.pageSize));
    },
  },
};
</script>
