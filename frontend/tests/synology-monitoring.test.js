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

  it("formats the approved NAS fields and dynamic disk metrics", () => {
    const methods = InfrastructureMonitoring.methods;
    expect(methods.metricLabel("serial_number")).toBe("Serial Number");
    expect(methods.metricLabel("volume_usage:/volume1")).toBe("/volume1 儲存使用率");
    expect(methods.metricLabel("disk_status:Drive 1")).toBe("Drive 1 Disk Status");
    expect(methods.displayValue(42, "volume_usage:/volume1")).toBe("42%");
    expect(methods.displayValue(90000, "uptime_seconds")).toBe("1 天 1 小時");
    expect(methods.displayValue("System Partition Failed", "disk_status:Drive 1"))
      .toBe("System Partition Failed（系統分割區損壞）");
    expect(methods.metricLabel("raid_status:Volume 1 RAID"))
      .toBe("Volume 1 RAID Status");
    expect(methods.displayValue(55, "disk_temperature:Disk 1")).toBe("55°C");
    expect(methods.metricStatusClass("disk_temperature:Disk 1", 55))
      .toBe("metric-warning");
    expect(methods.metricStatusClass("disk_bad_sectors:Disk 1", 1))
      .toBe("metric-critical");
    expect(methods.metricStatusClass("raid_status:Volume 1 RAID", "Degraded"))
      .toBe("metric-critical");
    expect(methods.metricStatusClass("system_fan_status", "Failed"))
      .toBe("metric-disconnected");
  });
});
