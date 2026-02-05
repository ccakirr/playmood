import os
import json
import uuid
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from services.agent import DjAI
from typing import List

class Track(BaseModel):
	artist: str
	title: str

class PlaylistResponse(BaseModel):
	playlist_name: str
	tracks: List[Track]

class PlaylistRequest(BaseModel):
	prompt: str


load_dotenv()
hg_api_key = os.getenv("HG_TOKEN")

if not hg_api_key:
	raise RuntimeError("HG_TOKEN is missing")

ai = DjAI(hg_api_key)


router = APIRouter(prefix="/playlist", tags=["playlist"])


@router.post("/generate", response_model=PlaylistResponse)
def generate_playlist(request: PlaylistRequest):
	raw_output = ai.send_message(request.prompt)

	if not raw_output:
		raise HTTPException(
			status_code=500,
			detail="AI returned empty response."
		)

	try:
		parsed = json.loads(raw_output)
	except json.JSONDecodeError:
		raise HTTPException(
			status_code=500,
			detail="AI returned invalid json."
		)
	
	if parsed.get("empty") is True:
		raise HTTPException(
			status_code=400,
			detail="Invalid or non-music prompt."
		)

	playlist_id = str(uuid.uuid4())

	# Store in temporary storage (shared with youtube_router)
	from routers.youtube_router import playlists_db
	playlists_db[playlist_id] = parsed

	return {
		"playlist_id": playlist_id,
		**parsed
	}
