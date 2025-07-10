"""Hybrid Golf Rules Assistant combining vector search with LLM interpretation."""
import os
from openai import OpenAI
from dotenv import load_dotenv
from vector_search import RulesVectorSearch

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize vector search
search_engine = RulesVectorSearch()

def get_hybrid_interpretation(question):
    """Get a golf rule interpretation using the hybrid approach."""
    try:
        # Step 1: Find relevant rules using vector search
        search_results = search_engine.search(question, top_n=2)
        
        # Check if we found any relevant rules
        if not search_results:
            return "I couldn't find any relevant rules for your question. Could you provide more details about the situation?"
        
        # Step 2: Format relevant rules for the LLM
        relevant_rules_text = ""
        for result in search_results:
            rule = result['rule']
            relevant_rules_text += f"Rule {rule['id']}: {rule['title']}\n{rule['text']}\n\n"
        
        # Step 3: Use LLM to interpret the question with context from relevant rules
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

        # Send request to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo" for a cheaper but less capable option
            messages=[
                {"role": "system", "content": "You are an expert golf rules official providing accurate rule interpretations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent, factual responses
        )
        
        # Extract the response
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error getting rule interpretation: {str(e)}"

def main():
    """Run the interactive assistant."""
    print("Welcome to the Hybrid Golf Rules Assistant!")
    print("This assistant combines vector search with LLM interpretation.")
    print("Ask a question about a golf rule situation (or type 'quit' to exit):")
    
    while True:
        user_input = input("\nYour question: ")
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Thank you for using the Golf Rules Assistant!")
            break
        
        # Get interpretation from hybrid system
        response = get_hybrid_interpretation(user_input)
        
        # Display response
        print("\n" + response)

if __name__ == "__main__":
    main()
