"""
CodingDuo - AI Intermediate Code Optimization Web Platform.
Applies code optimization passes to Three-Address Code, SSA, and IR with tactile Duolingo aesthetic.
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

logger = logging.getLogger("codingduo")

app = FastAPI(
    title="CodingDuo - AI Intermediate Code Optimizer",
    description="Interactive platform for applying compiler optimization techniques to Intermediate Code.",
    version="2.1.0",
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


class TTSRequest(BaseModel):
    text: str


# Preset Intermediate Code examples
IR_PRESETS: Dict[str, Dict[str, str]] = {
    "cse_const": {
        "title": "Constant Folding & CSE",
        "description": "Redundant calculations and constant expressions in Three-Address Code.",
        "code": (
            "# Expression: x = (2 * 4) + a; y = (2 * 4) + a + b\n"
            "t1 = 2 * 4\n"
            "t2 = t1 + a\n"
            "x = t2\n"
            "t3 = 2 * 4\n"
            "t4 = t3 + a\n"
            "t5 = t4 + b\n"
            "y = t5"
        ),
    },
    "loop_invariant": {
        "title": "Loop Invariant Code Motion (LICM)",
        "description": "Computations inside the loop that do not change across iterations.",
        "code": (
            "# while (i < 100) { a[i] = x + y; i++; }\n"
            "L1:\n"
            "  if i >= 100 goto L2\n"
            "  t1 = x + y\n"
            "  t2 = i * 4\n"
            "  a[t2] = t1\n"
            "  t3 = i + 1\n"
            "  i = t3\n"
            "  goto L1\n"
            "L2:\n"
            "  return"
        ),
    },
    "dead_code": {
        "title": "Dead Code & Variable Pruning",
        "description": "Unused temporaries and dead assignments that never affect output.",
        "code": (
            "t1 = a * b\n"
            "t2 = c + d\n"
            "t3 = t1 + 10\n"
            "dead_var = t2 * 5\n"
            "unused_res = a + 1\n"
            "return t3"
        ),
    },
    "strength_reduction": {
        "title": "Strength Reduction & Peephole",
        "description": "Replacing expensive multiplications with additions or bitwise shifts.",
        "code": (
            "# Array index stepping in loop\n"
            "t1 = i * 2\n"
            "t2 = t1 + 0\n"
            "t3 = x * 1\n"
            "t4 = j * 8\n"
            "ans = t2 + t3 + t4"
        ),
    },
}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": "CodingDuo",
        "optimizer": ai_solver.get_provider_name(),
        "model": ai_solver.get_model_name(),
        "elevenlabs_configured": web_config.is_elevenlabs_configured(),
    }


@app.get("/api/presets")
async def get_presets():
    return IR_PRESETS


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


@app.post("/api/optimize")
@app.post("/api/solve")
async def optimize_code(req: OptimizeRequest):
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Intermediate code cannot be empty.")

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


@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        audio_bytes = await elevenlabs_service.generate_speech_bytes(req.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
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
