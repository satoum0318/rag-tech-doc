# 🔍 TechScout - RAG技術文書検索システム

**TechScout** (テックスカウト) は、既にインストール済みのLM StudioのLLMを活用したRAGチャットボットです。

---

**開発**: 東洋電機製造株式会社 開発センター基盤技術部  
**バージョン**: 1.0.0  
**日付**: 2025年11月14日

---

## ✨ 特徴

- 🚀 **LM Studio統合** - 既にインストール済みのLLMを活用
- 💾 **軽量** - 追加の大きなモデルダウンロード不要
- ⚡ **高速起動** - PyTorchのCUDA版インストール不要
- 🎯 **正確** - ベクトル検索で関連箇所を特定
- 🧠 **高品質AI回答** - LM Studio上のLLMが自然な日本語で回答

## 📋 必要要件

- Python 3.8以上
- LM Studio（インストール済み）
- 2GB以上のメモリ

## 🚀 セットアップ手順

### ステップ1: LM Studioの準備

1. **LM Studioを起動**
2. **モデルをロード**（推奨：日本語対応モデル）
   - Elyza-japanese-Llama-2-7b
   - Swallow 7B
   - Mistral 7B Instruct
   - お好みの他のモデル
3. **Serverタブ**に移動
4. **「Start Server」をクリック**
   - デフォルト設定（Port: 1234）でOK

### ステップ2: アプリケーションの起動

PowerShellで以下を実行：

```powershell
.\start_lmstudio.ps1
```

または手動で：

```powershell
# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# アプリを起動
python app_lmstudio.py
```

### ステップ3: ブラウザでアクセス

```
http://localhost:7860
```

**ログイン情報：**
- ユーザー名: `admin`
- パスワード: `password123`

## 📚 ドキュメントの追加

`documents/` フォルダに技術文書を配置してください：

```
rag-tech-doc/
└── documents/
    ├── manual.txt
    ├── guide.pdf
    └── specification.docx
```

対応形式：`.txt`, `.pdf`, `.docx`

## 💡 使い方

1. ドキュメントを `documents/` フォルダに配置
2. アプリを起動（自動的にインデックス化）
3. 質問を入力
4. AIが文書を参照して回答

### 質問例

- "このシステムのインストール方法は？"
- "トラブルシューティングの手順を教えてください"
- "セキュリティ設定について説明してください"

## 🔧 カスタマイズ

### LM StudioのURL変更

`app_lmstudio.py` の以下の部分を編集：

```python
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"  # ポート番号を変更
```

### 検索結果の数

```python
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}  # 取得するチャンク数を変更
)
```

### チャンクサイズ

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # チャンクサイズ
    chunk_overlap=50,    # オーバーラップ
)
```

## 🆚 従来版との比較

| 項目 | LM Studio版 | 従来版（HuggingFace） |
|------|-------------|----------------------|
| モデルダウンロード | 不要（既存利用） | 必要（約14GB） |
| PyTorch CUDA | 不要 | 必要（約2.4GB） |
| 起動時間 | 数秒 | 数分 |
| メモリ管理 | LM Studioが管理 | 手動管理 |
| モデル切替 | LM Studioで簡単 | コード修正必要 |
| GPU対応 | LM Studioが自動 | 設定必要 |

## 🔒 セキュリティ

- IP制限機能搭載
- ユーザー認証機能
- 社内ネットワーク限定アクセス

**重要**: 本番環境では `VALID_USERS` のパスワードを変更してください！

## ⚠️ トラブルシューティング

### LM Studioに接続できない

**症状**: "[WARNING] LM Studio is not running"

**対処法**:
1. LM Studioを起動
2. Serverタブで「Start Server」をクリック
3. Port 1234が使用されていることを確認

### モデルが見つからない

**症状**: "No models loaded in LM Studio"

**対処法**:
1. LM Studioでモデルをロード
2. モデルが読み込まれていることを確認
3. アプリを再起動

### 日本語の回答品質が低い

**対処法**:
- 日本語対応モデルに変更（Elyza, Swallowなど）
- LM Studioの Temperature を調整（0.5～0.8推奨）
- プロンプトを調整（`app_lmstudio.py` の `prompt` 変数）

### ドキュメントが読み込まれない

**対処法**:
- ファイルが `documents/` フォルダにあるか確認
- ファイル形式が `.txt`, `.pdf`, `.docx` であるか確認
- テキストファイルのエンコーディングがUTF-8であるか確認

## 📖 推奨LLMモデル

### 日本語特化

1. **Elyza-japanese-Llama-2-7b** ⭐推奨
   - 日本語に最適化
   - 7Bで高品質

2. **Swallow 7B/13B**
   - 日本語性能優秀
   - 技術文書に強い

### 多言語対応

3. **Mistral 7B Instruct v0.2**
   - 英語・日本語両対応
   - バランス型

4. **Llama 2 7B Chat**
   - 安定性高い
   - 汎用的

### 軽量版（メモリ制限時）

5. **Phi-2 (2.7B)**
   - 軽量高速
   - 基本的な質問対応

## 🎯 次のステップ

1. 独自の技術文書を追加
2. 日本語対応LLMに変更
3. プロンプトをカスタマイズ
4. チャンクサイズを調整して精度向上

## 📧 サポート

問題が発生した場合は、以下を確認してください：
- LM Studioが起動しているか
- Serverが開始されているか
- ポート7860と1234が空いているか

## 📄 ライセンス

MIT License

---

**楽しいRAG体験を！** 🚀

