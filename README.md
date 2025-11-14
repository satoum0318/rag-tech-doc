# 🤖 RAG技術文書検索システム

LangChain、FAISS、Sentence Transformersを使用したRAG（Retrieval-Augmented Generation）ベースのチャットボットです。技術文書を検索し、質問に対して関連情報を素早く提供します。

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

