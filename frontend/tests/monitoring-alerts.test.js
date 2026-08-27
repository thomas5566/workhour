import { describe, expect, it } from "vitest";
import {
  getCriticalProblemCount,
  getResourceUtilizationClass,
  getSpeedFusionDrop,
} from "@/utils/monitoringAlerts";

describe("SpeedFusion alerts", () => {
  it("alerts after reload when connected count is lower than total", () => {
    expect(getSpeedFusionDrop(undefined, 64, 65)).toEqual({
      previous: 65,
      current: 64,
    });
  });

  it("alerts when connected count drops between refreshes", () => {
    expect(getSpeedFusionDrop(65, 64, 64)).toEqual({
      previous: 65,
      current: 64,
    });
  });

  it("clears the alert after all connections recover", () => {
    expect(getSpeedFusionDrop(64, 65, 65)).toBeNull();
  });
});

describe("VM resource utilization colors", () => {
  it("colors CPU, memory, and every discovered disk by threshold", () => {
    expect(getResourceUtilizationClass("cpu", 79.9)).toBe("metric-healthy");
    expect(getResourceUtilizationClass("memory", 80)).toBe("metric-warning");
    expect(getResourceUtilizationClass("disk_usage:C:", 89.9)).toBe("metric-warning");
    expect(getResourceUtilizationClass("disk_usage:D:", 90)).toBe("metric-critical");
  });

  it("does not color unrelated or invalid metrics", () => {
    expect(getResourceUtilizationClass("uptime_seconds", 99)).toBe("");
    expect(getResourceUtilizationClass("disk_usage:E:", "unknown")).toBe("");
  });
});

describe("critical monitoring badge", () => {
  it("counts only High and Disaster events", () => {
    expect(getCriticalProblemCount([
      { severity: 2 },
      { severity: "3" },
      { severity: 4 },
      { severity: "5" },
    ])).toBe(2);
  });

  it("returns zero when there are no active events", () => {
    expect(getCriticalProblemCount([])).toBe(0);
    expect(getCriticalProblemCount()).toBe(0);
  });
});
