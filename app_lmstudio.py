"""
RAGベースチャットボット - LM Studio版
LangChain、FAISS、Sentence Transformers、LM Studio APIを使用
"""

import os
import glob
from typing import List, Tuple, Optional
import gradio as gr
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
import pdfplumber
from langchain_core.documents import Document
from openai import OpenAI
import ipaddress
import time

# グローバル変数でretrieverとLM Studio clientを保持
retriever = None
lm_studio_client = None
document_summary = None  # ドキュメント概要を保持
all_documents_text = ""  # 全ドキュメントのテキスト

# LM Studio設定
LM_STUDIO_BASE_URL = "http://localhost:1234/v1"  # LM Studioのデフォルト
LM_STUDIO_API_KEY = "lm-studio"  # ダミー（LM Studioでは不要）

# ========================================
# セキュリティ設定
# ========================================

# IP制限の有効/無効（開発時はFalseにすると便利）
ENABLE_IP_RESTRICTION = False  # True = IP制限有効、False = 制限なし

# 許可するIPアドレス範囲（プライベートネットワーク全般）
ALLOWED_IP_RANGES = [
    "127.0.0.0/8",      # ローカルホスト
    "10.0.0.0/8",       # プライベートネットワーク（クラスA）
    "172.16.0.0/12",    # プライベートネットワーク（クラスB）
    "192.168.0.0/16",   # プライベートネットワーク（クラスC - 自宅環境で一般的）
    # 社内ネットワークなど特定のIPのみに制限したい場合は、上記を削除して設定
]

# 認証情報（ユーザー名とパスワード）
# 本番環境では環境変数から読み込むことを推奨
VALID_USERS = {
    "admin": "password123",      # 管理者
    "user1": "secure_pass",      # ユーザー1
    "tanaka": "tanaka2024",      # 田中さん
    "suzuki": "suzuki2024",      # 鈴木さん
    "sato": "sato2024",          # 佐藤さん
    # 必要に応じて追加
}

def check_ip_allowed(request: gr.Request) -> bool:
    """
    クライアントのIPアドレスが許可範囲内かチェック
    
    Args:
        request: Gradioリクエストオブジェクト
    
    Returns:
        許可されている場合True、そうでない場合False
    """
    # IP制限が無効な場合は常に許可
    if not ENABLE_IP_RESTRICTION:
        return True
    
    try:
        client_ip = request.client.host
        client_ip_obj = ipaddress.ip_address(client_ip)
        
        for ip_range in ALLOWED_IP_RANGES:
            if client_ip_obj in ipaddress.ip_network(ip_range):
                print(f"[OK] Access allowed: {client_ip}")
                return True
        
        print(f"[WARNING] Access denied: {client_ip} (not in allowed range)")
        return False
    except Exception as e:
        print(f"[ERROR] IP check error: {e}")
        return False

def authenticate_user(username: str, password: str) -> bool:
    """
    ユーザー認証
    
    Args:
        username: ユーザー名
        password: パスワード
    
    Returns:
        認証成功の場合True
    """
    if username in VALID_USERS and VALID_USERS[username] == password:
        print(f"[OK] User authenticated: {username}")
        return True
    print(f"[WARNING] Authentication failed: {username}")
    return False

def generate_document_summary(documents: List, client) -> str:
    """
    全ドキュメントの概要をLLMで生成
    
    Args:
        documents: 読み込まれた文書のリスト
        client: LM Studio client
    
    Returns:
        ドキュメントの概要テキスト
    """
    if not client or not documents:
        return None
    
    print("[INFO] Generating document summary with LLM...")
    
    try:
        # 全文書のテキストを結合（最大10,000文字まで）
        combined_text = ""
        for doc in documents:
            combined_text += doc.page_content + "\n\n"
            if len(combined_text) > 10000:
                combined_text = combined_text[:10000] + "..."
                break
        
        # LLMに概要生成を依頼
        prompt = f"""以下の技術文書の内容を分析して、包括的な概要を日本語で作成してください。

【文書内容】
{combined_text}

【出力形式】
以下の項目を含めて、見やすく整理して出力してください：
1. 主要トピック（箇条書き）
2. 文書の目的と対象読者
3. 重要なキーワード（箇条書き）
4. 推奨される質問例（3-5個）

【概要】"""
        
        response = client.chat.completions.create(
            model="local-model",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        )
        
        summary = response.choices[0].message.content
        print("[OK] Document summary generated successfully!")
        return summary
        
    except Exception as e:
        print(f"[WARNING] Could not generate summary: {e}")
        return None

def load_documents(documents_path: str = "./documents") -> List:
    """
    指定されたフォルダから技術文書を読み込む
    
    Args:
        documents_path: ドキュメントが格納されているフォルダのパス
    
    Returns:
        読み込まれた文書のリスト
    """
    print(f"[1/4] Loading documents from: {documents_path}")
    documents = []
    
    # TXTファイルを読み込む（エンコーディング指定）
    txt_files = glob.glob(os.path.join(documents_path, "*.txt"))
    for file_path in txt_files:
        try:
            print(f"  - Loading: {os.path.basename(file_path)}")
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"  [WARNING] Failed to load {file_path}: {e}")
    
    # PDFファイルを読み込む（サブプロセスで安全に実行）
    import json
    import subprocess
    import sys

    pdf_files = glob.glob(os.path.join(documents_path, "*.pdf"))
    total_pdfs = len(pdf_files)
    
    if total_pdfs > 0:
        print(f"  Found {total_pdfs} PDF files")

    # 以前のスキップリストは不要になったため削除しました
    # サブプロセス化により、クラッシュするファイルは自動的にスキップされます

    for idx, file_path in enumerate(pdf_files, 1):
        basename = os.path.basename(file_path)
        print(f"  [{idx}/{total_pdfs}] Loading: {basename}")
        
        try:
            # pdf_worker.py をサブプロセスとして実行
            # これにより、PDF読み込み中にクラッシュしてもメインプロセスは守られる
            result = subprocess.run(
                [sys.executable, "pdf_worker.py", file_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60  # 60秒でタイムアウト
            )
            
            if result.returncode == 0:
                # 成功した場合、JSON出力をパース
                try:
                    loaded_docs_data = json.loads(result.stdout)
                    
                    # 辞書データをDocumentオブジェクトに変換
                    loaded_count = 0
                    for doc_data in loaded_docs_data:
                        doc = Document(
                            page_content=doc_data['page_content'],
                            metadata=doc_data['metadata']
                        )
                        documents.append(doc)
                        loaded_count += 1
                        
                    loader_name = loaded_docs_data[0]['metadata'].get('loader', 'unknown')
                    print(f"    ✓ {loaded_count} pages loaded ({loader_name})")
                    
                except json.JSONDecodeError:
                    print(f"    [WARNING] Failed to parse worker output for {basename}")
            else:
                # 失敗した場合（クラッシュ含む）
                error_msg = result.stderr.strip()
                if not error_msg:
                    error_msg = "Process crashed or returned no output"
                
                print(f"    [WARNING] Failed to load {basename} (skipped)")
                # エラー詳細を表示（デバッグ用）
                # print(f"      Error: {error_msg[:200]}")
                
        except subprocess.TimeoutExpired:
            print(f"    [WARNING] Timeout while loading {basename} (skipped)")
        except Exception as e:
            print(f"    [ERROR] Unexpected error executing worker: {e}")
            
    # DOCXファイルを読み込む
    docx_files = glob.glob(os.path.join(documents_path, "*.docx"))
    for file_path in docx_files:
        try:
            print(f"  - Loading: {os.path.basename(file_path)}")
            loader = Docx2txtLoader(file_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"  [WARNING] Failed to load {file_path}: {e}")
    
    print(f"[OK] Loaded {len(documents)} documents")
    return documents

def create_vector_store(documents: List):
    """
    文書をチャンクに分割し、埋め込みを生成してFAISSベクトルストアを作成
    既にキャッシュが存在する場合はそれを再利用
    
    Args:
        documents: 読み込まれた文書のリスト
    
    Returns:
        FAISSベクトルストア
    """
    # キャッシュファイルのパス
    cache_dir = "./vectorstore_cache"
    faiss_index_path = os.path.join(cache_dir, "faiss.index")
    pkl_path = os.path.join(cache_dir, "index.pkl")
    
    # キャッシュが存在する場合は読み込む
    if os.path.exists(faiss_index_path) and os.path.exists(pkl_path):
        print("[INFO] Found cached vector store, loading...")
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
            )
            vector_store = FAISS.load_local(
                cache_dir,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print("[OK] Loaded cached vector store")
            return vector_store
        except Exception as e:
            print(f"[WARNING] Failed to load cache: {e}")
            print("[INFO] Rebuilding vector store...")
            # キャッシュが壊れている場合は削除
            try:
                os.remove(faiss_index_path)
                os.remove(pkl_path)
            except:
                pass
    
    print("[2/4] Splitting documents into chunks...")
    # テキストを重複を持たせながら分割（コンテキスト保持のため）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 各チャンクの文字数
        chunk_overlap=50,  # チャンク間の重複文字数
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    # 空のテキストやNoneを含むチャンクをフィルタリング
    filtered_chunks = []
    for chunk in chunks:
        # 文字列型であることを確認
        if (chunk.page_content and 
            isinstance(chunk.page_content, str) and 
            chunk.page_content.strip()):
            # テキストをクリーニング（制御文字や不正な文字を除去）
            cleaned_text = chunk.page_content.strip()
            # Noneや空文字列でないことを確認
            if cleaned_text and len(cleaned_text) > 0:
                chunk.page_content = cleaned_text
                filtered_chunks.append(chunk)
    
    original_count = len(chunks)
    chunks = filtered_chunks
    print(f"[OK] Created {len(chunks)} chunks (filtered from {original_count} total)")
    
    if not chunks:
        raise ValueError("No valid chunks found after filtering. Please check your documents.")
    
    print("[2/4] Loading embedding model...")
    # sentence-transformersを使用した埋め込みモデル
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
    )
    
    print("[3/4] Creating FAISS vector store...")
    # FAISSベクトルストアを作成（バッチ処理でメモリ効率を向上）
    try:
        # 大量のチャンクがある場合、バッチ処理で分割
        batch_size = 1000
        if len(chunks) > batch_size:
            print(f"  Processing {len(chunks)} chunks in batches of {batch_size}...")
            
            # バッチを検証してフィルタリングする関数
            def validate_batch(batch_chunks):
                """バッチ内のチャンクを検証し、有効なものだけを返す"""
                valid_chunks = []
                for chunk in batch_chunks:
                    # テキストが文字列型で、空でないことを確認
                    if (chunk.page_content and 
                        isinstance(chunk.page_content, str) and 
                        chunk.page_content.strip() and
                        len(chunk.page_content.strip()) > 0):
                        # 制御文字や不正な文字を除去
                        cleaned = chunk.page_content.strip()
                        # Noneや空文字列でないことを再確認
                        if cleaned:
                            chunk.page_content = cleaned
                            valid_chunks.append(chunk)
                return valid_chunks
            
            # 最初のバッチでベクトルストアを作成
            first_batch = validate_batch(chunks[:batch_size])
            if not first_batch:
                raise ValueError("No valid chunks in first batch")
            vector_store = FAISS.from_documents(first_batch, embeddings)
            
            # 残りのバッチを追加
            for i in range(batch_size, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                # バッチを検証してフィルタリング
                valid_batch = validate_batch(batch)
                if valid_batch:
                    try:
                        vector_store.add_documents(valid_batch)
                        print(f"  Processed {min(i+batch_size, len(chunks))}/{len(chunks)} chunks...")
                    except Exception as batch_error:
                        print(f"  [WARNING] Error processing batch {i//batch_size + 1}: {str(batch_error)[:100]}")
                        print(f"  Skipping this batch and continuing...")
                        continue
                else:
                    print(f"  [WARNING] Batch {i//batch_size + 1} had no valid chunks, skipping...")
        else:
            vector_store = FAISS.from_documents(chunks, embeddings)
        print("[OK] Vector store created")
        
        # キャッシュとして保存
        print("[INFO] Saving vector store to cache...")
        try:
            os.makedirs(cache_dir, exist_ok=True)
            vector_store.save_local(cache_dir)
            print("[OK] Vector store cached for future use")
        except Exception as cache_error:
            print(f"[WARNING] Failed to save cache: {cache_error}")
            print("  Vector store will be rebuilt on next run")
    except Exception as e:
        print(f"[ERROR] Failed to create vector store: {e}")
        print(f"  Number of chunks: {len(chunks)}")
        print(f"  Sample chunk content (first 100 chars): {chunks[0].page_content[:100] if chunks else 'N/A'}")
        raise
    
    return vector_store

def initialize_lm_studio():
    """
    LM Studio APIクライアントを初期化
    
    Returns:
        OpenAIクライアントインスタンス
    """
    print("[4/4] Connecting to LM Studio...")
    print(f"  Base URL: {LM_STUDIO_BASE_URL}")
    
    try:
        client = OpenAI(
            base_url=LM_STUDIO_BASE_URL,
            api_key=LM_STUDIO_API_KEY
        )
        
        # 接続テスト
        models = client.models.list()
        model_names = [model.id for model in models.data]
        
        if model_names:
            print(f"[OK] Connected to LM Studio")
            print(f"  Available models: {', '.join(model_names)}")
            return client
        else:
            print("[WARNING] No models loaded in LM Studio")
            print("  Please load a model in LM Studio and restart")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to connect to LM Studio: {e}")
        print("  Make sure LM Studio is running and server is started")
        return None

def setup_qa_chain(documents_path: str = "./documents"):
    """
    RAG QAチェーン全体をセットアップ
    
    Args:
        documents_path: ドキュメントフォルダのパス
    
    Returns:
        成功時はTrue、失敗時はFalse
    """
    global retriever, lm_studio_client, document_summary, all_documents_text
    
    print("=" * 60)
    print("RAG Search System - LM Studio Edition")
    print("=" * 60)
    
    # ステップ1: ドキュメントを読み込む
    try:
        documents = load_documents(documents_path)
    except KeyboardInterrupt:
        print("\n[INFO] Document loading interrupted by user")
        raise
    except Exception as e:
        print(f"\n[ERROR] Failed to load documents: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    if not documents:
        print("[WARNING] No documents found")
        print(f"  Place .txt, .pdf, or .docx files in {documents_path} folder")
        return False
    
    # 全ドキュメントのテキストを保存
    all_documents_text = "\n\n".join([doc.page_content for doc in documents])
    
    # ステップ2: ベクトルストアを作成
    vector_store = create_vector_store(documents)
    
    # ステップ3: Retrieverを作成
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}  # 上位5つの関連チャンクを取得（より多くの情報）
    )
    
    # ステップ4: LM Studioに接続
    lm_studio_client = initialize_lm_studio()
    
    # ステップ5: ドキュメント概要を生成（LM Studioが利用可能な場合）
    if lm_studio_client:
        document_summary = generate_document_summary(documents, lm_studio_client)
    
    print("=" * 60)
    print("[OK] Initialization complete!")
    print("=" * 60)
    
    return True

def chat(message: str, history: List) -> str:
    """
    チャット機能 - ユーザーの質問に回答（LM Studio版）
    
    Args:
        message: ユーザーからの質問
        history: チャット履歴（Gradioが自動管理）
    
    Returns:
        ボットからの回答
    """
    global retriever, lm_studio_client, document_summary
    
    if retriever is None:
        return "[ERROR] Chatbot not initialized. Please restart the app."
    
    # 特殊コマンドの処理
    if message.strip() in ["概要", "サマリー", "summary", "/概要", "/summary"]:
        if document_summary:
            return f"# 📚 ドキュメント概要\n\n{document_summary}"
        else:
            return "ドキュメント概要はまだ生成されていません。LM Studioが接続されていない可能性があります。"
    
    # 自由会話モード（/chat または /talk で開始）
    if message.strip().startswith(("/chat ", "/talk ", "雑談 ", "会話 ")):
        # プレフィックスを削除
        for prefix in ["/chat ", "/talk ", "雑談 ", "会話 "]:
            if message.strip().startswith(prefix):
                actual_message = message.strip()[len(prefix):]
                break
        
        if lm_studio_client:
            try:
                response = lm_studio_client.chat.completions.create(
                    model="local-model",
                    messages=[{"role": "user", "content": actual_message}],
                    temperature=0.8,
                    max_tokens=512,
                )
                return f"**💬 自由会話モード**\n\n{response.choices[0].message.content}"
            except Exception as e:
                return f"[ERROR] LM Studio error: {e}"
        else:
            return "自由会話モードを使うには、LM Studioを起動してサーバーを開始してください。"
    
    try:
        # ステップ1: 関連文書を検索
        docs = retriever.invoke(message)
        
        if not docs:
            return "申し訳ございません。関連する情報が見つかりませんでした。"
        
        # ステップ2: LM Studioを使用する場合
        if lm_studio_client is not None:
            # コンテキストを作成（上位5件を使用）
            context = "\n\n".join([doc.page_content for doc in docs[:5]])
            
            # プロンプトを作成（コンシェルジュ的なトーン）
            prompt = f"""あなたは技術文書検索のコンシェルジュです。お客様の「ふんわりとした質問」から、関連する技術文書の内容を見つけて、わかりやすく案内します。

以下の文書から、お客様の質問に関連する情報を探して、丁寧に説明してください。

【お客様からの質問】
{message}

【関連する技術文書の内容】
{context}

【ご案内】
上記の文書を確認したところ、"""
            
            # LM Studioで回答を生成
            try:
                response = lm_studio_client.chat.completions.create(
                    model="local-model",  # LM Studioは自動的にロード中のモデルを使用
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1024,  # より詳しい回答のために増加
                )
                
                ai_response = response.choices[0].message.content
                
                answer = f"## 💬 ご質問\n{message}\n\n"
                answer += f"## 🔍 TechScoutからのご案内\n{ai_response}\n\n"
                
                # より詳細な参照元情報を追加
                answer += "---\n\n"
                answer += "## 📚 参照した文書\n\n"
                seen_sources = {}
                for doc in docs[:5]:
                    source = doc.metadata.get('source', '不明')
                    source_name = os.path.basename(source)
                    
                    if source_name not in seen_sources:
                        seen_sources[source_name] = []
                    
                    # ページ番号を取得（PDFの場合）
                    page = doc.metadata.get('page', None)
                    preview = doc.page_content[:150].replace('\n', ' ')
                    seen_sources[source_name].append({
                        'page': page,
                        'preview': preview
                    })
                
                for source_name, chunks in seen_sources.items():
                    answer += f"### 📄 {source_name}\n"
                    if source_name.endswith('.pdf'):
                        answer += f"📍 場所: `documents/{source_name}`\n\n"
                    
                    for idx, chunk_info in enumerate(chunks, 1):
                        if chunk_info['page'] is not None:
                            answer += f"- **ページ {chunk_info['page'] + 1}**: {chunk_info['preview']}...\n"
                        else:
                            answer += f"- {chunk_info['preview']}...\n"
                    answer += "\n"
                
                return answer
                
            except Exception as llm_error:
                print(f"[ERROR] LM Studio error: {llm_error}")
                # LLMが失敗した場合は検索結果を直接表示
                pass
        
        # ステップ3: LM Studio未接続時は検索結果を整形して返す
        answer = f"## 💬 ご質問\n{message}\n\n"
        answer += f"## 🔍 TechScoutが見つけた関連情報\n\n"
        
        if lm_studio_client is None:
            answer += "_💡 LM Studioに接続すると、AIが内容を要約して回答します_\n\n"
        
        # より詳しく表示
        for i, doc in enumerate(docs[:5], 1):
            source = doc.metadata.get('source', '不明')
            source_name = os.path.basename(source)
            page = doc.metadata.get('page', None)
            
            # ページ情報付きで表示
            page_info = f" (ページ {page + 1})" if page is not None else ""
            answer += f"### 📄 関連箇所 {i}: {source_name}{page_info}\n\n"
            
            # 各ドキュメントの内容を表示
            content = doc.page_content[:600]  # 表示を増やす
            if len(doc.page_content) > 600:
                content += "..."
            
            answer += f"{content}\n\n"
        
        # ソース文書のファイルパス情報を追加
        answer += "---\n\n"
        answer += "## 📁 文書ファイルの場所\n\n"
        seen_sources = set()
        for doc in docs:
            source = doc.metadata.get('source', '不明')
            source_name = os.path.basename(source)
            if source_name not in seen_sources:
                source_path = os.path.abspath(source)
                answer += f"- **{source_name}**\n"
                answer += f"  📍 `{source_path}`\n"
                if source_name.endswith('.pdf'):
                    answer += f"  💡 エクスプローラーで開いて確認できます\n"
                answer += "\n"
                seen_sources.add(source_name)
        
        return answer
    
    except Exception as e:
        return f"[ERROR] An error occurred: {str(e)}"

def main():
    """
    Gradio UIを起動してチャットボットを実行
    """
    # documentsフォルダが存在しない場合は作成
    if not os.path.exists("./documents"):
        os.makedirs("./documents")
        print("[INFO] Created 'documents' folder")
        print("  Place your technical documents here")
    
    # QAチェーンを初期化（LM Studio版）
    setup_qa_chain("./documents")
    
    # Gradioチャットインターフェースを作成
    with gr.Blocks(title="TechScout - RAG Document Search") as demo:
        gr.Markdown(
            """
            # 🔍 TechScout
            ### RAG技術文書検索システム
            
            <div style="font-size: 0.85em; color: #666; margin-top: -15px; margin-bottom: 20px;">
            2025年11月14日<br>
            東洋電機製造株式会社<br>
            開発センター基盤技術部
            </div>
            
            技術文書について質問してください。**LM Studio上のLLM**が高品質な回答を生成します。
            
            ## ✨ 新機能
            - 📚 **ドキュメント概要自動生成** - 起動時に全文書の概要を自動作成
            - 💬 **自由会話モード** - LLMと直接会話できます
            - 🎯 **強化されたRAG検索** - より正確な回答
            
            ## 🎮 使い方
            
            ### RAG検索モード（デフォルト）
            普通に質問を入力すると、文書を検索してAIが回答します。
            ```
            例: インストール方法を教えてください
            ```
            
            ### 📚 ドキュメント概要表示
            ```
            概要
            または
            /summary
            ```
            
            ### 💬 自由会話モード
            ```
            /chat こんにちは
            雑談 今日の天気は？
            ```
            
            ## 📝 サンプル質問
            - **概要を知りたい**: 「概要」または「サマリー」
            - **インストール**: 「インストール手順を教えてください」
            - **トラブル対応**: 「エラーが出た時の対処法は？」
            - **モデル比較**: 「どのLLMモデルを使うべきですか？」
            - **設定方法**: 「セキュリティ設定について説明してください」
            - **自由会話**: 「/chat プログラミングのコツは？」
            
            ## 📊 対応ファイル形式
            - `.txt` - テキストファイル
            - `.pdf` - PDFファイル
            - `.docx` - Word文書
            
            ---
            _💡 ヒント: LM Studioが起動していない場合は検索結果のみ表示されます_
            """
        )
        
        # チャットインターフェース
        chatbot = gr.ChatInterface(
            fn=chat,
            examples=[
                "概要",
                "永久磁石同期モータの温度推定方法について教えてください",
                "誘導電動機のセンサレス制御の原理を説明してください",
                "モータ制御における回生運転とは何ですか？",
                "PMSMとIM（誘導機）の違いについて",
                "磁石温度推定における寸法ばらつきの影響は？",
                "/chat モータ制御の勉強方法を教えて",
            ],
            title="",
            description="",
            theme=gr.themes.Soft(),
        )
    
    # アプリを起動
    print("\n" + "=" * 60)
    print("Starting Gradio app...")
    print("Security enabled:")
    print(f"  - IP restriction: {', '.join(ALLOWED_IP_RANGES)}")
    print(f"  - Authentication: Enabled ({len(VALID_USERS)} users)")
    print("=" * 60)
    
    try:
        demo.launch(
            share=False,  # 公開リンクを生成しない
            server_name="0.0.0.0",  # LAN内の全てのマシンからアクセス可能
            server_port=7861,  # ポート番号（7860が使用中のため7861に変更）
            auth=authenticate_user,  # ユーザー名/パスワード認証
            auth_message="🔍 TechScout - 東洋電機製造株式会社 開発センター基盤技術部",
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        return

if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Application crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

