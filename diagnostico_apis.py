#!/usr/bin/env python3
"""
Diagnóstico directo de APIs y modelos
Prueba cada proveedor sin pasar por TensorHemisphere
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src/architecture"))

# Cargar .env
if (project_root / ".env").exists():
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
    print(f"✓ Cargado .env desde {project_root / '.env'}")
else:
    print(f"✗ No encontrado .env en {project_root / '.env'}")

print("\n" + "="*70)
print("DIAGNÓSTICO DE APIs")
print("="*70)

# 1. GOOGLE / GEMINI
print("\n[1] GOOGLE (Gemini 3.1 Flash Lite)")
print("-" * 70)

google_key = os.getenv("GOOGLE_API_KEY")
if not google_key:
    print("✗ GOOGLE_API_KEY no encontrada en ambiente")
else:
    print(f"✓ GOOGLE_API_KEY presente: {google_key[:20]}...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel("gemini-3.1-flash-lite")
        response = model.generate_content("Hola, ¿quién eres?", stream=False)
        print(f"✓ ÉXITO: Gemini responde")
        print(f"  Modelo: gemini-3.1-flash-lite ✓")
        print(f"  Respuesta: {response.text[:100]}...")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print(f"  Verifica: modelo ID correcto, API key válida, cuota disponible")

# 2. XAI / GROK
print("\n[2] XAI (Grok 4.6)")
print("-" * 70)

xai_key = os.getenv("XAI_API_KEY")
if not xai_key:
    print("✗ XAI_API_KEY no encontrada en ambiente")
else:
    print(f"✓ XAI_API_KEY presente: {xai_key[:20]}...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=xai_key, base_url="https://api.x.ai/v1")
        response = client.chat.completions.create(
            model="grok-4.6",
            messages=[{"role": "user", "content": "Hola, ¿quién eres?"}],
            max_tokens=100
        )
        print(f"✓ ÉXITO: Grok responde")
        print(f"  Modelo: grok-4.6 ✓")
        print(f"  Respuesta: {response.choices[0].message.content[:100]}...")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print(f"  Verifica: base_url correcta, modelo ID correcto, API key válida")

# 3. ALIBABA / QWEN
print("\n[3] ALIBABA (Qwen 3.8 Max)")
print("-" * 70)

qwen_key = os.getenv("QWEN_API_KEY")
if not qwen_key:
    print("✗ QWEN_API_KEY no encontrada en ambiente")
else:
    print(f"✓ QWEN_API_KEY presente: {qwen_key[:20]}...")
    try:
        from dashscope import Generation
        response = Generation.call(
            model="qwen3.8-max",
            messages=[{"role": "user", "content": "Hola, ¿quién eres?"}],
            api_key=qwen_key
        )
        if response.status_code == 200:
            print(f"✓ ÉXITO: Qwen responde")
            print(f"  Modelo: qwen3.8-max ✓")
            print(f"  Respuesta: {response.output['text'][:100]}...")
        else:
            print(f"✗ ERROR: Qwen retornó status {response.status_code}")
            print(f"  Response: {response}")
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print(f"  Verifica: modelo ID correcto, API key válida, dashscope instalado")

print("\n" + "="*70)
print("FIN DIAGNÓSTICO")
print("="*70)
