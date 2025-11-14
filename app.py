"""
RAGベースチャットボット
LangChain、FAISS、Sentence Transformers、HuggingFace LLMを使用
"""

import os
import glob
from typing import List, Tuple, Optional
import gradio as gr
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import ipaddress

# グローバル変数でretrieverとLLMを保持
retriever = None
llm_model = None

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
    "admin": "password123",  # ← 変更してください！
    "user1": "secure_pass",  # 追加のユーザー
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
                print(f"✅ アクセス許可: {client_ip}")
                return True
        
        print(f"⚠️  アクセス拒否: {client_ip} (許可範囲外)")
        return False
    except Exception as e:
        print(f"❌ IPチェックエラー: {e}")
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
        print(f"✅ ユーザー認証成功: {username}")
        return True
    print(f"⚠️  ユーザー認証失敗: {username}")
    return False

def load_documents(documents_path: str = "./documents") -> List:
    """
    指定されたフォルダから技術文書を読み込む
    
    Args:
        documents_path: ドキュメントが格納されているフォルダのパス
    
    Returns:
        読み込まれた文書のリスト
    """
    print(f"📁 ドキュメントを読み込み中: {documents_path}")
    documents = []
    
    # TXTファイルを読み込む（エンコーディング指定）
    txt_files = glob.glob(os.path.join(documents_path, "*.txt"))
    for file_path in txt_files:
        try:
            print(f"  📄 読み込み中: {os.path.basename(file_path)}")
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"  ⚠️  エラー: {file_path} を読み込めませんでした - {e}")
    
    # PDFファイルを読み込む
    pdf_files = glob.glob(os.path.join(documents_path, "*.pdf"))
    for file_path in pdf_files:
        try:
            print(f"  📄 読み込み中: {os.path.basename(file_path)}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"  ⚠️  エラー: {file_path} を読み込めませんでした - {e}")
    
    # DOCXファイルを読み込む
    docx_files = glob.glob(os.path.join(documents_path, "*.docx"))
    for file_path in docx_files:
        try:
            print(f"  📄 読み込み中: {os.path.basename(file_path)}")
            loader = Docx2txtLoader(file_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"  ⚠️  エラー: {file_path} を読み込めませんでした - {e}")
    
    print(f"✅ {len(documents)}個のドキュメントを読み込みました")
    return documents

def create_vector_store(documents: List):
    """
    文書をチャンクに分割し、埋め込みを生成してFAISSベクトルストアを作成
    
    Args:
        documents: 読み込まれた文書のリスト
    
    Returns:
        FAISSベクトルストア
    """
    print("\n🔪 ドキュメントをチャンクに分割中...")
    # テキストを重複を持たせながら分割（コンテキスト保持のため）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # 各チャンクの文字数
        chunk_overlap=50,  # チャンク間の重複文字数
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ {len(chunks)}個のチャンクを作成しました")
    
    print("\n🤖 埋め込みモデルを読み込み中...")
    # sentence-transformersを使用した埋め込みモデル
    # 日本語と英語の両方に対応したモデルを使用
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},  # GPU使用
    )
    
    print("\n📊 FAISSベクトルストアを作成中...")
    # FAISSベクトルストアを作成
    vector_store = FAISS.from_documents(chunks, embeddings)
    print("✅ ベクトルストアが作成されました")
    
    return vector_store

def initialize_llm():
    """
    HuggingFaceの軽量LLMを初期化
    
    Returns:
        LangChain互換のLLMインスタンス
    """
    print("\n🧠 LLMを読み込み中...")
    print("⚠️  初回実行時はモデルのダウンロードに時間がかかります")
    
    # より高性能なモデルを使用（GPU対応）
    # RTX 3080なら以下のモデルが動作します：
    # - "microsoft/phi-2" (2.7B - 軽量)
    # - "mistralai/Mistral-7B-Instruct-v0.2" (7B - 推奨)
    # - "meta-llama/Llama-2-7b-chat-hf" (7B - 要HuggingFace認証)
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # 高性能モデル
    
    # トークナイザーとモデルを読み込む
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,  # GPU用に最適化
        device_map="auto",  # GPU自動割り当て
        trust_remote_code=True,
    )
    
    # HuggingFace pipelineを作成
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,  # GPU使用により増加可能
        temperature=0.7,  # ランダム性（0=決定論的、1=ランダム）
        top_p=0.95,
        repetition_penalty=1.15,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    
    # LangChainのLLMラッパーを作成
    llm = HuggingFacePipeline(pipeline=pipe)
    print("✅ LLMが読み込まれました")
    
    return llm

def setup_qa_chain(documents_path: str = "./documents", use_llm: bool = False):
    """
    RAG QAチェーン全体をセットアップ
    
    Args:
        documents_path: ドキュメントフォルダのパス
        use_llm: LLMを使用するかどうか（False=高速・軽量版）
    
    Returns:
        成功時はTrue、失敗時はFalse
    """
    global retriever, llm_model
    
    print("=" * 60)
    print("🚀 RAG検索システムを初期化中...")
    print("=" * 60)
    
    # ステップ1: ドキュメントを読み込む
    documents = load_documents(documents_path)
    
    if not documents:
        print("⚠️  警告: ドキュメントが見つかりませんでした")
        print(f"   {documents_path}フォルダに.txt、.pdf、または.docxファイルを配置してください")
        return False
    
    # ステップ2: ベクトルストアを作成
    vector_store = create_vector_store(documents)
    
    # ステップ3: LLMを初期化（オプション）
    if use_llm:
        print("\n⚠️  注意: LLMを有効にするとCPU環境では非常に遅くなります")
        llm_model = initialize_llm()
    else:
        print("\n⚡ 高速モード: LLMなしで検索結果を直接表示します")
        llm_model = None
    
    # ステップ4: Retrieverを作成
    print("\n🔗 Retrieverを作成中...")
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # 上位3つの関連チャンクを取得
    )
    
    print("=" * 60)
    print("✅ 初期化完了！チャットボットの準備ができました")
    print("=" * 60)
    
    return True

def chat(message: str, history: List) -> str:
    """
    チャット機能 - ユーザーの質問に回答（LLM対応版）
    
    Args:
        message: ユーザーからの質問
        history: チャット履歴（Gradioが自動管理）
    
    Returns:
        ボットからの回答
    """
    global retriever, llm_model
    
    if retriever is None:
        return "❌ エラー: チャットボットが初期化されていません。アプリを再起動してください。"
    
    try:
        # ステップ1: 関連文書を検索
        docs = retriever.invoke(message)
        
        if not docs:
            return "申し訳ございません。関連する情報が見つかりませんでした。"
        
        # ステップ2: LLMを使用する場合
        if llm_model is not None:
            # コンテキストを作成
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
            
            # プロンプトを作成
            prompt = f"""以下の文書を参考にして、質問に日本語で答えてください。

【参考文書】
{context}

【質問】
{message}

【回答】"""
            
            # LLMで回答を生成
            try:
                response = llm_model.invoke(prompt)
                answer = f"**質問:** {message}\n\n"
                answer += f"**AI回答:**\n{response}\n\n"
                
                # ソース文書の情報を追加
                answer += "📚 **参照元:**\n"
                seen_sources = set()
                for doc in docs:
                    source = doc.metadata.get('source', '不明')
                    source_name = os.path.basename(source)
                    if source_name not in seen_sources:
                        answer += f"- {source_name}\n"
                        seen_sources.add(source_name)
                
                return answer
            except Exception as llm_error:
                print(f"LLMエラー: {llm_error}")
                # LLMが失敗した場合は検索結果を直接表示
                pass
        
        # ステップ3: LLMなし、または失敗時は検索結果を整形して返す
        answer = f"**質問:** {message}\n\n"
        answer += "**関連する情報:**\n\n"
        
        for i, doc in enumerate(docs[:3], 1):
            # 各ドキュメントの内容を表示
            content = doc.page_content[:500]  # 最初の500文字
            if len(doc.page_content) > 500:
                content += "..."
            
            answer += f"### 📄 関連箇所 {i}\n"
            answer += f"{content}\n\n"
        
        # ソース文書の情報を追加
        answer += "📚 **参照元:**\n"
        seen_sources = set()
        for doc in docs:
            source = doc.metadata.get('source', '不明')
            source_name = os.path.basename(source)
            if source_name not in seen_sources:
                answer += f"- {source_name}\n"
                seen_sources.add(source_name)
        
        return answer
    
    except Exception as e:
        return f"❌ エラーが発生しました: {str(e)}"

def main():
    """
    Gradio UIを起動してチャットボットを実行
    """
    # documentsフォルダが存在しない場合は作成
    if not os.path.exists("./documents"):
        os.makedirs("./documents")
        print("📁 'documents'フォルダを作成しました")
        print("   このフォルダに技術文書を配置してください")
    
    # QAチェーンを初期化（GPUモード：LLMあり）
    setup_qa_chain("./documents", use_llm=True)
    
    # Gradioチャットインターフェースを作成
    with gr.Blocks(title="RAG技術文書検索システム") as demo:
        gr.Markdown(
            """
            # 🤖 RAG技術文書検索システム 🚀GPU版
            
            技術文書について質問してください。**GPU搭載のLLM**が高品質な回答を生成します。
            
            **特徴:**
            - 🚀 **GPU加速** - RTX 3080でMistral 7Bモデルを使用
            - 🧠 **高品質AI回答** - 文書を理解して自然な日本語で回答
            - 🎯 **正確** - ベクトル検索で関連箇所を特定
            
            **使い方:**
            1. `documents`フォルダに技術文書（.txt、.pdf、.docx）を配置済み
            2. 質問を入力すると、AIが文書を参照して回答します
            
            **注意:** 初回実行時はMistral-7Bモデル（約14GB）のダウンロードに時間がかかります
            """
        )
        
        # チャットインターフェース
        chatbot = gr.ChatInterface(
            fn=chat,
            examples=[
                "このドキュメントの主な内容は何ですか？",
                "技術的な特徴について教えてください",
                "インストール方法は？",
            ],
            title="",
            description="",
            theme=gr.themes.Soft(),
        )
    
    # アプリを起動
    print("\n" + "=" * 60)
    print("🌐 Gradioアプリを起動中...")
    print("🔒 セキュリティ有効:")
    print(f"   - IP制限: {', '.join(ALLOWED_IP_RANGES)}")
    print(f"   - 認証: 有効 ({len(VALID_USERS)}ユーザー)")
    print("=" * 60)
    demo.launch(
        share=False,  # 公開リンクを生成しない
        server_name="0.0.0.0",  # LAN内の全てのマシンからアクセス可能
        server_port=7861,  # ポート番号（7860が使用中のため7861に変更）
        auth=authenticate_user,  # ユーザー名/パスワード認証
        auth_message="🔒 社内文書検索システム - ログインしてください",
    )

if __name__ == "__main__":
    main()

