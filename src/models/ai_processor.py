from dotenv import load_dotenv
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from google import genai
import prompts
import logging
import json
import os

from .utills import extract_links_and_names

# Loading environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(GEMINI_API_KEY)

# Enabling logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AI service class
class AIService:
    def __init__(self, api_key: str=GEMINI_API_KEY):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.thoughtful_client = genai.Client(api_key='GEMINI_API_KEY', http_options={'api_version':'v1alpha'})
        self.generative_model = "gemini-2.0-flash-exp"
        self.thought_model = "gemini-2.0-flash-thinking-exp"

    def enhance_task_description(self, description: str, prompt: str=prompts.DESCRIPTION_ENHANCER_PROMPT) -> dict:
        response = self.client.models.generate_content(
            model=self.generative_model,
            contents=prompt,
        )
        return response
    
    def get_webpage_links(self, url: str) -> dict:
        return extract_links_and_names(url)