import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
CORS(app)

# Nuclia API configuration
NUCLIA_API_KEY = os.getenv("NUCLIA_API_KEY")
NUCLIA_API_URL = os.getenv("NUCLIA_API_URL", "https://aws-us-east-2-1.nuclia.cloud")
NUCLIA_ZONE = os.getenv("NUCLIA_ZONE", "aws-us-east-2-1")
NUCLIA_KB = os.getenv("NUCLIA_KB", "2eebe115-73dd-4790-ac54-78a025a0961b")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Handle question requests to Nuclia API"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Prepare request to Nuclia API
        headers = {
            'X-NUCLIA-SERVICEACCOUNT': f'Bearer {NUCLIA_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': question,
            'features': ['keyword', 'semantic'],
            'show': ['basic', 'values', 'origin'],
            'extracted': ['text'],
            'highlight': True,
            'with_search': True
        }
        
        # Make request to Nuclia API
        api_url = f'{NUCLIA_API_URL}/api/v1/kb/{NUCLIA_KB}/ask'
        logging.debug(f"Making request to: {api_url}")
        logging.debug(f"Payload: {payload}")
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        logging.debug(f"Response text: {response.text[:500]}...")
        
        if response.status_code == 200:
            # Handle NDJSON streaming response
            answer_text = ""
            sources = []
            search_data = None
            
            # First, let's capture all the response data
            response_lines = response.text.strip().split('\n')
            
            for line in response_lines:
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        logging.debug(f"Processing chunk type: {chunk.get('item', {}).get('type', 'unknown')}")
                        
                        if isinstance(chunk, dict) and 'item' in chunk:
                            item = chunk['item']
                            if isinstance(item, dict):
                                chunk_type = item.get('type')
                                if chunk_type == 'answer':
                                    answer_text += item.get('text', '')
                                elif chunk_type == 'retrieval':
                                    search_data = item
                                    resources_count = len(item.get('results', {}).get('resources', {}))
                                    logging.debug(f"Found retrieval data with {resources_count} resources")
                                    if resources_count > 0:
                                        logging.debug(f"Retrieval data keys: {list(item.get('results', {}).keys())}")
                                elif chunk_type == 'search':
                                    search_data = item
                                    resources_count = len(item.get('results', {}).get('resources', {}))
                                    logging.debug(f"Found search data with {resources_count} resources")
                                    if resources_count > 0:
                                        logging.debug(f"Search data keys: {list(item.get('results', {}).keys())}")
                                else:
                                    logging.debug(f"Unhandled chunk type: {chunk_type}")
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse JSON line: {line} - Error: {e}")
                        continue
                    except Exception as e:
                        logging.warning(f"Error processing chunk: {line} - Error: {e}")
                        continue
            
            # Extract sources from search data
            if search_data and 'results' in search_data:
                results = search_data['results']
                logging.debug(f"Search results keys: {list(results.keys())}")
                
                if 'resources' in results:
                    logging.debug(f"Processing {len(results['resources'])} resources")
                    temp_sources = []
                    
                    for resource_id, resource_data in results['resources'].items():
                        # Get document title - try multiple sources
                        title = 'Unknown Document'
                        
                        # Try to get title from various locations
                        # First check the direct title field
                        if 'title' in resource_data and resource_data['title']:
                            title = resource_data['title']
                        # Try metadata locations
                        elif 'metadata' in resource_data:
                            metadata = resource_data['metadata']
                            if 'filename' in metadata:
                                title = metadata['filename']
                            elif 'title' in metadata:
                                title = metadata['title']
                        # Try user metadata
                        elif 'usermetadata' in resource_data:
                            usermetadata = resource_data['usermetadata']
                            if 'filename' in usermetadata:
                                title = usermetadata['filename']
                            elif 'title' in usermetadata:
                                title = usermetadata['title']
                        # Try slug as last resort
                        elif 'slug' in resource_data:
                            title = resource_data['slug']
                        
                        # If we still have unknown, try to extract from the text content
                        if title == 'Unknown Document':
                            # Look at the first paragraph to see if we can extract a document type
                            if 'fields' in resource_data:
                                for field_id, field_data in resource_data['fields'].items():
                                    if 'paragraphs' in field_data:
                                        for para_id, para_data in field_data['paragraphs'].items():
                                            text = para_data.get('text', '').strip()
                                            # Try to extract title from content
                                            if 'Meeting Minutes' in text:
                                                title = 'Council Meeting Minutes'
                                            elif 'FAQs' in text or 'Frequently Asked' in text:
                                                title = 'Smallville FAQs'
                                            elif 'Zoning' in text and 'Regulations' in text:
                                                title = 'Zoning Regulations'
                                            elif 'Business Permit' in text:
                                                title = 'Business Permit Guide'
                                            elif 'Mayor' in text and ('announce' in text or 'recycling' in text):
                                                title = 'Mayor Announcement'
                                            break
                                    break
                        
                        # Remove file extension if present and clean up
                        if title.endswith('.pdf'):
                            title = title[:-4]
                        title = title.replace('-', ' ').replace('_', ' ').title()
                        
                        # Process each field/paragraph in the resource
                        if 'fields' in resource_data:
                            for field_id, field_data in resource_data['fields'].items():
                                if 'paragraphs' in field_data:
                                    for para_id, para_data in field_data['paragraphs'].items():
                                        # Skip very low quality or filename-only results
                                        text = para_data.get('text', '').strip()
                                        score = para_data.get('score', 0)
                                        
                                        # Filter out low-quality sources
                                        if (score < 0.001 or 
                                            len(text) < 50 or 
                                            text.endswith('.pdf') or
                                            text.startswith('Smallville') and len(text) < 100):
                                            continue
                                        
                                        # Extract page number safely
                                        page_num = 1
                                        if 'position' in para_data and 'page_number' in para_data['position']:
                                            page_num = para_data['position']['page_number'] + 1
                                        
                                        source = {
                                            'title': title,
                                            'text': text,
                                            'score': score,
                                            'page': f"p. {page_num}",
                                            'pageNumber': f"p. {page_num}",
                                            'section': text[:100] + '...' if len(text) > 100 else text
                                        }
                                        temp_sources.append(source)
                    
                    # Sort by score (highest first) and limit to top 5 unique sources
                    temp_sources.sort(key=lambda x: x['score'], reverse=True)
                    seen_texts = set()
                    for source in temp_sources:
                        if len(sources) >= 5:  # Limit to 5 sources
                            break
                        # Avoid duplicate content
                        text_hash = source['text'][:50]  # Use first 50 chars as hash
                        if text_hash not in seen_texts:
                            sources.append(source)
                            seen_texts.add(text_hash)
                            logging.debug(f"Added source: {source['title']} - {source['page']} (score: {source['score']:.4f})")
            else:
                logging.debug(f"No search data found or search data structure: {search_data}")
            

            
            # Log final processing results
            logging.debug(f"Final answer_text: '{answer_text}'")
            logging.debug(f"Final sources count: {len(sources)}")
            logging.debug(f"Sources data: {sources}")
            
            # Fallback if no answer was found
            if not answer_text.strip():
                answer_text = "I couldn't find a specific answer to your question in the available documents."
            
            return jsonify({
                'success': True,
                'answer': answer_text,
                'sources': sources,
                'question': question
            })
        
        elif response.status_code == 401:
            return jsonify({
                'success': False,
                'error': 'Invalid API key. Please check your Nuclia API configuration.'
            }), 401
        
        elif response.status_code == 429:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded. Please try again later.'
            }), 429
        
        else:
            logging.error(f"Nuclia API error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'API request failed with status {response.status_code}'
            }), 500
    
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timed out. Please try again.'
        }), 504
    
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Unable to connect to the AI service. Please check your internet connection.'
        }), 503
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
