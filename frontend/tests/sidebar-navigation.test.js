import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("Sidebar navigation", () => {
  it("uses client-side routes for role-controlled pages", () => {
    const sidebar = readFileSync(resolve("src/dashboard/Sidebar.vue"), "utf8");
    const targets = [...sidebar.matchAll(/<router-link\s+to="([^"]+)"/g)]
      .map((match) => match[1]);

    expect(targets).toEqual([
      "/allworkhourlist",
      "/home",
      "/serverlist",
      "/fetnetlist",
      "/ipcamlist",
      "/monitoring",
      "/master-data",
      "/user-management",
    ]);
    expect(sidebar).not.toContain('getUsername === "');
    expect(sidebar).toContain('v-if="canUseServerInventory"');
    expect(sidebar).toContain('v-if="isAdmin"');
  });
});
