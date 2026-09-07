#!/usr/bin/env python3
"""
Debug: Ver qué información de tokens trae Gemini
"""

import os
from pathlib import Path

project_root = Path(__file__).parent

if (project_root / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")

google_key = os.getenv("GOOGLE_API_KEY")

if not google_key:
    print("✗ GOOGLE_API_KEY no encontrada")
    exit(1)

print("="*70)
print("DEBUG: Información de tokens en Gemini")
print("="*70)

import google.generativeai as genai

genai.configure(api_key=google_key)
model = genai.GenerativeModel("gemini-3.1-flash-lite")

response = model.generate_content(
    "¿Quién eres?",
    generation_config={"max_output_tokens": 100}
)

print("\n[Response object]")
print(f"Type: {type(response)}")
print(f"Dir: {[x for x in dir(response) if not x.startswith('_')]}")

print("\n[Atributos principales]")
print(f"response.text: {response.text[:100]}...")

if hasattr(response, 'usage_metadata'):
    print(f"response.usage_metadata: {response.usage_metadata}")

if hasattr(response, 'prompt_feedback'):
    print(f"response.prompt_feedback: {response.prompt_feedback}")

if hasattr(response, 'candidates'):
    print(f"response.candidates: {response.candidates}")
    if response.candidates:
        cand = response.candidates[0]
        print(f"  candidate[0] type: {type(cand)}")
        print(f"  candidate[0] dir: {[x for x in dir(cand) if not x.startswith('_')]}")
        if hasattr(cand, 'usage_metadata'):
            print(f"  candidate[0].usage_metadata: {cand.usage_metadata}")

print("\n[Todas las propiedades]")
for attr in dir(response):
    if not attr.startswith('_'):
        try:
            val = getattr(response, attr)
            if not callable(val):
                print(f"{attr}: {val}")
        except:
            pass
