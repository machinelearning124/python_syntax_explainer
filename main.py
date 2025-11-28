import streamlit as st
import utils
import os
import streamlit.components.v1 as components
# from code_editor import code_editor

# Page Config
st.set_page_config(
    page_title="Python Syntax Explainer",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Inject specific styles for the arrow buttons using :has() selector if supported or attribute selectors
    # Since we can't easily target by text, we'll target by the specific layout structure
    # The nav buttons are in a row with 3 columns.
    st.markdown("""
        <style>
        /* Reduce top padding */
        .block-container {
            padding-top: 2rem !important;
        }
        
        /* Target the Previous Button (First column in the nav row) */
        div[data-testid="stHorizontalBlock"] .stColumn:nth-child(1) button p:contains("←") {
             /* This doesn't work in CSS */
        }
        
        /* Valid CSS approach: Target by hierarchy */
        /* We assume the nav row is distinctive */
        
        /* Previous Button - Blue/Purple Neon */
        div[data-testid="column"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button {
            background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
            border: 2px solid #00c6ff !important;
            box-shadow: 0 0 10px #00c6ff, 0 0 20px #0072ff, inset 0 0 10px rgba(0, 198, 255, 0.5) !important;
            border-radius: 15px !important;
        }
        
        /* Next Button - Pink/Red Neon */
        div[data-testid="column"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button {
            background: linear-gradient(135deg, #f857a6, #ff5858) !important;
            border: 2px solid #ff5858 !important;
            box-shadow: 0 0 10px #ff5858, 0 0 20px #f857a6, inset 0 0 10px rgba(255, 88, 88, 0.5) !important;
            border-radius: 15px !important;
        }
        
        /* Hover Effects */
        div[data-testid="column"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) button:hover {
            box-shadow: 0 0 20px #00c6ff, 0 0 40px #0072ff !important;
            transform: scale(1.05);
        }
        
        div[data-testid="column"] div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) button:hover {
            box-shadow: 0 0 20px #ff5858, 0 0 40px #f857a6 !important;
            transform: scale(1.05);
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# Initialize Session State
if "code_input" not in st.session_state:
    st.session_state.code_input = ""
if "explanation_data" not in st.session_state:
    st.session_state.explanation_data = None
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "flowchart_code" not in st.session_state:
    st.session_state.flowchart_code = None
if "explanation" not in st.session_state:
    st.session_state.explanation = None

# Title - Hide when in debug mode
if not st.session_state.explanation_data:
    st.title("🐍 Python Syntax Explainer")
    st.markdown("Enter your Python code below to get a step-by-step interactive explanation.")


# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    api_key = st.text_input("Google API Key", type="password", help="Enter your Gemini API Key here.")
    
    model_name = st.selectbox(
        "Model Name",
        ["gemini-pro-latest"],
        index=0
    )
    
    st.markdown("---")


# ============ TOP NAVIGATION BAR ============
if st.session_state.explanation_data:
    total_steps = len(st.session_state.explanation_data)
    current_idx = st.session_state.current_step
    step_data = st.session_state.explanation_data[current_idx]
    
    # Keyboard Navigation Logic
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                const buttons = Array.from(doc.querySelectorAll('button'));
                const prev = buttons.find(el => el.innerText === '←');
                if (prev && !prev.disabled) {
                    prev.click();
                }
            }
            if (e.key === 'ArrowRight') {
                const buttons = Array.from(doc.querySelectorAll('button'));
                const next = buttons.find(el => el.innerText === '→');
                if (next && !next.disabled) {
                    next.click();
                }
            }
        });
        </script>
        """,
        height=0,
        width=0,
    )

    # Navigation Container - Centered
    with st.container():
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h3 style='color: #888; margin-bottom: 10px;'>🎯 Step Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
    
        nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
        
        with nav_col1:
            if st.button("←", disabled=(current_idx == 0), use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
                
        with nav_col2:
            # Slider
            if total_steps > 1:
                # Show min/max labels above slider
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: -5px;'>
                    <span>Step 1</span>
                    <span>Step {total_steps}</span>
                </div>
                """, unsafe_allow_html=True)
                
                selected_step = st.slider(
                    "Step Navigation",
                    min_value=1,
                    max_value=total_steps,
                    value=current_idx + 1,
                    label_visibility="collapsed"
                )
                # Sync slider with state
                if selected_step - 1 != current_idx:
                    st.session_state.current_step = selected_step - 1
                    st.rerun()
            else:
                st.progress(1.0)
            
            st.markdown(f"<div style='text-align: center; color: #888;'>Step {current_idx + 1} of {total_steps}</div>", unsafe_allow_html=True)

        with nav_col3:
            if st.button("→", disabled=(current_idx == total_steps - 1), use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()
    
    st.markdown("---")

# Main Layout
col1, col2 = st.columns([5, 4])

# Input Parsing Logic
import re
def extract_input_prompts(code):
    # Find all input() calls and extract the prompt text and variable name
    prompts = []
    lines = code.split('\n')
    for line in lines:
        if 'input(' in line:
            # Simple heuristic for variable assignment
            var_name = None
            if '=' in line:
                # Split by the FIRST '=' to handle cases like "x = input('a=b')"
                parts = line.split('=', 1)
                lhs = parts[0].strip()
                # Handle simple assignment "x ="
                if lhs.isidentifier():
                    var_name = lhs
            
            # Extract prompt text
            match = re.search(r'input\s*\((.*?)\)', line)
            prompt_text = ""
            if match:
                prompt_text = match.group(1).strip('"\'')
            
            if not var_name:
                var_name = f"Input {len(prompts) + 1}"
                
            prompts.append({
                "var_name": var_name,
                "prompt": prompt_text
            })
    return prompts

with col1:
    st.subheader("📝 Code Input")
    
    # Toggle between Edit and Debug mode
    # If explanation data exists, we are in "Debug Mode" (unless user clears)
    is_debug_mode = st.session_state.explanation_data is not None
    
    if is_debug_mode:
        # --- DEBUG MODE ---
        current_idx = st.session_state.current_step
        step_data = st.session_state.explanation_data[current_idx]
        
        line_no = step_data.get("line_no", -1)
        variables = step_data.get("variables", {})
        
        # Work on a COPY of the code to avoid modifying the original
        lines = st.session_state.code_input.split('\n')
        
        if 0 < line_no <= len(lines):
            # Add variable values as a comment if present
            if variables:
                var_annotations = []
                for k, v in variables.items():
                    var_annotations.append(f"{k}: {v}")
                var_text = ", ".join(var_annotations)
                lines[line_no - 1] = lines[line_no - 1].rstrip() + f"  # {var_text}"
            
            # Add red arrow at the beginning of the active line
            lines[line_no - 1] = "🔴 ➜ " + lines[line_no - 1]
                
        code_to_display = '\n'.join(lines)
        
        # Show active line indicator
        st.markdown(f"**🔍 Executing Line {line_no}**")
        
        # Display code with st.code (has built-in syntax highlighting)
        st.code(code_to_display, language="python", line_numbers=True)
        
        if st.button("Stop Debugging / Edit Code", use_container_width=True):
            st.session_state.explanation_data = None
            st.session_state.current_step = 0
            st.rerun()
            
    else:
        # --- EDIT MODE (st_ace) ---
        from streamlit_ace import st_ace
        
        # Initialize editor version if not set
        if 'editor_version' not in st.session_state:
            st.session_state.editor_version = 0
        
        code_input = st_ace(
            value=st.session_state.code_input,
            language='python',
            theme='dracula',
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=False,
            auto_update=True,
            readonly=False,
            key=f"code_editor_{st.session_state.editor_version}",  # Use version in key
            height=300
        )
        
        # Update session state
        st.session_state.code_input = code_input
        
        # Check for input() calls
        input_prompts = extract_input_prompts(st.session_state.code_input)
        user_inputs = {}
        
        if input_prompts:
            st.info("⌨️ This code requires input. Please provide values below:") 
            for i, item in enumerate(input_prompts):
                label = item["var_name"]
                prompt = item["prompt"]
                # Show prompt as help text or part of label if useful
                display_label = f"{label}"
                if prompt:
                    display_label += f" ({prompt})"
                    
                val = st.text_input(display_label, key=f"user_input_{i}")
                user_inputs[f"input_{i}"] = val

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            if st.button("Explain Syntax", use_container_width=True):
                if not code_input.strip():
                    st.warning("Please enter some code first.")
                else:
                    with st.spinner("Analyzing code logic..."):
                        model = utils.configure_gemini(api_key, model_name)
                        if model:
                            input_values = list(user_inputs.values())
                            data = utils.get_explanation(model, code_input, input_values)
                            if data:
                                # Handle new dictionary format
                                if isinstance(data, dict) and "steps" in data:
                                    st.session_state.explanation = data
                                    st.session_state.explanation_data = data["steps"]
                                    st.session_state.flowchart_code = data.get("flowchart_code")
                                else:
                                    # Fallback for old format (list of steps)
                                    st.session_state.explanation_data = data
                                    st.session_state.flowchart_code = None
                                    
                                st.session_state.current_step = 0
                                st.rerun()

        with btn_col2:
            if st.button("Clear Code", use_container_width=True):
                st.session_state.code_input = ""
                st.session_state.explanation_data = None
                st.session_state.explanation = None
                st.session_state.flowchart_code = None
                st.session_state.current_step = 0
                # Force st_ace to refresh by incrementing version
                if 'editor_version' not in st.session_state:
                    st.session_state.editor_version = 0
                st.session_state.editor_version += 1
                st.session_state.editor_version += 1
                st.rerun()

        st.markdown("---")
        if st.button("🌟 Explain with Analogy", use_container_width=True):
            if not code_input.strip():
                st.warning("Please enter some code first.")
            else:
                with st.spinner("Generating analogy..."):
                    model = utils.configure_gemini(api_key, model_name)
                    if model:
                        # user_inputs is a dict like {'input_0': 'val'}, we want a list or dict of values
                        # The utils function expects a dict or list? The prompt just prints it.
                        # Let's pass the dictionary of values directly.
                        st.markdown("### 🌟 Overall Explanation & Analogy")
                        analogy = utils.get_overall_explanation(model, code_input, user_inputs)
                        st.markdown(analogy)

with col2:
    # Hide app header in debugger mode
    if not st.session_state.explanation_data:
        st.markdown("*Debugger will appear here after clicking 'Explain Syntax'*")
    
    if st.session_state.explanation_data:
        current_idx = st.session_state.current_step
        step_data = st.session_state.explanation_data[current_idx]
        
        # ============ FLOWCHART CONTAINER ============
        with st.container():
            explanation = st.session_state.explanation
            if "flowchart_data" in explanation or "flowchart_code" in explanation:
                st.markdown("### 🗺️ Flowchart")
                
                flowchart_data = st.session_state.explanation.get("flowchart_data")
                active_node_id = step_data.get("flowchart_node_id", "")
        
            if flowchart_data:
                # Convert JSON graph data to Graphviz DOT format with vibrant colors
                nodes = flowchart_data.get("nodes", [])
                edges = flowchart_data.get("edges", [])
                
                # Color palette for different node types
                node_colors = {
                    "step": {"fill": "#4A90E2", "border": "#2E5C8A"},      # Blue
                    "condition": {"fill": "#F5A623", "border": "#C77F1B"},  # Orange
                    "input": {"fill": "#7ED321", "border": "#5FA119"},     # Green
                    "output": {"fill": "#D0021B", "border": "#A00115"},    # Red
                    "process": {"fill": "#9013FE", "border": "#6A0FB3"},   # Purple
                }
                
                # Build DOT string with enhanced styling
                dot_lines = ["digraph G {"]
                dot_lines.append('  bgcolor="#1e1e1e";')
                dot_lines.append('  rankdir="TB";')  # Top to Bottom
                dot_lines.append('  splines=ortho;')  # Orthogonal edges
                dot_lines.append('  nodesep=0.8;')
                dot_lines.append('  ranksep=0.8;')
                dot_lines.append('  node [fontname="Arial", fontsize=11, penwidth=2];')
                dot_lines.append('  edge [fontname="Arial", fontsize=9, penwidth=2, color="#50E3C2"];')
                
                # Add nodes with varied shapes and colors
                for node in nodes:
                    node_id = node["id"]
                    label = node["label"].replace('"', '\\"')  # Escape quotes
                    node_type = node.get("type", "step")
                    
                    # Determine shape based on type
                    shape_map = {
                        "condition": "diamond",
                        "input": "parallelogram",
                        "output": "parallelogram", 
                        "process": "box",
                        "step": "ellipse"
                    }
                    shape = shape_map.get(node_type, "box")
                    
                    # Get colors for this node type
                    colors = node_colors.get(node_type, node_colors["step"])
                    
                    # Apply highlighting to active node
                    if node_id == active_node_id:
                        dot_lines.append(f'  {node_id} [label="{label}", shape={shape}, style=filled, fillcolor="#FF4B2B", fontcolor="white", color="#FF6B4A", penwidth=3];')
                    else:
                        dot_lines.append(f'  {node_id} [label="{label}", shape={shape}, style=filled, fillcolor="{colors["fill"]}", fontcolor="white", color="{colors["border"]}"];')
                
                # Add edges with labels
                for edge in edges:
                    source = edge["from"]
                    target = edge["to"]
                    label = edge.get("label", "")
                    
                    if label:
                        label_escaped = label.replace('"', '\\"')
                        dot_lines.append(f'  {source} -> {target} [label="{label_escaped}", fontcolor="white"];')
                    else:
                        dot_lines.append(f'  {source} -> {target};')
                
                dot_lines.append("}")
                dot_code = "\n".join(dot_lines)
                
                # Debug: Show DOT code to ensure it's generated correctly
                with st.expander("🛠️ Debug: View Graphviz DOT Code"):
                    st.code(dot_code, language="dot")
                
                # Render with viz.js + custom zoom/pan (Pure JS solution)
                import streamlit.components.v1 as components
                import json
                
                dot_code_js = json.dumps(dot_code)
                
                html_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{
                            background-color: #1e1e1e;
                            color: white;
                            font-family: sans-serif;
                            overflow: hidden;
                        }}
                        #graph-container {{
                            width: 100%;
                            height: 600px;
                            border: 1px solid #444;
                            border-radius: 8px;
                            background-color: #1e1e1e;
                            position: relative;
                            overflow: auto;
                        }}
                        #svg-wrapper {{
                            transform-origin: 0 0;
                            transition: transform 0.2s ease-out;
                        }}
                        #controls {{
                            position: absolute;
                            top: 10px;
                            left: 10px;
                            z-index: 100;
                            display: flex;
                            gap: 5px;
                            background: rgba(0,0,0,0.7);
                            padding: 5px;
                            border-radius: 6px;
                        }}
                        .btn {{
                            background: #2d2d2d;
                            color: #eee;
                            border: 1px solid #555;
                            width: 30px;
                            height: 30px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 16px;
                            font-weight: bold;
                            transition: all 0.2s;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }}
                        .btn:hover {{
                            background: #444;
                            border-color: #777;
                            transform: scale(1.05);
                        }}
                        .btn:active {{
                            background: #555;
                        }}
                        #loading {{
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            color: #888;
                        }}
                        #error-message {{
                            color: #ff6b6b;
                            padding: 20px;
                            display: none;
                            background: rgba(255,0,0,0.1);
                            border-radius: 8px;
                        }}
                    </style>
                </head>
                <body>
                    <div id="controls">
                        <button class="btn" id="zoom-in-btn" title="Zoom In">+</button>
                        <button class="btn" id="zoom-out-btn" title="Zoom Out">−</button>
                        <button class="btn" id="reset-btn" title="Reset">R</button>
                    </div>
                    
                    <div id="graph-container">
                        <div id="loading">Generating Flowchart...</div>
                        <div id="error-message"></div>
                        <div id="svg-wrapper"></div>
                    </div>

                    <script>
                        let currentScale = 1.0;
                        const scaleStep = 0.2;
                        const minScale = 0.3;
                        const maxScale = 3.0;
                        
                        function updateTransform() {{
                            const wrapper = document.getElementById('svg-wrapper');
                            if (wrapper) {{
                                wrapper.style.transform = 'scale(' + currentScale + ')';
                            }}
                        }}
                        
                        function doZoomIn() {{
                            if (currentScale < maxScale) {{
                                currentScale += scaleStep;
                                updateTransform();
                            }}
                        }}
                        
                        function doZoomOut() {{
                            if (currentScale > minScale) {{
                                currentScale -= scaleStep;
                                updateTransform();
                            }}
                        }}
                        
                        function doReset() {{
                            currentScale = 1.0;
                            updateTransform();
                            const container = document.getElementById('graph-container');
                            if (container) {{
                                container.scrollTop = 0;
                                container.scrollLeft = 0;
                            }}
                        }}

                        // Attach event listeners
                        document.getElementById('zoom-in-btn').addEventListener('click', doZoomIn);
                        document.getElementById('zoom-out-btn').addEventListener('click', doZoomOut);
                        document.getElementById('reset-btn').addEventListener('click', doReset);

                        // Generate flowchart
                        var viz = new Viz();
                        var dot = {dot_code_js};
                        
                        function showError(msg) {{
                            document.getElementById('loading').style.display = 'none';
                            var errDiv = document.getElementById('error-message');
                            errDiv.style.display = 'block';
                            errDiv.innerText = 'Error: ' + msg;
                        }}

                        if (!dot) {{
                            showError("No DOT code provided.");
                        }} else {{
                            viz.renderSVGElement(dot)
                                .then(function(element) {{
                                    document.getElementById('loading').style.display = 'none';
                                    var wrapper = document.getElementById('svg-wrapper');
                                    wrapper.innerHTML = '';
                                    wrapper.appendChild(element);
                                }})
                                .catch(function(error) {{
                                    showError(error.toString());
                                }});
                        }}
                    </script>
                </body>
                </html>
                """
                components.html(html_code, height=600)
            else:
                st.warning("Flowchart data not available.")
# ============ BOTTOM SECTION: Analysis & Variables ============
if st.session_state.explanation_data:
    st.markdown("---")
    bottom_col1, bottom_col2 = st.columns([5, 4])
    
    # BOTTOM LEFT: Analysis
    with bottom_col1:
        current_idx = st.session_state.current_step
        step_data = st.session_state.explanation_data[current_idx]
        st.markdown(f"<div class='explanation-card'><h3>💡 Analysis</h3>{step_data.get('explanation', '')}</div>", unsafe_allow_html=True)

    # BOTTOM RIGHT: Variables
    with bottom_col2:
        # Variables State - Table View
        current_idx = st.session_state.current_step # Redefine current_idx for this scope
        step_data = st.session_state.explanation_data[current_idx] # Redefine step_data for this scope
        if step_data.get("variables"):
            st.markdown("### 📊 Variables")
            
            # Get previous variables for diffing
            prev_vars = {}
            if current_idx > 0:
                prev_vars = st.session_state.explanation_data[current_idx - 1].get("variables", {})
            
            current_vars = step_data["variables"]
                        # CSS for Memory Blocks
            st.markdown("""
            <style>
            .memory-container {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 10px;
            }
            .memory-card {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
                min-width: 120px;
                position: relative;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .memory-card.changed {
                border-color: #FF4B2B;
                box-shadow: 0 0 15px rgba(255, 75, 43, 0.2);
                animation: pulse 1.5s infinite;
            }
            .memory-card.new {
                border-color: #00c6ff;
                box-shadow: 0 0 15px rgba(0, 198, 255, 0.2);
            }
            @keyframes pulse {
                0% { box-shadow: 0 0 0 0 rgba(255, 75, 43, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(255, 75, 43, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 75, 43, 0); }
            }
            .var-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
                border-bottom: 1px solid #333;
                padding-bottom: 4px;
            }
            .var-name {
                font-family: 'Fira Code', monospace;
                font-weight: 600;
                color: #fafafa;
                font-size: 0.9rem;
            }
            .var-type {
                font-size: 0.7rem;
                color: #888;
                background: #2d2d2d;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .var-value {
                font-family: 'Fira Code', monospace;
                color: #a6e22e;
                font-size: 1rem;
                word-break: break-all;
            }
            .list-container {
                display: flex;
                gap: 4px;
                overflow-x: auto;
                padding-bottom: 4px;
            }
            .list-item {
                background: #2d2d2d;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.9rem;
                border: 1px solid #444;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Generate HTML for blocks
            blocks_html = '<div class="memory-container">'
            
            for var_name, var_value in current_vars.items():
                # Determine status
                status_class = ""
                if var_name not in prev_vars:
                    status_class = "new"
                elif str(prev_vars[var_name]) != str(var_value):
                    status_class = "changed"
                
                # Determine type label
                # Since we only have string representation from backend, we infer or just use generic
                # But we can try to parse simple types for display
                type_label = "variable"
                display_value = str(var_value)
                
                # Custom rendering for lists (simple heuristic)
                value_html = f'<div class="var-value">{display_value}</div>'
                if display_value.startswith('[') and display_value.endswith(']'):
                    type_label = "list"
                    try:
                        # Safe-ish parsing for display
                        import ast
                        items = ast.literal_eval(display_value)
                        if isinstance(items, list):
                            value_html = '<div class="list-container">'
                            for item in items:
                                value_html += f'<div class="list-item">{item}</div>'
                            value_html += '</div>'
                    except:
                        pass # Fallback to string
                elif display_value.startswith('{') and display_value.endswith('}'):
                    type_label = "dict"
                elif display_value.isdigit():
                    type_label = "int"
                elif display_value.replace('.', '', 1).isdigit():
                    type_label = "float"
                elif display_value.startswith("'") or display_value.startswith('"'):
                    type_label = "str"
                
                blocks_html += f"""
<div class="memory-card {status_class}">
<div class="var-header">
    <span class="var-name">{var_name}</span>
    <span class="var-type">{type_label}</span>
</div>
{value_html}
</div>
"""
            
            blocks_html += '</div>'
            st.markdown(blocks_html, unsafe_allow_html=True)
        
        # Program Output Box
        # Collect all outputs up to current step
        all_outputs = []
        for i in range(current_idx + 1):
            output = st.session_state.explanation_data[i].get("output", "")
            if output:
                all_outputs.append(output)
        
        if all_outputs:
            st.markdown("### 🖥️ Program Output")
            output_text = "\n".join(all_outputs)
            st.code(output_text, language="text")
