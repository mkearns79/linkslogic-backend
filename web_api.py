# api/web_api.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import time
from datetime import datetime

# Add parent directory to path so we can import your existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing golf rules system
from golf_rules_hybrid_clean import get_clean_interpretation
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Club configuration
CLUB_CONFIG = {
    "columbia_cc": {
        "club_name": "Columbia Country Club",
        "features": {
            "voice_enabled": True,
            "local_rules_enabled": True,
            "quick_responses": True
        },
        "branding": {
            "primary_color": "#2d5016",
            "secondary_color": "#4a7c59"
        }
    }
}

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """
    Main endpoint for golf rules questions
    """
    try:
        data = request.json
        question = data.get('question', '').strip()
        club_id = data.get('club_id', 'columbia_cc')
        fast_mode = data.get('fast_mode', True)
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        print(f"🚨 API CALL at {datetime.now()}: {question[:50]}...")
        print(f"🚨 Client IP: {request.remote_addr}")

        request_hash = hash(question + str(time.time() // 10))  # 10-second window
        if hasattr(app, 'recent_requests'):
            if request_hash in app.recent_requests:
                print(f"🚨 DUPLICATE REQUEST BLOCKED: {question[:30]}...")
                return jsonify({
                    'success': False,
                    'error': 'Duplicate request detected'
                }), 429
            app.recent_requests.add(request_hash)
        else:
            app.recent_requests = {request_hash}

        print(f"🔍 Question: {question}")
        
        start_time = time.time()
        
        # Use your existing system
        answer = get_clean_interpretation(question, fast_mode=fast_mode)
        
        response_time = round(time.time() - start_time, 2)
        
        # Determine rule type from response
        rule_type = 'official'  # default
        rule_numbers = []
        confidence = 'medium'  # default
        
        if "Columbia's local rules" in answer or "Columbia Country Club" in answer:
            rule_type = 'local'
            confidence = 'high'
        elif "Rule " in answer:
            rule_type = 'official'
            # Extract rule numbers from response
            import re
            rule_matches = re.findall(r'Rule (\d+\.?\d*)', answer)
            rule_numbers = list(set(rule_matches))
            confidence = 'high'
        
        response_data = {
            'success': True,
            'answer': answer,
            'question': question,
            'club_id': club_id,
            'rule_type': rule_type,
            'rule_numbers': rule_numbers,
            'confidence': confidence,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Response generated in {response_time}s")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error processing question: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to process question: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'golf_rules_api',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/quick-questions', methods=['GET'])
def get_quick_questions():
    """Get common questions for quick access"""
    quick_questions = [
        {
            'id': 'water_hazard',
            'text': 'Water on 17',
            'category': 'local_rules',
            'icon': '💧'
        },
        {
            'id': 'lost_ball',
            'text': 'I lost my ball',
            'category': 'local_rules',
            'icon': '🔍'
        },
        {
            'id': 'green_stakes',
            'text': 'Can I get relief from portions of the cart path marked by green stakes?',
            'category': 'local_rules',
            'icon': '🌱'
        },
        {
            'id': 'maintenance_facility',
            'text': 'My ball is lost or found near the maintenance building',
            'category': 'local_rules',
            'icon': '🏢'
        },
        {
            'id': 'construction_fence',
            'text': 'My ball is against the mesh construction fence',
            'category': 'local_rules',
            'icon': '🚧'
        },
        {
            'id': 'out_of_bounds',
            'text': 'My ball went out of bounds',
            'category': 'local_rules',
            'icon': '🚫'
        }
    ]
    
    return jsonify({
        'success': True,
        'questions': quick_questions
    })

@app.route('/api/test', methods=['POST'])
def test_integration():
    """Test endpoint for development"""
    data = request.json
    test_question = data.get('question', 'Can I move my ball marker?')
    
    try:
        answer = get_clean_interpretation(test_question, fast_mode=True)
        
        return jsonify({
            'success': True,
            'test_question': test_question,
            'test_answer': answer,
            'integration_status': 'working'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'integration_status': 'failed'
        }), 500

if __name__ == '__main__':
    print("🏌️ Golf Rules API starting...")
    print("🚀 Features enabled:")
    print("  • Voice recognition support")
    print("  • Local rules integration")
    print("  • Ultra-fast responses")
    print("\n📡 API Endpoints:")
    print("  • POST /api/ask - Main rules question endpoint")
    print("  • GET /api/health - Health check")
    print("  • GET /api/quick-questions - Common questions")
    print("  • POST /api/test - Integration test")
    print("\n🌐 Starting server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
