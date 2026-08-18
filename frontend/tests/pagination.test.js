import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";

import JwPagination from "../src/components/UI/JwPagination.vue";

describe("JwPagination", () => {
  it("emits the first page and navigates without the retired Vue 2 plugin", async () => {
    const wrapper = mount(JwPagination, {
      props: { items: Array.from({ length: 12 }, (_, index) => index + 1), pageSize: 5 },
    });

    expect(wrapper.emitted("changePage")[0]).toEqual([[1, 2, 3, 4, 5]]);
    await wrapper.findAll("button").at(-1).trigger("click");
    expect(wrapper.emitted("changePage").at(-1)).toEqual([[6, 7, 8, 9, 10]]);
  });
});
