import { describe, expect, it } from "vitest";

import {
  createServerListAPI,
  deleteFetnetListAPI,
  deleteIpCamListAPI,
  deleteServerListAPI,
  getBranchListAPI,
  getAllWorkListsByShopIdAPI,
  getAllWorkListsByUserIdAPI,
  getTaskAPI,
  getMonitoringSummaryAPI,
  getMonitoringAlertLogsAPI,
  revealIpCamPasswordsAPI,
  revealServerPasswordAPI,
} from "../src/service/apis";
import http from "../src/service/http";

describe("FastAPI client contract", () => {
  it("uses the same-origin API prefix by default", () => {
    expect(http.defaults.baseURL).toBe("/api");
  });

  it("maps summary functions to the matching backend endpoints", async () => {
    const requestedUrls = [];
    const monitoringOptions = [];
    const alertLogQueries = [];
    http.defaults.adapter = async (config) => {
      requestedUrls.push(config.url);
      if (config.url === "/monitoring/summary") {
        monitoringOptions.push({ background: config.background, silent: config.silent });
      }
      if (config.url === "/monitoring/alert-logs") {
        alertLogQueries.push(config.params);
      }
      return { data: [], status: 200, statusText: "OK", headers: {}, config };
    };

    await getTaskAPI();
    await getAllWorkListsByUserIdAPI();
    await getAllWorkListsByShopIdAPI();
    await getMonitoringSummaryAPI({ background: true, silent: true });
    await getMonitoringAlertLogsAPI({ message: "CPU", limit: 100 });
    await getBranchListAPI();
    await createServerListAPI({ server_name: "ERP Server" });
    await deleteServerListAPI(7);
    await deleteFetnetListAPI(8);
    await deleteIpCamListAPI(9);
    await revealServerPasswordAPI(10);
    await revealIpCamPasswordsAPI(11);

    expect(requestedUrls).toEqual([
      "/task/",
      "/workhour/worklist-userid",
      "/workhour/worklist-shopid",
      "/monitoring/summary",
      "/monitoring/alert-logs",
      "/branchlist/",
      "/serverlist/",
      "/serverlist/7",
      "/fetnetlist/8",
      "/ipcamlist/9",
      "/serverlist/10/reveal-password",
      "/ipcamlist/11/reveal-passwords",
    ]);
    expect(monitoringOptions).toEqual([{ background: true, silent: true }]);
    expect(alertLogQueries).toEqual([{ message: "CPU", limit: 100 }]);
  });
});
