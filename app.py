import streamlit as st
import os
from dotenv import load_dotenv

# Import your search functions
from seach import query_router, query_json_conversion

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI MF Search",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🔍 AI Mutual Fund Search</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent fund discovery powered by AI</p>', unsafe_allow_html=True)

# Main search interface
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input(
        "Search mutual funds:",
        placeholder="e.g., 'Is Parag Parikh Flexi Cap good?' or 'Compare HDFC vs ICICI large cap'",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔎 Search", type="primary", use_container_width=True)

# Example queries (clickable)
st.caption("💡 Quick examples:")
example_cols = st.columns(3)
with example_cols[0]:
    if st.button("📊 Single fund search", use_container_width=True):
        query = "Is Parag Parikh Flexi Cap a good fund?"
        search_button = True
with example_cols[1]:
    if st.button("⚖️ Compare funds", use_container_width=True):
        query = "Compare UTI Nifty 200 vs Parag Parikh Flexicap"
        search_button = True
with example_cols[2]:
    if st.button("🔍 Filtered search", use_container_width=True):
        query = "Best large cap funds"
        search_button = True

st.markdown("---")

# Search execution
if search_button and query:
    # Show what we're doing
    with st.spinner("🤖 Understanding your query..."):
        try:
            intent = query_json_conversion(query)
            
            # Show detected intent
            mode_emoji = {
                "single": "📊",
                "comparison": "⚖️",
                "filtered": "🔍"
            }
            st.info(f"{mode_emoji.get(intent['mode'], '🤖')} Detected: **{intent['mode'].upper()}** search")
            
        except Exception as e:
            st.error(f"❌ Error detecting intent: {str(e)}")
            st.stop()
    
    # Execute search
    with st.spinner("🔎 Searching 16,197 mutual funds..."):
        try:
            result = query_router(query)
            
            # Display results
            st.markdown("### 📈 Results")
            st.markdown(result)
            
            # Footer info
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("💡 Powered by semantic search (ChromaDB) + GPT-4o")
            with col2:
                st.caption("⚠️ Fund metrics are synthetic for demo purposes")
                
        except Exception as e:
            st.error(f"❌ Error during search: {str(e)}")
            with st.expander("🔍 Debug info"):
                st.write(f"Query: {query}")
                st.write(f"Intent: {intent}")
                st.write(f"Error: {str(e)}")

elif search_button:
    st.warning("⚠️ Please enter a search query")

# Sidebar
with st.sidebar:
    st.markdown("### 📝 Example Queries")
    
    st.markdown("**Single Fund Search:**")
    st.code("Is Parag Parikh Flexi Cap good?", language=None)
    st.code("Tell me about HDFC Balanced Advantage", language=None)
    st.code("How is Axis Bluechip performing?", language=None)
    
    st.markdown("**Compare Funds:**")
    st.code("Compare UTI Nifty 200 vs Parag Parikh", language=None)
    st.code("HDFC vs ICICI large cap - which is better?", language=None)
    # st.code("Compare 3 best large cap funds", language=None)
    
    st.markdown("**Filtered Search:**")
    st.code("Top large cap funds", language=None)
    st.code("Top mid cap funds", language=None)
    st.code("Top small cap funds", language=None)
    
    st.markdown("---")
    
    st.markdown("### 📊 System Info")
    st.metric("Total Funds", "16,197")
    st.metric("Search Modes", "3")
    st.caption("• Single fund analysis")
    st.caption("• Multi-fund comparison")
    st.caption("• Filtered search")
    
    st.markdown("---")
    
    st.markdown("### 👨‍💻 About")
    st.caption("Built by **Rakshit Lodha**")