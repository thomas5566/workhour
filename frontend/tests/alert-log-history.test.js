import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AlertLogHistory from "../src/components/AlertLogHistory.vue";
import { getMonitoringAlertLogsAPI } from "../src/service/apis";

vi.mock("../src/service/apis", () => ({
  getMonitoringAlertLogsAPI: vi.fn(),
}));

describe("AlertLogHistory", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getMonitoringAlertLogsAPI.mockResolvedValue({
      data: {
        items: [{
          id: 1,
          event_id: "101",
          host_name: "VM-01",
          severity: 4,
          severity_label: "High",
          occurred_at: "2026-10-02T01:00:00Z",
          last_observed_at: "2026-10-02T01:01:00Z",
          resolved_at: null,
          source: "zabbix",
          message: "CPU utilization is high",
        }],
        total: 1,
      },
    });
  });

  it("loads and displays durable High alert records", async () => {
    const wrapper = mount(AlertLogHistory);
    await flushPromises();

    expect(getMonitoringAlertLogsAPI).toHaveBeenCalledWith(expect.objectContaining({
      limit: 100,
      offset: 0,
    }));
    expect(wrapper.text()).toContain("VM-01");
    expect(wrapper.text()).toContain("CPU utilization is high");
    expect(wrapper.text()).toContain("持續中");
  });
});
