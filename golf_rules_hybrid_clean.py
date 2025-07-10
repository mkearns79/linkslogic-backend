# golf_rules_hybrid_clean.py
# Production-ready version with debug code removed

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from vector_search import ClubSpecificVectorSearch

# Common query templates for ultra-fast responses
COMMON_QUERY_TEMPLATES = {
    "clear_lost_ball": {
        "keywords": ["lost my ball in the woods", "lost my ball in the rough", "can't find my ball in the woods", "lost ball in trees", "lost ball in the fescue"],
        "local_rule": "CCC-1",
        "quick_response": """At Columbia Country Club, you have TWO options for lost balls:

OPTION 1 - Columbia CC Special Relief (2 penalty strokes):
Instead of going back to where you last played, you can:
- Estimate where your ball was lost
- Find the nearest fairway point to that spot  
- Drop anywhere between two imaginary lines from the hole through each point
- Stay within two club-lengths of those lines
- Must not be closer to the hole than where ball was lost

OPTION 2 - Standard Rule (1 penalty stroke):
Return to where you last played and hit again (stroke and distance).

Most golfers prefer the Columbia CC option since you don't have to walk back."""
    },

    "clear_out_of_bounds": {
        "keywords": ["out of bounds", "over the fence", "ob"],
        "local_rule": "CCC-1",
        "quick_response": """At Columbia, you have TWO options for out-of-bounds balls:

OPTION 1 - Columbia CC Special Relief (2 penalty strokes):
Instead of going back to where you last played, you can:
• Estimate where your ball crossed out of bounds or was lost
• Find the nearest fairway point to that spot
• Drop anywhere between two imaginary lines: one from the hole through where your ball was lost, and one from the hole through the nearest fairway point
• Stay within two club-lengths of those lines
• Must not be closer to the hole than where ball was lost

OPTION 2 - Standard Rule (1 penalty stroke):
Return to where you last played and hit again (stroke and distance).

Exception: player gets FREE RELIEF from a ball hit into the maintenance area to the left of #10, whether the ball is found or not. The player is entitled to a free drop at the nearest point of full relief (in most cases, just to the right of the paved driveway lining the maintenance area"""
    },
    
    "water_hazard_16": {
        "keywords": ["water on 16", "water on #16", "penalty area on #16", "water on hole 16", "hit it in the water on the 16th", "water hazard on 16"],
        "local_rule": "CCC-2",
        "quick_response": """On the 16th hole at Columbia CC, you have EXTRA relief options:

If your ball goes in the water/penalty area:
• Standard relief under Rule 17.1 (1 penalty stroke), OR
• Use the special DROPPING ZONE near the 16th green (1 penalty stroke)

The dropping zone is often the better choice as it gives you a good angle to the pin without having to go way back or play from a difficult angle."""
    },
    
    "water_hazard_17": {
        "keywords": ["water on seventeen", "water on 17", "17th hole water", "pond on hole seventeen", "17th water", "drop zone on seventeen"],
        "local_rule": "CCC-2", 
        "quick_response": """On the 17th hole at Columbia CC:

If your ball goes in the POND (west of the footbridge):
• Standard relief under Rule 17.1 (1 penalty stroke), OR  
• Use the special DROPPING ZONE near the 17th green (1 penalty stroke)

If your ball is in other penalty areas on 17th:
• Standard relief under Rule 17.1 only

The dropping zone is only available for the main pond area, not other water hazards on the hole."""
    },

    "turf_nursery": {
        "keywords": ["turf nursery", "turf farm", "fairway farm", "nursery area", "ball in nursery", "tahoma farm", "nursery near maintenance", "grass farm", "farm near the shack", "nursery near the shack", "sod farm", "sod nursery"],
        "local_rule": "CCC-8",
        "quick_response": """According to Columbia Country Club's local rules, the turf nursery adjacent to the maintenance area is a No Play Zone.

MANDATORY FREE RELIEF required:
- You CANNOT play the ball as it lies
- You MUST take free relief under Rule 16.1f
- Drop at nearest point of complete relief from the nursery area
- Within one club-length, not nearer hole
- No penalty stroke

This is different from regular ground under repair - relief is mandatory, not optional."""
    },
    
    "maintenance_facility": {
        "keywords": ["maintenance", "building", "facility", "shed", "equipment", "roof"],
        "local_rule": "CCC-7",
        "quick_response": """Maintenance facility at Columbia CC (near holes 9 & 10):

FREE RELIEF available from:
• All maintenance buildings
• Storage tanks and sheds  
• Paved and gravel areas
• Retention ponds
• Equipment

The entire maintenance complex is treated as one large immovable obstruction. Drop within one club-length of your nearest point of complete relief, no closer to the hole."""
    },
    
    "aeration_holes": {
        "keywords": ["aeration", "hole in green", "aerify", "punched green"],
        "local_rule": "CCC-11",
        "quick_response": """Aeration holes at Columbia CC:

FREE RELIEF available when:
• Ball is IN an aeration hole
• Ball TOUCHES an aeration hole  
• Aeration hole interferes with your swing

NO RELIEF when:
• Aeration hole only affects your stance
• On putting green: only affects your line of putt

Relief: Drop/place within one club-length of nearest point of relief. If you get relief and the ball rolls into another aeration hole, you get relief again."""
    },

    "construction_fence_relief": {
        "keywords": ["mesh fence relief", "against purple line fence", "against construction fence", "construction fence interfering with swing", "construction fence relief", "purple line fence relief"],
        "local_rule": "CCC-6",
        "quick_response": """According to Columbia Country Club's local rules, the fence around the Purple Line construction area (including mesh/green fencing) is considered a boundary fence.

NO FREE RELIEF is available from this fence, or any fence at Columbia.

Your options:
- Play the ball as it lies if possible
- Declare the ball unplayable under Rule 19 (1 penalty stroke)
  - Drop within two club-lengths, not nearer hole
  - Drop on line from hole through ball, going back as far as desired
  - Return to previous spot where you played

The construction fence is treated as a boundary, not a regular obstruction."""
    }  
}

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
        
        with open("usage_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except:
        pass  # Don't let logging errors break the main function

def check_common_query(question):
    """Check if question matches common query templates for ultra-fast response."""
    question_lower = question.lower()
    
    for template_name, template_data in COMMON_QUERY_TEMPLATES.items():
        for keyword_phrase in template_data["keywords"]:
            if keyword_phrase in question_lower:
                return template_data
    
    return None

def get_ultra_fast_interpretation(question, verbose=False):
    """Ultra-fast response for common queries using templates."""
    
    # Check for common query patterns
    template = check_common_query(question)
    
    if template:
        # Log the ultra-fast usage
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tokens": 0,  # Template uses no LLM tokens
            "cost": 0,
            "question_preview": question[:50],
            "optimization": "template",
            "template_used": template["local_rule"]
        }
        
        try:
            with open("usage_log_optimized.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
        
        return template["quick_response"]
    
    else:
        # Fall back to optimized search
        return get_hybrid_interpretation(question, verbose=verbose, use_compression=True)

def _build_ultra_compressed_context(search_results, context_type, verbose=False):
    """Build ultra-compressed context to minimize LLM tokens."""
    if not search_results:
        return "No specific rules found for this situation."
    
    context_parts = []
    
    for result in search_results:
        rule = result['rule']
        
        if result.get('is_local', False):
            # Compressed local rule format
            rule_text = f"LOCAL Rule {rule['id']}: {rule['title']}"
            
            # Add only essential rule text (first 150 chars)
            text_preview = rule['text'][:150] + "..." if len(rule['text']) > 150 else rule['text']
            rule_text += f". {text_preview}"
            
            # Add key conditions that affect relief
            if 'conditions' in rule and rule['conditions']:
                for condition in rule['conditions'][:2]:  # First 2 conditions only
                    if 'no relief' in condition.get('explanation', '').lower():
                        rule_text += f" IMPORTANT: {condition['explanation'][:100]}..."
                        break
        else:
            # Compressed official rule format
            rule_text = f"OFFICIAL Rule {rule['id']}: {rule['title']}"
            
            # Add only first 100 chars of rule text
            text_preview = rule['text'][:100] + "..." if len(rule['text']) > 100 else rule['text']
            rule_text += f". {text_preview}"
        
        context_parts.append(rule_text)
    
    return "\n\n".join(context_parts)

def _build_detailed_context(search_results, verbose=False):
    """Build detailed context for comparison purposes."""
    try:
        context_parts = []
        
        for result in search_results:
            rule = result['rule']
            similarity_percent = round(result.get('best_similarity', 0) * 100, 1)
            
            # Build rule context
            rule_context = f"Rule {rule['id']}: {rule['title']}\n"
            rule_context += f"Rule Text: {rule['text']}\n"
            
            # Add best condition if available
            if result.get('best_condition') and result['best_condition'].get('condition_data'):
                condition = result['best_condition']['condition_data']
                rule_context += f"Specific Situation: {condition.get('situation', '')}\n"
                rule_context += f"Explanation: {condition.get('explanation', '')}\n"
                
                if condition.get('examples'):
                    rule_context += f"Examples: {', '.join(condition['examples'][:2])}\n"
            
            # Add keywords if available
            if rule.get('keywords'):
                rule_context += f"Keywords: {', '.join(rule['keywords'][:5])}\n"
            
            context_parts.append(rule_context)
        
        return "\n" + "-"*40 + "\n".join(context_parts)

    except Exception as e:
        raise

def _create_optimized_prompt(question, context, context_type):
    """Create context-optimized prompts."""
    
    if context_type == "local_only":
        return f"""Columbia Country Club Local Rule:
{context}

Q: {question}

Give direct answer with rule number and procedure. Under 100 words."""
    
    elif context_type == "local_priority":
        return f"""Golf Rules (Columbia Country Club local rules apply first):
{context}

Q: {question}

If answering using a LOCAL rule, start with 'According to Columbia's local rules...' 
If answering using an OFFICIAL rule, start with 'According to the Rules of Golf, Rule X.X...'
Be concise and include key steps."""
    
    else:
        return f"""Golf Rules Context:
{context}

Q: {question}

Provide:
1. Direct answer (start with "According to Columbia's local rules..." for LOCAL rules, or "According to the Rules of Golf, Rule X.X..." for OFFICIAL rules)
2. Rule number
3. Key procedure

Under 150 words."""

def enhance_context_for_ambiguous_scenarios(search_results, query, hole_number, verbose=False):
    """Add clarifying context for ambiguous scenarios where location matters."""
    query_lower = query.lower()
    
    # HOLE 17 WATER AMBIGUITY
    if (hole_number == 17 and 
        any(term in query_lower for term in ['water', 'pond', 'penalty', 'hazard']) and
        not any(specific in query_lower for specific in ['west of', 'east of', 'bridge', 'creek', 'stream'])):
        
        # Find CCC-2 in results and enhance its context
        for result in search_results:
            if result['rule']['id'] == 'CCC-2':
                if 'enhanced_context' not in result['rule']:
                    result['rule']['enhanced_context'] = ""
                
                result['rule']['enhanced_context'] += (
                    "\n\nLOCATION MATTERS ON HOLE 17: The dropping zone is only available "
                    "for balls in the main pond west of the footbridge. Balls in other "
                    "water areas (streams, ditches, etc.) must use standard penalty relief "
                    "under Rule 17.1 only."
                )
                break
    
    return search_results

def get_hybrid_interpretation(question, verbose=False, use_compression=True):
    """Get a golf rule interpretation using the hybrid approach."""
    try:
        # Find relevant rules using vector search
        import re
        hole_match = re.search(r'\b(\d{1,2})(?:th|st|nd|rd)?\s+(?:hole|green)\b', question.lower())
        hole_number = int(hole_match.group(1)) if hole_match else None

        # Enhance context for ambiguous scenarios
        search_results = search_engine.search_with_precedence(question, hole_number=hole_number, top_n=2)
        search_results = enhance_context_for_ambiguous_scenarios(search_results, question, hole_number, verbose)
        
        # Smart filtering: If first result is local and strong, remove official rules
        context_type = "hybrid"
        if (search_results and 
            search_results[0].get('is_local', False) and 
            search_results[0]['best_similarity'] > 0.6):
            
            search_results = [r for r in search_results if r.get('is_local', False)][:1]
            context_type = "local_priority"

        # Build context
        if use_compression:
            relevant_rules_text = _build_ultra_compressed_context(search_results, context_type, verbose)
        else:
            relevant_rules_text = _build_detailed_context(search_results, verbose)
        
        # Create prompt
        prompt = _create_optimized_prompt(question, relevant_rules_text, context_type)

        # Send request
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a golf rules expert for Columbia Country Club. When answering GENERAL rules questions (no specific hole mentioned), prioritize official Rules of Golf and reference rule numbers. When answering HOLE-SPECIFIC questions, prioritize Columbia's local rules. Use 'According to Columbia's local rules...' for local rules (NEVER mention CCC codes), 'According to the Rules of Golf, Rule X.X...' for official rules. Be concise but complete."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200 if use_compression else None
        )
        
        result = response.choices[0].message.content
        
        # Log usage
        if response.usage:
            total_cost = (response.usage.prompt_tokens * 0.01 + response.usage.completion_tokens * 0.03) / 1000
            log_usage(response.usage.total_tokens, total_cost, question)
        
        return result
    
    except Exception as e:
        return f"Error getting rule interpretation: {str(e)}"

# Production API functions - no debug output
def get_clean_interpretation(question, fast_mode=True):
    """Clean API function for web interface - no debug output."""
    if fast_mode:
        return get_ultra_fast_interpretation(question, verbose=False)
    else:
        return get_hybrid_interpretation(question, verbose=False, use_compression=True)