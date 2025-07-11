import streamlit as st
import requests
import json
import time
from datetime import datetime
import markdown
from io import BytesIO

# Configure Streamlit page
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .blog-preview {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .metric-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'generated_blog' not in st.session_state:
    st.session_state.generated_blog = None
if 'blog_history' not in st.session_state:
    st.session_state.blog_history = []

def fetch_categories():
    """Fetch available categories from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/categories")
        if response.status_code == 200:
            return response.json()["categories"]
        else:
            return ["Technology", "Health & Wellness", "Travel", "Food & Cooking", 
                   "Lifestyle", "Business", "Education", "Entertainment"]
    except:
        return ["Technology", "Health & Wellness", "Travel", "Food & Cooking", 
               "Lifestyle", "Business", "Education", "Entertainment"]

def generate_blog_post(topic, category, length, tone, target_audience, include_seo):
    """Generate blog post via API"""
    payload = {
        "topic": topic,
        "category": category,
        "length": length,
        "tone": tone,
        "target_audience": target_audience,
        "include_seo": include_seo
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/generate-blog", json=payload, timeout=60)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection Error: {str(e)}"

def save_blog_to_history(blog_data, topic, category):
    """Save generated blog to history"""
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic,
        "category": category,
        "title": blog_data.get("title", "Untitled"),
        "word_count": blog_data.get("word_count", 0),
        "content": blog_data.get("content", "")
    }
    st.session_state.blog_history.append(history_entry)
    # Keep only last 10 entries
    if len(st.session_state.blog_history) > 10:
        st.session_state.blog_history = st.session_state.blog_history[-10:]

def export_blog_as_markdown(blog_data, topic):
    """Export blog as markdown file"""
    content = f"# {blog_data.get('title', 'Blog Post')}\n\n"
    content += f"**Topic:** {topic}\n"
    content += f"**Category:** {blog_data.get('category', 'N/A')}\n"
    content += f"**Word Count:** {blog_data.get('word_count', 0)}\n"
    content += f"**Estimated Read Time:** {blog_data.get('estimated_read_time', 0)} minutes\n\n"
    content += "---\n\n"
    content += blog_data.get('content', '')
    
    return content

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Blog Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2em;">Generate high-quality blog posts using AI in seconds!</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    st.sidebar.header("📝 Blog Configuration")
    
    # Fetch categories
    categories = fetch_categories()
    
    # Topic input
    topic = st.sidebar.text_input(
        "Blog Topic",
        placeholder="Enter your blog topic here...",
        help="What would you like to write about?"
    )
    
    # Category selection
    category = st.sidebar.selectbox(
        "Category",
        categories,
        help="Select the category that best fits your blog topic"
    )
    
    # Blog length
    length = st.sidebar.select_slider(
        "Blog Length",
        options=["short", "medium", "long"],
        value="medium",
        help="Short: 300-500 words | Medium: 800-1200 words | Long: 1500-2500 words"
    )
    
    # Tone selection
    tone = st.sidebar.selectbox(
        "Writing Tone",
        ["informative", "casual", "professional", "friendly", "persuasive", "humorous"],
        help="Choose the tone for your blog post"
    )
    
    # Target audience
    target_audience = st.sidebar.selectbox(
        "Target Audience",
        ["general", "beginners", "experts", "professionals", "students", "seniors"],
        help="Who is your target audience?"
    )
    
    # SEO optimization
    include_seo = st.sidebar.checkbox(
        "Include SEO Optimization",
        value=True,
        help="Add SEO-friendly headings and structure"
    )
    
    # Generate button
    if st.sidebar.button("🚀 Generate Blog Post", type="primary"):
        if not topic.strip():
            st.sidebar.error("Please enter a blog topic!")
        else:
            with st.spinner("🤖 Generating your blog post... This may take a moment."):
                blog_data, error = generate_blog_post(
                    topic, category, length, tone, target_audience, include_seo
                )
                
                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.session_state.generated_blog = blog_data
                    save_blog_to_history(blog_data, topic, category)
                    st.success("✅ Blog post generated successfully!")
                    st.rerun()
    
    # Main content area
    if st.session_state.generated_blog:
        blog_data = st.session_state.generated_blog
        
        # Blog metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Word Count", blog_data.get("word_count", 0))
        with col2:
            st.metric("⏱️ Read Time", f"{blog_data.get('estimated_read_time', 0)} min")
        with col3:
            st.metric("📂 Category", blog_data.get("category", "N/A"))
        with col4:
            st.metric("📝 Title Length", len(blog_data.get("title", "")))
        
        # Blog preview
        st.markdown("## 📖 Blog Preview")
        
        # Title
        st.markdown(f"### {blog_data.get('title', 'Generated Blog Post')}")
        
        # Content
        st.markdown("---")
        st.markdown(blog_data.get("content", "No content generated."))
        
        # Export options
        st.markdown("## 📥 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Copy to clipboard button
            if st.button("📋 Copy to Clipboard"):
                st.code(blog_data.get("content", ""), language="markdown")
                st.success("Blog content displayed above - copy from the code block!")
        
        with col2:
            # Download as markdown
            markdown_content = export_blog_as_markdown(blog_data, topic)
            st.download_button(
                label="📥 Download as Markdown",
                data=markdown_content,
                file_name=f"blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    else:
        # Welcome message
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #666;">
            <h3>👋 Welcome to AI Blog Generator!</h3>
            <p>Configure your blog settings in the sidebar and click "Generate Blog Post" to get started.</p>
            <p>✨ Features:</p>
            <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                <li>Multiple categories and topics</li>
                <li>Customizable length and tone</li>
                <li>SEO optimization</li>
                <li>Export to Markdown</li>
                <li>Blog history tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Blog history in sidebar
    if st.session_state.blog_history:
        st.sidebar.markdown("---")
        st.sidebar.header("📚 Recent Blogs")
        
        for i, blog in enumerate(reversed(st.session_state.blog_history[-5:])):
            with st.sidebar.expander(f"📝 {blog['title'][:30]}..."):
                st.write(f"**Topic:** {blog['topic']}")
                st.write(f"**Category:** {blog['category']}")
                st.write(f"**Words:** {blog['word_count']}")
                st.write(f"**Created:** {blog['timestamp']}")
                
                if st.button(f"Load Blog {i+1}", key=f"load_{i}"):
                    st.session_state.generated_blog = {
                        "title": blog['title'],
                        "content": blog['content'],
                        "word_count": blog['word_count'],
                        "category": blog['category'],
                        "estimated_read_time": max(1, round(blog['word_count'] / 200))
                    }
                    st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9em;">'
        '🤖 Powered by Grok AI | Built with Streamlit & FastAPI'
        '</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()