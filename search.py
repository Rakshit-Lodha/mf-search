import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import json

load_dotenv()
# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chromadb_data")
collection = chroma_client.get_collection(name="mutual_funds")

def mf_query(text, output = 5):

    query_text = text

    print(query_text)

    if len(query_text.split()) <= 2:
        query_text = text + " mutual fund"

    query_conversion = create_embeddings([query_text])

    result = collection.query(
        query_embeddings = query_conversion,
        n_results = output
    )

    print(query_text)

    return result

def create_embeddings(text, batch_size = 500):
    all_embeddings = []

    for i in range(0,len(text), batch_size):
        batch = text[i:i+batch_size]

        embeddings = client.embeddings.create(
            model = "text-embedding-3-small",
            input = batch
        )

        batch_embeddings = [item.embedding for item in embeddings.data]

        all_embeddings.extend(batch_embeddings)

    return all_embeddings

# All your function definitions
def query_json_conversion(text):
    query = text
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role": "system", "content": f""" 
            You are a financial translator and your job is to convert the {query} into a JSON response for mutual fund search query. 
            
            Your task is as follows:
            1. Understand the user intent
            2. Extract the fund names, if you detect one. YOU'RE NOT SUPPOSED TO HALLCUINATE FUNDS
            3. If you detect more than 1 fund you're supposed to store all the funds as a list inside "funds"
            4. If the response to anything doesn't exist, we NEED to make it null and nothing else like none
            5. semantic_query MUST ONLY contain the user's investment theme or fund category.

            Examples of valid semantic_query:
            - "large cap"
            - "mid cap"
            - "small cap"
            - "momentum"
            - "index fund"
            - "bluechip"
            - "ELSS"
            - "international fund"
            
            INVALID semantic_query (set to null instead):
            - descriptions ("comparison of mutual funds")
            - meta-comments ("market investment timing")
            - generic words ("performance", "returns", "mutual fund")
            - summaries of the query
            - fund names (fund names go only in the funds list)
            
            If the user is asking for:
            - comparison → semantic_query = null
            - specific fund → semantic_query = null
            - vague/general financial question → semantic_query = null
            - theme-based search → semantic_query = the theme

            The JSON response needs to be as follows:
            {{
            "mode": "comparison | single | filtered",
            "funds": ["HDFC Top 100", "ICICI Bluechip Fund"],
            "semantic_query": "large cap",
            "filters": {{
            "min_1yr_return": 10,
            "min_3yr_return": null,
            "max_expense_ratio": 1.5,
            "category": "Mid Cap"
            }}
            }}

            Make sure that the JSON format is never broken regardless of anything. If there is something which does not fit, 
            you can make it null. For example even if filters don't exist, the JSON response needs to be:
            {{
            "mode": "comparison | single | filtered",
            "funds": ["HDFC Top 100", "ICICI Bluechip Fund"],
            "semantic_query": "large cap",
            "filters": {{
            "min_1yr_return": null,
            "min_3yr_return": null,
            "max_expense_ratio": null,
            "category": null
            }}
            }}
            """}
        ], temperature = 0, seed = 1
    )

    model_output = response.choices[0].message.content

    json_output = json.loads(model_output)

    return json_output
    
    
def single_fund_search(text):
    fund_name = text['funds'][0]
    mf_data = mf_query(fund_name,1)
    metadata = mf_data['metadatas'][0][0]

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": f""" 
            You are a financial advisor and based on the {text} of the user, you need to analyse the fund performance based on {metadata}.
            
            Rules:
            1. If it is a generic query about the fund. Eg: how is fund X doing, use the entire {metadata} output, to give a quality 2-3
            line output about how the fund is doing. 
            2. If it is a specific query related to the data present in {metadata}. Eg: Is Fund X's AUM greater than 2000Cr? Then, take
            that specific element and return output. 
            3. If a {metadata} DOES NOT EXIST, say that you don't have the required data for the same. DO NOT HALLUCINATE!


            Important Ground Rule:
            In case the {fund_name} contains a mutual fund which is not matching with funds gotten through {mf_data}, 
            then say that this fund does not exist.

            At the end of the answer ALWAYS inject the following line:

            The fund metrics are synthetic and for illustrative purpose ONLY and should not be used to make financial decisions. 
            """}
        ], temperature = 0.3, seed = 1
    )
    
    return response.choices[0].message.content
    
def comparison_fund_search(text):

    fund_data = []

    for i in text['funds']:
        fund_name = i
        mf_data = mf_query(fund_name,1)
        metadata = mf_data['metadatas'][0][0]

        fund_data.append(
            {
                "fund_name": fund_name,
                "metadata": metadata
            }
        )

    valid_funds = [f for f in fund_data if "metadata" in f]

    best_fund_1yr = max(
    valid_funds,
    key = lambda f: f['metadata'].get('1_Yr_Return')
    )

    best_fund_3yr = max(
    valid_funds,
    key = lambda f: f['metadata'].get('3_Yr_Return')
    )

    best_fund_5yr = max(
    valid_funds,
    key = lambda f: f['metadata'].get('5_Yr_Return')
    )

    best_fund_aum = max(
    valid_funds,
    key = lambda f: f['metadata'].get('aum')
    )

    best_fund_expense = min(
        valid_funds,
        key = lambda f: f['metadata'].get('expense_ratio')
    )


    summary = {
        "best_1yr_fund": best_fund_1yr['fund_name'],
        "best_1yr_return": best_fund_1yr['metadata'].get('1_Yr_Return'),
        "best_3yr_fund": best_fund_3yr['fund_name'],
        "best_3yr_return": best_fund_3yr['metadata'].get('3_Yr_Return'),
        "best_5yr_fund": best_fund_5yr['fund_name'],
        "best_5yr_return": best_fund_5yr['metadata'].get('5_Yr_Return'),
        "best_aum_fund": best_fund_aum['fund_name'],
        "best_aum_value": best_fund_aum['metadata'].get('aum'),
        "best_expense_fund": best_fund_expense['fund_name'],
        "best_expense_value": best_fund_expense['metadata'].get('expense_ratio'),
        
    }

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": f""" 
            You are a financial advisor. Compare the following funds using this structured summary:

            User Query: {text}
            Fund Data: {fund_data}
            Comparison Summary: {summary}

            Always structure the answer in the following format:

            1. Overview (1 short paragraph)
            2. Fund-by-fund breakdown
            3. Final recommendation summary
            
            Rules:
            1. Use ONLY values from fund_data or summary.
            2. Do not hallucinate extra metrics.
            3. Create a 3–4 paragraph comparison.
            4. End with:
            
            "The fund metrics are synthetic and for illustrative purpose ONLY and should not be used for financial decisions 
            """}
        ], temperature = 0.3, seed = 1
    )

    return response.choices[0].message.content
    
def filtered_fund_search(text):

    semantic_query = text['semantic_query']
    filters = text['filters']

    if semantic_query:
        query_vector = create_embeddings([semantic_query])

    else:
        print("I did not understand the query, please explain it more")

    where_clause = {}

    if filters["min_1yr_return"]:
        where_clause["1_Yr_Return"] = {"$gt": filters["min_1yr_return"]}

    if filters["min_3yr_return"]:
        where_clause["3_Yr_Return"] = {"$gt": filters["min_3yr_return"]}

    if filters["max_expense_ratio"]:
        where_clause["Expense_Ratio"] = {"$lt": filters["max_expense_ratio"]}

    

    result = collection.query(
        query_embeddings = query_vector,
        n_results = 20,
        where = where_clause if where_clause else None
    )

    raw_mf = result['metadatas'][0]
    raw_docs = result['documents'][0]

    fund_list = []

    for meta, doc in zip(raw_mf, raw_docs):
        fund_list.append(
            {
                "name": doc,
                "1_Yr_Return": meta.get("1_Yr_Return"),
                "3_Yr_Return": meta.get("3_Yr_Return"),
                "5_Yr_Return": meta.get("5_Yr_Return"),
                "expense_ratio": meta.get("expense_ratio"),
                "aum": meta.get("aum"),
                "benchmark": meta.get("benchmark")
            }
        )

    sorted_list = sorted(
        fund_list, 
        key = lambda f: f['1_Yr_Return'],
        reverse = True
    )

    final_list_llm = sorted_list[:5]


    response = client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {"role": "system", "content": f""" 
            You are a financial advisor. You've been given the top 5 funds, for which the user has asked the {text} of. We have filtered
            the list and you can find it under {sorted_list}.

            You are first supposed to list down the names in the {sorted_list}, one by one

            And give a one line explanation for each fund in the {sorted_list} talking about their returns, expense ratio, AUM and benchmark
            returns.

            Rules:
            1. Use ONLY values from fund_data or summary.
            2. Do not hallucinate extra metrics.
            3. Create a 3–4 paragraph comparison.
            4. End with:
            
            "The fund metrics are synthetic and for illustrative purpose ONLY and should not be used for financial decisions 
            """}
        ], temperature = 0.3, seed = 1
    )


    return response.choices[0].message.content
    
def query_router(user_query):
    intent = query_json_conversion(user_query)

    if intent['mode'].lower() == "single":
        return single_fund_search(intent)

    if intent['mode'].lower() == "comparison":
        return comparison_fund_search(intent)

    if intent['mode'].lower() == "filtered":
        return filtered_fund_search(intent)