"""Module for matching user questions to golf rules."""
import json
from src.config import RULES_FILE, SIMILARITY_THRESHOLD, MAX_RESULTS
from src.text_processor import calculate_similarity, extract_keywords, preprocess_text

def load_rules_database():
    """Load the rules database from JSON file."""
    with open(RULES_FILE, 'r') as f:
        return json.load(f)

def find_matching_rules(question, database=None):
    """Find rules that match the user's question."""
    if database is None:
        database = load_rules_database()
    
    # Extract keywords from the question
    question_keywords = extract_keywords(question)
    preprocessed_question = preprocess_text(question)
    
    matches = []
    
    # Check each rule for matches
    for rule in database["rules"]:
        # Calculate similarity scores
        keyword_overlap = len(set(question_keywords) & set(rule["keywords"])) / max(len(question_keywords), 1)
        
        # Check examples for direct matches
        example_scores = []
        for example in rule["examples"]:
            similarity = calculate_similarity(question, example["question"])
            example_scores.append(similarity)
        
        # Use the best example match if available
        example_score = max(example_scores) if example_scores else 0
        
        # Calculate overall score (weighted combination)
        overall_score = 0.3 * keyword_overlap + 0.7 * example_score
        
        if overall_score >= SIMILARITY_THRESHOLD:
            matches.append({
                "rule": rule,
                "score": overall_score
            })
    
    # Sort by score and limit results
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:MAX_RESULTS]

def format_rule_response(matches):
    """Format the rule matches into a readable response."""
    if not matches:
        return "I couldn't find a specific rule that addresses your question. Could you provide more details?"
    
    # Format the top match
    top_match = matches[0]
    rule = top_match["rule"]
    
    response = f"According to {rule['title']}:\n\n{rule['text']}\n\n"
    
    # Add example if available
    if rule["examples"]:
        response += f"For example: {rule['examples'][0]['answer']}\n\n"
    
    # Add related rules
    if rule["related_rules"]:
        response += f"You might also want to check: {', '.join(rule['related_rules'])}"
    
    return response
