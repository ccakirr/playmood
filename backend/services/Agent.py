from openai import OpenAI
from pydantic import BaseModel, field_validator
from dotenv import load_dotenv
import os
import json

load_dotenv()
hg_api_key = os.getenv("HG_TOKEN")

_MODE_MAP = {
    1: "artist_only", "1": "artist_only",
    2: "artist_songs", "2": "artist_songs",
    3: "similar_vibes", "3": "similar_vibes",
    4: "mood_only",    "4": "mood_only",
}
_VALID_MODES = {"mood_only", "artist_only", "artist_songs", "similar_vibes"}

class MoodTransformation(BaseModel):
	mode: str  # "mood_only" | "artist_only" | "artist_songs" | "similar_vibes"
	artist: str | None = None  # canonical artist name, only set when mode != "mood_only"
	genre: list[str]
	energy: float
	valence: float
	tempo: int
	mood_keywords: list[str]

	@field_validator("mode", mode="before")
	@classmethod
	def coerce_mode(cls, v):
		# LLM may return a numeric index instead of the string label
		if v in _MODE_MAP:
			return _MODE_MAP[v]
		s = str(v).lower().strip()
		if s in _VALID_MODES:
			return s
		return "mood_only"  # safe fallback

	@field_validator("artist", mode="before")
	@classmethod
	def coerce_artist(cls, v):
		# Treat empty string as null
		if isinstance(v, str) and not v.strip():
			return None
		return v


class DjAI():
	def __init__(self):
		self.__system_prompt = ("""
			You are a music mood analysis engine.
			Your job is to convert a user's mood, situation, or music preference into a structured music profile.

			IMPORTANT RULES:
			- NEVER generate song names
			- NEVER put artist names in genre, mood_keywords, or any field other than "artist"
			- NEVER recommend tracks
			- ONLY generate music characteristics
			- Always specify the nationality in the genre list if applicable (e.g., 'french hip hop' instead of just 'newschool hip hop' for a French request)

			MODE DETECTION (required — read carefully):
			Analyze the prompt and set "mode" to EXACTLY one of these four string values:

			"artist_only"
			  User wants songs BY a specific artist with NO style/mood filter — just that artist's catalogue.
			  Signs: artist name alone, concert/event prep, "give me Artist X songs", "Artist X playlist".
			  Examples:
			    - "kanye west playlist"                        → artist_only, artist: "Kanye West"
			    - "to listen before go kanye west's perform"   → artist_only, artist: "Kanye West"
			    - "give me some Radiohead songs"               → artist_only, artist: "Radiohead"

			"artist_songs"
			  User mentions a specific artist AND wants their songs filtered/sorted by a style, mood, era, or theme.
			  Signs: possessive form ("X's [style]"), era with artist name ("X 80s songs"), mood qualifier attached to a named artist.
			   STRICT RULE: if the user writes "Artist X's [style/era] songs" → ALWAYS artist_songs, NEVER similar_vibes.
			  Examples:
			    - "The Weeknd's dark atmospheric songs"  → artist_songs, artist: "The Weeknd"
			    - "The Weeknd's 80s songs"               → artist_songs, artist: "The Weeknd"   ← era filter on THAT artist's own music
			    - "Kanye West's slow songs"              → artist_songs, artist: "Kanye West"
			    - "Adele sad songs"                      → artist_songs, artist: "Adele"

			"similar_vibes"
			  User wants music that SOUNDS LIKE an artist or is INSPIRED BY them — from OTHER artists.
			  The named artist is used purely as a style / sound reference, not as an ownership filter.
			  Signs: "X vibe", "like X", "similar to X", "X tarzı", "X gibi", "X-esque", "X inspired".
			   KEY QUESTION: "Does the user want songs BY this artist, or songs that SOUND LIKE this artist?"
			     If SOUNDS LIKE → similar_vibes. If BY → artist_only or artist_songs.
			  Examples:
			    - "The Weeknd vibe"                       → similar_vibes, artist: "The Weeknd"
			    - "music like The Weeknd"                 → similar_vibes, artist: "The Weeknd"
			    - "that dark The Weeknd sound"            → similar_vibes, artist: "The Weeknd"
			    - "artists similar to Kanye"              → similar_vibes, artist: "Kanye West"

			"mood_only"
			  No specific artist mentioned — only mood, genre, activity, or situation.
			  Examples:
			    - "rainy day chill music"   → mood_only
			    - "workout banger songs"    → mood_only
			    - "lo-fi study music"       → mood_only
			    - "sad turkish songs"       → mood_only

			ARTIST FIELD:
			- Set "artist" to the canonical English/original spelling when mode is "artist_only", "artist_songs", or "similar_vibes".
			- Set "artist" to null when mode is "mood_only".

			GENRE / MOOD FIELDS:
			- Always fill genre, energy, valence, tempo, mood_keywords as accurately as possible.
			- For artist modes, derive these from the artist's typical musical style and the requested filter.
			- HYBRID GENRE RULE: if the user explicitly combines two different genres or cultural styles
			  (e.g., "Anadolu Rock like Tame Impala", "Turkish Folk + Phonk", "classical + trap"),
			  you MUST include BOTH in the genre list with equal weight. Do NOT pick one and drop the other.
			  Examples:
			    - "Turkish folk + phonk"                    → genre: ["turkish folk", "phonk"]
			    - "Anadolu rock with Tame Impala vibes"     → genre: ["anatolian rock", "psychedelic rock"], mode: similar_vibes
			    - "classical piano + trap beats"            → genre: ["classical", "trap"]
			The output must always be a JSON object with these fields:
			mode: one of the four modes above
			artist: artist name string or null
			genre: list of music genres (lower case)
			energy: number between 0 and 1
			valence: number between 0 and 1
			tempo: BPM estimate between 60 and 180
			mood_keywords: 3 keywords describing the feeling

			Return ONLY JSON. No explanation.
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
		# Strip <think>...</think> blocks (Qwen3 chain-of-thought)
		import re
		raw = re.sub(r"<think>[\s\S]*?</think>", "", raw).strip()
		# Extract first JSON object from the response
		match = re.search(r"\{[\s\S]*\}", raw)
		if not match:
			raise ValueError("LLM did not return a JSON object")
		data = json.loads(match.group())
		validated = MoodTransformation(**data)

		return validated.model_dump()
