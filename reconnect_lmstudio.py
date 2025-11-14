"""
LM Studio接続テストスクリプト
"""
from openai import OpenAI

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"

def test_lm_studio_connection():
    """LM Studioへの接続をテスト"""
    print("=" * 60)
    print("LM Studio Connection Test")
    print("=" * 60)
    
    try:
        client = OpenAI(
            base_url=LM_STUDIO_BASE_URL,
            api_key="lm-studio"
        )
        
        # 利用可能なモデルを取得
        print("\n[1/2] Checking available models...")
        models = client.models.list()
        model_names = [model.id for model in models.data]
        
        if model_names:
            print(f"[OK] Connected to LM Studio!")
            print(f"[OK] Available models: {', '.join(model_names)}")
            
            # テストメッセージ送信
            print("\n[2/2] Testing chat completion...")
            response = client.chat.completions.create(
                model="local-model",
                messages=[
                    {"role": "user", "content": "こんにちは"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            print(f"[OK] Test response: {reply}")
            print("\n" + "=" * 60)
            print("✅ LM Studio is ready!")
            print("=" * 60)
            return True
        else:
            print("[ERROR] No models loaded in LM Studio")
            print("Please load a model in LM Studio Chat tab")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        print("\nPlease check:")
        print("  1. LM Studio is running")
        print("  2. A model is loaded")
        print("  3. Server is started (Local Server tab)")
        return False

if __name__ == "__main__":
    test_lm_studio_connection()

