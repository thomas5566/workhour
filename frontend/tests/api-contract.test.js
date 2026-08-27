import { describe, expect, it } from "vitest";

import {
  createServerListAPI,
  deleteServerListAPI,
  getBranchListAPI,
  getAllWorkListsByShopIdAPI,
  getAllWorkListsByUserIdAPI,
  getTaskAPI,
  getMonitoringSummaryAPI,
} from "../src/service/apis";
import http from "../src/service/http";

describe("FastAPI client contract", () => {
  it("uses the same-origin API prefix by default", () => {
    expect(http.defaults.baseURL).toBe("/api");
  });

  it("maps summary functions to the matching backend endpoints", async () => {
    const requestedUrls = [];
    const monitoringOptions = [];
    http.defaults.adapter = async (config) => {
      requestedUrls.push(config.url);
      if (config.url === "/monitoring/summary") {
        monitoringOptions.push({ background: config.background, silent: config.silent });
      }
      return { data: [], status: 200, statusText: "OK", headers: {}, config };
    };

    await getTaskAPI();
    await getAllWorkListsByUserIdAPI();
    await getAllWorkListsByShopIdAPI();
    await getMonitoringSummaryAPI({ background: true, silent: true });
    await getBranchListAPI();
    await createServerListAPI({ server_name: "ERP Server" });
    await deleteServerListAPI(7);

    expect(requestedUrls).toEqual([
      "/task/",
      "/workhour/worklist-userid",
      "/workhour/worklist-shopid",
      "/monitoring/summary",
      "/branchlist/",
      "/serverlist/",
      "/serverlist/7",
    ]);
    expect(monitoringOptions).toEqual([{ background: true, silent: true }]);
  });
});
