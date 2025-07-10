"""Golf Rules Assistant using LLM API (OpenAI 1.0+ compatible)."""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_golf_rule_interpretation(question):
    """Use LLM to interpret a golf rule question."""
    try:
        # Create a prompt with context about golf rules
        prompt = f"""You are an expert golf rules official. Interpret the following situation 
according to the official USGA/R&A Rules of Golf (2023 edition).

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

        # Send request to OpenAI API using the new format
        response = client.chat.completions.create(
            model="gpt-4",  # Or "gpt-3.5-turbo" for a cheaper but less capable option
            messages=[
                {"role": "system", "content": "You are an expert golf rules official. Provide accurate rule interpretations with proper citations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent, factual responses
        )
        
        # Extract the response using the new format
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error getting rule interpretation: {str(e)}"

def main():
    """Run the interactive assistant."""
    print("Welcome to the Golf Rules Assistant!")
    print("Ask a question about a golf rule situation (or type 'quit' to exit):")
    
    while True:
        user_input = input("\nYour question: ")
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Thank you for using the Golf Rules Assistant!")
            break
        
        # Get interpretation from LLM
        response = get_golf_rule_interpretation(user_input)
        
        # Display response
        print("\n" + response)

if __name__ == "__main__":
    main()

