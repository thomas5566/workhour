import { describe, expect, it } from "vitest";

import InfrastructureMonitoring from "@/pages/InfrastructureMonitoring.vue";


describe("Synology NAS monitoring tab", () => {
  it("shows a dynamic count from the monitoring summary", () => {
    const context = {
      summary: {
        firewalls: [], peplinks: [], branch_peplinks: [], servers: [],
        synology_nas: [{ host_id: "1" }, { host_id: "2" }],
        mssql: [], nutanix: [], problems: [],
      },
    };

    const tabs = InfrastructureMonitoring.computed.tabs.call(context);
    expect(tabs.find((tab) => tab.id === "synology-nas")).toMatchObject({
      label: "Synology NAS",
      count: 2,
    });
  });
});
