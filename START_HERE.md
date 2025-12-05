# 🚀 TechScout 起動ガイド

**最も簡単な起動方法**をまとめました！

---

## ⚡ 30秒で起動（推奨）

### Windowsエクスプローラーから

**`run.bat` をダブルクリックするだけ！**

---

## 💻 コマンドラインから起動

### PowerShell
```powershell
.\run.ps1
```

### コマンドプロンプト
```cmd
run.bat
```

### Python直接実行
```powershell
.\venv\Scripts\Activate.ps1
python app_lmstudio.py
```

---

## 🌐 アクセスURL

### TechScout（RAGアプリ）
```
http://localhost:7861
```

### LM Studio（LLMサーバー）
```
http://localhost:1234
```

**LM Studioの確認**: ブラウザで `http://localhost:1234/v1/models` にアクセス  
→ JSONが表示されれば起動中です ✅

---

## 🔐 ログイン情報

```
ユーザー名: admin
パスワード: password123
```

---

## ✅ 起動前チェックリスト

- [ ] LM Studioが起動している（Local Serverタブで「Start Server」が押されている）
- [ ] `documents/` フォルダに文書が配置されている
- [ ] 仮想環境が作成されている（初回のみ）

---

## 📝 起動時のログ

正常に起動すると、以下のようなメッセージが表示されます：

```
============================================================
RAG Search System - LM Studio Edition
============================================================
[1/4] Loading documents from: ./documents
  - Loading: sample_tech_doc.txt
  [OK] Loaded 19 documents
[2/4] Splitting documents into chunks...
[OK] Created 101 chunks
[3/4] Creating FAISS vector store...
[OK] Vector store created
[4/4] Connecting to LM Studio...
[OK] Connected to LM Studio
============================================================
[OK] Initialization complete!
============================================================
Running on local URL:  http://127.0.0.1:7861
```

このメッセージが表示されたら、ブラウザで **http://localhost:7861** にアクセスしてください！

---

## 🆘 よくある問題

### ポート7861が使用中

```powershell
# TechScoutを停止
Get-NetTCPConnection -LocalPort 7861 | Select-Object -ExpandProperty OwningProcess | Stop-Process -Force
```

### LM Studioに接続できない

1. LM Studioを開く
2. Local Serverタブで「Start Server」をクリック
3. `http://localhost:1234/v1/models` で確認

### モジュールが見つからない

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📚 詳細情報

- **README.md** - 完全なドキュメント
- **QUICKSTART.md** - 5分ガイド
- **HOW_TO_RUN.md** - 実行方法の詳細

---

**TechScout URL**: http://localhost:7861  
**LM Studio URL**: http://localhost:1234








