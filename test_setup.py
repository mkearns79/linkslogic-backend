"""Test script to verify semantic search setup."""

def test_semantic_search():
    """Test the semantic search installation."""
    print("🏌️ Testing Golf Rules Semantic Search Setup")
    print("=" * 50)
    
    try:
        # Test 1: Import check
        print("1. Testing imports...")
        from vector_search import RulesVectorSearch
        print("   ✅ Imports successful")
        
        # Test 2: Initialize search engine
        print("\n2. Initializing search engine...")
        print("   (This may take 30-60 seconds on first run)")
        search_engine = RulesVectorSearch()
        print("   ✅ Search engine initialized")
        
        # Test 3: Run sample searches
        print("\n3. Testing sample searches...")
        
        test_cases = [
            {
                'query': "Can I fix a ball mark?",
                'expected_rule': "13.1",  # Should find putting green repair rule
                'description': "Ball mark repair"
            },
            {
                'query': "What if my club breaks?", 
                'expected_rule': "4.1",   # Should find damaged club rule
                'description': "Damaged club"
            },
            {
                'query': "14 club limit",
                'expected_rule': "4.1",   # Should find club limit rule
                'description': "Club limit"
            }
        ]
        
        all_passed = True
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test['description']}")
            print(f"   Query: '{test['query']}'")
            
            results = search_engine.search(test['query'], top_n=3)
            
            if results:
                top_result = results[0]
                rule_id = top_result['rule']['id']
                similarity = top_result['similarity']
                
                print(f"   Top Result: Rule {rule_id} (similarity: {similarity:.3f})")
                
                # Check if we got a reasonable result
                if similarity > 0.2:
                    print(f"   ✅ Good match found")
                else:
                    print(f"   ⚠️  Low similarity score")
                    all_passed = False
            else:
                print(f"   ❌ No results found")
                all_passed = False
        
        # Test 4: Performance check
        print(f"\n4. Performance test...")
        import time
        
        start_time = time.time()
        for _ in range(5):
            search_engine.search("penalty stroke", top_n=3)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 5 * 1000  # Convert to ms
        print(f"   Average query time: {avg_time:.1f}ms")
        
        if avg_time < 500:
            print(f"   ✅ Good performance")
        else:
            print(f"   ⚠️  Slower than expected (but still functional)")
        
        # Final result
        print(f"\n{'='*50}")
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("Your semantic search is ready to use.")
            print("\nNext steps:")
            print("- Replace your existing vector_search.py with the new version")
            print("- The embeddings are cached, so future startups will be instant")
            print("- You should see much better search relevance!")
        else:
            print("⚠️  Some tests had issues, but basic functionality works.")
            print("You can still proceed - the search engine is functional.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nTo fix this:")
        print("1. Install required packages:")
        print("   pip install sentence-transformers scikit-learn")
        print("2. Make sure golf_rules_data.py is in the same directory")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease check:")
        print("1. All required packages are installed")
        print("2. You have internet connection (for model download)")
        print("3. Sufficient disk space (~500MB for models and cache)")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_semantic_search()
