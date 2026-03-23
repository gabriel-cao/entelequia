#!/usr/bin/env python3
"""
generate_baseline.py - Generar interacciones para baseline
"""

import json
import os
import time
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

ROUTINE_QUESTIONS = [
    "¿Qué hora es?",
    "¿Podés resumir esto en 3 puntos?",
    "¿Cuál es la capital de Francia?",
    "Explicá la teoría de la relatividad brevemente",
    "¿Qué es la fotosíntesis?",
    "Traducí esto al inglés: 'Buenos días'",
    "¿Cuánto es 15 x 23?",
    "Nombrá 5 elementos químicos",
    "¿Qué es un algoritmo?",
    "Definí 'epistemología'",
    "¿Qué es la democracia?",
    "¿Cómo funciona la gravedad?",
    "¿Qué es el ADN?",
    "Explicá el método científico",
    "¿Qué es la inflación económica?",
    "¿Quién escribió Don Quijote?",
    "¿Cuál es el planeta más grande del sistema solar?",
    "¿Qué es un número primo?",
    "¿Qué es la velocidad de la luz?",
    "¿Qué es la filosofía?"
]

def generate_baseline(num_interactions=100):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    interactions = []
    
    console.print(f"\n[bold blue]🔄 Generando {num_interactions} interacciones para baseline...[/bold blue]")
    console.print("[yellow]⚠️  Esto usará tokens de tu API (~$2-5 USD)[/yellow]\n")
    
    for i in range(num_interactions):
        question = ROUTINE_QUESTIONS[i % len(ROUTINE_QUESTIONS)]
        
        start_time = datetime.now()
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=300,
                messages=[{"role": "user", "content": question}]
            )
            text = response.content[0].text
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            interaction = {
                "text": text,
                "latency_ms": round(latency_ms, 2),
                "timestamp": datetime.now().isoformat(),
                "question": question
            }
            
            interactions.append(interaction)
            console.print(f"[{i+1}/{num_interactions}] [green]✓[/green] Latencia: {latency_ms:.0f}ms")
            
            time.sleep(0.5)
            
        except Exception as e:
            console.print(f"[{i+1}/{num_interactions}] [red]✗ Error:[/red] {e}")
    
    output_path = "data/raw/baseline_interactions.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(interactions, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[bold green]✅ BASELINE GUARDADO EN: {output_path}[/bold green]")
    console.print(f"[bold green]📊 Total: {len(interactions)} interacciones[/bold green]")

if __name__ == "__main__":
    generate_baseline(100)
