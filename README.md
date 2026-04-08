# AI Design Critic

AI Design Critic is a modern, premium web application built with Streamlit that analyzes UI designs using AI and provides detailed feedback on design quality, UX, and accessibility.

## Features
- **Image Upload:** Drag and drop PNG, JPG, or JPEG files.
- **Computer Vision Checks:** Basic image heuristics (like dominant color extraction) using OpenCV.
- **AI Feedback Engine:** Uses OpenAI API to analyze layout, accessibility concerns, and overall UX, generating a structured score and actionable feedback.
- **Modern UI:** Streamlit interface customized with premium CSS (glassmorphism, subtle gradients, and dark mode optimizations).

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   **Note**: If no API key is set, the application will gracefully fall back to a mock AI response so you can still preview the UI and functionality.

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Modular Structure
- `app.py`: The Streamlit frontend and UI styling.
- `ai_feedback.py`: Handles API interaction with OpenAI (with mock fallback).
- `image_analysis.py`: Handles deterministic image processing with OpenCV.

## Deployment
Ready to be deployed directly to [Streamlit Community Cloud](https://streamlit.io/cloud). Connect your GitHub repository and hit deploy!
