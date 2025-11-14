"""
PDFの内容が正しく抽出されているかテスト
"""
import os
import sys
from langchain_community.document_loaders import PyPDFLoader

# UTF-8出力設定
sys.stdout.reconfigure(encoding='utf-8')

pdf_files = [
    "./documents/埋込磁石同期モータの寸法ばらつきが磁石温度推定に与える影響.pdf",
    "./documents/誘導電動機の速度センサレスベクトル制御における回生運転の高トルク制御法.pdf"
]

print("=" * 80)
print("PDF Content Extraction Test")
print("=" * 80)
print()

for pdf_path in pdf_files:
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        continue
    
    print(f"Testing: {os.path.basename(pdf_path)}")
    print("-" * 80)
    
    try:
        loader = PyPDFLoader(pdf_path, extract_images=False)
        docs = loader.load()
        
        print(f"[OK] Pages loaded: {len(docs)}")
        
        # 最初のページの内容をチェック
        if docs:
            first_page = docs[0].page_content
            
            # クリーニング
            import re
            first_page = first_page.replace('\x00', '')
            first_page = re.sub(r'\s+', ' ', first_page)
            first_page = first_page.strip()
            
            print(f"\nFirst page content (first 500 chars):")
            print(first_page[:500])
            print()
            
            # キーワード検索テスト
            keywords = ['永久磁石', '同期モータ', '温度', '推定', '誘導電動機', 'センサレス', 'ベクトル', '制御']
            found_keywords = [kw for kw in keywords if kw in ' '.join([doc.page_content for doc in docs])]
            
            if found_keywords:
                print(f"[OK] Found keywords: {', '.join(found_keywords)}")
            else:
                print("[WARNING] No Japanese keywords found - possible encoding issue")
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    
    print()

print("=" * 80)

