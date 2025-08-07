"""
Vercel serverless function for enhanced blog generation using Python Gemini SDK.
"""

import json
import os
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import sys
from pathlib import Path

# Add the project root to the path so we can import our services
sys.path.append(str(Path(__file__).parent.parent))

try:
    from services.gemini_service import gemini_service
    GEMINI_SERVICE_AVAILABLE = True
except ImportError as e:
    GEMINI_SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)

class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""
    
    def do_GET(self):
        """Handle GET requests - return service status."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'ok',
            'service': 'Enhanced Python Gemini Blog Generator',
            'gemini_service_available': GEMINI_SERVICE_AVAILABLE,
            'endpoints': {
                'POST /api/generate-blog': 'Generate complete blog post',
                'POST /api/generate-outline': 'Generate blog outline only',
                'POST /api/generate-persona': 'Generate customer persona',
                'POST /api/trending-topics': 'Get trending topics'
            }
        }
        
        if not GEMINI_SERVICE_AVAILABLE:
            response['error'] = f'Gemini service not available: {IMPORT_ERROR}'
            
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_POST(self):
        """Handle POST requests for blog generation."""
        # Handle CORS preflight
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if not GEMINI_SERVICE_AVAILABLE:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': 'Gemini service not available',
                'details': IMPORT_ERROR,
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
            return
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            # Get the specific action from the request
            action = request_data.get('action', 'generate_blog')
            
            # Process the request asynchronously
            response_data = asyncio.run(self.process_request(action, request_data))
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, default=str).encode())
            
        except Exception as error:
            # Handle errors
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                'error': str(error),
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    async def process_request(self, action: str, data: dict):
        """Process the API request based on action type."""
        
        if action == 'generate_blog':
            return await self.generate_complete_blog(data)
        elif action == 'generate_outline':
            return await self.generate_outline_only(data)
        elif action == 'generate_persona':
            return await self.generate_persona(data)
        elif action == 'trending_topics':
            return await self.get_trending_topics()
        elif action == 'seo_analysis':
            return await self.analyze_seo(data)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def generate_complete_blog(self, data: dict):
        """Generate a complete blog post with all metadata."""
        # Extract parameters with defaults
        title = data.get('title', 'Skincare Tips for Pakistani Women')
        keywords = data.get('keywords', 'skincare, Pakistani beauty, glowing skin')
        tone = data.get('tone', 'Professional')
        content_template = data.get('content_template', 'Standard Blog Post')
        author_persona = data.get('author_persona', 'Beauty Expert')
        target_audience = data.get('target_audience', 'Pakistani women aged 20-35')
        
        # Generate customer persona first
        persona = None
        if target_audience:
            try:
                persona = await gemini_service.generate_customer_persona(target_audience)
            except Exception as e:
                print(f"Could not generate persona: {e}")
        
        # Generate outline
        outline = await gemini_service.generate_blog_outline(
            title=title,
            keywords=keywords,
            content_template=content_template,
            author_persona=author_persona,
            target_persona=persona
        )
        
        # Generate full blog post
        blog_post = await gemini_service.generate_full_blog_post(
            title=title,
            tone=tone,
            keywords=keywords,
            content_template=content_template,
            author_persona=author_persona,
            brand_voice_profile=data.get('brand_voice'),
            outline=outline,
            target_persona=persona
        )
        
        # Generate SEO data
        seo_data = await gemini_service.generate_seo_and_faq(
            blog_post.content,
            blog_post.title,
            keywords
        )
        
        return {
            'status': 'success',
            'blog_post': {
                'title': blog_post.title,
                'content': blog_post.content,
                'meta_title': blog_post.meta_title,
                'meta_description': blog_post.meta_description,
                'tags': blog_post.tags,
                'word_count': blog_post.word_count
            },
            'seo_data': {
                'meta_titles': seo_data.meta_titles,
                'meta_descriptions': seo_data.meta_descriptions,
                'faq': [{'question': item.question, 'answer': item.answer} for item in seo_data.faq],
                'key_takeaways': seo_data.key_takeaways
            },
            'outline': [{'id': section.id, 'heading': section.heading, 'key_points': section.key_points} for section in outline],
            'persona': {
                'name': persona.name,
                'age': persona.age,
                'location': persona.location,
                'bio': persona.bio
            } if persona else None
        }
    
    async def generate_outline_only(self, data: dict):
        """Generate just a blog outline."""
        title = data.get('title', 'Skincare Tips for Pakistani Women')
        keywords = data.get('keywords', 'skincare Pakistan')
        content_template = data.get('content_template', 'Standard Blog Post')
        author_persona = data.get('author_persona', 'Beauty Expert')
        
        outline = await gemini_service.generate_blog_outline(
            title=title,
            keywords=keywords,
            content_template=content_template,
            author_persona=author_persona
        )
        
        return {
            'status': 'success',
            'outline': [{'id': section.id, 'heading': section.heading, 'key_points': section.key_points} for section in outline]
        }
    
    async def generate_persona(self, data: dict):
        """Generate a customer persona."""
        description = data.get('description', 'Pakistani women interested in skincare')
        
        persona = await gemini_service.generate_customer_persona(description)
        
        return {
            'status': 'success',
            'persona': {
                'name': persona.name,
                'age': persona.age,
                'occupation': persona.occupation,
                'location': persona.location,
                'skincare_goals': persona.skincare_goals,
                'pain_points': persona.pain_points,
                'motivations': persona.motivations,
                'personality': persona.personality,
                'bio': persona.bio
            }
        }
    
    async def get_trending_topics(self):
        """Get trending skincare topics."""
        topics = await gemini_service.get_trending_topics()
        
        return {
            'status': 'success',
            'topics': [{'topic': topic.topic, 'reason': topic.reason} for topic in topics]
        }
    
    async def analyze_seo(self, data: dict):
        """Analyze SEO for given content."""
        content = data.get('content', '')
        keywords = data.get('keywords', '')
        
        if not content:
            raise ValueError("Content is required for SEO analysis")
        
        seo_score = await gemini_service.get_seo_score(content, keywords)
        
        return {
            'status': 'success',
            'seo_analysis': {
                'score': seo_score.score,
                'recommendations': seo_score.recommendations
            }
        }

# Vercel expects this format
def handler_function(request):
    """Vercel handler function."""
    return handler(request)
