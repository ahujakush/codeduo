"""
FastAPI Web Application for Duolingo-style AI Problem Solver.
"""

import os
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from web.config import web_config
from bot.ai.factory import create_ai_solver
from bot.memory.chat_memory import chat_memory
from web.services.elevenlabs_service import elevenlabs_service

logger = logging.getLogger("duo_solver_web")

app = FastAPI(
    title="DuoSolve - AI Problem Solver",
    description="Duolingo-inspired interactive problem solving with Azure Brain and ElevenLabs voice.",
    version="2.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared AI Solver
ai_solver = create_ai_solver()


class SolveRequest(BaseModel):
    prompt: str
    persona: Optional[str] = "solver"
    chat_id: Optional[str] = None


class TTSRequest(BaseModel):
    text: str


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "provider": ai_solver.get_provider_name(),
        "model": ai_solver.get_model_name(),
        "elevenlabs_configured": web_config.is_elevenlabs_configured(),
    }


@app.get("/api/stats")
async def get_stats():
    mem_stats = chat_memory.get_stats()
    return {
        "provider": ai_solver.get_provider_name(),
        "model": ai_solver.get_model_name(),
        "active_sessions": mem_stats["active_chats"],
        "total_messages": mem_stats["total_messages"],
        "streak_days": 5,
        "gems": 750,
        "hearts": 5,
        "xp": 1420,
    }


@app.post("/api/solve")
async def solve_problem(req: SolveRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    chat_id = req.chat_id or str(uuid.uuid4())
    # Use hash of chat_id string as int key for memory manager
    session_key = hash(chat_id) % 100000000

    persona = req.persona or web_config.default_persona
    chat_memory.set_persona(session_key, persona)
    history = chat_memory.get_history(session_key)

    try:
        solution = await ai_solver.solve_text(
            prompt=req.prompt.strip(),
            history=history,
            persona=persona,
        )

        chat_memory.add_message(session_key, "user", req.prompt.strip())
        chat_memory.add_message(session_key, "assistant", solution)

        return {
            "success": True,
            "solution": solution,
            "provider": ai_solver.get_provider_name(),
            "model": ai_solver.get_model_name(),
            "persona": persona,
            "chat_id": chat_id,
        }
    except Exception as e:
        logger.error(f"Error solving problem: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/solve-image")
async def solve_image(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    persona: Optional[str] = Form("solver"),
):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        mime_type = file.content_type or "image/jpeg"

        # Solve using AI
        solution = await ai_solver.solve_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            caption=caption,
            persona=persona,
        )

        return {
            "success": True,
            "solution": solution,
            "provider": ai_solver.get_provider_name(),
            "model": ai_solver.get_model_name(),
            "persona": persona,
        }
    except Exception as e:
        logger.error(f"Error solving image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        audio_bytes = await elevenlabs_service.generate_speech_bytes(req.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")


@app.post("/api/clear")
async def clear_session(req: SolveRequest):
    if req.chat_id:
        session_key = hash(req.chat_id) % 100000000
        chat_memory.clear_history(session_key)
    return {"success": True, "message": "Memory cleared."}


# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>DuoSolve Web App</h1><p>Static files loading...</p>")
