import os
import base64
import json
import time
from dotenv import load_dotenv

load_dotenv(override=True)

def get_api_keys():
    keys = {
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "").strip(),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "").strip()
    }
    if not keys["GEMINI_API_KEY"] and not keys["OPENAI_API_KEY"]:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        if k in keys:
                            keys[k] = v.strip('"').strip("'").strip()
                            os.environ[k] = keys[k]
    return keys["GEMINI_API_KEY"], keys["OPENAI_API_KEY"]

def get_ai_feedback(image_bytes: bytes) -> dict:
    """
    Sends the image to the selected AI provider (Gemini or OpenAI).
    Config is read securely from backend environment variables so end-users never have to input keys.
    Falls back to a mock response if no keys exist.
    """
    gemini_key, openai_key = get_api_keys()

    if not gemini_key and not openai_key:
        time.sleep(1.5)
        return get_mock_response()

    prompt = """Analyze this UI design image and provide feedback in the following strict JSON format:
{
    "overall_score": 85,
    "color_feedback": [
        {"issue": "Low contrast", "reason": "Gray text on white background is hard to read.", "suggestion": "Darken the text to #333"}
    ],
    "layout_feedback": [
        {"issue": "Overcrowded header", "reason": "Too many icons in the top right.", "suggestion": "Move some actions to a dropdown menu."}
    ],
    "accessibility_issues": [
        {"issue": "Missing focus states", "reason": "Can't tell which element is selected.", "suggestion": "Add a visible focus ring."}
    ],
    "ux_suggestions": [
        {"issue": "Unclear primary action", "reason": "Both buttons have the same visual weight.", "suggestion": "Make the primary button a solid color."}
    ]
}
Be specific, practical, and actionable. Base your analysis on REAL layout laws and accessibility standards. ONLY RETURN THE RAW JSON OBJECT. No markdown code blocks, no other text."""

    if gemini_key:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            image = Image.open(io.BytesIO(image_bytes))
            
            response = model.generate_content([prompt, image])
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            raise Exception(f"Gemini API Error: {str(e)}")
            
    elif openai_key:
        from openai import OpenAI
        try:
            client = OpenAI(api_key=openai_key)
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")

    return get_mock_response()

def get_mock_response() -> dict:
    return {
        "overall_score": 78,
        "color_feedback": [
            {
                "issue": "Contrast ratio warnings",
                "reason": "The subtitle text uses a light gray (#B0B0B0) against a white background, which fails WCAG AA guidelines.",
                "suggestion": "Darken the subtitle text to at least #767676 to improve readability."
            },
            {
                "issue": "Color palette inconsistency",
                "reason": "There are three different shades of blue used for primary actions.",
                "suggestion": "Standardize the primary action color to a single hex value across the application."
            }
        ],
        "layout_feedback": [
            {
                "issue": "Overcrowded navigation",
                "reason": "The top navigation bar has too many elements, making it difficult to scan.",
                "suggestion": "Move secondary links (e.g., 'Help', 'Settings') into a hidden hamburger menu or user dropdown."
            },
            {
                "issue": "Improper spacing",
                "reason": "The margins between the cards are inconsistent (some 8px, some 16px).",
                "suggestion": "Implement a consistent 16px or 24px gap between all card elements."
            }
        ],
        "accessibility_issues": [
            {
                "issue": "Button visibility",
                "reason": "The 'Cancel' button is entirely text-based without an outline, making it hard to identify as interactive.",
                "suggestion": "Add a subtle border or background hover state to the 'Cancel' button."
            }
        ],
        "ux_suggestions": [
            {
                "issue": "Call-to-action clarity",
                "reason": "The main 'Subscribe' button doesn't stand out enough from the rest of the page.",
                "suggestion": "Use a contrasting accent color for the primary CTA and slightly increase its size."
            },
            {
                "issue": "Visual hierarchy issues",
                "reason": "The section header is the same font weight and size as the regular body text.",
                "suggestion": "Increase the section header to H2 size and use a semibold font weight."
            }
        ]
    }
