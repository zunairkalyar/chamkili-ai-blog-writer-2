#!/usr/bin/env python3
"""
Enhanced Auto Blog Poster for Chamkili using the new Python Gemini SDK.
Features structured outputs, better error handling, and improved reliability.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import schedule
import time
from pathlib import Path

# Import our enhanced Gemini service
from services.gemini_service import (
    gemini_service, 
    CustomerPersona,
    OutlineBlock,
    BlogPost
)

# Shopify integration
import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_poster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoBlogPoster:
    """Enhanced auto blog poster with structured outputs."""
    
    def __init__(self):
        self.load_config()
        self.is_processing = False
        logger.info("✅ Auto Blog Poster initialized with enhanced Gemini SDK")
    
    def load_config(self):
        """Load configuration from file and environment variables."""
        try:
            config_path = Path(__file__).parent / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Override with environment variables
            self.config['gemini']['apiKey'] = os.getenv('GEMINI_API_KEY', self.config['gemini']['apiKey'])
            self.config['shopify']['storeName'] = os.getenv('SHOPIFY_STORE_NAME', self.config['shopify']['storeName'])
            self.config['shopify']['accessToken'] = os.getenv('SHOPIFY_ACCESS_TOKEN', self.config['shopify']['accessToken'])
            
            logger.info("✅ Configuration loaded successfully")
            
        except Exception as error:
            logger.error(f"❌ Error loading config: {error}")
            # Fallback configuration
            self.config = {
                'schedule': {'interval': '*/10 * * * *', 'description': 'Every 10 minutes'},
                'gemini': {
                    'apiKey': os.getenv('GEMINI_API_KEY', 'GEMINI_API_KEY_PLACEHOLDER'),
                    'model': 'gemini-2.0-flash-exp'
                },
                'shopify': {
                    'storeName': os.getenv('SHOPIFY_STORE_NAME', 'SHOPIFY_STORE_NAME_PLACEHOLDER'),
                    'accessToken': os.getenv('SHOPIFY_ACCESS_TOKEN', 'SHOPIFY_ACCESS_TOKEN_PLACEHOLDER')
                },
                'blogSettings': {
                    'topics': [
                        "Best Korean Skincare Routine for Pakistani Skin",
                        "How to Get Rid of Dark Spots Naturally in Pakistan", 
                        "Vitamin C Serum Benefits for Oily Skin",
                        "Niacinamide vs Hyaluronic Acid: Which is Better",
                        "Summer Skincare Tips for Hot Pakistani Weather"
                    ],
                    'tones': ['Warm & Friendly', 'Professional', 'Empathetic'],
                    'contentTemplates': ['Standard Blog Post', 'Step-by-Step Guide', 'Product Deep Dive'],
                    'authorPersonas': ['Beauty Guru', 'The Dermatologist', 'Skincare Scientist'],
                    'keywords': ['skincare routine Pakistan', 'glowing skin tips', 'Pakistani beauty']
                }
            }

    def get_random_blog_config(self) -> Dict:
        """Generate random blog configuration using structured approach."""
        import random
        
        return {
            'title': random.choice(self.config['blogSettings']['topics']),
            'tone': random.choice(self.config['blogSettings']['tones']),
            'content_template': random.choice(self.config['blogSettings']['contentTemplates']),
            'author_persona': random.choice(self.config['blogSettings']['authorPersonas']),
            'keywords': ', '.join(random.sample(self.config['blogSettings']['keywords'], 
                                               min(3, len(self.config['blogSettings']['keywords']))))
        }

    async def shopify_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Shopify API."""
        url = f"https://{self.config['shopify']['storeName']}.myshopify.com/admin/api/2024-07/{endpoint}"
        
        headers = {
            'X-Shopify-Access-Token': self.config['shopify']['accessToken'],
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as error:
            logger.error(f"Shopify API error: {error}")
            raise Exception(f"Shopify API request failed: {error}")

    async def get_or_create_blog(self) -> Dict:
        """Get existing blog or create new one."""
        try:
            # Try to get existing blogs
            blogs_response = await self.shopify_request('blogs.json')
            blogs = blogs_response.get('blogs', [])
            
            if blogs:
                logger.info(f"Using existing blog: {blogs[0]['title']}")
                return blogs[0]
            
            # Create new blog if none exists
            logger.info("Creating new blog...")
            blog_data = {
                'blog': {
                    'title': 'Chamkili Beauty Blog',
                    'handle': 'chamkili-beauty-blog',
                    'commentable': 'yes',
                    'feedburner': '',
                    'feedburner_location': ''
                }
            }
            
            response = await self.shopify_request('blogs.json', 'POST', blog_data)
            return response['blog']
            
        except Exception as error:
            logger.error(f"Error managing Shopify blog: {error}")
            raise

    async def publish_to_shopify(self, blog_post: BlogPost, blog_id: int) -> Dict:
        """Publish the structured blog post to Shopify."""
        try:
            # Prepare article data with metafields for SEO
            article_data = {
                'article': {
                    'title': blog_post.title,
                    'author': 'Chamkili AI Writer',
                    'body_html': blog_post.content,
                    'published': True,
                    'tags': ', '.join(blog_post.tags),
                    'metafields': [
                        {
                            'key': 'title_tag',
                            'namespace': 'global', 
                            'value': blog_post.meta_title,
                            'type': 'single_line_text_field'
                        },
                        {
                            'key': 'description_tag',
                            'namespace': 'global',
                            'value': blog_post.meta_description, 
                            'type': 'single_line_text_field'
                        }
                    ]
                }
            }
            
            response = await self.shopify_request(
                f'blogs/{blog_id}/articles.json', 
                'POST', 
                article_data
            )
            
            article = response['article']
            logger.info(f"✅ Article published successfully! Shopify ID: {article['id']}")
            return article
            
        except Exception as error:
            logger.error(f"Error publishing to Shopify: {error}")
            raise

    async def generate_and_publish_blog(self):
        """Main function to generate and publish blog with structured outputs."""
        if self.is_processing:
            logger.info("⏳ Already processing, skipping this cycle...")
            return
        
        self.is_processing = True
        logger.info(f"\n🚀 Starting enhanced blog generation at {datetime.now()}")
        
        try:
            # 1. Generate blog configuration
            blog_config = self.get_random_blog_config()
            logger.info(f"📝 Blog config: {blog_config['title']}")
            
            # 2. Generate customer persona (optional enhancement)
            try:
                target_audience = "Pakistani women aged 20-35 interested in natural skincare solutions"
                persona = await gemini_service.generate_customer_persona(target_audience)
                logger.info(f"👤 Generated persona: {persona.name}")
            except Exception as e:
                logger.warning(f"Could not generate persona: {e}")
                persona = None
            
            # 3. Generate structured outline
            outline = await gemini_service.generate_blog_outline(
                title=blog_config['title'],
                keywords=blog_config['keywords'],
                content_template=blog_config['content_template'],
                author_persona=blog_config['author_persona'],
                brand_voice_profile=None,  # Could be loaded from config
                target_persona=persona
            )
            logger.info(f"📋 Generated outline with {len(outline)} sections")
            
            # 4. Generate complete blog post with structured output
            blog_post = await gemini_service.generate_full_blog_post(
                title=blog_config['title'],
                tone=blog_config['tone'],
                keywords=blog_config['keywords'],
                content_template=blog_config['content_template'],
                author_persona=blog_config['author_persona'],
                brand_voice_profile=None,
                outline=outline,
                target_persona=persona
            )
            logger.info(f"✍️ Generated complete blog post: {blog_post.word_count} words")
            
            # 5. Get or create Shopify blog
            blog = await self.get_or_create_blog()
            
            # 6. Publish to Shopify
            article = await self.publish_to_shopify(blog_post, blog['id'])
            
            logger.info("✨ Blog generation and publishing completed successfully!")
            logger.info(f"📊 Article stats: {blog_post.word_count} words, {len(blog_post.tags)} tags")
            
            # Optional: Log additional metadata
            if persona:
                logger.info(f"🎯 Targeted for: {persona.name} ({persona.location})")
            
        except Exception as error:
            logger.error(f"❌ Error in blog generation process: {error}")
            
        finally:
            self.is_processing = False

    def start_scheduler(self):
        """Start the blog posting scheduler."""
        logger.info("🤖 Chamkili Auto Blog Poster starting with enhanced SDK...")
        logger.info(f"📅 Schedule: {self.config['schedule']['description']}")
        logger.info(f"🎯 Topics available: {len(self.config['blogSettings']['topics'])}")
        logger.info(f"🤖 AI Model: {self.config['gemini']['model']}")
        logger.info(f"🏪 Shopify Store: {self.config['shopify']['storeName']}")
        
        # Schedule the job (convert cron to schedule library format)
        # For now, let's use a simple interval - can be enhanced with proper cron parsing
        schedule.every(10).minutes.do(lambda: asyncio.run(self.generate_and_publish_blog()))
        
        # Generate first blog immediately
        logger.info("🎬 Generating first blog post...")
        asyncio.run(self.generate_and_publish_blog())
        
        logger.info("✅ Auto-poster is now running! Press Ctrl+C to stop.")
        
        # Main scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal. Shutting down gracefully...")
        except Exception as error:
            logger.error(f"❌ Scheduler error: {error}")

    async def test_connection(self):
        """Test all connections and configurations."""
        logger.info("🔍 Testing connections...")
        
        try:
            # Test Gemini connection
            test_topics = await gemini_service.get_trending_topics()
            logger.info(f"✅ Gemini AI: Connected - {len(test_topics)} trending topics found")
            
            # Test Shopify connection  
            blogs = await self.shopify_request('blogs.json')
            logger.info(f"✅ Shopify: Connected - {len(blogs.get('blogs', []))} blogs found")
            
            return True
            
        except Exception as error:
            logger.error(f"❌ Connection test failed: {error}")
            return False


def main():
    """Main entry point."""
    poster = AutoBlogPoster()
    
    # Test connections first
    if asyncio.run(poster.test_connection()):
        poster.start_scheduler()
    else:
        logger.error("❌ Connection tests failed. Please check your configuration.")
        exit(1)


if __name__ == "__main__":
    main()
