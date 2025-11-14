# LM Studio設定ガイド - RAG用最適化

## 🎯 現在の問題

RAGシステムからの質問に対して、LLMが適切に回答できない原因は**コンテキスト長が短すぎる**ことです。

現在のログ:
```
model is loaded with context length of only 4096 tokens
```

RAGシステムでは、検索結果（複数のチャンク）+ 質問 + プロンプトで、
少なくとも **8192トークン以上**のコンテキスト長が必要です。

---

## 🔧 LM Studioの設定変更手順

### ステップ1: LM Studioを開く

### ステップ2: Local Server タブに移動

左側の緑色アイコン（Local Server）をクリック

### ステップ3: Context Length を変更

画面右側の設定で：

```
Context Length: 8192
```

または

```
Context Length: 16384  （より良い）
```

に設定してください。

### ステップ4: サーバーを再起動

1. 「Stop Server」をクリック
2. Context Length設定を変更
3. 「Start Server」をクリック

---

## 📊 推奨設定

### 最小構成（動作はするが品質低い）
- **Context Length**: 4096
- **Temperature**: 0.7
- **Max Tokens**: 512

### 推奨構成（バランス良好）
- **Context Length**: 8192 ⭐
- **Temperature**: 0.7
- **Max Tokens**: 512

### 高品質構成（メモリに余裕がある場合）
- **Context Length**: 16384
- **Temperature**: 0.7
- **Max Tokens**: 1024

---

## 🎯 設定後のテスト

設定を変更したら、RAGアプリを再起動してください：

```powershell
# 現在のアプリを停止
# Ctrl+C または以下のコマンド
Get-Process python | Where-Object {$_.Path -like "*rag-tech-doc*"} | Stop-Process

# 再起動
.\run.ps1
```

そして、以下のような**具体的な質問**を試してください：

```
PMSMの温度推定における寸法ばらつきの影響について説明してください

誘導電動機の速度センサレス制御の原理を教えてください

回生運転時の高トルク制御法の特徴は何ですか？
```

---

## 🔍 設定確認方法

RAGアプリの起動ログで以下を確認：

```
[OK] Connected to LM Studio
```

の後に警告が出なければ成功です。

---

## ⚡ 他の最適化ヒント

### GPUメモリが足りない場合

1. **より小さい量子化レベルのモデルを使用**
   - Q5_K_M → Q4_K_M
   - Q4_K_M → Q3_K_M

2. **より小さいモデルを使用**
   - Mistral-7B → Phi-2 (2.7B)

### CPU使用の場合

- Context Lengthを8192以下に抑える
- より小さいモデル（Phi-2）を推奨

---

## 📝 チェックリスト

- [ ] LM Studioを開く
- [ ] Local Serverタブに移動
- [ ] Context Length を 8192 または 16384 に設定
- [ ] サーバーを再起動
- [ ] RAGアプリを再起動
- [ ] 具体的な質問でテスト

---

設定完了後、回答品質が劇的に改善するはずです！

