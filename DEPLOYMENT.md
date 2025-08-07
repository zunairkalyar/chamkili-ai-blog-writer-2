# Vercel Deployment Guide

🚀 Deploy your enhanced Chamkili AI Blog Writer to Vercel with both JavaScript and Python capabilities.

## 📋 Pre-Deployment Checklist

### ✅ **Environment Variables Required**
You'll need to set these in your Vercel dashboard:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `SHOPIFY_STORE_NAME` - Your Shopify store name (e.g., 'uxxpvu-hd')  
- `SHOPIFY_ACCESS_TOKEN` - Your Shopify Admin API access token

### ✅ **Project Structure** 
```
chamkili-ai-blog-writer-2/
├── api/                          # Serverless functions
│   ├── generate-blog.py          # Python Gemini service
│   ├── shopify-proxy.js          # Shopify API proxy  
│   ├── test-shopify.js           # Shopify connection test
│   └── requirements.txt          # Python dependencies
├── services/
│   ├── gemini_service.py         # Enhanced Python service
│   └── geminiService.ts          # Original TypeScript service
├── dist/                         # Built frontend (auto-generated)
├── vercel.json                   # Vercel configuration
└── package.json                  # Node.js dependencies
```

## 🚀 Deployment Steps

### **Method 1: Vercel CLI (Recommended)**

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from Project Directory**
   ```bash
   # From your project root
   vercel
   
   # Follow the prompts:
   # ? Set up and deploy "~/chamkili-ai-blog-writer-2"? [Y/n] y
   # ? Which scope do you want to deploy to? [Your account]
   # ? What's your project's name? chamkili-ai-blog-writer
   # ? In which directory is your code located? ./
   ```

4. **Set Environment Variables**
   ```bash
   # Add your API keys
   vercel env add GEMINI_API_KEY
   vercel env add SHOPIFY_STORE_NAME  
   vercel env add SHOPIFY_ACCESS_TOKEN
   
   # Choose "Production" for each when prompted
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

### **Method 2: GitHub Integration**

1. **Push to GitHub** (already done ✅)
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import from GitHub: `zunairkalyar/chamkili-ai-blog-writer-2`
   - Configure project settings:
     - Framework: **Vite**
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **Set Environment Variables in Dashboard**
   - Go to Project Settings → Environment Variables
   - Add:
     - `GEMINI_API_KEY` = your_actual_api_key
     - `SHOPIFY_STORE_NAME` = your_store_name  
     - `SHOPIFY_ACCESS_TOKEN` = your_access_token

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy

## 🧪 Testing Your Deployment

### **1. Test Frontend**
Visit your Vercel URL (e.g., `https://chamkili-ai-blog-writer.vercel.app`)

### **2. Test Python API Endpoint**
```bash
# Check if Python service is running
curl https://your-deployment-url.vercel.app/api/generate-blog

# Generate a blog post
curl -X POST https://your-deployment-url.vercel.app/api/generate-blog \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_blog",
    "title": "Best Vitamin C Serums for Pakistani Skin",
    "keywords": "vitamin c serum, Pakistani skincare",
    "tone": "Professional"
  }'
```

### **3. Test Shopify Integration**
```bash
# Test Shopify connection
curl https://your-deployment-url.vercel.app/api/test-shopify
```

## 📊 API Endpoints Available

### **Python Enhanced Service**
- `GET /api/generate-blog` - Service status
- `POST /api/generate-blog` - Enhanced blog generation

**Request body options:**
```json
{
  "action": "generate_blog",        // generate_blog, generate_outline, generate_persona, trending_topics
  "title": "Your Blog Title",
  "keywords": "relevant keywords",
  "tone": "Professional",           // Professional, Warm & Friendly, Empathetic
  "content_template": "Standard Blog Post",
  "author_persona": "Beauty Expert",
  "target_audience": "Pakistani women aged 20-35",
  "brand_voice": "Optional brand voice description"
}
```

### **JavaScript Legacy Endpoints** 
- `POST /api/shopify-proxy` - Shopify API proxy
- `GET /api/test-shopify` - Shopify connection test

## 🔧 Configuration Details

### **vercel.json Explained**
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"      // Python serverless functions
    },
    "api/**/*.js": {  
      "runtime": "nodejs18.x"     // Node.js serverless functions
    }
  }
}
```

### **Environment Variables in Production**
```bash
# These are automatically available to your functions:
process.env.GEMINI_API_KEY        // Node.js
os.getenv('GEMINI_API_KEY')       // Python
```

## 🐛 Troubleshooting

### **Common Issues**

1. **"Module not found" errors**
   - Check `api/requirements.txt` has all Python dependencies
   - Verify `package.json` has all Node.js dependencies

2. **Environment variables not working**
   ```bash
   # Check if variables are set:
   vercel env list
   
   # Add missing variables:
   vercel env add VARIABLE_NAME
   ```

3. **Python import errors**
   - Ensure `services/` directory is at project root
   - Check Python path in `api/generate-blog.py`

4. **Shopify API timeouts**
   - Verify your access tokens are correct
   - Check store name format (no `.myshopify.com`)

### **Debug Commands**
```bash
# View deployment logs
vercel logs

# Run local development
vercel dev

# Check function status  
vercel functions list
```

## 📈 Performance Optimization

### **Serverless Function Limits**
- **Execution time**: 10 seconds (Hobby), 60 seconds (Pro)
- **Memory**: 1024 MB
- **Payload size**: 4.5 MB

### **Optimization Tips**
1. **Cache responses** where possible
2. **Minimize dependencies** in `api/requirements.txt`
3. **Use environment variables** for configuration
4. **Handle timeouts gracefully** for AI generation

## 🔄 Continuous Deployment

Once set up, your deployment will:
- ✅ **Auto-deploy on Git push** to main branch
- ✅ **Preview deployments** for pull requests  
- ✅ **Environment variable sync** across deployments
- ✅ **Both Python and JavaScript** function support

## 🎯 Next Steps After Deployment

1. **Test all endpoints** with real data
2. **Monitor function logs** for errors
3. **Set up domain** (optional): Project Settings → Domains
4. **Configure webhooks** for Shopify integration (optional)

---

🚀 **Your enhanced Chamkili AI Blog Writer is now live on Vercel with both JavaScript and Python capabilities!**

### **URLs to Save:**
- **Frontend**: `https://your-project.vercel.app`
- **Python API**: `https://your-project.vercel.app/api/generate-blog`
- **Shopify Test**: `https://your-project.vercel.app/api/test-shopify`
