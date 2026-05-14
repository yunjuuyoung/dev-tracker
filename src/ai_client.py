AI_CLIENTS = {}

try:
    import google.generativeai as genai
    AI_CLIENTS['gemini'] = True
except ImportError:
    AI_CLIENTS['gemini'] = False

try:
    import openai
    AI_CLIENTS['chatgpt'] = True
except ImportError:
    AI_CLIENTS['chatgpt'] = False

try:
    import requests
    AI_CLIENTS['ollama'] = True
except ImportError:
    AI_CLIENTS['ollama'] = False


class AIClient:
    """AI API 클라이언트 통합 클래스"""

    def __init__(self, config):
        self.provider = config.get('ai_provider', 'gemini')
        self.api_key = config.get('api_key', '')
        self.ollama_model = config.get('ollama_model', 'llama3.2')
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')

        if self.provider == 'gemini':
            if not AI_CLIENTS['gemini']:
                raise ImportError("google-generativeai가 설치되지 않았습니다. pip install google-generativeai")
            genai.configure(api_key=self.api_key)
            gemini_model = config.get('gemini_model', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(gemini_model)

        elif self.provider == 'chatgpt':
            if not AI_CLIENTS['chatgpt']:
                raise ImportError("openai가 설치되지 않았습니다. pip install openai")
            self.client = openai.OpenAI(api_key=self.api_key)

        elif self.provider == 'ollama':
            if not AI_CLIENTS['ollama']:
                raise ImportError("requests가 설치되지 않았습니다. pip install requests")
            try:
                response = requests.get(f"{self.ollama_url}/api/tags")
                if response.status_code != 200:
                    print(f"⚠️  Ollama 서버에 연결할 수 없습니다: {self.ollama_url}")
                    print("   Ollama를 설치하고 실행했는지 확인하세요.")
            except Exception as e:
                print(f"⚠️  Ollama 연결 오류: {e}")

    def generate_explanation(self, prompt):
        try:
            if self.provider == 'gemini':
                return self._generate_gemini(prompt)
            elif self.provider == 'chatgpt':
                return self._generate_chatgpt(prompt)
            elif self.provider == 'ollama':
                return self._generate_ollama(prompt)
        except Exception as e:
            return f"⚠️ AI 설명 생성 실패: {str(e)}\n(변경사항은 기록되었습니다)"

    def _generate_gemini(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def _generate_chatgpt(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 코드 변경사항을 분석하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content

    def _generate_ollama(self, prompt):
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()['response']
        raise Exception(f"Ollama API 오류: {response.status_code}")
