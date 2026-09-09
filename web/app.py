"""
CodingDuo - AI Intermediate Code Optimization Web Platform.
Features 6 famous language boilerplates, compiler optimization passes,
real-time code mistake detection with (i) info badges, 1-click 'Apply' fixes,
and teacher-style audio walkthroughs powered by ElevenLabs.
"""

import os
import uuid
import logging
from typing import Optional, List, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from web.config import web_config
from bot.ai.factory import create_ai_solver
from bot.memory.chat_memory import chat_memory
from web.services.elevenlabs_service import elevenlabs_service
from web.services.boilerplates import LANGUAGE_BOILERPLATES
from web.services.teacher_explainer import generate_teacher_explanation
from web.services.code_checker import analyze_code_for_errors

logger = logging.getLogger("codingduo")

app = FastAPI(
    title="CodingDuo - AI Intermediate Code Optimizer",
    description="Interactive platform for applying compiler optimization techniques to Intermediate Code.",
    version="2.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_solver = create_ai_solver()


class OptimizeRequest(BaseModel):
    code: str
    pass_type: Optional[str] = "all_passes"
    session_id: Optional[str] = None
    language: Optional[str] = "python"


class CheckCodeRequest(BaseModel):
    code: str
    language: Optional[str] = "python"


class TTSRequest(BaseModel):
    text: Optional[str] = None
    code: Optional[str] = None
    solution: Optional[str] = None
    teacher_mode: Optional[bool] = True


class TeacherScriptRequest(BaseModel):
    code: str
    solution: str


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": "CodingDuo",
        "optimizer": ai_solver.get_provider_name(),
        "model": ai_solver.get_model_name(),
        "elevenlabs_configured": web_config.is_elevenlabs_configured(),
    }


@app.get("/api/boilerplates")
@app.get("/api/presets")
async def get_boilerplates():
    """Return the 6 famous programming language boilerplate templates."""
    return LANGUAGE_BOILERPLATES


@app.get("/api/stats")
async def get_stats():
    mem_stats = chat_memory.get_stats()
    return {
        "platform": "CodingDuo",
        "optimizer": ai_solver.get_provider_name(),
        "model": ai_solver.get_model_name(),
        "active_sessions": mem_stats["active_chats"],
        "total_optimizations": mem_stats["total_messages"] // 2,
        "streak_days": 5,
        "gems": 750,
        "xp": 1420,
    }


@app.post("/api/check-code")
async def check_code(req: CheckCodeRequest):
    """Analyze code for mistakes, syntax errors, and return line numbers, explanations, and 1-click fixes."""
    res = await analyze_code_for_errors(req.code, req.language or "python")
    return res


@app.post("/api/optimize")
@app.post("/api/solve")
async def optimize_code(req: OptimizeRequest):
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    session_id = req.session_id or str(uuid.uuid4())
    session_key = hash(session_id) % 100000000

    pass_type = req.pass_type or "all_passes"
    chat_memory.set_persona(session_key, pass_type)
    history = chat_memory.get_history(session_key)

    try:
        solution = await ai_solver.solve_text(
            prompt=req.code.strip(),
            history=history,
            persona=pass_type,
        )

        chat_memory.add_message(session_key, "user", req.code.strip())
        chat_memory.add_message(session_key, "assistant", solution)

        return {
            "success": True,
            "solution": solution,
            "optimizer": ai_solver.get_provider_name(),
            "model": ai_solver.get_model_name(),
            "pass_type": pass_type,
            "session_id": session_id,
        }
    except Exception as e:
        logger.error(f"Error optimizing intermediate code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize-image")
@app.post("/api/solve-image")
async def optimize_image(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    pass_type: Optional[str] = Form("all_passes"),
):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        mime_type = file.content_type or "image/jpeg"

        solution = await ai_solver.solve_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            caption=caption,
            persona=pass_type,
        )

        return {
            "success": True,
            "solution": solution,
            "optimizer": ai_solver.get_provider_name(),
            "model": ai_solver.get_model_name(),
            "pass_type": pass_type,
        }
    except Exception as e:
        logger.error(f"Error optimizing image IR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/teacher-explanation")
async def get_teacher_explanation(req: TeacherScriptRequest):
    """Generate an intuitive, warm teacher-style explanation of the code optimizations."""
    if not req.code or not req.solution:
        raise HTTPException(status_code=400, detail="Both code and solution are required.")

    script = await generate_teacher_explanation(req.code, req.solution)
    return {"success": True, "teacher_script": script}


@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    """
    Generate speech audio via ElevenLabs.
    If teacher_mode is True and code/solution are provided,
    speaks as a friendly professor explaining the concepts intuitively.
    """
    speech_text = req.text

    if req.teacher_mode and req.code and req.solution:
        speech_text = await generate_teacher_explanation(req.code, req.solution)

    if not speech_text or not speech_text.strip():
        raise HTTPException(status_code=400, detail="No text provided for speech.")

    try:
        audio_bytes = await elevenlabs_service.generate_speech_bytes(speech_text)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"X-Spoken-Text": speech_text[:200].replace("\n", " ")},
        )
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Voice narration failed: {e}")


@app.post("/api/clear")
async def clear_session(req: OptimizeRequest):
    if req.session_id:
        session_key = hash(req.session_id) % 100000000
        chat_memory.clear_history(session_key)
    return {"success": True, "message": "Optimization session reset."}


static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>CodingDuo - AI Intermediate Code Optimizer</h1>")
