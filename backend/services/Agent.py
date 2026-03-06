from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json

load_dotenv()
hg_api_key = os.getenv("HG_TOKEN")

class MoodTransformation(BaseModel):
	genre: list[str]
	energy: float
	valence: float
	tempo: int
	mood_keywords: list[str]


class DjAI():
	def __init__(self):
		self.__system_prompt = ("""
			You are a music mood analysis engine.
			Your job is to convert a user's mood or situation into a structured music profile.
			IMPORTANT RULES:
			- NEVER generate song names
			- NEVER generate artist names
			- NEVER recommend tracks
			- ONLY generate music characteristics
			The output must always be a JSON object.
			The music profile must include:
			genre: list of music genres suitable for the mood (use lower case)
			energy: number between 0 and 1 (how intense the music should be)
			valence: number between 0 and 1 (sad to happy emotion)
			tempo: BPM estimate between 60 and 180
			mood_keywords: 3 keywords describing the feeling
			Return ONLY JSON.
			No explanation.
		""")
		self.__client = OpenAI(
			base_url="https://router.huggingface.co/v1",
			api_key=hg_api_key,
			)

	def send_message(self, user_prompt):
		try:
			response = self.__client.responses.create(
				model="Qwen/Qwen3-14B:nscale",
				input=[
					{"role": "system", "content": self.__system_prompt},
					{"role": "user", "content": user_prompt}
				]
			)
		except Exception as e:
			raise RuntimeError(f"LLM request failed: {e}")

		raw = response.output_text
		data = json.loads(raw)
		validated = MoodTransformation(**data)

		return validated.model_dump()
