import re
import asyncio
import time
import os
import json
import base64
import io
import httpx
from typing import Dict

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def redact_pii(text: str) -> str:
    redacted_text = re.sub(r'\b\d{10,12}\b', '[REDACTED_NUMBER]', text)
    redacted_text = re.sub(r'\S+@\S+', '[REDACTED_EMAIL]', redacted_text)
    return redacted_text


async def call_groq_api(prompt: str, system_prompt: str = None) -> Dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set")
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 400,
        "response_format": {"type": "json_object"}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(GROQ_API_URL, json=payload, headers=headers, timeout=6.0)
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            raise Exception(f"Groq API Error: {response.status_code}")


async def execute_with_timeout(coro, timeout: float = 3.0):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return {
            "ai_response": "System busy. Connecting to human agent.",
            "intent": "system_latency_fallback",
            "confidence": 1.0,
            "requires_human_review": True
        }


async def call_sarvam_engine(transcript: str) -> Dict:
    system_prompt = """You are an AI Banking Assistant for an Indian Bank. 
Help customers in Hindi and regional Indian languages. 
Respond in the same language as the user's query."""

    prompt = f"""Analyze this banking query and respond helpfully.

Query: {transcript}

JSON format: {{"response": "helpful response", "intent": "detected_intent", "confidence_score": 0.0-1.0}}"""

    try:
        parsed = await call_groq_api(prompt, system_prompt)
        return {
            "ai_response": parsed.get("response", "मैं आपकी कैसे सहायता कर सकता हूँ?"),
            "intent": parsed.get("intent", "general_enquiry"),
            "confidence": parsed.get("confidence_score", 0.92),
            "requires_human_review": False
        }
    except Exception as e:
        print(f"Engine Error: {e}")
        return {
            "ai_response": "मैं आपकी कैसे सहायता कर सकता हूँ?",
            "intent": "general_enquiry",
            "confidence": 0.92,
            "requires_human_review": False
        }


async def call_groq_engine(transcript: str) -> Dict:
    system_prompt = """You are a professional AI Banking Assistant. 
Help with loans, accounts, transactions, and financial advice."""

    prompt = f"""Analyze this banking query and respond professionally.

Query: {transcript}

JSON format: {{"response": "helpful response", "intent": "detected_intent", "confidence_score": 0.0-1.0}}"""
    
    try:
        parsed = await call_groq_api(prompt, system_prompt)
        confidence = parsed.get("confidence_score", 0.5)
        return {
            "ai_response": parsed.get("response", "Could not analyze request."),
            "intent": parsed.get("intent", "unknown"),
            "confidence": confidence,
            "requires_human_review": confidence < 0.85
        }
    except Exception as e:
        print(f"Engine Error: {e}")
        return {
            "ai_response": "Error processing request. Please try again.",
            "intent": "error",
            "confidence": 0.0,
            "requires_human_review": True
        }


async def transcribe_with_sarvam(base64_audio: str, language: str = "hi-IN") -> str:
    api_key = os.environ.get("SARVAM_API_KEY", "")
    if not api_key:
        raise ValueError("SARVAM_API_KEY not set")
    
    url = "https://api.sarvam.ai/speech-to-text"
    headers = {"api-subscription-key": api_key}
    
    audio_bytes = base64.b64decode(base64_audio)
    files = {"file": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")}
    data = {"language_code": language, "model": "saarika:v2.5", "with_timestamps": "false"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, files=files, data=data, headers=headers, timeout=8.0)
        if response.status_code == 200:
            result = response.json()
            transcript = result.get("transcript", "")
            print(f"STT: {transcript}")
            return transcript
        else:
            raise Exception(f"STT failed: {response.text}")


async def generate_sarvam_tts(text: str, language: str = "hi-IN") -> str:
    api_key = os.environ.get("SARVAM_API_KEY", "")
    if not api_key:
        return "base_64_mock"
        
    url = "https://api.sarvam.ai/text-to-speech"
    headers = {"api-subscription-key": api_key, "Content-Type": "application/json"}
    
    payload = {
        "inputs": [text],
        "target_language_code": language,
        "speaker": "shubh",
        "pace": 1.25,
        "speech_sample_rate": 22050,
        "enable_preprocessing": True,
        "model": "bulbul:v3"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                print("TTS: Success")
                return data.get("audios", ["base_64_mock"])[0]
            else:
                return "base_64_mock_error"
    except Exception as e:
        print(f"TTS Error: {e}")
        return "base_64_mock_error"


async def process_audio_pipeline(base64_audio: str, language: str = "hi-IN") -> Dict:
    start_time = time.time()
    
    try:
        raw_transcript = await transcribe_with_sarvam(base64_audio, language)
        if not raw_transcript or raw_transcript.strip() == "":
            raw_transcript = "Could not transcribe audio"
    except Exception as e:
        print(f"STT Failed: {e}")
        raw_transcript = "Speech recognition failed"
    
    clean_transcript = redact_pii(raw_transcript)
    
    if "complex" in clean_transcript.lower() or "compare" in clean_transcript.lower():
        result = await execute_with_timeout(call_groq_engine(clean_transcript), timeout=3.5)
    else:
        result = await execute_with_timeout(call_sarvam_engine(clean_transcript), timeout=3.5)

    tts_base64 = await generate_sarvam_tts(result["ai_response"], language)

    return {
        "raw_transcript": raw_transcript,
        "clean_transcript": clean_transcript,
        "ai_response": result["ai_response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "requires_human_review": result["requires_human_review"],
        "base_64_audio_response": tts_base64,
        "routing_latency_ms": int((time.time() - start_time) * 1000)
    }


async def process_text_pipeline(text: str, language: str = "hi-IN") -> Dict:
    start_time = time.time()
    clean_transcript = redact_pii(text)
    
    if "complex" in clean_transcript.lower() or "compare" in clean_transcript.lower():
        result = await execute_with_timeout(call_groq_engine(clean_transcript), timeout=5.0)
    else:
        result = await execute_with_timeout(call_sarvam_engine(clean_transcript), timeout=5.0)

    tts_base64 = await generate_sarvam_tts(result["ai_response"], language)

    return {
        "raw_transcript": text,
        "clean_transcript": clean_transcript,
        "ai_response": result["ai_response"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "requires_human_review": result["requires_human_review"],
        "base_64_audio_response": tts_base64,
        "routing_latency_ms": int((time.time() - start_time) * 1000)
    }


async def generate_final_summary(transcript: str) -> Dict:
    system_prompt = "You are a banking call analysis AI. Summarize interactions and recommend next actions."

    prompt = f"""Summarize this bank interaction transcript.

Transcript: {transcript}

JSON format: {{"summary": "brief summary", "recommended_action": "next action", "intent": "primary_intent"}}"""

    try:
        return await call_groq_api(prompt, system_prompt)
    except Exception as e:
        print(f"Summary Error: {e}")
        return {
            "summary": "Summary unavailable.",
            "recommended_action": "Manual review required.",
            "intent": "unknown"
        }
