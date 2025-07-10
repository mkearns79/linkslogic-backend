"""Text processing utilities for the Golf Rules Assistant."""
import re
import string
from fuzzywuzzy import fuzz

# Simple stopwords list
STOP_WORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
                 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
                 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
                 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
                 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
                 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
                 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 
                 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 
                 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
                 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 
                 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very'])

# Simple lemmatizer function that doesn't rely on NLTK
def simple_lemmatize(word):
    """Very simple lemmatization - just handles some common endings."""
    if word.endswith('ing'):
        return word[:-3]
    elif word.endswith('ed') and len(word) > 3:
        return word[:-2]
    elif word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word

def preprocess_text(text):
    """Clean and normalize text for processing."""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_keywords(text):
    """Extract important keywords from text."""
    # Preprocess text
    text = preprocess_text(text)
    
    # Basic tokenization - split by space
    tokens = text.split()
    
    # Remove stopwords and lemmatize
    keywords = []
    for token in tokens:
        if token not in STOP_WORDS and len(token) > 2:
            keywords.append(simple_lemmatize(token))
    
    return keywords

def calculate_similarity(text1, text2):
    """Calculate similarity between two texts using fuzzy matching."""
    # Preprocess texts
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    
    # Calculate token sort ratio (handles word order differences)
    return fuzz.token_sort_ratio(text1, text2) / 100.0
