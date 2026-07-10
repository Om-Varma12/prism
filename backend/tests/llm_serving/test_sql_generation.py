import os
import sys
# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import zcatalyst_sdk
from services.llm_client import CatalystLLMClient
from agents.text_to_sql.agent import TextToSQLAgent

def main():
    llm_client = CatalystLLMClient()
    agent = TextToSQLAgent(llm_client)
    
    query = "Show me cases where victim is Lakshmi Devi"
    print(f"Generating query for: '{query}'")
    
    result = agent.generate_query(query)
    zcql_query = result.get("zcql_query")
    print("\nResult:")
    print("zcql_query:", zcql_query)
    print("intent:", result.get("intent"))
    print("entities:", result.get("entities"))
    print("is_valid:", result.get("is_valid"))
    print("error:", result.get("error"))
    
    if zcql_query:
        print("\nExecuting query against Catalyst...")
        try:
            app = zcatalyst_sdk.initialize()
            zcql = app.zcql()
            res = zcql.execute_query(zcql_query)
            print("Raw ZCQL Results count:", len(res) if res else 0)
            if res:
                print("First row:", res[0])
        except Exception as e:
            print("Execution failed:", e)

if __name__ == "__main__":
    main()
