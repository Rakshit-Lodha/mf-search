# AI-Powered Mutual Fund Search

Intelligent fund discovery using semantic search and GPT-4o reasoning. 
Searches 16,000+ Indian mutual funds with natural language queries.

**Live Demo:** [https://mf-search.streamlit.app](https://mf-ai-search.streamlit.app/)

## Features

**Smart Intent Detection**
- Automatically routes queries to single search, comparison, or filtered mode
- Handles typos and fuzzy matching ("parag parikh" finds "Parag Parikh Flexi Cap")

**Semantic Search**
- ChromaDB vector embeddings for intelligent matching
- Works with partial names, categories, investment styles

**AI-Powered Analysis**
- GPT-4o provides investment recommendations
- Analyzes returns, risk, expense ratios
- Professional financial advisor tone

**Three Search Modes**
- Single fund lookup and analysis
- Side-by-side fund comparison
- Filtered search by category, market cap, risk

## How It Works

1. **User enters natural language query**
   - "Is Parag Parikh Flexi Cap good?"
   - "Compare HDFC vs ICICI large cap"
   - "Top performing large cap funds"

2. **LLM classifies intent** (GPT-4o-mini)
   - Determines search mode
   - Extracts fund names and filters

3. **Semantic search** (ChromaDB + OpenAI embeddings)
   - Finds relevant funds from 16K+ database
   - Handles misspellings and variations

4. **AI generates response** (GPT-4o)
   - Analyzes fund metrics
   - Provides recommendation with reasoning
   - Professional, unbiased tone
  

## Tech Stack

- **Frontend:** Streamlit
- **Vector DB:** ChromaDB (persistent)
- **Embeddings:** OpenAI text-embedding-3-small
- **LLM:** GPT-4o, GPT-4o-mini
- **Data:** 16,197 Indian mutual funds (synthetic for demo)
- **Deployment:** Streamlit Cloud

## Screenshot

<img width="2586" height="1816" alt="Screenshot 2025-12-07 at 7 33 12 PM" src="https://github.com/user-attachments/assets/cf376e22-1f4c-4073-bf84-be9ee586b83b" />


## Try It

**Live Demo:** [https://mf-search.streamlit.app](https://mf-ai-search.streamlit.app/)

**Example queries:**
- "Is Parag Parikh Flexi Cap a good fund?"
- "Compare HDFC Balanced Advantage vs ICICI Prudential Balanced Advantage"
- "Top 5 large cap equity funds"

## Run Locally
```bash
git clone https://github.com/Rakshit-Lodha/mf-search
cd mf-search
pip install -r requirements.txt

# Add your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

streamlit run app.py
```





