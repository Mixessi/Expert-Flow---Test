import asyncio
import json
import time
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.audio_processor import AudioBuffer, transcribe_audio
from app.database import async_session
from app.models.interview import Interview
from app.models.transcript import TranscriptSegment
from app.services.credibility import evaluate_credibility
from app.services.followup_engine import generate_followup_prompts
from app.services.number_engine import cross_check_numbers, extract_numbers, save_extracted_numbers

router = APIRouter()


class InterviewSession:
    """Manages the real-time state of a live interview."""

    def __init__(self, interview_id: uuid.UUID):
        self.interview_id = interview_id
        self.audio_buffer = AudioBuffer()
        self.audio_queue: asyncio.Queue[str] = asyncio.Queue()
        self.transcript_segments: list[dict] = []
        self.segment_counter = 0
        self.start_time = time.time()
        self.last_followup_time = 0.0
        self.last_crosscheck_time = 0.0
        self.last_credibility_time = 0.0

    @property
    def elapsed_ms(self) -> int:
        return int((time.time() - self.start_time) * 1000)

    @property
    def recent_transcript(self) -> str:
        """Last ~2 minutes of transcript text."""
        texts = [s["text"] for s in self.transcript_segments[-20:]]
        return " ".join(texts)

    async def run_audio_consumer(self, ws: WebSocket):
        """Consume audio chunks, buffer, transcribe, and broadcast."""
        while True:
            base64_audio = await self.audio_queue.get()
            segment_data = self.audio_buffer.add_chunk(base64_audio)

            if segment_data:
                result = await transcribe_audio(segment_data)
                if result["text"].strip():
                    seg = {
                        "segment_index": self.segment_counter,
                        "speaker": "expert",
                        "text": result["text"],
                        "start_time_ms": self.elapsed_ms - 3000,
                        "end_time_ms": self.elapsed_ms,
                        "confidence": result["confidence"],
                    }
                    self.transcript_segments.append(seg)
                    self.segment_counter += 1

                    # Save to DB
                    async with async_session() as db:
                        db_seg = TranscriptSegment(
                            interview_id=self.interview_id,
                            **seg,
                        )
                        db.add(db_seg)
                        await db.commit()
                        await db.refresh(db_seg)

                        # Extract numbers
                        numbers = extract_numbers(result["text"])
                        if numbers:
                            saved = await save_extracted_numbers(
                                db, self.interview_id, db_seg.id, numbers
                            )
                            for num in saved:
                                await ws.send_json({
                                    "type": "number_extracted",
                                    "data": {
                                        "id": str(num.id),
                                        "value": num.value,
                                        "context": num.context,
                                        "category": num.category,
                                        "verification": num.verification,
                                    },
                                })

                    # Broadcast transcript
                    await ws.send_json({"type": "transcript_segment", "data": seg})

    async def run_followup_engine(self, ws: WebSocket):
        """Periodically generate JIT follow-up prompts."""
        while True:
            await asyncio.sleep(15)
            if not self.transcript_segments:
                continue

            now = time.time()
            if now - self.last_followup_time < 14:
                continue
            self.last_followup_time = now

            try:
                async with async_session() as db:
                    prompts = await generate_followup_prompts(
                        db=db,
                        interview_id=self.interview_id,
                        recent_transcript=self.recent_transcript,
                    )
                if prompts:
                    await ws.send_json({"type": "followup_prompt", "data": {"prompts": prompts}})
            except Exception as e:
                await ws.send_json({"type": "error", "data": {"message": f"Follow-up error: {e}"}})

    async def run_number_crosscheck(self, ws: WebSocket):
        """Periodically cross-check extracted numbers."""
        while True:
            await asyncio.sleep(30)
            if not self.transcript_segments:
                continue

            now = time.time()
            if now - self.last_crosscheck_time < 29:
                continue
            self.last_crosscheck_time = now

            try:
                async with async_session() as db:
                    result = await cross_check_numbers(db, self.interview_id)
                if result.get("inconsistencies"):
                    await ws.send_json({"type": "number_flag", "data": result})
            except Exception as e:
                await ws.send_json({"type": "error", "data": {"message": f"Cross-check error: {e}"}})

    async def run_credibility_engine(self, ws: WebSocket):
        """Periodically evaluate expert credibility."""
        while True:
            await asyncio.sleep(60)
            if not self.transcript_segments:
                continue

            now = time.time()
            if now - self.last_credibility_time < 59:
                continue
            self.last_credibility_time = now

            try:
                async with async_session() as db:
                    interview = await db.get(Interview, self.interview_id)
                    result = await evaluate_credibility(
                        expert_bio=interview.expert_bio or "",
                        transcript_window=self.recent_transcript,
                    )
                    # Update interview credibility score
                    if "score" in result:
                        interview.credibility_score = result["score"]
                        await db.commit()

                await ws.send_json({"type": "credibility_update", "data": result})
            except Exception as e:
                await ws.send_json({"type": "error", "data": {"message": f"Credibility error: {e}"}})


@router.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: uuid.UUID):
    await websocket.accept()
    session = InterviewSession(interview_id)

    # Launch background analysis tasks
    tasks = [
        asyncio.create_task(session.run_audio_consumer(websocket)),
        asyncio.create_task(session.run_followup_engine(websocket)),
        asyncio.create_task(session.run_number_crosscheck(websocket)),
        asyncio.create_task(session.run_credibility_engine(websocket)),
    ]

    try:
        while True:
            msg = await websocket.receive_json()
            msg_type = msg.get("type")

            if msg_type == "audio_chunk":
                await session.audio_queue.put(msg["data"])
            elif msg_type == "request_followup":
                async with async_session() as db:
                    prompts = await generate_followup_prompts(
                        db=db,
                        interview_id=interview_id,
                        recent_transcript=session.recent_transcript,
                    )
                if prompts:
                    await websocket.send_json({"type": "followup_prompt", "data": {"prompts": prompts}})
    except WebSocketDisconnect:
        pass
    finally:
        for t in tasks:
            t.cancel()
        # Flush remaining audio
        remaining = session.audio_buffer.flush()
        if remaining:
            result = await transcribe_audio(remaining)
            if result["text"].strip():
                async with async_session() as db:
                    seg = TranscriptSegment(
                        interview_id=interview_id,
                        segment_index=session.segment_counter,
                        speaker="expert",
                        text=result["text"],
                        start_time_ms=session.elapsed_ms - 1000,
                        end_time_ms=session.elapsed_ms,
                    )
                    db.add(seg)
                    await db.commit()
