#!/usr/bin/env python3
"""
generate_sonnet_responses.py - Generar respuestas Sonnet para preguntas de GPT-4o
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

def generate_sonnet_responses():
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Cargar preguntas de GPT-4o
    input_path = "data/raw/paired_responses_gpt4o_only.json"
    
    if not os.path.exists(input_path):
        console.print("[red]✗ No se encontró:[/red] " + input_path)
        console.print("[yellow]Ejecutá primero: python scripts/extract_history.py[/yellow]")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        gpt4o_pairs = json.load(f)
    
    console.print(f"\n[bold blue]📊 Preguntas cargadas: {len(gpt4o_pairs)}[/bold blue]\n")
    
    paired_responses = []
    
    for i, pair in enumerate(gpt4o_pairs, 1):
        question = pair.get('question', '')
        gpt4o_response = pair.get('gpt4o_response', '')
        
        if not question:
            console.print(f"[yellow]⚠️  Saltando par {i}: sin pregunta[/yellow]")
            continue
        
        console.print(f"[{i}/{len(gpt4o_pairs)}] {question[:60]}...")
        
        # Generar respuesta con Sonnet
        start_time = datetime.now()
        try:
            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                messages=[{"role": "user", "content": question}]
            )
            sonnet_response = response.content[0].text
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            paired = {
                "question": question,
                "gpt4o_response": gpt4o_response,
                "sonnet_response": sonnet_response,
                "gpt4o_latency_ms": pair.get('latency_ms', 0),
                "sonnet_latency_ms": round(latency_ms, 2),
                "source": pair.get('source', 'historical'),
                "timestamp": datetime.now().isoformat()
            }
            
            paired_responses.append(paired)
            console.print(f"  [green]✓ Sonnet:[/green] {len(sonnet_response)} caracteres, {latency_ms:.0f}ms\n")
            
            # Pausa para no saturar API
            time.sleep(1)
            
        except Exception as e:
            console.print(f"  [red]✗ Error:[/red] {e}\n")
            # Guardar con placeholder
            paired = {
                "question": question,
                "gpt4o_response": gpt4o_response,
                "sonnet_response": "ERROR_EN_GENERACION",
                "gpt4o_latency_ms": pair.get('latency_ms', 0),
                "sonnet_latency_ms": 0,
                "source": pair.get('source', 'historical'),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            paired_responses.append(paired)
    
    # Guardar resultado final
    output_path = "data/raw/paired_responses.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(paired_responses, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[bold green]✅ PARES COMPLETOS GUARDADOS EN: {output_path}[/bold green]")
    console.print(f"[bold green]📊 Total: {len(paired_responses)} pares[/bold green]")
    console.print(f"\n[bold]Ahora podés ejecutar:[/bold] python scripts/run_all_tests.py")


if __name__ == "__main__":
    generate_sonnet_responses()
