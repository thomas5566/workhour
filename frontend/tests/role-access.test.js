import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { canAccessPath, getAccessRole } from "../src/router";

describe("role-based route access", () => {
  it("limits general and IT users while preserving administrator access", () => {
    expect(canAccessPath("/home", "general")).toBe(true);
    expect(canAccessPath("/fetnetlist", "general")).toBe(true);
    expect(canAccessPath("/ipcamlist/add", "general")).toBe(true);
    expect(canAccessPath("/serverlist", "general")).toBe(false);
    expect(canAccessPath("/user-management", "general")).toBe(false);

    expect(canAccessPath("/serverlist", "it")).toBe(true);
    expect(canAccessPath("/serverlist/add", "it")).toBe(true);
    expect(canAccessPath("/monitoring", "it")).toBe(false);
    expect(canAccessPath("/user-management", "it")).toBe(false);

    expect(canAccessPath("/user-management", "admin")).toBe(true);
    expect(canAccessPath("/monitoring", "admin")).toBe(true);
  });

  it("derives roles from persisted account attributes", () => {
    const account = (isSuperuser, itPermission) => ({
      getters: {
        getSuperUser: isSuperuser,
        getchecklistAll_permission: itPermission,
      },
    });

    expect(getAccessRole(account(false, 0))).toBe("general");
    expect(getAccessRole(account(false, 1))).toBe("it");
    expect(getAccessRole(account(true, 0))).toBe("admin");
  });

  it("shows camera credential reveal only to IT users and administrators", () => {
    const component = readFileSync(
      resolve("src/components/ipcamlist/IpCamListDetail.vue"),
      "utf8",
    );

    expect(component).toContain('v-if="canRevealCredentials"');
    expect(component).toContain("getchecklistAll_permission === 1");
    expect(component).toContain("getSuperUser");
  });
});
