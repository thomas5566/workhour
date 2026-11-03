import { describe, expect, it } from "vitest";

import {
  createServerListAPI,
  deleteFetnetListAPI,
  deleteIpCamListAPI,
  deleteServerListAPI,
  getAllServerListsAPI,
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

  it("loads every server inventory page for full-list keyword search", async () => {
    const queries = [];
    http.defaults.adapter = async (config) => {
      queries.push(config.params);
      const skip = config.params.skip;
      const data = skip === 0
        ? Array.from({ length: 1000 }, (_, index) => ({ id: index + 1 }))
        : [{ id: 1001 }];
      return { data, status: 200, statusText: "OK", headers: {}, config };
    };

    const serverLists = await getAllServerListsAPI();

    expect(serverLists).toHaveLength(1001);
    expect(serverLists.at(-1)).toEqual({ id: 1001 });
    expect(queries).toEqual([
      { skip: 0, limit: 1000 },
      { skip: 1000, limit: 1000 },
    ]);
  });
});
