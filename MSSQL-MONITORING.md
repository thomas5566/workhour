# Zabbix MSSQL → WorkHour 整合

## 工作順序

1. 在 Zabbix 建立並驗證 Host、Items、Triggers 與 Dependencies。
2. 確認 WorkHour 的 Zabbix API 帳號對該 Host group 有 Read 權限。
3. WorkHour `/api/monitoring/summary` 唯讀取得資料，Vue `/monitoring` 的 MSSQL 分頁顯示結果。
4. 在 Zabbix Latest data 與網頁逐項比對「取樣時間」，不要比較不同時間的數值。

不需更改現有 Item Key，也不需額外提供 SQL 密碼給 WorkHour。Zabbix token 僅留在 Backend。
本整合不建立、修改或刪除 Zabbix 物件，也不執行 SQL 查詢。

## 支援的自訂採集契約

`mssql.<instance>.<suffix>`，instance 可含英數、底線及連字號；資料庫名稱需以雙引號括住。

| suffix | 意義 | 資料新鮮度上限 |
| --- | --- | --- |
| `version` | SQL Server 數字版本 | 24 小時 |
| `service` / `agent` | 1 執行中，0 未執行 | 5 分鐘 |
| `db.state["database"]` | SQL 資料庫狀態，0 ONLINE | 5 分鐘 |
| `db.recovery["database"]` | 1 FULL、2 BULK_LOGGED、3 SIMPLE | 1 小時 |
| `db.logused["database"]` | Transaction Log 使用百分比 | 5 分鐘 |
| `db.fullbackup.age["database"]` | 完整備份距今秒數 | 15 分鐘 |
| `db.logbackup.age["database"]` | Log 備份距今秒數 | 5 分鐘 |

僅接收啟用主機上的啟用 Items；不是通用匯入所有官方 MSSQL Template 的解析器。
新鮮度上限不同於「備份允許多久未執行」；若調整採集週期，應同步審視上述上限。
只有已建立且符合契約的指標會顯示；缺少某項指標不代表該功能已受到監控。

## 狀態與警告

- 服務未執行或 DB 非 ONLINE：紅色。
- Zabbix 未恢復且未 suppressed 的 Warning / Average：黃色；High / Disaster：紅色。
- 透過 Trigger functions 的 itemid 關聯指標，避免其他資料庫或執行個體的告警誤套。
- 不在網頁另設 Log 使用率與備份過期門檻，以 Zabbix Trigger 為準。
- 每個 Item 個別檢查取樣時間；過期、Unsupported、無值或無效數值顯示明確文字與 `—`。
- API 查詢失敗顯示錯誤，而非「沒有監控主機」。

前端沿用既有共用的 60 秒背景輪詢與 in-flight request 去重；沒有新增整頁重新整理，
也沒有新增 Backend 定時快取工作。

## 本地更新（PowerShell，repository 根目錄）

```powershell
$env:BACKEND_HOST_PORT = '5567'
$env:FRONTEND_HOST_PORT = '8082'
docker compose --env-file .env.production -p workhour-production-smoke -f docker-compose.production-db.yml up -d --build app frontend
```

這個 Compose 檔使用既有外部資料庫；上述命令不執行 migration。
重新開啟 `/monitoring`，選取 MSSQL 分頁。需要有效的 WorkHour 管理者登入。

API 欄位依據 [Zabbix item.get](https://www.zabbix.com/documentation/7.4/en/manual/api/reference/item/get)
與 [trigger.get](https://www.zabbix.com/documentation/7.4/en/manual/api/reference/trigger/get)。
