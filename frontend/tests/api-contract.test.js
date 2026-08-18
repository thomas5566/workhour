import { describe, expect, it } from "vitest";

import {
  getAllWorkListsByShopIdAPI,
  getAllWorkListsByUserIdAPI,
  getTaskAPI,
} from "../src/service/apis";
import http from "../src/service/http";

describe("FastAPI client contract", () => {
  it("uses the same-origin API prefix by default", () => {
    expect(http.defaults.baseURL).toBe("/api");
  });

  it("maps summary functions to the matching backend endpoints", async () => {
    const requestedUrls = [];
    http.defaults.adapter = async (config) => {
      requestedUrls.push(config.url);
      return { data: [], status: 200, statusText: "OK", headers: {}, config };
    };

    await getTaskAPI();
    await getAllWorkListsByUserIdAPI();
    await getAllWorkListsByShopIdAPI();

    expect(requestedUrls).toEqual([
      "/task/",
      "/workhour/worklist-userid",
      "/workhour/worklist-shopid",
    ]);
  });
});
