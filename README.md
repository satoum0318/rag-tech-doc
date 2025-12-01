# 🔍 TechScout - RAG技術文書検索システム

**TechScout** (テックスカウト) は、LangChain、FAISS、Sentence Transformers、LM Studioを使用したRAG（Retrieval-Augmented Generation）ベースの技術文書検索システムです。

**開発**: 東洋電機製造株式会社 開発センター基盤技術部  
**バージョン**: 1.0.0  
**日付**: 2025年11月14日

---

## 🚀 クイックスタート（最も簡単な起動方法）

### 方法1: バッチファイルで起動（推奨・最も簡単）

**Windowsエクスプローラーで `run.bat` をダブルクリック**するだけ！

または、コマンドプロンプトで：
```cmd
run.bat
```

### 方法2: PowerShellスクリプトで起動

```powershell
.\run.ps1
```

### 方法3: Pythonで直接起動

```powershell
# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# アプリを起動
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

**確認方法**: ブラウザで `http://localhost:1234/v1/models` にアクセス  
→ JSONが表示されればLM Studioは起動中です

---

## 🔐 ログイン情報

- **ユーザー名**: `admin`
- **パスワード**: `password123`

---

## 📋 起動前の確認事項

### ✅ LM Studioが起動しているか確認

1. **LM Studioアプリを開く**
2. **Local Serverタブ**（左側の緑色アイコン）をクリック
3. **「Start Server」**が押されているか確認
4. ステータスが **"Server Running"** になっているか確認

**URL**: `http://localhost:1234`

### ✅ ドキュメントが配置されているか確認

`documents/` フォルダに以下のファイル形式を配置：
- `.txt` - テキストファイル（UTF-8推奨）
- `.pdf` - PDFファイル
- `.docx` - Word文書

---

## 💻 コードの実行方法（詳細）

### ステップ1: 仮想環境を有効化

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**コマンドプロンプト:**
```cmd
venv\Scripts\activate.bat
```

### ステップ2: アプリを起動

**LM Studio版（推奨）:**
```powershell
python app_lmstudio.py
```

**GPU版（要CUDA）:**
```powershell
python app.py
```

### ステップ3: ブラウザでアクセス

起動後、以下のメッセージが表示されます：
```
Running on local URL:  http://127.0.0.1:7861
```

ブラウザで **http://localhost:7861** にアクセスしてください。

---

## 🛠️ トラブルシューティング

### 問題: ポート7861が使用中

**エラー**: `OSError: Cannot find empty port in range: 7861-7861`

**解決策**:
```powershell
# ポート7861を使用しているプロセスを確認
Get-NetTCPConnection -LocalPort 7861

# TechScoutを停止（PIDを確認してから）
Stop-Process -Id <PID>
```

### 問題: LM Studioに接続できない

**エラー**: `Failed to connect to LM Studio`

**解決策**:
1. LM Studioを起動
2. Local Serverタブで「Start Server」をクリック
3. `http://localhost:1234/v1/models` にアクセスして確認

### 問題: モジュールが見つからない

**エラー**: `ModuleNotFoundError: No module named 'gradio'`

**解決策**:
```powershell
# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# パッケージを再インストール
pip install -r requirements.txt
```

### 問題: PDFが文字化けする

**解決策**: `pdfplumber`がインストールされているか確認
```powershell
pip install pdfplumber
```

---

## 📝 起動時のログ確認

正常に起動すると、以下のようなログが表示されます：

```
============================================================
RAG Search System - LM Studio Edition
============================================================
[1/4] Loading documents from: ./documents
  - Loading: sample_tech_doc.txt
  - Loading: 埋込磁石同期モータ.pdf
  [OK] Loaded 19 documents
[2/4] Splitting documents into chunks...
[OK] Created 101 chunks
[3/4] Creating FAISS vector store...
[OK] Vector store created
[4/4] Connecting to LM Studio...
  Base URL: http://localhost:1234/v1
[OK] Connected to LM Studio
============================================================
[OK] Initialization complete!
============================================================
Running on local URL:  http://127.0.0.1:7861
```

---

## 🎯 使い方

### 基本的な質問

```
永久磁石同期モータの温度推定方法について教えてください

誘導電動機のセンサレス制御の原理を説明してください

概要
```

### 特殊コマンド

**ドキュメント概要を表示:**
```
概要
または
/summary
```

**自由会話モード:**
```
/chat こんにちは
雑談 プログラミングのコツは？
```

---

## 📚 詳細ドキュメント

- **QUICKSTART.md** - 5分で起動するガイド
- **HOW_TO_RUN.md** - 実行方法の詳細
- **README_LMSTUDIO.md** - LM Studio版の詳細
- **PROJECT_REPORT.md** - プロジェクトの完全レポート
- **LM_STUDIO_SETTINGS.md** - LM Studioの最適化設定

---

## 🔧 環境変数（オプション）

起動前に設定すると便利：

```powershell
# UTF-8エンコーディング設定
$env:PYTHONIOENCODING="utf-8"

# バッファリング無効化（ログが即座に表示）
$env:PYTHONUNBUFFERED="1"
```

---

## 📞 サポート

問題が解決しない場合は、以下を確認：
1. 仮想環境が有効化されているか
2. LM Studioが起動しているか
3. ポート7861と1234が空いているか
4. ログファイル（`startup.log`）を確認

---

## 🎉 まとめ

**最も簡単な起動方法**:
1. `run.bat` をダブルクリック
2. ブラウザで `http://localhost:7861` にアクセス
3. `admin` / `password123` でログイン
4. 質問を入力！

**TechScout URL**: http://localhost:7861  
**LM Studio URL**: http://localhost:1234

## ✨ 特徴

- ⚡ **超高速応答** - LLMを使わずベクトル検索のみで動作（高速モード）
- 💾 **軽量** - CPUでもサクサク動作
- 🎯 **正確** - 元文書から直接関連箇所を抽出
- 📚 **マルチフォーマット対応** - TXT、PDF、DOCX形式をサポート
- 🔒 **セキュリティ機能** - IP制限とユーザー認証
- 🌐 **Webインターフェース** - Gradioによる使いやすいUI

## 📋 必要要件

- Python 3.8以上
- 2GB以上のメモリ推奨

## 🚀 インストール方法

### 1. リポジトリをクローン（または作成）

```bash
git clone <repository-url>
cd rag-tech-doc
```

### 2. 仮想環境を作成（推奨）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

## 📝 使い方

### 1. ドキュメントを配置

`documents`フォルダに技術文書を配置します：

```
rag-tech-doc/
├── app.py
├── requirements.txt
├── README.md
└── documents/          ← ここに文書を配置
    ├── manual.txt
    ├── guide.pdf
    └── specification.docx
```

サポートされているファイル形式：
- `.txt` - テキストファイル
- `.pdf` - PDFファイル
- `.docx` - Word文書

### 2. アプリケーションを起動

```bash
python app.py
```

### 3. ブラウザでアクセス

起動後、以下のURLにアクセスします：

```
http://localhost:7860
```

### 4. ログイン

デフォルトの認証情報：
- ユーザー名: `admin`
- パスワード: `password123`

**⚠️ セキュリティ警告**: 本番環境では必ず `app.py` の `VALID_USERS` を変更してください！

## ⚙️ 設定のカスタマイズ

### セキュリティ設定

`app.py` の以下の部分を編集：

```python
# IP制限の設定
ALLOWED_IP_RANGES = [
    "172.16.0.0/16",    # 社内ネットワーク
    "127.0.0.0/8",      # ローカルホスト
    "192.168.0.0/16",   # プライベートネットワーク（追加例）
]

# ユーザー認証
VALID_USERS = {
    "admin": "your_secure_password",
    "user1": "another_password",
}
```

### チャンクサイズとオーバーラップ

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # より大きな値で長いコンテキスト
    chunk_overlap=50,    # より大きな値でコンテキスト保持
)
```

### 検索結果の数

```python
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}  # 取得する関連チャンク数
)
```

## 🧠 LLMモードの有効化（オプション）

デフォルトでは高速モード（LLMなし）で動作しますが、LLMを有効にすることもできます：

```python
# app.py の main() 関数内
setup_qa_chain("./documents", use_llm=True)  # True に変更
```

**注意**: LLMモードはCPU環境では非常に遅くなります。GPU環境を推奨します。

## 🔧 トラブルシューティング

### ドキュメントが読み込まれない

- `documents`フォルダが存在するか確認
- ファイル形式が `.txt`, `.pdf`, `.docx` であるか確認
- テキストファイルのエンコーディングがUTF-8であるか確認

### メモリ不足エラー

- チャンクサイズを小さくする
- 一度に読み込むドキュメント数を減らす
- システムメモリを増やす

### モデルのダウンロードが遅い

初回実行時は埋め込みモデル（約90MB）がダウンロードされます。インターネット接続を確認してください。

## 📊 システム構成

```
ユーザーの質問
    ↓
埋め込みモデル（Sentence Transformers）
    ↓
ベクトル検索（FAISS）
    ↓
関連文書の取得
    ↓
結果の整形と表示
```

## 🌟 使用例

### 質問例

- "このドキュメントの主な内容は何ですか？"
- "インストール方法を教えてください"
- "エラーコード404の対処方法は？"
- "APIの認証方法について"

## 🛡️ セキュリティのベストプラクティス

1. **パスワードの変更**: デフォルトのパスワードを必ず変更
2. **環境変数の使用**: 本番環境では環境変数からパスワードを読み込む
3. **HTTPS使用**: 本番環境ではリバースプロキシ（nginx等）でHTTPSを設定
4. **IP制限**: 信頼できるネットワークからのみアクセス許可
5. **ログ監視**: 不正アクセスの試行を監視

## 📦 プロジェクト構造

```
rag-tech-doc/
├── app.py              # メインアプリケーション
├── requirements.txt    # 依存パッケージ
├── README.md          # このファイル
└── documents/         # 技術文書フォルダ
```

## 🤝 貢献

バグ報告や機能リクエストは、Issueを作成してください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

このプロジェクトは以下のオープンソースプロジェクトを使用しています：

- [LangChain](https://github.com/langchain-ai/langchain)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Gradio](https://www.gradio.app/)
- [HuggingFace Transformers](https://huggingface.co/transformers/)

