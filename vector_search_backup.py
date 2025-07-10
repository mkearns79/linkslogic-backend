"""Vector-based search for golf rules."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import our rules database
from golf_rules_data import RULES_DATABASE

class RulesVectorSearch:
    """Search engine for golf rules using TF-IDF vectors."""
    
    def __init__(self):
        """Initialize the vector search engine."""
        try:
            # Prepare documents for vectorization
            self.rules = RULES_DATABASE
            self.documents = []
            self.rule_ids = []
        
            # Create documents for vectorization
            for rule in self.rules:
                # Combine rule text with keywords and examples for better matching
                doc = f"{rule['title']} {rule['text']} {' '.join(rule['keywords'])} {' '.join(rule['examples'])}"
            
                # Add condition text if it exists
                if 'conditions' in rule:
                    for cond in rule['conditions']:
                        if 'situation' in cond and 'explanation' in cond:
                            condition_text = f"{cond['situation']} {cond['explanation']}"
                            if 'examples' in cond and isinstance(cond['examples'], list):
                                condition_text += f" {' '.join(cond['examples'])}"
                            doc += " " + condition_text
            
                self.documents.append(doc)
                self.rule_ids.append(rule['id'])
        
            # Initialize and fit the vectorizer
            self.vectorizer = TfidfVectorizer(
                min_df=1, 
                stop_words='english',
                ngram_range=(1, 2)  # Include both single words and bigrams
            )
            self.document_vectors = self.vectorizer.fit_transform(self.documents)
        except Exception as e:
            print(f"Error initializing RulesVectorSearch: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def search(self, query, top_n=3):
        """Search for relevant rules given a query."""
        # Vectorize the query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarity to all documents
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]
        
        # Get top N matches
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        # Return relevant rules with similarity scores
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.0:  # Only include non-zero matches
                # Find the full rule data
                rule_id = self.rule_ids[idx]
                rule_data = next((r for r in self.rules if r['id'] == rule_id), None)
                
                results.append({
                    'rule': rule_data,
                    'similarity': similarities[idx]
                })
        
        return results
