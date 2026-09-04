# 分店 Peplink 監控

## 顯示範圍與權限

在基礎設施監控的「分店Peplink」頁籤，每次背景更新重新識別 Zabbix **Host name**
`Peplink-正整數`（不限 91，例如 Peplink-202），以及 Host group **Peplink** 的主機。
Visible name 可使用門市名稱；六台原有主要 Peplink 排除於分店頁籤之外。
頁籤數量是 API 實際可讀取的主機數，不會虛構不存在或無權限的設備。
原本六台 Peplink 保留在原頁籤。

1. 確認 WorkHour `.env.production` 中 ZABBIX_TOKEN 所屬的 Zabbix 使用者。
2. 在該使用者的 User group → Host permissions，為分店所屬的 **Peplink** 群組設定 Read。
3. 儲存後在 WorkHour 按「立即更新」，或等待既有的背景更新。
4. 使用搜尋與分頁查看設備；每頁 12 台，背景更新不會清除搜尋或重設目前頁碼。

API 僅執行 host.get / item.get，不會修改 Zabbix 或網路設備，也不會把 Token 傳到前端。

## 監控項目契約

| 顯示欄位 | Zabbix item key | 預期數值 |
| --- | --- | --- |
| WAN 狀態 | `wanState[介面名稱]` | 優先採用 Zabbix value mapping |
| WAN 健康檢查 | `wanHealthCheckState[介面名稱]` | 優先採用 value mapping；0=Fail、1=Success |
| CPU | `system.cpu.util` | 0～100，單位 % |
| CPU（替代來源） | `system.cpu.util[,idle]` | 閒置百分比，顯示時以 100 減去此值 |
| Memory | `vm.memory.util` | 0～100，單位 % |
| 運行時間 | `system.uptime` | 秒，須先在 Zabbix 將 SNMP TimeTicks 等來源轉換為秒 |

CPU／Memory／運行時間必須先有實際採集項目，不能僅建立空白 key。
依設備型號、韌體與 MIB 確認可用 OID，再設定 SNMP item 與 preprocessing；
勿把 bytes 當百分比，或把 TimeTicks 當秒。不同 key 應先核對語意再新增映射。

2026-09-02 初次權限驗證時可讀取 58 台分店（含 Peplink-202），當時尚無資源指標。
同日使用者完成共用 Peplink Template 後，再次唯讀確認可取得 CPU、Memory、運行時間；
Peplink-01 的 FET 為 Disable、健康檢查 Fail，不產生本頁告警。主機數量以每次 API 回應為準。

Peplink 提供依韌體版本區分的 [官方 SNMP MIB](https://www.peplink.com/support/downloads/supplementary-materials/)，
[官方支援討論](https://forum.peplink.com/t/snmp-monitor-peplink-cpu-ram-usage-oid/4809)
說明部分韌體可提供 CPU／Memory。仍須逐機型核對支援情況與回傳值；本次未變更設備或 Zabbix Template。
使用者已完成 CPU 與 Console 同步比對，以及 Template 設定；本次不修改 Zabbix 範本。
記憶體原始 KB 單位使用 `!KB`，運行時間由 Zabbix 轉換為秒。新主機套用範本後自動顯示。

## 顏色與資料品質

- Connected / Success 綠色；Disconnect / Disconnected / Fail / Health-check-fail 紅色。
- FET／Cellular（含編號介面）：Standby 狀態綠色、Disable 狀態紅色。
  Disable / Standby 的健康檢查 Fail 保留原值但不標紅，避免未使用介面誤報。
- Wi-Fi WAN、Wi-Fi WAN on 2.4 GHz、Wi-Fi WAN on 5 GHz、VLAN WAN（含數字後綴）不顯示。
- CPU／Memory 達 80% 黃色 Warning、90% 紅色 Critical，產生本頁告警，不建立 Zabbix trigger。
- 運行時間超過 90 天（嚴格大於 7776000 秒）為黃色 Warning 並列入本頁告警。
- `metric_severities` 與 `alert_severity` 讓卡片顏色、主機徽章與事件清單共用後端規則。
- 個別取樣超過 10 分鐘顯示「資料已過期」；缺少、不支援、無效值各自標示，絕不以 0 替代。
- 主機徽章同時反映 SNMP 可用性及資料完整性；「需要注意」可能代表缺少指標，不等同設備故障。

## 警告事件規則（僅 WorkHour）

- FET／Cellular 為新鮮的 Disable 值時，排除只關聯該介面的原生事件。
- 來源為 Zabbix 且事件名稱為 `FET Link down`（可含主機名稱前綴）的事件一律於本頁隱藏，
  不列入告警數量與卡片事件嚴重度；不修改 Zabbix 原始事件，其他事件與本頁規則仍保留。
- FET／Cellular 為新鮮 Standby 值時，也排除僅關聯其健康檢查的原生事件。
- 排除只關聯上述隱藏 Wi-Fi WAN／VLAN WAN 的原生事件。
- 依 trigger 的主機及 item key 精確關聯，不根據事件文字猜測；混合主機／混合指標事件仍保留。
- WAN 介面（包括 FET／Cellular）為 Disconnect 時，若沒有對應 Zabbix 原生事件，
  加入 Warning 等級的「本頁規則」事件；恢復連線後在下一次更新自動移除。
- 有效啟用線路健康檢查 Fail／Health-check-fail 產生本頁 Warning；
  若同介面已 Disconnect，合併為同一事件。Disable／Standby 健康檢查 Fail 不產生本頁事件。
- 停用主機、不支援或過期取樣不產生本頁資源／WAN 警告。
- 資源 Critical 使用數字等級 4（與 Zabbix High 同級）；原生事件保留原始等級及名稱。
- 本頁事件時間是目前取樣時間，不冒充首次故障時間；沒有確認狀態或持久歷史。
- 原生事件保留 Zabbix 等級；相同主機和介面的原生事件優先，不重複建立本頁事件。
- 總覽目前問題數使用同一份過濾後事件清單。本頁規則不寫入、不確認、不關閉 Zabbix 事件。

## 本地驗證

後端 `tests/test_branch_peplink.py` 覆蓋主機範圍、批次讀取、WAN value mapping、
缺少／過期／不支援的資料，以及原六台 Peplink 分流。
前端 `tests/branch-peplink.test.js` 使用 91 台測試資料驗證搜尋、分頁、背景更新保留狀態及顏色。
這些是隔離測試，不會寫入正式 Zabbix 或 PostgreSQL。

2026-09-02 告警調整驗證：後端 160 項、前端 26 項測試通過，Ruff／ESLint 通過。
本機 8082 之前後端容器已重建且健康；即時唯讀 API 驗證 58 台分店，VLAN WAN 無輸出，
Peplink-01 停用 FET 的 Fail 未列入警告。瀏覽器端完整視覺驗證需重新登入。
