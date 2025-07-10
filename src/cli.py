"""Command-line interface for the Golf Rules Assistant."""
import sys
from src.rule_matcher import find_matching_rules, format_rule_response, load_rules_database

def main():
    """Run the command-line interface."""
    print("Welcome to the Golf Rules Assistant!")
    print("Ask a question about golf rules (or type 'quit' to exit):")
    
    # Load database once
    try:
        database = load_rules_database()
    except Exception as e:
        print(f"Error loading database: {e}")
        print("Please run the database creation script first: python src/create_database.py")
        sys.exit(1)
    
    while True:
        user_input = input("\nYour question: ")
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Thank you for using the Golf Rules Assistant!")
            sys.exit(0)
        
        # Find matching rules
        matches = find_matching_rules(user_input, database)
        
        # Format and display response
        response = format_rule_response(matches)
        print("\n" + response)

if __name__ == "__main__":
    main()
