"""Production Golf Rules Assistant combining vector search with LLM interpretation."""
import os
import time
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from vector_search import ClubSpecificVectorSearch

# Suppress tokenizer warnings for production
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize vector search
search_engine = ClubSpecificVectorSearch(club_id='columbia_cc')

def log_usage(tokens_used, cost, question_preview):
    """Simple usage logging for production monitoring."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens_used,
            "cost": round(cost, 4),
            "question_preview": question_preview[:50] + "..." if len(question_preview) > 50 else question_preview
        }
        
        # Append to usage log file
        with open("usage_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass  # Don't let logging errors break the main function

def get_hybrid_interpretation(question, verbose=False, use_compression=True):
    """Get a golf rule interpretation using the hybrid approach."""
    try:
        # Step 1: Find relevant rules using vector search
        if verbose:
            print("\n🔍 Performing vector search...")
            search_start = time.time()
            
        import re
        hole_match = re.search(r'\b(\d{1,2})(?:th|st|nd|rd)?\s+hole\b', question.lower())
        hole_number = int(hole_match.group(1)) if hole_match else None

        search_results = search_engine.search_with_precedence(question, hole_number=hole_number, top_n=2)

        if verbose:
            search_end = time.time()
            search_time = round(search_end - search_start, 2)
            print(f"✓ Vector search completed in {search_time} seconds")
        
        # Check if we found any relevant rules
        if not search_results:
            if verbose:
                print("❌ No relevant rules found. Using LLM without rule context.")
            
            # Use LLM without specific rule context
            prompt = f"""You are an expert golf rules official. Interpret the following situation 
according to the official USGA/R&A Rules of Golf (2023 edition).

Since I couldn't find specific rules that match this query, please provide your best 
understanding of the applicable rules. If this is a specialized or uncommon situation,
please indicate that and suggest where the player might look for more definitive guidance.

Situation: {question}

Be concise but thorough. If the situation is ambiguous, explain what additional 
information would help clarify the ruling.
"""
            
            if verbose:
                print("\n🧠 Consulting LLM (without specific rule context)...")
                llm_start = time.time()
                
            # Send request to OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert golf rules official providing accurate rule interpretations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            result = response.choices[0].message.content
            
            if verbose:
                llm_end = time.time()
                llm_time = round(llm_end - llm_start, 2)
                print(f"✓ LLM response received in {llm_time} seconds")
                print(f"📊 Tokens used: {response.usage.total_tokens}")
                print("💡 Source: LLM knowledge only (no specific rules matched)")
            
            # Log usage
            if response.usage:
                total_cost = (response.usage.prompt_tokens * 0.01 + response.usage.completion_tokens * 0.03) / 1000
                log_usage(response.usage.total_tokens, total_cost, question)
            
            return result
        
        # Step 2: Build context - COMPRESSED vs DETAILED
        if use_compression:
            if verbose:
                print("\n📋 Building compressed context...")
            relevant_rules_text = search_engine.get_compressed_context_for_llm(search_results, question)
            prompt_type = "compressed"
        else:
            if verbose:
                print("\n📋 Building detailed context...")
            relevant_rules_text = _build_detailed_context(search_results, verbose)
            prompt_type = "detailed"
        
        # Step 3: Create optimized prompt
        if use_compression:
            prompt = f"""Golf rules context:
{relevant_rules_text}

Question: {question}

Provide:
1. Direct answer
2. Applicable rule number  
3. Key procedure (if relief/penalty involved)

Keep response under 150 words unless situation requires detailed steps."""
        else:
            # Original detailed prompt
            prompt = f"""You are an expert golf rules official. Interpret the following situation 
according to the official USGA/R&A Rules of Golf (2023 edition).

Based on these relevant rules:

{relevant_rules_text}

For your response:
First, if possible, provide a concise answer to the question. Sometimes the user will ask "what do I do if... [then explains a situation]?" For the concise answer to this type of question, either explain the only rule-based solution, or explain that the user has options, if multiple solutions exist.  Then, if applicable,:
1. Identify the applicable rule number
2. Explain the relevant part of the rule
3. Provide a clear procedure for the golfer to follow
4. Include any free relief or penalty options

Situation: {question}

Be concise but thorough. If the situation is ambiguous, explain what additional 
information would help clarify the ruling.
"""

        if verbose:
            print(f"\n🧠 Consulting LLM ({prompt_type} context)...")
            print(f"📏 Prompt length: {len(prompt)} characters")
            llm_start = time.time()
        
        # Send request with token limiting
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert golf rules official providing accurate rule interpretations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200 if use_compression else None
        )
        
        result = response.choices[0].message.content
        
        if verbose:
            llm_end = time.time()
            llm_time = round(llm_end - llm_start, 2)
            print(f"✓ LLM response received in {llm_time} seconds")
            print(f"📊 Tokens used: {response.usage.total_tokens}")
            print(f"💡 Source: Vector search + LLM interpretation ({prompt_type})")
        
        # Log usage
        if response.usage:
            total_cost = (response.usage.prompt_tokens * 0.01 + response.usage.completion_tokens * 0.03) / 1000
            log_usage(response.usage.total_tokens, total_cost, question)
        
        return result
    
    except Exception as e:
        if verbose:
            print(f"\nError in get_hybrid_interpretation: {str(e)}")
            import traceback
            traceback.print_exc()
        return f"Error getting rule interpretation: {str(e)}"

def _build_detailed_context(search_results, verbose):
    """Build detailed context (original method) for comparison."""
    try:
        if verbose:
            print("\nBuilding detailed rules text...")
            
        relevant_rules_text = ""
        for i, result in enumerate(search_results):
            rule = result['rule']
            similarity = result['best_similarity']
            
            if verbose:
                print(f"Processing rule {rule['id']}...")
            
            # Add the basic rule information
            relevant_rules_text += f"Rule {rule['id']}: {rule['title']}\n{rule['text']}\n\n"
            
            # Add condition details if available
            if 'conditions' in rule:
                if verbose:
                    print(f"Rule has conditions. Processing {len(rule['conditions'])} conditions...")
                    
                relevant_rules_text += "Specific situations covered by this rule:\n"
                for idx, cond in enumerate(rule['conditions']):
                    if verbose:
                        print(f"Processing condition {idx+1}...")
                        
                    relevant_rules_text += f"- {cond['situation']}: {cond['explanation']}\n"
                relevant_rules_text += "\n"
            
            if verbose:
                similarity_percent = round(similarity * 100, 1)
                print(f"  {i+1}. Rule {rule['id']} - {rule['title']} (Similarity: {similarity_percent}%)")
                
        return relevant_rules_text
        
    except Exception as e:
        if verbose:
            print(f"Error building detailed context: {str(e)}")
        raise

def compare_compression(question):
    """Compare compressed vs detailed versions for testing."""
    print(f"🧪 TESTING COMPRESSION FOR: {question}\n")
    
    print("🔥 COMPRESSED VERSION:")
    print("-" * 30)
    compressed_result = get_hybrid_interpretation(question, verbose=True, use_compression=True)
    
    print("\n" + "🐌 DETAILED VERSION:")
    print("-" * 30)  
    detailed_result = get_hybrid_interpretation(question, verbose=True, use_compression=False)
    
    print(f"\n📝 RESPONSE COMPARISON:")
    print(f"Compressed: {compressed_result[:100]}...")
    print(f"Detailed: {detailed_result[:100]}...")

def main():
    """Run the production golf rules assistant."""
    print("🏌️ Golf Rules Assistant - Production Mode")
    print("="*50)
    print("Optimized for cost efficiency with vector search + LLM")
    print("Compression enabled for 65-70% cost savings")
    print("="*50)
    
    while True:
        try:
            # Get user input
            question = input("\n❓ Enter your golf rules question (or 'quit' to exit): ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Golf Rules Assistant!")
                break
                
            if not question:
                print("Please enter a question.")
                continue
            
            # Get interpretation (compressed by default, minimal output)
            print("\n🔍 Looking up rules...")
            result = get_hybrid_interpretation(question, verbose=False, use_compression=True)
            
            print(f"\n📋 **Answer:**")
            print(result)
            print("\n" + "-"*50)
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Golf Rules Assistant!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try rephrasing your question.")

# Development/Testing functions
def run_test_suite():
    """Run comprehensive tests for development."""
    test_questions = [
        "My ball is in casual water in a bunker, what are my options?",
        "During a tournament, my ball hit another player's ball that was at rest on the green. Both balls moved. What happens next and are there any penalties?",
        "In match play, I accidentally marked my opponent's ball on the green. What do we do?"
    ]
    
    print("🧪 RUNNING COMPRESSION TEST SUITE")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔬 TEST {i}: {question}")
        print("-"*60)
        compare_compression(question)
        print("\n" + "="*60)
    
    print("🏁 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    # Production mode by default
    # Uncomment the line below to run tests instead:
    # run_test_suite()
    
    main()
