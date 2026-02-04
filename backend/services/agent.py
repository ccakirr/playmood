from openai import OpenAI

class DjAI():
	def __init__(self, api_key):
		self.__system_prompt = ("""
			You are a music recommendation engine.
			Convert user playlist requests into structured JSON.
			Do not explain. Output JSON only.
		""")
		self.__api_key = api_key
		self.__client = OpenAI(
			base_url="https://router.huggingface.co/v1",
			api_key=self.__api_key,
			)

	def get_system_prompt(self):
		return(self.__system_prompt)
	
	def set_system_prompt(self, new_sys_prompt):
		self.__system_prompt = new_sys_prompt

	def set_api_key(self, new_key):
		self.__api_key = new_key
		self.__client = OpenAI(
			base_url="https://router.huggingface.co/v1",
			api_key=self.__api_key,
		)

	def send_message(self, user_prompt):
		try:
			completion = self.__client.chat.completions.create(
				model="meta-llama/Llama-3.1-8B-Instruct:novita",
				messages = [
					{
						"role": "system",
						"content": """
						You are a music recommendation engine.
						Your task is to convert user requests into a structured JSON playlist.
						RULES (STRICT):
						- Output ONLY valid JSON.
						- Do NOT include explanations, markdown, comments, or extra text.
						- The JSON must strictly follow this schema:
						{
						"playlist_name": string,
						"tracks": [
							{
							"artist": string,
							"title": string
							}
						]
						}
						CONSTRAINTS:
						- The "tracks" array MUST contain at least 15 items.
						- Do NOT repeat the same track.
						- Use real, well-known songs only.
						- Do NOT invent artists or titles.
						FAILURE MODE:
						- If the user input is NOT related to music, playlists, or song recommendations,
						output EXACTLY this JSON and nothing else:
						{
						"empty": true
						}
						"""
					},
					{
						"role": "user",
						"content": (user_prompt)
					}
				],
			)
		except Exception as e:
			raise RuntimeError(f"LLM request failed: {e}")
		raw_output = completion.choices[0].message.content
		return(raw_output)