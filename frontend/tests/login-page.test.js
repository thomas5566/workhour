import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";

import LoginPage from "../src/components/loginpage/LoginPage.vue";

describe("LoginPage", () => {
  it("accepts text in both login fields", async () => {
    const push = vi.fn(() => Promise.resolve());
    const wrapper = mount(LoginPage, {
      global: {
        mocks: {
          $store: { dispatch: () => Promise.resolve() },
          $router: { push },
        },
      },
    });

    await wrapper.get("#username").setValue("tester");
    await wrapper.get("#password").setValue("secret");

    expect(wrapper.vm.form).toMatchObject({
      username: "tester",
      password: "secret",
    });

    await wrapper.findAll(".login-button")[1].trigger("click");
    expect(push).toHaveBeenCalledWith("/register");
  });
});
