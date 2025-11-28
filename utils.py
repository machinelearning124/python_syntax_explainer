import os
import google.generativeai as genai
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def configure_gemini(api_key=None, model_name='gemini-pro-latest'):
    """Configures the Gemini API client."""
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Try getting from streamlit secrets
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
            except:
                pass
            
    if not api_key:
        st.error("Gemini API Key not found. Please set GEMINI_API_KEY in .env or secrets.toml, or enter it in the sidebar.")
        return None

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def get_explanation(model, code, user_inputs=None):
    """
    Sends the code to Gemini and retrieves a structured step-by-step explanation.
    """
    if user_inputs is None:
        user_inputs = {}

    prompt = f"""
    You are an expert Python code tutor. Your task is to explain the following Python code step-by-step, EXACTLY as it would execute at runtime.
    
    CRITICAL RULES:
    1. **EXECUTE EXACTLY AS A DEBUGGER WOULD.** Do not summarize or skip steps.
    2. **LOOPS**: You MUST step onto the loop header line (e.g., `for i in range(3):`) at the START of EVERY iteration to check the condition.
       - Iteration 1: Step on header -> Step into body -> ... -> End of body
       - Iteration 2: Step on header -> Step into body -> ... -> End of body
       - ...
       - Final check: Step on header (condition false) -> Exit loop
    3. **IF/ELSE**: Execute ONLY the branch that matches the condition. Do NOT step into the other branch.
    4. **FUNCTION CALLS**:
       - Step 1: Step on the line calling the function.
       - Step 2: Step into the function definition line (def ...).
       - Step 3: Execute function body.
       - Step 4: Return to the line AFTER the function call (or the same line if used in an expression).
    5. **RETURN**: When a return statement is executed, stop the function immediately and return to the caller.
    6. **PRINT**: Track all print() outputs and include them in the output field.
    7. **VARIABLES**: You MUST include the state of ALL local and global variables at EACH step.
    
    The user has provided the following inputs for any `input()` calls in the code:
    {user_inputs}
    
    Please use these values when simulating the execution.
    
    Code to explain:
    ```python
    {code}
    ```
    
    Please provide the output as a JSON object with two keys:
    1. "flowchart_data": A dictionary containing "nodes" and "edges" for the flowchart.
       - "nodes": A list of objects, each having:
         - "id": String (e.g., "A", "B").
         - "label": String (Text to display).
         - "type": String ("step" for normal, "condition" for decisions).
       - "edges": A list of objects, each having:
         - "from": String (Source node ID).
         - "to": String (Target node ID).
         - "label": String (Optional label for the edge, e.g., "Yes", "No").
    2. "steps": A list of step objects.
    
    Each step object must have:
    - "step_number": Integer (1-based index)
    - "line_no": Integer (1-based line number)
    - "line_content": The actual line of code
    - "explanation": A detailed explanation of what is happening in this step.
       - **FORMAT AS AN HTML UNORDERED LIST (`<ul>` with `<li>` items).**
       - **COLOR CODE variables and function names using HTML `<span>` tags.**
         - Variables: `<span style='color: #a6e22e'>variable_name</span>`
         - Functions: `<span style='color: #66d9ef'>function_name()</span>`
         - Values (numbers, strings): `<span style='color: #e6db74'>value</span>`
       - Explain the logic clearly, breaking it down into multiple bullet points if complex.
    - "variables": Dictionary of variable states (exclude function names - only include data variables like numbers, strings, lists, dicts, etc.). **MUST BE POPULATED.**
    - "output": String of printed output (or empty string). **MUST BE POPULATED IF PRINT EXECUTED.**
    - "flowchart_node_id": The ID of the node in the flowchart that corresponds to this step (e.g., "A").
    
    Example format:
    {{
        "flowchart_data": {{
            "nodes": [
                {{"id": "A", "label": "Start", "type": "step"}},
                {{"id": "B", "label": "x > 5", "type": "condition"}},
                {{"id": "C", "label": "Print Big", "type": "step"}},
                {{"id": "D", "label": "Print Small", "type": "step"}}
            ],
            "edges": [
                {{"from": "A", "to": "B"}},
                {{"from": "B", "to": "C", "label": "Yes"}},
                {{"from": "B", "to": "D", "label": "No"}}
            ]
        }},
        "steps": [
            {{
                "step_number": 1,
                "line_no": 1,
                "line_content": "x = 10",
                "explanation": "<ul><li>Assign <span style='color: #e6db74'>10</span> to variable <span style='color: #a6e22e'>x</span>.</li><li>This initializes the variable for later use.</li></ul>",
                "variables": {{"x": 10}},
                "output": "",
                "flowchart_node_id": "A"
            }}
        ]
    }}
    
    Remember: Only include steps for lines that ACTUALLY execute. Skip unreachable code paths.
    RETURN ONLY THE RAW JSON. Do not include markdown formatting like ```json ... ```.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up potential markdown code blocks if the model ignores the instruction
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text)
            
    except Exception as e:
        st.error(f"Error generating explanation: {e}")
        return None

def get_overall_explanation(model, code, user_inputs=None):
    """
    Generates a high-level explanation of the code with a real-world analogy.
    """
    if user_inputs is None:
        user_inputs = {}

    prompt = f"""
    You are an expert Python code tutor.
    Please provide a high-level explanation of the following Python code.
    
    The user has provided the following inputs for any `input()` calls in the code:
    {user_inputs}
    
    Please incorporate these specific input values into your explanation and analogy where relevant.
    
    Structure your response as follows:
    
    ### 📝 Summary
    [Briefly explain what the code does in simple terms]
    
    ### 🌍 Real-World Analogy
    [Explain the logic using a creative and easy-to-understand real-world analogy. Be descriptive and fun!]
    
    Code:
    ```python
    {code}
    ```
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating explanation: {e}"
