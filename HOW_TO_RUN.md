# 🚀 実行方法ガイド

このプロジェクトには複数の実行方法があります。お好みの方法を選んでください。

## 📋 目次

1. [Cursor/VSCodeで実行](#1-cursorvscodeで実行-最も簡単)
2. [バッチファイルで実行](#2-バッチファイルで実行)
3. [PowerShellスクリプトで実行](#3-powershellスクリプトで実行)
4. [ターミナルから直接実行](#4-ターミナルから直接実行)

---

## 1. Cursor/VSCodeで実行（最も簡単！）⭐

### 方法A: デバッグ実行（F5キー）

1. **Cursor/VSCodeで `app_lmstudio.py` を開く**
2. **F5キーを押す**
3. 実行構成を選択：
   - `RAG App - LM Studio版` （推奨）
   - `RAG App - GPU版（要CUDA）`

### 方法B: 右クリックメニュー

1. `app_lmstudio.py` を右クリック
2. 「ターミナルでPythonファイルを実行」を選択

### 方法C: タスクから実行

1. **Ctrl+Shift+P** を押す
2. 「**Tasks: Run Task**」と入力
3. タスクを選択：
   - `Run: LM Studio版`
   - `Run: GPU版`
   - `Install Dependencies`

---

## 2. バッチファイルで実行

### Windows エクスプローラーから

**ダブルクリック**するだけ：
```
run.bat
```

### コマンドプロンプトから

```cmd
run.bat
```

これでLM Studio版が起動します！

---

## 3. PowerShellスクリプトで実行

### LM Studio版（推奨）

```powershell
.\run.ps1
```

または

```powershell
.\run.ps1 lmstudio
```

### GPU版

```powershell
.\run.ps1 gpu
```

---

## 4. ターミナルから直接実行

### ステップ1: 仮想環境を有効化

```powershell
.\venv\Scripts\Activate.ps1
```

### ステップ2: アプリを実行

**LM Studio版:**
```powershell
python app_lmstudio.py
```

**GPU版:**
```powershell
python app.py
```

---

## 🌐 アクセス方法

アプリが起動したら、ブラウザで以下にアクセス：

```
http://localhost:7860
```

### ログイン情報

- **ユーザー名**: `admin`
- **パスワード**: `password123`

⚠️ **セキュリティ**: 本番環境では必ずパスワードを変更してください！

---

## 🔧 トラブルシューティング

### 問題: `ModuleNotFoundError: No module named 'gradio'`

**原因**: 仮想環境が有効化されていない、またはパッケージ未インストール

**解決策**:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 問題: LM Studioに接続できない

**原因**: LM Studioが起動していない、またはServerが開始されていない

**解決策**:
1. LM Studioを起動
2. モデルをロード
3. **Server**タブで「**Start Server**」をクリック

### 問題: ポート7860が使用中

**原因**: 別のアプリケーションがポート7860を使用している

**解決策**:
`app_lmstudio.py` または `app.py` の最後の方を編集：
```python
server_port=7860,  # 7861など別のポートに変更
```

### 問題: Cursorで実行ボタン（▶️）が機能しない

**原因**: Pythonインタープリターが正しく設定されていない

**解決策**:
1. **Ctrl+Shift+P** を押す
2. 「**Python: Select Interpreter**」と入力
3. `.\venv\Scripts\python.exe` を選択

---

## 📝 どの方法を使うべき？

| 方法 | 推奨度 | メリット | デメリット |
|------|--------|----------|------------|
| **Cursor/VSCodeのF5** | ⭐⭐⭐⭐⭐ | デバッグ可能、最も便利 | 初回設定必要 |
| **バッチファイル** | ⭐⭐⭐⭐ | ダブルクリックで起動 | Windows専用 |
| **PowerShellスクリプト** | ⭐⭐⭐⭐ | 柔軟、エラーチェック | PowerShell必要 |
| **直接実行** | ⭐⭐⭐ | シンプル | 手順が多い |

---

## 🎯 推奨フロー

### 初回セットアップ

1. 仮想環境を作成
   ```powershell
   python -m venv venv
   ```

2. 仮想環境を有効化
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. パッケージをインストール
   ```powershell
   pip install -r requirements.txt
   ```

4. LM Studioを起動してServerを開始

### 2回目以降

**簡単な方法**:
- `run.bat` をダブルクリック

**開発中**:
- Cursorで `app_lmstudio.py` を開いて **F5**

---

## 💡 ヒント

- **LM Studio版を推奨**: 追加のモデルダウンロード不要
- **GPU版**: PyTorch CUDA版のインストールが必要（約2.4GB）
- **開発時**: IP制限を無効化（`ENABLE_IP_RESTRICTION = False`）
- **本番時**: パスワード変更、IP制限を有効化

---

## 📚 詳細情報

- LM Studio版の詳細: [README_LMSTUDIO.md](README_LMSTUDIO.md)
- 全体的な情報: [README.md](README.md)
- クイックスタート: [QUICKSTART.md](QUICKSTART.md)

---

**楽しいRAG体験を！** 🎉

