"""
pdfplumberでPDFが正しく読み込めるかテスト
"""
import pdfplumber
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_files = [
    "./documents/埋込磁石同期モータの寸法ばらつきが磁石温度推定に与える影響.pdf",
]

print("=" * 80)
print("pdfplumber Test - Japanese PDF")
print("=" * 80)
print()

for pdf_path in pdf_files:
    print(f"Testing: {pdf_path}")
    print("-" * 80)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"[OK] Total pages: {len(pdf.pages)}")
            
            # 最初のページを抽出
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            
            if text:
                # クリーニング
                import re
                text = text.replace('\x00', '')
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
                
                print(f"\n[OK] First page extracted successfully")
                print(f"Length: {len(text)} characters")
                print(f"\nFirst 500 characters:")
                print("-" * 80)
                print(text[:500])
                print("-" * 80)
                
                # 日本語キーワードチェック
                keywords = ['永久磁石', '同期モータ', '温度', '推定', 'PMSM', 'モータ']
                found = [kw for kw in keywords if kw in text]
                
                if found:
                    print(f"\n[OK] Found keywords: {', '.join(found)}")
                else:
                    # 全ページをチェック
                    all_text = ' '.join([page.extract_text() or '' for page in pdf.pages])
                    found = [kw for kw in keywords if kw in all_text]
                    if found:
                        print(f"\n[OK] Found keywords in document: {', '.join(found)}")
                    else:
                        print(f"\n[WARNING] No Japanese keywords found")
                        print("Checking for English...")
                        eng_keywords = ['magnet', 'temperature', 'motor', 'permanent']
                        eng_found = [kw for kw in eng_keywords if kw.lower() in all_text.lower()]
                        if eng_found:
                            print(f"[OK] Found English keywords: {', '.join(eng_found)}")
            else:
                print("[ERROR] No text extracted")
                
    except Exception as e:
        print(f"[ERROR] {e}")

print()
print("=" * 80)

