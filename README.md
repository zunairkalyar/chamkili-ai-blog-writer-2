# Chamkili AI Blog Writer

An intelligent blog writing system powered by AI that automatically generates and publishes content to Shopify stores.

## Features

- AI-powered blog content generation
- Automatic publishing to Shopify
- SEO optimization
- Multiple content templates
- Brand voice customization

## Tech Stack

- React + TypeScript
- Vite
- Tailwind CSS
- Google Gemini AI (JavaScript & Python SDKs)
- Shopify Admin API
- Python (Enhanced AI service)
- Pydantic (Structured data validation)

## Setup

### 1. Environment Variables

For security reasons, API credentials are stored in environment variables. Follow these steps:

1. Copy the environment template:
   ```bash
   cp .env.example .env.local
   ```

2. Edit `.env.local` and replace placeholders with your actual API credentials:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_api_key
   SHOPIFY_STORE_NAME=your_actual_store_name
   SHOPIFY_ACCESS_TOKEN=your_actual_shopify_access_token
   ```

### 2. Installation

**Prerequisites:** Node.js

```bash
npm install
```

### 3. Development

```bash
npm run dev
```

### 4. Auto-Poster (Optional)

#### JavaScript Version (Original)
```bash
node auto-poster.js
```

#### Python Version (Enhanced) 🆕

The new Python service offers structured outputs and improved reliability:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Test the enhanced service
python test_gemini_service.py

# Run the enhanced auto-poster
python auto_poster.py
```

**Key improvements in Python version:**
- ✅ Structured JSON outputs with Pydantic validation
- ✅ Better error handling and fallbacks
- ✅ Customer persona generation for Pakistani market
- ✅ Enhanced SEO analysis and recommendations
- ✅ Comprehensive logging and debugging

📖 [Full Python Setup Guide](PYTHON_SETUP.md)

## Important Security Notes

- Never commit your `.env.local` file to version control
- The `.env.local` file is already included in `.gitignore`
- When deploying to Vercel, set your environment variables in the Vercel dashboard
- All placeholder values in configuration files have been sanitized for security
