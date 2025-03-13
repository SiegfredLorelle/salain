# scripts/llm_explainer.py
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
import hashlib
import os
import streamlit as st

def generate_llm_explanation(text, prediction, confidence, features=None):
    """Generate natural language explanation using LLM."""
    # Create cache key based on inputs to avoid redundant API calls
    cache_key = hashlib.md5(f"{text}{prediction}{confidence}".encode()).hexdigest()
    
    # Try to get cached response
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Initialize LLM - Choose one approach below
    try:
        # Option 1: OpenAI (requires API key)
        llm = ChatAnthropic(
            temperature=0.2,
            model="claude-3-haiku-20240307",
            anthropic_api_key=st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
        )

        # Prepare prompts
        system_prompt = """You are a cybersecurity expert explaining email classification results. 
        Provide clear, concise explanations in bullet points. Use simple language for non-experts. 
        """

        # Format features for display
        feature_text = "None detected"
        if features:
            feature_text = ", ".join([f"{k}" for k in features.keys()])

        user_prompt = f"""
        Email Content: {text[:3000]}  # Truncate to avoid context limits
        Classification: {'Malicious' if prediction == 1 else 'Safe'}
        Confidence: {confidence:.2%}
        Key Features: {feature_text}
        
        No need to include pleasantries like 'thank you' or 'nice question' in your response. 
        Directly explain this classification to a non-technical user. Highlight 3-5 main reasons.
        For malicious classifications, list red flags. For safe emails, explain positive indicators.
        """
        
        # Generate response
        response = llm([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        explanation = response.content
        
        # Cache the response
        st.session_state[cache_key] = explanation
        return explanation
        
    except Exception as e:
        st.error(f"Explanation generation failed: {str(e)}")
        return "Could not generate explanation at this time."

def get_fallback_explanation(prediction, features):
    """Generate a simple explanation without LLM when API access fails."""
    if prediction == 1:
        explanation = "## Potential Warning Signs:\n\n"
        if features:
            for key, value in features.items():
                explanation += f"- {key}\n"
        else:
            explanation += "- Suspicious patterns detected in email content\n"
            explanation += "- Unusual formatting or structure\n"
            explanation += "- Patterns matching known malicious emails\n"
        explanation += "\nExercise caution before responding or clicking any links."
    else:
        explanation = "## Email appears safe:\n\n"
        explanation += "- No suspicious patterns detected\n"
        explanation += "- Content follows expected email structure\n"
        explanation += "- No matches with known malicious indicators\n"
        
    return explanation