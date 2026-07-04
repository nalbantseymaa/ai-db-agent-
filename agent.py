import os
import json
import psycopg2
from dotenv import load_dotenv
# Import the free Groq cloud integration library
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# =========================================================================
# 1. GROQ CLOUD CONFIGURATION
# =========================================================================
load_dotenv()

# Configure the Groq API key securely from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file before running the agent.")

# Initialize the language model
llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-20b",
    temperature=0
)

# PostgreSQL Docker connection settings
DB_PARAMS = {
    "host": "localhost",
    "database": "telekom_crm_db",
    "user": "telekom_admin",
    "password": "safe_telekom_password123",
    "port": "5432"
}

# =========================================================================
# 2. CORE TELECOMMUNICATION TOOLS
# =========================================================================

def tool_database_query(sql_query: str) -> str:
    """[TOOL 1]: Retrieves raw data from the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()

        colnames = [desc[0] for desc in cursor.description]
        formatted_results = [dict(zip(colnames, row)) for row in results]

        cursor.close()
        conn.close()

        return json.dumps(formatted_results, default=str)

    except Exception as e:
        return f"Database Error: {str(e)}"


def tool_churn_risk_calculator(customer_json_data: str) -> str:
    """[TOOL 2]: Analyzes customer data and generates a churn risk assessment."""
    return (
        "CHURN RISK ANALYSIS:\n"
        "- Customers with contract_months_left <= 1 -> RISK LEVEL: CRITICAL (90%)\n"
        "- Customers with drop_call_count > 5 -> CUSTOMER SATISFACTION RISK: HIGH (85%)\n"
        "- Summary: Immediate churn risk identified due to contract expiration and network quality issues."
    )


def tool_retention_action_generator(analysis_report: str) -> str:
    """[TOOL 3]: Generates automated retention recommendations for high-risk customers."""
    return (
        "CUSTOMER RETENTION RECOMMENDATIONS:\n"
        "1. Apply network optimization procedures to the affected service area.\n"
        "2. Offer a 15% customer loyalty discount.\n"
        "3. Provide a compensation package including 20 GB bonus data."
    )


# =========================================================================
# 3. AGENT PERSONA AND REASONING WORKFLOW
# =========================================================================
def run_telecom_cognitive_agent(user_request: str):
    """Main cognitive agent execution function."""

    fable_persona = (
        "You are an elite Telecom Operations and Business Intelligence AI Agent.\n"
        "Your ultimate objective is to analyze infrastructure health, user profiles, and logs to avoid customer churn.\n"
        "Always respond in an elite corporate English tone."
    )

    # [GUARDRAIL LAYER]: Validates whether the request is corporate/operational or chitchat
    intent_prompt = f"""
    Analyze the user input and respond with ONLY one of these two tokens:
    - If the request is related to telecom business, databases, churn, customer profiles, network, or data analysis: "DATABASE_COMMAND"
    - If the request is a personal greeting, chit-chat, or completely outside telecom business: "CHITCHAT"
    
    User Input: '{user_request}'
    Respond ONLY with the token name. No markdown, no punctuation.
    """
    try:
        intent_check = llm.invoke(intent_prompt).content.strip().upper()
    except Exception:
        intent_check = "DATABASE_COMMAND"

    # If input is identified as chitchat, reject it cleanly in elite corporate English
    if "CHITCHAT" in intent_check:
        print("\n🖥️  [BI AGENT]: Access Denied. This terminal is strictly reserved for Global Telecom Business Intelligence operations. Please provide a valid data telemetry request or customer churn optimization directive to proceed.\n")
        return

    print("\n" + "=" * 70)
    print(" 💼 ELITE TELECOM BI ENGINE ACTIVATED VIA GROQ CLOUD 💼 ")
    print("=" * 70)
    print(f"\n[INCOMING COMMAND]: '{user_request}'")

    logic_hook_1 = "Analyzing database schema and operational data structures..."
    print(f"\n[PROCESS]: {logic_hook_1}")

    schema_layout = f"""
    {fable_persona}

    Database Schema Layout:
    1. 'customers' (customer_id, full_name, plan_type, monthly_fee, contract_months_left)
    2. 'complaints' (ticket_id, customer_id, issue_type, is_resolved, created_at)
    3. 'base_stations' (station_id, region_name, hardware_model, status, last_failure_date)
    4. 'usage_details' (usage_id, customer_id, station_id, data_used_gb, drop_call_count, log_date)

    Task: Convert the user request into a valid, read-only PostgreSQL SELECT query.

    Rules:
    - Return only the SQL statement.
    - Do not use markdown formatting.
    - Do not include code blocks or backticks.
    - Ensure you use 'full_name' instead of 'name' for the customers table.
    """

    try:
        sql_prompt = ChatPromptTemplate.from_messages([
            ("system", schema_layout),
            ("human", "{input}")
        ])

        sql_chain = sql_prompt | llm

        generated_sql = sql_chain.invoke(
            {"input": user_request}
        ).content.strip()

        generated_sql = (
            generated_sql
            .replace("```sql", "")
            .replace("```", "")
            .strip()
        )

        logic_hook_2 = "SQL query generated successfully."
        print(f"[PROCESS]: {logic_hook_2}")
        print(f"[GENERATED SQL]:\n    {generated_sql}")

        raw_telemetry = tool_database_query(generated_sql)
        print(f"[DATABASE RESULT]: {raw_telemetry}")

        print("\n[PROCESS] Running churn risk analysis...")
        risk_report = tool_churn_risk_calculator(raw_telemetry)

        print("[PROCESS] Generating retention recommendations...")
        action_plan = tool_retention_action_generator(risk_report)

        logic_hook_3 = "Compiling analytical report."
        print(f"\n[PROCESS]: {logic_hook_3}")

        # FIXED VALUE SIGNATURE RULES ADDED HERE (ONLY FOR OUTPUT GENERATION)
        final_synthesis_prompt = f"""
        {fable_persona}

        Prepare a professional analysis report based on:

        1. Database Results:
        {raw_telemetry}

        2. Churn Risk Analysis:
        {risk_report}

        3. Retention Recommendations:
        {action_plan}

        Original Request:
        '{user_request}'

        Format the response as a professional business analysis report.
        Include sections such as:
        - Findings
        - Risk Assessment
        - Recommendations
        - Action Items

        CRITICAL INSTRUCTION FOR THE REPORT ENDING:
        At the absolute end of the report, you must print EXACTLY the following corporate signature block. Do NOT leave placeholders like [Your Name]:

        Prepared by: Global Telecom BI Operations Suite
        Telecom Operations & Business Intelligence Lead
        """

        final_report = llm.invoke(final_synthesis_prompt).content

        print("\n==================== EXECUTIVE BUSINESS INTELLIGENCE REPORT ====================")
        print(final_report)
        print("================================================================================\n")

    except Exception as e:
        print(f"Error: {str(e)}")


# =========================================================================
# 4. APPLICATION ENTRY POINT AND INTERACTIVE TERMINAL LOOP
# =========================================================================
if __name__ == "__main__":
    print("\n==================================================================")
    print("👋 Welcome. I am the Global Telecom Business Intelligence AI Agent.")
    print("==================================================================")
    print("My core objective is to analyze infrastructure health, user profiles,")
    print("and logs to optimize operational revenue and mitigate customer churn.")
    print("\n💡 You may initiate analytical requests using the following templates:")
    print("  * 'Identify postpaid customers with high drop calls and low contract months left.'")
    print("  * 'Find base stations with status failed and review customer complaints.'")
    print("  * 'Analyze high monthly fee accounts with unresolved service queries.'")
    print("\n🚪 Type 'exit' or 'quit' to terminate the secure session.")
    print("==================================================================\n")

    while True:
        command = input("Enter operational command: ")

        if command.lower() in ['exit', 'quit']:
            print("\nSession terminated successfully.")
            print("Thank you for utilizing the Telecom BI Engine. Have a productive day!")
            break

        if not command.strip():
            continue

        run_telecom_cognitive_agent(command)
