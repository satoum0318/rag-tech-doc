"""
PDFファイルが正しく読み込まれているかテストするスクリプト
"""
import glob
import os
from langchain_community.document_loaders import PyPDFLoader

print("=" * 60)
print("PDF Loading Test")
print("=" * 60)
print()

documents_path = "./documents"
pdf_files = glob.glob(os.path.join(documents_path, "*.pdf"))

print(f"Found {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {os.path.basename(pdf)}")

print()
print("Testing PDF loading...")
print("-" * 60)

total_pages = 0
total_chars = 0

for pdf_path in pdf_files:
    filename = os.path.basename(pdf_path)
    print(f"\nProcessing: {filename}")
    
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        pages = len(docs)
        chars = sum(len(doc.page_content) for doc in docs)
        
        print(f"  [OK] Loaded successfully!")
        print(f"  Pages: {pages}")
        print(f"  Total characters: {chars:,}")
        print(f"  First 200 chars: {docs[0].page_content[:200]}...")
        
        total_pages += pages
        total_chars += chars
        
    except Exception as e:
        print(f"  [ERROR] Failed to load: {e}")

print()
print("=" * 60)
print("Summary:")
print(f"  Total pages loaded: {total_pages}")
print(f"  Total characters: {total_chars:,}")
print("=" * 60)

if total_pages > 0:
    print()
    print("[OK] PDFs can be loaded successfully!")
    print("The RAG system should be able to search these documents.")
else:
    print()
    print("[ERROR] No PDFs were loaded!")
    print("Please check the error messages above.")

