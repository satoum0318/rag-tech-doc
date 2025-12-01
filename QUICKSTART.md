# 🚀 TechScout クイックスタートガイド

**TechScout** (RAG技術文書検索システム) を5分で起動できます！

---

## ⚡ 最も簡単な方法（30秒）

### Windowsの場合

**`run.bat` をダブルクリックするだけ！**

または、コマンドプロンプトで：
```cmd
run.bat
```

### PowerShellの場合

```powershell
.\run.ps1
```

これで自動的に：
1. 仮想環境を有効化
2. アプリを起動
3. ブラウザで `http://localhost:7861` にアクセス

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
→ JSONが表示されれば起動中です

---

## 🔐 ログイン情報

```
ユーザー名: admin
パスワード: password123
```

## ステップ1: 環境準備

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

## ステップ2: パッケージインストール

```bash
pip install -r requirements.txt
```

⏱️ **所要時間**: 5-10分（インターネット速度による）

## ステップ3: LM Studioの確認（重要）

**LM Studioが起動しているか確認**:

1. LM Studioアプリを開く
2. 左側の**緑色アイコン**（Local Server）をクリック
3. **「Start Server」**が押されているか確認
4. ステータスが **"Server Running"** になっているか確認

**確認URL**: `http://localhost:1234/v1/models`

---

## ステップ4: TechScoutを起動

### 方法A: バッチファイル（推奨）
```cmd
run.bat
```

### 方法B: PowerShellスクリプト
```powershell
.\run.ps1
```

### 方法C: Pythonで直接起動
```powershell
# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# アプリを起動
python app_lmstudio.py
```

⏱️ **初回起動時**: 30-60秒（PDF処理に時間がかかります）
⏱️ **2回目以降**: 10-20秒

---

## ステップ5: ブラウザでアクセス

起動後、以下のURLにアクセス：

```
http://localhost:7861
```

**ログイン情報**:
```
ユーザー名: admin
パスワード: password123
```

---

## ステップ6: 質問してみる

### サンプル質問

**技術文書検索:**
- "永久磁石同期モータの温度推定方法について教えてください"
- "誘導電動機のセンサレス制御の原理を説明してください"
- "モータ制御における回生運転とは何ですか？"

**ドキュメント概要:**
- "概要"

**自由会話:**
- "/chat モータ制御の勉強方法を教えて"

## 🎉 完了！

これで技術文書検索システムが使えるようになりました。

## 次のステップ

1. **独自の文書を追加**: `documents/` フォルダに TXT、PDF、DOCX ファイルを配置
2. **アプリを再起動**: 新しい文書が自動的にインデックスされます
3. **セキュリティ設定**: `app.py` のパスワードを変更

## トラブルシューティング

### エラー: "No module named 'XXX'"
```bash
pip install -r requirements.txt
```

### エラー: "Address already in use" (ポート7861が使用中)
別のアプリケーションがポート7861を使用しています。

**解決策**:
```powershell
# ポート7861を使用しているプロセスを確認
Get-NetTCPConnection -LocalPort 7861

# TechScoutを停止（PIDを確認してから）
Stop-Process -Id <PID>
```

または、`app_lmstudio.py` の `server_port=7861` を別のポート（例: 7862）に変更してください。

### 動作が遅い
- GPUがある場合は `device='cuda'` に変更
- `chunk_size` を小さくする
- LLMモードを無効に（デフォルトで無効）

## 詳細情報

詳しい設定やカスタマイズについては、[README.md](README.md) を参照してください。

