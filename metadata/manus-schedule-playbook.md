每週一 08:00（Asia/Taipei）執行以下工作，使用已授權的 GitHub connector 存取 private repository `https://github.com/rellikhsu/manus-skills`。不要使用 sandbox 內的 `/home/ubuntu` 檔案，也不要把本機檔案狀態當作同步成功。

先讀取 `metadata/source-commits.json`、`metadata/manus-imports.tsv` 與 mirror 的最新 commit，確認三個上游來源：`https://github.com/mattpocock/skills`、`https://github.com/awslabs/agent-plugins`、`https://github.com/obra/superpowers`。比對上次執行記錄；若 mirror commit 沒有變更，回報「mirror 無變更」並停止，不要重複匯入。

若 mirror commit 有變更，讀取 `metadata/manus-imports.tsv` 中的三個 bundle URL 與來源 commit，列出變更的 namespace 和 skills。接著只使用 Manus 官方支援的個人 Skills library 更新方法處理變更；不得修改無法確認來源的其他 skills，不得刪除個人 skills，不得透過 Claude Code 或本機 `.agents`／`.claude` 目錄冒充 Manus 更新。

如果目前執行環境沒有能把 private GitHub 內容寫入 Manus 個人 Skills library 的正式操作，必須明確回報「GitHub connector 可讀取 private mirror，但目前沒有可用的 Skills library 寫入 API／操作」，並列出待更新的 bundle、mirror commit、失敗原因與下次可重試的步驟；不要把 GitHub Actions 成功或讀取成功宣稱為 Manus Skills 已更新。

完成後回報：執行時間、private mirror commit、三個上游來源狀態、已更新的 Manus skills、已是最新的 skills、失敗或跳過的項目，以及任何權限或操作限制。
