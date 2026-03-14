"""
FashionHub AI Assistant - ChatGPT Style
Clean, minimalist design inspired by ChatGPT's interface
"""

import os
import gradio as gr
import openai
from typing import List, Dict, Tuple
import json
import base64
from io import BytesIO
import tempfile

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key")

# System prompt for clothes shopping assistant
SYSTEM_PROMPT = """You are a helpful and friendly online clothes shopping assistant for "FashionHub". 
Your role is to help customers find the perfect clothing items, provide style advice, 
and assist with their shopping needs.

Key capabilities:
1. Help users find clothing items by category (shirts, pants, dresses, shoes, accessories)
2. Provide style recommendations based on occasion (casual, formal, party, work, date night)
3. Suggest outfit combinations and color coordination
4. Provide size guidance and fit recommendations
5. Share information about current sales, promotions, and new arrivals
6. Help with order tracking and returns
7. Offer fashion tips and trends

Always be polite, enthusiastic about fashion, and focused on helping customers find what they need.
If you don't have specific information about inventory, suggest checking the website or contacting customer service.
Keep responses concise but helpful."""

class ClothesShoppingChatbot:
    def __init__(self):
        self.conversation_history: List[Dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.clothing_categories = {
            "men": ["Shirts", "T-shirts", "Jeans", "Pants", "Jackets", "Shoes", "Accessories"],
            "women": ["Dresses", "Tops", "Skirts", "Jeans", "Jackets", "Shoes", "Accessories"],
            "kids": ["T-shirts", "Shorts", "Dresses", "Pants", "Shoes", "Accessories"]
        }
        self.current_promotions = [
            "Spring Sale: 30% off all dresses and skirts",
            "New Arrivals: Summer collection now available",
            "Free shipping on orders over $50",
            "Student discount: 15% off with valid ID"
        ]
    
    def get_chatgpt_response(self, user_message: str) -> str:
        """Get response from ChatGPT API"""
        try:
            self.conversation_history.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.conversation_history,
                max_tokens=500,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            if len(self.conversation_history) > 11:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
            
            return assistant_response
            
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting to our service. Error: {str(e)}. Please try again or check your API key."
    
    def transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(audio_file, "rb") as audio:
                transcript = openai.Audio.transcribe("whisper-1", audio)
            return transcript.text
        except Exception as e:
            return f"Could not transcribe audio: {str(e)}"
    
    def text_to_speech(self, text: str) -> str:
        """Convert text to speech using OpenAI TTS API"""
        try:
            response = openai.Audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text[:200]
            )
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                response.stream_to_file(f.name)
                return f.name
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def get_clothing_recommendations(self, category: str, occasion: str = "casual") -> str:
        """Get clothing recommendations based on category and occasion"""
        recommendations = {
            "casual": ["Cotton t-shirts", "Jeans", "Sneakers", "Hoodies", "Shorts"],
            "formal": ["Blazers", "Dress shirts", "Slacks", "Dress shoes", "Ties"],
            "party": ["Sequined tops", "Leather pants", "Heels", "Statement jewelry", "Cocktail dresses"],
            "work": ["Blouses", "Pencil skirts", "Blazers", "Dress pants", "Loafers"],
            "date": ["Little black dresses", "Button-up shirts", "Nice jeans", "Boots", "Romantic tops"]
        }
        
        occasion_items = recommendations.get(occasion, recommendations["casual"])
        return f"For {occasion} {category.lower()}, I recommend: {', '.join(occasion_items[:3])}. Check our {category} section for more options!"
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
        return "Conversation cleared! How can I help you with your clothes shopping today?"

# Initialize chatbot
chatbot = ClothesShoppingChatbot()

def chat_response(message: str, history):
    """Handle text chat responses"""
    if not message.strip():
        return "", history
    
    response = chatbot.get_chatgpt_response(message)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
    return "", history

def voice_chat(audio_file: str) -> Tuple[str, str]:
    """Handle voice chat: transcribe audio, get response, and convert to speech"""
    if audio_file is None:
        return "No audio file provided", None
    
    user_message = chatbot.transcribe_audio(audio_file)
    
    if "Could not transcribe" in user_message:
        return user_message, None
    
    response = chatbot.get_chatgpt_response(user_message)
    audio_response = chatbot.text_to_speech(response)
    
    return f"**You said:** {user_message}\n\n**Assistant:** {response}", audio_response

def get_promotions():
    """Get current promotions"""
    promotions_text = "### Current Promotions\n"
    for i, promo in enumerate(chatbot.current_promotions, 1):
        promotions_text += f"- {promo}\n"
    return promotions_text

def get_categories():
    """Get clothing categories"""
    categories_text = "### Categories\n"
    for gender, items in chatbot.clothing_categories.items():
        categories_text += f"**{gender.title()}**\n"
        categories_text += f"{', '.join(items)}\n\n"
    return categories_text

def get_recommendation(category: str, occasion: str):
    """Get clothing recommendations"""
    return chatbot.get_clothing_recommendations(category, occasion)

# ChatGPT-inspired CSS
custom_css = """
/* ChatGPT-inspired styling */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f7f7f8;
    --border-color: #e5e5e5;
    --text-primary: #2d2d2d;
    --text-secondary: #6e6e80;
    --accent-color: #10a37f;
    --accent-hover: #0e8a6b;
    --user-message-bg: #f7f7f8;
    --assistant-message-bg: #ffffff;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #343541;
        --bg-secondary: #444654;
        --border-color: #565869;
        --text-primary: #ececf1;
        --text-secondary: #acacbe;
        --accent-color: #10a37f;
        --accent-hover: #0e8a6b;
        --user-message-bg: #343541;
        --assistant-message-bg: #444654;
    }
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    background: var(--bg-primary) !important;
}

body {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif !important;
}

/* Header styling */
.header-container {
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 2rem;
    background: var(--bg-primary);
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}

.header-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.header-subtitle {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 0.25rem;
}

/* Chat container */
.chat-container {
    background: var(--bg-primary) !important;
    padding: 0 !important;
}

/* Sidebar styling */
.sidebar {
    background: var(--bg-secondary) !important;
    border-radius: 12px;
    padding: 1.5rem !important;
    border: 1px solid var(--border-color);
    height: fit-content;
    position: sticky;
    top: 80px;
    margin-left: 1rem;
}

.sidebar-section {
    margin-bottom: 2rem;
}

.sidebar-section h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sidebar-section ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.sidebar-section li {
    padding: 0.5rem 0;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-color);
    font-size: 0.9rem;
}

.sidebar-section li:last-child {
    border-bottom: none;
}

/* Buttons */
.gr-button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    border: 1px solid var(--border-color) !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.gr-button.primary {
    background: var(--accent-color) !important;
    color: white !important;
    border: none !important;
}

.gr-button.primary:hover {
    background: var(--accent-hover) !important;
}

/* Input fields */
.gr-textbox input, .gr-dropdown select {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
}

.gr-textbox input:focus, .gr-dropdown select:focus {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2) !important;
}

/* Message input area */
.message-input-container {
    background: var(--bg-primary);
    border-top: 1px solid var(--border-color);
    padding: 1rem 2rem;
    position: sticky;
    bottom: 0;
    margin-top: 1rem;
}

/* Tabs */
.tabs {
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

.tab-nav {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid var(--border-color) !important;
    padding: 0.5rem !important;
}

.tab-nav button {
    color: var(--text-secondary) !important;
    border: none !important;
    background: transparent !important;
    padding: 0.5rem 1rem !important;
    border-radius: 6px !important;
}

.tab-nav button.selected {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Quick recommendations */
.recommendation-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}

/* Voice chat section */
.voice-section {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem;
    border: 1px solid var(--border-color);
}

/* Markdown styling */
.markdown-text {
    color: var(--text-primary) !important;
}

.markdown-text h1, .markdown-text h2, .markdown-text h3 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}

.markdown-text p {
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}

/* Example questions */
.example-questions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem;
}

.example-question {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s ease;
}

.example-question:hover {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

/* Avatar styling */
.avatar-container {
    width: 30px;
    height: 30px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.avatar-user {
    background: var(--accent-color);
    color: white;
}

.avatar-assistant {
    background: var(--bg-secondary);
    color: var(--text-primary);
}

/* Chatbot message styling */
.gr-chatbot {
    background: var(--bg-primary) !important;
}

.gr-chatbot .message {
    padding: 1rem !important;
    border-radius: 8px !important;
    margin: 0.5rem 0 !important;
}

.gr-chatbot .user {
    background: var(--user-message-bg) !important;
    border: 1px solid var(--border-color) !important;
}

.gr-chatbot .bot {
    background: var(--assistant-message-bg) !important;
    border: 1px solid var(--border-color) !important;
}
"""

# Create Gradio interface
with gr.Blocks(
    title="FashionHub AI",
    css=custom_css,
    theme=gr.themes.Soft(),
    fill_height=True
) as demo:

    # Header
    with gr.Row(elem_classes="header-container"):
        with gr.Column(scale=1):
            gr.Markdown(
                """
                <div class="header-title">
                    <span>👗</span> FashionHub AI
                </div>
                <div class="header-subtitle">
                    Your personal fashion assistant
                </div>
                """,
                elem_classes="markdown-text"
            )

    with gr.Row(equal_height=True):
        # Left Sidebar - ChatGPT style
        with gr.Column(scale=1, min_width=300):
            with gr.Column(elem_classes="sidebar"):
                # Promotions section
                with gr.Column(elem_classes="sidebar-section"):
                    gr.Markdown("### 🏷️ Promotions")
                    promotions_display = gr.Markdown(get_promotions(), elem_classes="markdown-text")
                    refresh_promos = gr.Button("Refresh", size="sm")

                # Categories section
                with gr.Column(elem_classes="sidebar-section"):
                    gr.Markdown("### 📋 Categories")
                    categories_display = gr.Markdown(get_categories(), elem_classes="markdown-text")

                # Quick recommendations
                with gr.Column(elem_classes="sidebar-section"):
                    gr.Markdown("### ⚡ Quick Recommendations")
                    
                    category_dropdown = gr.Dropdown(
                        choices=["Dresses", "Shirts", "Pants", "Jeans", "Jackets", "Shoes", "Accessories"],
                        value="Dresses",
                        label="Category",
                        container=False
                    )
                    
                    occasion_dropdown = gr.Dropdown(
                        choices=["casual", "formal", "party", "work", "date"],
                        value="casual",
                        label="Occasion",
                        container=False
                    )
                    
                    get_rec_btn = gr.Button("Generate", variant="primary", size="sm")
                    
                    recommendation_output = gr.Textbox(
                        label="",
                        lines=3,
                        interactive=False,
                        container=False,
                        elem_classes="recommendation-card"
                    )

        # Main Chat Area
        with gr.Column(scale=2):
            # Chatbot interface
            chatbot_interface = gr.Chatbot(
                elem_id="chatbot",
                height=500,
                avatar_images=("👤", "🤖"),
                show_label=False
            )

            # Message input area
            with gr.Column(elem_classes="message-input-container"):
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Ask about clothes, style, outfits...",
                        scale=20,
                        container=False,
                        show_label=False
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1, min_width=80)
                
                with gr.Row():
                    voice_mode_btn = gr.Button("🎤 Voice Mode", size="sm", scale=1)
                    clear_btn = gr.Button("🗑️ Clear", size="sm", scale=1)

    # Example questions
    with gr.Row():
        gr.Markdown(
            """
            <div class="example-questions">
                <span class="example-question" onclick="document.querySelector('textarea').value = 'I need a formal dress for a wedding'; document.querySelector('textarea').focus()">👰 Wedding outfit</span>
                <span class="example-question" onclick="document.querySelector('textarea').value = 'What are the current promotions?'; document.querySelector('textarea').focus()">💰 Promotions</span>
                <span class="example-question" onclick="document.querySelector('textarea').value = 'Help me with size guide'; document.querySelector('textarea').focus()">📏 Size guide</span>
                <span class="example-question" onclick="document.querySelector('textarea').value = 'Casual outfit ideas'; document.querySelector('textarea').focus()">👕 Casual style</span>
                <span class="example-question" onclick="document.querySelector('textarea').value = 'What shoes go with jeans?'; document.querySelector('textarea').focus()">👟 Shoe tips</span>
            </div>
            """,
            elem_classes="markdown-text"
        )

    # Voice chat section (initially hidden)
    with gr.Row(visible=False, elem_classes="voice-section") as voice_section:
        with gr.Column():
            gr.Markdown("### 🎤 Voice Chat Mode")
            gr.Markdown("Click the microphone below to start speaking")
            
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="",
                show_label=False
            )
            
            with gr.Row():
                process_voice_btn = gr.Button("Process Voice Message", variant="primary")
                back_to_text_btn = gr.Button("← Back to Text Chat", size="sm")
            
            voice_output_text = gr.Markdown("")
            voice_output_audio = gr.Audio(label="Assistant's Response", type="filepath")

    # Event handlers
    submit_btn.click(
        fn=chat_response,
        inputs=[msg, chatbot_interface],
        outputs=[msg, chatbot_interface]
    )
    
    msg.submit(
        fn=chat_response,
        inputs=[msg, chatbot_interface],
        outputs=[msg, chatbot_interface]
    )
    
    clear_btn.click(
        fn=lambda: ("", []),
        inputs=[],
        outputs=[msg, chatbot_interface]
    ).then(
        fn=chatbot.clear_conversation,
        inputs=[],
        outputs=[msg]
    )
    
    # Voice mode toggle
    def toggle_voice_mode():
        return gr.Row(visible=True), gr.Row(visible=False)
    
    def toggle_text_mode():
        return gr.Row(visible=False), gr.Row(visible=True)
    
    voice_mode_btn.click(
        fn=toggle_voice_mode,
        inputs=[],
        outputs=[voice_section, gr.Row(visible=True)]  # This will hide the main chat row
    )
    
    back_to_text_btn.click(
        fn=toggle_text_mode,
        inputs=[],
        outputs=[voice_section, gr.Row(visible=True)]  # This will show the main chat row
    )
    
    process_voice_btn.click(
        fn=voice_chat,
        inputs=[audio_input],
        outputs=[voice_output_text, voice_output_audio]
    )
    
    get_rec_btn.click(
        fn=get_recommendation,
        inputs=[category_dropdown, occasion_dropdown],
        outputs=[recommendation_output]
    )
    
    refresh_promos.click(
        fn=get_promotions,
        inputs=[],
        outputs=[promotions_display]
    )

if __name__ == "__main__":
    if os.getenv("OPENAI_API_KEY") is None and openai.api_key == "your-api-key-here":
        print("WARNING: OpenAI API key not set!")
        print("Please set your OpenAI API key as environment variable OPENAI_API_KEY")
    
    print("\n" + "="*50)
    print("🚀 FashionHub AI Assistant - ChatGPT Style")
    print("="*50)
    print("Server will be available at: http://localhost:7860")
    print("Press Ctrl+C to stop the server\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False
    )
