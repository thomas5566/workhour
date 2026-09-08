import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../src/service/apis.js", () => ({
  postUserLogInAPI: vi.fn(),
  postUserLogoutAPI: vi.fn(),
}));

import { postUserLogoutAPI } from "../src/service/apis.js";
import auth from "../src/store/modules/auth.js";

describe("authentication logout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("revokes the server token before clearing local authentication", async () => {
    const commit = vi.fn();
    postUserLogoutAPI.mockResolvedValue({ status: 204 });

    await auth.actions.LogOut({ commit, state: { token: "issued-token" } });

    expect(postUserLogoutAPI).toHaveBeenCalledOnce();
    expect(commit).toHaveBeenCalledWith("LogOut");
    expect(postUserLogoutAPI.mock.invocationCallOrder[0]).toBeLessThan(
      commit.mock.invocationCallOrder[0],
    );
  });

  it("clears local authentication when server revocation cannot complete", async () => {
    const commit = vi.fn();
    postUserLogoutAPI.mockRejectedValue(new Error("network unavailable"));

    await auth.actions.LogOut({ commit, state: { token: "issued-token" } });
    expect(commit).toHaveBeenCalledWith("LogOut");
  });
});
