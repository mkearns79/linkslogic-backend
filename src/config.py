"""Configuration settings for the Golf Rules Assistant."""

# Paths
DATA_DIR = "data"
RULES_FILE = f"{DATA_DIR}/rules_database.json"

# NLP Settings
SIMILARITY_THRESHOLD = 0.5  # Minimum similarity score for a match
MAX_RESULTS = 3  # Maximum number of rule matches to return

# Logging
LOG_LEVEL = "INFO"

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
    
    # Basic tokenization - split by space if nltk tokenizer not available
    try:
        tokens = word_tokenize(text)
    except:
        tokens = text.split()
    
    # Remove stopwords and lemmatize
    keywords = []
    for token in tokens:
        if token not in stop_words and len(token) > 2:
            keywords.append(lemmatizer.lemmatize(token))
    
    return keywords

def calculate_similarity(text1, text2):
    """Calculate similarity between two texts using fuzzy matching."""
    # Preprocess texts
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    
    # Calculate token sort ratio (handles word order differences)
    return fuzz.token_sort_ratio(text1, text2) / 100.0
