from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Blog Generator API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class BlogRequest(BaseModel):
    topic: str
    category: str
    length: str = "medium"
    tone: str = "informative"
    target_audience: str = "general"
    include_seo: bool = True

class BlogResponse(BaseModel):
    title: str
    content: str
    word_count: int
    category: str
    estimated_read_time: int

# Hugging Face configuration
HF_API_KEY = os.getenv("HF_API_KEY", "HF_API_KEY=")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

# Alternative models you can use:
# "microsoft/DialoGPT-medium" - Good for conversational text
# "gpt2" - Classic GPT-2
# "EleutherAI/gpt-j-6B" - Larger model, better quality
# "facebook/blenderbot-400M-distill" - Good for content generation

# Blog categories
CATEGORIES = [
    "Technology", "Health & Wellness", "Travel", "Food & Cooking", 
    "Lifestyle", "Business", "Education", "Entertainment", "Sports",
    "Science", "Politics", "Finance", "Fashion", "Home & Garden"
]

# Length configurations
LENGTH_CONFIG = {
    "short": {"words": "300-500", "prompt_modifier": "Keep it concise and to the point."},
    "medium": {"words": "800-1200", "prompt_modifier": "Provide comprehensive coverage with good detail."},
    "long": {"words": "1500-2500", "prompt_modifier": "Write an in-depth, detailed article with multiple sections."}
}

def create_blog_prompt(request: BlogRequest) -> str:
    """Create a detailed prompt for Grok AI"""
    length_info = LENGTH_CONFIG.get(request.length, LENGTH_CONFIG["medium"])
    
    seo_instruction = "Include SEO-optimized headings and structure." if request.include_seo else ""
    
    prompt = f"""Write a high-quality blog post about "{request.topic}" for the {request.category} category.

Requirements:
- Target audience: {request.target_audience}
- Tone: {request.tone}
- Length: {length_info['words']} words
- {length_info['prompt_modifier']}
- {seo_instruction}

Structure the blog post with:
1. An engaging title
2. Introduction that hooks the reader
3. Main content with clear headings and subheadings
4. Conclusion that summarizes key points
5. Use markdown formatting for headings, bold text, and lists where appropriate

Make it engaging, informative, and well-structured. Focus on providing value to readers."""

    return prompt

async def generate_blog_with_huggingface(prompt: str) -> str:
    """Generate blog content using Hugging Face free API"""
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # For better blog generation, let's use a more suitable model
    model_url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-j-6B"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1000,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(model_url, headers=headers, json=payload)
            
            # Debug information
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 503:
                # Model is loading, try with a different model
                fallback_url = "https://api-inference.huggingface.co/models/gpt2"
                response = await client.post(fallback_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_detail = response.text
                print(f"Error response: {error_detail}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Hugging Face API error: {response.status_code} - {error_detail}"
                )
            
            result = response.json()
            
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Remove the original prompt from the response
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                return generated_text
            else:
                return "Unable to generate blog content. Please try again."
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Hugging Face API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Alternative: Use OpenAI-compatible free services
async def generate_blog_with_free_api(prompt: str) -> str:
    """Generate blog using free alternatives"""
    # Option 1: Try Hugging Face first
    try:
        return await generate_blog_with_huggingface(prompt)
    except:
        # Option 2: Fallback to a simple template-based generation
        return generate_template_blog(prompt)

def generate_template_blog(prompt: str) -> str:
    """Generate a template-based blog when APIs are unavailable"""
    lines = prompt.lower().split('\n')
    topic = "Blog Topic"
    
    for line in lines:
        if 'topic' in line or 'about' in line:
            topic = line.split(':')[-1].strip() if ':' in line else line.strip()
            break
    
    return f"""# {topic.title()}

## Introduction

Welcome to this comprehensive guide about {topic}. In this blog post, we'll explore the key aspects and important considerations that make this topic relevant and interesting.

## What You Need to Know

Understanding {topic} requires looking at several important factors:

- **Background**: The foundation and context surrounding this subject
- **Current State**: Where things stand today and recent developments
- **Key Benefits**: The advantages and positive aspects
- **Challenges**: Potential obstacles and considerations
- **Future Outlook**: What to expect moving forward

## Main Content

### Getting Started

When approaching {topic}, it's important to start with the basics. This foundation will help you build a solid understanding of the core concepts.

### Key Considerations

There are several important factors to keep in mind:

1. **Research thoroughly** - Understanding the fundamentals is crucial
2. **Stay informed** - Keep up with latest developments and trends
3. **Practice regularly** - Apply what you learn to gain experience
4. **Connect with others** - Join communities and discussions

### Best Practices

To make the most of your journey with {topic}, consider these proven strategies:

- Set clear goals and expectations
- Take a systematic approach to learning
- Seek out reliable sources and expert opinions
- Be patient with the learning process

## Conclusion

{topic.title()} is a fascinating subject that offers many opportunities for learning and growth. By taking the time to understand the fundamentals and staying committed to continuous learning, you'll be well-positioned to succeed.

Remember that every expert was once a beginner, so don't be discouraged by initial challenges. With persistence and the right approach, you can master this topic and potentially help others along their journey.

---

*This blog post provides a comprehensive overview of {topic}. For more detailed information, consider exploring additional resources and connecting with experts in the field.*"""

def extract_title_from_content(content: str) -> str:
    """Extract title from the generated content"""
    lines = content.split('\n')
    for line in lines:
        if line.strip().startswith('#') and not line.strip().startswith('##'):
            return line.strip().lstrip('#').strip()
    return "Generated Blog Post"

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def estimate_read_time(word_count: int) -> int:
    """Estimate read time based on word count (avg 200 words per minute)"""
    return max(1, round(word_count / 200))

@app.get("/")
async def root():
    return {"message": "Blog Generator API is running!"}

@app.get("/categories")
async def get_categories():
    """Get available blog categories"""
    return {"categories": CATEGORIES}

@app.post("/generate-blog", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """Generate a blog post based on the request"""
    try:
        # Validate category
        if request.category not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        # Create prompt
        prompt = create_blog_prompt(request)
        
        # Generate blog content
        content = await generate_blog_with_free_api(prompt)
        
        # Extract title
        title = extract_title_from_content(content)
        
        # Calculate metrics
        word_count = count_words(content)
        read_time = estimate_read_time(word_count)
        
        return BlogResponse(
            title=title,
            content=content,
            word_count=word_count,
            category=request.category,
            estimated_read_time=read_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

@app.get("/test-api")
async def test_api_connection():
    """Test connection to Hugging Face API"""
    if not HF_API_KEY or HF_API_KEY == "your-hugging-face-api-key-here":
        return {
            "status": "no_api_key",
            "message": "No API key configured, will use template generation",
            "fallback": "template_based"
        }
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    simple_payload = {
        "inputs": "Write a short blog about technology:",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json=simple_payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "response": result,
                    "service": "huggingface"
                }
            else:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text,
                    "fallback": "template_based"
                }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fallback": "template_based"
        }

@app.get("/test-grok")
async def test_grok_connection():
    """Test connection to Grok API"""
    if not GROK_API_KEY or GROK_API_KEY == "your-grok-api-key-here":
        raise HTTPException(status_code=400, detail="Grok API key not configured")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    simple_payload = {
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is a test message. Please respond with 'API connection successful!'"
            }
        ],
        "model": "grok-beta",
        "max_tokens": 50
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROK_API_URL, headers=headers, json=simple_payload)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text
                }
            
            result = response.json()
            return {
                "status": "success",
                "response": result["choices"][0]["message"]["content"],
                "model": result.get("model", "unknown")
            }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "blog-generator-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)