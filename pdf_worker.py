import sys
import os
import json
import warnings
import traceback

# エンコーディング設定
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def load_single_pdf(file_path):
    """
    単一のPDFファイルを読み込んでJSON形式で返す
    """
    documents = []
    
    try:
        # pdfplumberを優先
        import pdfplumber
        import re
        
        # 特定の警告を無視
        warnings.filterwarnings('ignore')
        
        loaded = False
        
        try:
            pdf_docs = []
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text()
                        if text:
                            text = text.replace('\x00', '').strip()
                            text = re.sub(r'\s+', ' ', text).strip()
                            if text:
                                doc_data = {
                                    'page_content': text,
                                    'metadata': {
                                        'source': file_path,
                                        'page': page_num,
                                        'total_pages': total_pages,
                                        'loader': 'pdfplumber'
                                    }
                                }
                                pdf_docs.append(doc_data)
                    except Exception:
                        pass
            
            if pdf_docs:
                documents.extend(pdf_docs)
                loaded = True
                
        except Exception as e:
            # pdfplumberでの失敗はstderrに出力して続行
            sys.stderr.write(f"pdfplumber failed: {str(e)}\n")
        
        # pdfplumberでダメならPyPDFLoaderを試す
        if not loaded:
            try:
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                
                for doc in docs:
                    # PyPDFの結果をシリアライズ可能な辞書に変換
                    doc_data = {
                        'page_content': doc.page_content,
                        'metadata': doc.metadata
                    }
                    doc_data['metadata']['loader'] = 'PyPDFLoader'
                    documents.append(doc_data)
                
                if documents:
                    loaded = True
                    
            except Exception as e:
                sys.stderr.write(f"PyPDFLoader failed: {str(e)}\n")
    
        # 結果をJSONとして標準出力に出力
        if documents:
            print(json.dumps(documents, ensure_ascii=False))
            return 0
        else:
            sys.stderr.write("No text content extracted\n")
            return 1

    except Exception as e:
        sys.stderr.write(f"Unexpected error in worker: {str(e)}\n")
        sys.stderr.write(traceback.format_exc())
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python pdf_worker.py <pdf_file_path>\n")
        sys.exit(1)
        
    file_path = sys.argv[1]
    sys.exit(load_single_pdf(file_path))

