# ファイアウォール設定手順

外部からアクセスするには、Windowsファイアウォールでポート7861を開く必要があります。

## 🛡️ 方法1: PowerShellで設定（推奨）

### ステップ1: PowerShellを管理者として起動

1. **スタートボタン**を右クリック
2. **「Windows PowerShell (管理者)」**を選択
   または
   **「Windows Terminal (管理者)」**を選択

### ステップ2: 以下のコマンドをコピー&ペースト

```powershell
New-NetFirewallRule -DisplayName "RAG App Port 7861" -Direction Inbound -LocalPort 7861 -Protocol TCP -Action Allow -Profile Any
```

### ステップ3: 確認

成功すると以下のような出力が表示されます：
```
Name                  : {ランダムなGUID}
DisplayName           : RAG App Port 7861
Description           : 
DisplayGroup          : 
Group                 : 
Enabled               : True
...
```

---

## 🛡️ 方法2: GUIで設定

### ステップ1: ファイアウォールを開く

1. **Windowsキー + R** を押す
2. `wf.msc` と入力して **Enter**

### ステップ2: 新しい規則を作成

1. 左側の **「受信の規則」** をクリック
2. 右側の **「新しい規則...」** をクリック

### ステップ3: ポートの設定

1. **「ポート」** を選択 → **次へ**
2. **「TCP」** を選択
3. **「特定のローカルポート」** を選択
4. **`7861`** と入力 → **次へ**

### ステップ4: 接続を許可

1. **「接続を許可する」** を選択 → **次へ**

### ステップ5: プロファイルを選択

1. **すべてにチェック**を入れる
   - ドメイン
   - プライベート
   - パブリック
2. **次へ**

### ステップ6: 名前を設定

1. 名前: **`RAG App Port 7861`**
2. 説明: **`RAG技術文書検索システム用`**
3. **完了**

---

## ✅ 設定完了の確認

PowerShellで確認：
```powershell
Get-NetFirewallRule -DisplayName "RAG App Port 7861"
```

外部からアクセス：
```
http://192.168.2.101:7861
```

---

## 🔍 トラブルシューティング

### まだアクセスできない場合

1. **アプリを再起動**
   ```powershell
   .\run.ps1
   ```

2. **PCを再起動**（ファイアウォール設定の反映）

3. **アンチウイルスソフトを確認**
   - サードパーティのセキュリティソフトがブロックしている可能性

4. **ルーターの設定**
   - 同じLAN内なら不要ですが、外部からの場合はポートフォワーディングが必要

---

## 📞 ヘルプ

問題が解決しない場合は、以下を確認してください：

```powershell
# アプリの状態確認
Get-NetTCPConnection -LocalPort 7861

# ファイアウォールルール確認
Get-NetFirewallRule -DisplayName "*7861*" | Select-Object DisplayName, Enabled, Direction, Action

# 接続テスト（ローカル）
Invoke-WebRequest -Uri "http://localhost:7861" -TimeoutSec 5
```

