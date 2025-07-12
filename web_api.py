from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Smart template responses (no AI models needed)
GOLF_RESPONSES = {
    "lost ball": "At Columbia Country Club, you have TWO options for lost balls: Standard stroke and distance (1 penalty) or Columbia CC Special Relief (2 penalty strokes).",
    "water": "For water hazards at Columbia CC: Use dropping zones on holes 16-17 OR standard relief under Rule 17.1 (1 penalty stroke).",
    "bunker": "According to Rule 12.2, you cannot ground your club in a bunker before making your stroke.",
    "aeration": "According to Columbia's local rules: FREE RELIEF available when ball is IN aeration hole or interferes with swing."
}

def get_smart_response(question):
    question_lower = question.lower()
    if any(word in question_lower for word in ["lost", "can't find"]):
        return GOLF_RESPONSES["lost ball"]
    elif any(word in question_lower for word in ["water", "pond"]):
        return GOLF_RESPONSES["water"]
    elif any(word in question_lower for word in ["bunker", "sand"]):
        return GOLF_RESPONSES["bunker"]
    elif any(word in question_lower for word in ["aeration", "hole in green"]):
        return GOLF_RESPONSES["aeration"]
    else:
        return "I can help with Columbia Country Club golf rules! Ask about lost balls, water hazards, bunkers, or aeration holes."

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': 'Question required'}), 400
        
        answer = get_smart_response(question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'question': question,
            'rule_type': 'local',
            'confidence': 'high',
            'response_time': 0.1
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/quick-questions', methods=['GET'])
def get_quick_questions():
    return jsonify({
        'success': True,
        'questions': [
            {'id': 'lost', 'text': 'I lost my ball', 'icon': '🔍'},
            {'id': 'water', 'text': 'Ball in water', 'icon': '💧'}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
