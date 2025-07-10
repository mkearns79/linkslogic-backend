# test_clean.py
from golf_rules_hybrid_clean import get_clean_interpretation

# Test a few different scenarios
test_questions = [
    "My ball is lost in the woods",  # Should use template
    "Can I get relief from aeration holes?",  # Should use template  
    "What happens if my ball is in the water on hole 17?",  # Should use template
    "Can I ground my club in a bunker?"  # Should use full system (no template)
]

print("🧪 Testing Clean Golf Rules System")
print("="*50)

for i, question in enumerate(test_questions, 1):
    print(f"\n{i}. Question: {question}")
    print("-" * 40)
    
    try:
        answer = get_clean_interpretation(question, fast_mode=True)
        print(f"Answer: {answer[:100]}...")  # Just first 100 chars
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n🏁 Test complete!")
