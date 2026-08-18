import litellm
from deepeval.models.base_model import DeepEvalBaseLLM

class GeminiDeepEvalModel(DeepEvalBaseLLM):
    def __init__(self, model_name="gemini/gemini-2.5-flash"):
        self.model_name = model_name
        
    def load_model(self):
        return self.model_name
        
    def generate(self, prompt: str) -> str:
        response = litellm.completion(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            num_retries=3
        )
        return response.choices[0].message.content
        
    async def a_generate(self, prompt: str) -> str:
        response = await litellm.acompletion(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            num_retries=3
        )
        return response.choices[0].message.content
        
    def get_model_name(self):
        return self.model_name
