"""
Enhanced Gemini AI service using the new Python SDK with structured outputs.
This provides more reliable and type-safe content generation.
"""

import os
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
import asyncio


# Configure the client - works with both Gemini Developer API and Vertex AI
client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY'),
    http_options={'api_version': 'v1beta'}
)

# Pydantic models for structured outputs
class OutlineBlock(BaseModel):
    id: str = Field(description="Unique identifier for the section")
    heading: str = Field(description="H2 heading for the section")
    key_points: str = Field(description="Markdown list of key points to cover")

class BlogOutline(BaseModel):
    sections: List[OutlineBlock] = Field(description="List of blog sections")

class SeoMetadata(BaseModel):
    meta_titles: List[str] = Field(description="3 SEO-optimized title options", min_length=3, max_length=3)
    meta_descriptions: List[str] = Field(description="3 SEO-optimized description options", min_length=3, max_length=3)

class FaqItem(BaseModel):
    question: str = Field(description="Frequently asked question")
    answer: str = Field(description="Clear, concise answer")

class SeoFaqData(BaseModel):
    meta_titles: List[str] = Field(min_length=3, max_length=3)
    meta_descriptions: List[str] = Field(min_length=3, max_length=3)
    faq: List[FaqItem] = Field(description="FAQ items")
    key_takeaways: List[str] = Field(description="Key takeaways from the article")

class CustomerPersona(BaseModel):
    name: str = Field(description="Pakistani name")
    age: int = Field(description="Age in years", ge=18, le=65)
    occupation: str = Field(description="Job or occupation")
    location: str = Field(description="Pakistani city")
    skincare_goals: List[str] = Field(description="What they want to achieve")
    pain_points: List[str] = Field(description="Their skincare struggles")
    motivations: List[str] = Field(description="What drives their purchasing decisions")
    personality: str = Field(description="Personality summary")
    bio: str = Field(description="Brief bio bringing the persona to life")

class TrendingTopic(BaseModel):
    topic: str = Field(description="Trending skincare topic")
    reason: str = Field(description="Why it's trending")

class TrendingTopics(BaseModel):
    topics: List[TrendingTopic] = Field(min_length=5, max_length=5)

class CalendarTopic(BaseModel):
    date: str = Field(description="Target publish date in YYYY-MM-DD format")
    title: str = Field(description="SEO-friendly blog post title")
    keywords: str = Field(description="Comma-separated SEO keywords")
    content_type: str = Field(description="Content template type")
    notes: str = Field(description="Strategic angle or hook")

class ContentCalendar(BaseModel):
    topics: List[CalendarTopic] = Field(min_length=8, max_length=10)

class SeoScore(BaseModel):
    score: int = Field(description="SEO score from 0-100", ge=0, le=100)
    recommendations: List[str] = Field(description="Actionable SEO recommendations")

class CompetitorAnalysis(BaseModel):
    strengths: List[str] = Field(description="What the competitor does well")
    weaknesses: List[str] = Field(description="Where the competitor falls short")
    content_gap_opportunities: List[str] = Field(description="Topics they missed")
    suggested_outline: List[OutlineBlock] = Field(description="Better article outline")

# Blog post generation with streaming
class StreamBlock(BaseModel):
    type: str = Field(description="Type: 'html' or 'image_suggestion'")
    content: str = Field(description="HTML content or image prompt")

class BlogPost(BaseModel):
    title: str = Field(description="Main blog post title")
    content: str = Field(description="Full HTML content")
    meta_title: str = Field(description="SEO meta title")
    meta_description: str = Field(description="SEO meta description")
    tags: List[str] = Field(description="Relevant tags")
    word_count: int = Field(description="Approximate word count")

class GeminiService:
    """Enhanced Gemini service with structured outputs."""
    
    def __init__(self):
        self.model_name = "gemini-2.0-flash-exp"
        self.product_links = [
            'https://www.chamkili.com/products/vitamin-c-skin-serum',
            'https://www.chamkili.com/products/niacinamide-zinc-skin-serum'
        ]
    
    async def generate_blog_outline(
        self, 
        title: str, 
        keywords: str = "", 
        content_template: str = "Standard Blog Post",
        author_persona: str = "Beauty Expert",
        brand_voice_profile: Optional[str] = None,
        target_persona: Optional[CustomerPersona] = None
    ) -> List[OutlineBlock]:
        """Generate a structured blog post outline."""
        
        # Build context prompts
        keywords_prompt = f'Target SEO keywords: "{keywords}"' if keywords else ''
        brand_voice_prompt = f'Brand Voice: {brand_voice_profile}' if brand_voice_profile else ''
        persona_prompt = ''
        if target_persona:
            persona_prompt = f'Target Audience: Write for {target_persona.name}, {target_persona.age}, who wants to {", ".join(target_persona.skincare_goals[:2])}'
        
        prompt = f"""You are a strategic content planner for Chamkili, a Pakistani skincare brand.
Your persona: "{author_persona}"

Create a detailed blog post outline for: "{title}"
{keywords_prompt}
{brand_voice_prompt}
{persona_prompt}

Template: {content_template}

Requirements:
1. Create 4-6 logical sections with H2 headings
2. Include Introduction and Conclusion
3. Each section should have 3-4 key points
4. Focus on Pakistani skincare needs and climate
5. Incorporate Chamkili product opportunities

Return as structured JSON with sections array."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=BlogOutline,
                    temperature=0.7,
                    top_p=0.9,
                )
            )
            
            outline_data = BlogOutline.model_validate_json(response.text)
            return outline_data.sections
            
        except Exception as error:
            print(f"Error generating outline: {error}")
            # Fallback outline
            return [
                OutlineBlock(
                    id="intro",
                    heading="Introduction", 
                    key_points="- Hook the reader\n- Introduce the topic\n- Preview main points"
                ),
                OutlineBlock(
                    id="main1",
                    heading="Understanding the Basics",
                    key_points="- Define key concepts\n- Explain importance\n- Pakistani context"
                ),
                OutlineBlock(
                    id="main2", 
                    heading="Step-by-Step Guide",
                    key_points="- Detailed instructions\n- Tips and tricks\n- Common mistakes"
                ),
                OutlineBlock(
                    id="conclusion",
                    heading="Conclusion",
                    key_points="- Summarize key points\n- Product recommendations\n- Call to action"
                )
            ]

    async def generate_full_blog_post(
        self,
        title: str,
        tone: str,
        keywords: str,
        content_template: str,
        author_persona: str,
        brand_voice_profile: Optional[str],
        outline: List[OutlineBlock],
        target_persona: Optional[CustomerPersona] = None
    ) -> BlogPost:
        """Generate a complete blog post with structured output."""
        
        # Build context
        keywords_prompt = f'Naturally incorporate keywords: "{keywords}"' if keywords else ''
        brand_voice_prompt = f'Brand Voice: {brand_voice_profile}' if brand_voice_profile else ''
        persona_context = ''
        if target_persona:
            persona_context = f'Write for {target_persona.name}: {target_persona.bio}'
        
        outline_text = "\n".join([f"## {section.heading}\n{section.key_points}" for section in outline])
        
        prompt = f"""You are {author_persona} writing for Chamkili, a Pakistani skincare brand.

Write a complete blog post:
Title: "{title}"
Tone: {tone}
{keywords_prompt}
{brand_voice_prompt}
{persona_context}

Article Outline:
{outline_text}

Products to feature:
- Vitamin C Serum: {self.product_links[0]}
- Niacinamide Serum: {self.product_links[1]}

Requirements:
1. Write 500-700 words
2. Use HTML formatting (h1, h2, p, ul, li, a tags)
3. Include product links naturally
4. SEO-optimized for Pakistani audience
5. Include compelling meta title and description
6. Add relevant tags

Return complete structured blog post."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=BlogPost,
                    temperature=0.6,
                    top_p=0.95,
                )
            )
            
            return BlogPost.model_validate_json(response.text)
            
        except Exception as error:
            print(f"Error generating blog post: {error}")
            raise Exception(f"Failed to generate blog content: {error}")

    async def generate_seo_and_faq(
        self, 
        blog_content: str, 
        blog_title: str, 
        keywords: str = ""
    ) -> SeoFaqData:
        """Generate SEO metadata and FAQ with structured output."""
        
        keywords_prompt = f'Target keywords: "{keywords}"' if keywords else ''
        # Strip HTML and limit content length
        clean_content = blog_content.replace('<', ' <').replace('>', '> ')[:4000]
        
        prompt = f"""Based on this blog post, generate SEO metadata and FAQ:

Title: "{blog_title}"
{keywords_prompt}

Content: {clean_content}

Generate:
1. 3 compelling meta titles (under 60 chars each)
2. 3 engaging meta descriptions (under 160 chars each)  
3. 3-4 relevant FAQ items with clear answers
4. 3-4 key takeaways

Focus on Pakistani skincare audience and search intent."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=SeoFaqData,
                    temperature=0.7,
                )
            )
            
            return SeoFaqData.model_validate_json(response.text)
            
        except Exception as error:
            print(f"Error generating SEO/FAQ: {error}")
            # Return fallback
            return SeoFaqData(
                meta_titles=[blog_title[:57] + "..."] * 3,
                meta_descriptions=[f"Learn about {blog_title.lower()} with expert tips."] * 3,
                faq=[],
                key_takeaways=[f"Key insights about {blog_title.lower()}"]
            )

    async def generate_customer_persona(self, description: str) -> CustomerPersona:
        """Generate a detailed customer persona."""
        
        prompt = f"""Create a detailed customer persona for a Pakistani skincare brand.

Target audience description: "{description}"

Generate a realistic persona with:
- Pakistani name and details
- Age, occupation, location (major Pakistani city)
- Specific skincare goals and pain points
- Purchase motivations
- Personality traits
- Engaging bio

Make it authentic and relatable to the Pakistani market."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=CustomerPersona,
                    temperature=0.8,
                )
            )
            
            return CustomerPersona.model_validate_json(response.text)
            
        except Exception as error:
            print(f"Error generating persona: {error}")
            raise Exception(f"Failed to generate customer persona: {error}")

    async def get_trending_topics(self) -> List[TrendingTopic]:
        """Get trending skincare topics for Pakistan."""
        
        prompt = """Identify 5 trending skincare topics for Pakistani women right now.

Consider:
- Seasonal factors (weather, humidity)
- Popular social media trends
- Local ingredients and remedies
- Common skin concerns in Pakistan
- Emerging skincare science

For each topic, explain why it's trending."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=TrendingTopics,
                    temperature=0.8,
                )
            )
            
            trending_data = TrendingTopics.model_validate_json(response.text)
            return trending_data.topics
            
        except Exception as error:
            print(f"Error getting trending topics: {error}")
            return []

    async def generate_content_calendar(
        self,
        goal: str,
        month: str,
        persona: Optional[CustomerPersona] = None,
        brand_voice_profile: Optional[str] = None
    ) -> List[CalendarTopic]:
        """Generate a content calendar for the month."""
        
        persona_context = ''
        if persona:
            persona_context = f'Target persona: {persona.name} - {persona.bio}'
        
        brand_voice_context = f'Brand voice: {brand_voice_profile}' if brand_voice_profile else ''
        
        prompt = f"""Create a strategic content calendar for {month}.

Goal: "{goal}"
{persona_context}
{brand_voice_context}

Generate 8-10 diverse blog post ideas for Chamkili:
1. Distribute logically throughout the month
2. Mix content types: guides, product focus, seasonal topics
3. Include SEO-friendly titles and keywords
4. Strategic notes for each post

Focus on Pakistani skincare market and seasonal relevance."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=ContentCalendar,
                    temperature=0.7,
                )
            )
            
            calendar_data = ContentCalendar.model_validate_json(response.text)
            return calendar_data.topics
            
        except Exception as error:
            print(f"Error generating content calendar: {error}")
            return []

    async def get_seo_score(self, html_content: str, keywords: str) -> SeoScore:
        """Analyze content and provide SEO score with recommendations."""
        
        clean_content = html_content.replace('<', ' <').replace('>', '> ')[:4000]
        
        prompt = f"""Analyze this blog post for SEO performance.

Target keywords: "{keywords}"
Content: {clean_content}

Evaluate:
1. Keyword usage and density
2. Content structure and readability  
3. Title and heading optimization
4. Content depth and relevance
5. Pakistani market alignment

Provide score (0-100) and actionable recommendations."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=SeoScore,
                    temperature=0.3,
                )
            )
            
            return SeoScore.model_validate_json(response.text)
            
        except Exception as error:
            print(f"Error analyzing SEO: {error}")
            return SeoScore(score=50, recommendations=["Unable to analyze content"])

    async def analyze_brand_voice(self, text: str) -> str:
        """Analyze brand voice from sample text."""
        
        prompt = f"""Analyze the brand voice in this text:

{text[:4000]}

Write a concise brand voice profile that describes:
- Tone and personality
- Language style and vocabulary  
- Sentence structure patterns
- Key characteristics

This will be used to guide future AI content generation."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                )
            )
            
            return response.text
            
        except Exception as error:
            print(f"Error analyzing brand voice: {error}")
            return "Warm, knowledgeable, and approachable tone with clear, practical advice."

    async def repurpose_content(
        self,
        blog_content: str,
        platform: str,
        brand_voice_profile: Optional[str] = None,
        persona: Optional[CustomerPersona] = None
    ) -> str:
        """Repurpose blog content for different social platforms."""
        
        platform_instructions = {
            'twitter': """Create a Twitter thread (1/5, 2/5, etc.):
- Hook in first tweet
- Key points in subsequent tweets  
- Emojis and hashtags (#Skincare #Beauty #Pakistan)
- Under 280 chars per tweet""",
            
            'linkedin': """Create a professional LinkedIn post:
- Strong opening question/statement
- Bullet points for readability
- Professional value angle
- Discussion-driving question
- 3-5 relevant hashtags""",
            
            'instagram': """Create an Instagram caption:
- Captivating hook
- Emojis for visual appeal
- Short paragraphs for mobile
- Clear call-to-action
- 5-10 hashtags (#Chamkili #PakistaniSkincare #GlowUp)""",
            
            'email': """Create email newsletter content:
- Compelling subject line
- Personal greeting
- Scannable summary format
- Clear CTA button text"""
        }
        
        brand_context = f'Brand voice: {brand_voice_profile}' if brand_voice_profile else ''
        persona_context = f'Writing for: {persona.name} - {persona.bio}' if persona else ''
        
        prompt = f"""Repurpose this blog content for {platform}:

{brand_context}
{persona_context}

{platform_instructions.get(platform, 'Create engaging social content')}

Original content: {blog_content[:5000]}

Create platform-optimized content that maintains the core message."""

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                )
            )
            
            return response.text
            
        except Exception as error:
            print(f"Error repurposing content: {error}")
            return f"Error repurposing content for {platform}"

# Create global instance
gemini_service = GeminiService()

# Export main functions for compatibility with existing code
async def generate_blog_outline(*args, **kwargs):
    return await gemini_service.generate_blog_outline(*args, **kwargs)

async def generate_full_blog_post(*args, **kwargs):
    return await gemini_service.generate_full_blog_post(*args, **kwargs)

async def generate_seo_and_faq(*args, **kwargs):
    return await gemini_service.generate_seo_and_faq(*args, **kwargs)

async def generate_customer_persona(*args, **kwargs):
    return await gemini_service.generate_customer_persona(*args, **kwargs)

async def get_trending_topics(*args, **kwargs):
    return await gemini_service.get_trending_topics(*args, **kwargs)

async def generate_content_calendar(*args, **kwargs):
    return await gemini_service.generate_content_calendar(*args, **kwargs)

async def get_seo_score(*args, **kwargs):
    return await gemini_service.get_seo_score(*args, **kwargs)

async def analyze_brand_voice(*args, **kwargs):
    return await gemini_service.analyze_brand_voice(*args, **kwargs)

async def repurpose_content(*args, **kwargs):
    return await gemini_service.repurpose_content(*args, **kwargs)
