#!/usr/bin/env python3
"""
generate_sonnet_for_manual.py - Generar Sonnet para preguntas manuales
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

def main():
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    input_path = "data/raw/paired_responses_manual.json"
    
    if not os.path.exists(input_path):
        console.print("[red]✗ No se encontró:[/red] " + input_path)
        console.print("[yellow]Creá el archivo primero con tus pares GPT-4o + Sonnet[/yellow]")
        return
    
    with open(input_path, 'r', encoding='utf-8') as f:
        manual_pairs = json.load(f)
    
    console.print(f"\n[bold blue]📊 Preguntas cargadas: {len(manual_pairs)}[/bold blue]\n")
    
    paired_responses = []
    
    for i, pair in enumerate(manual_pairs, 1):
        question = pair.get('question', '')
        gpt4o_response = pair.get('gpt4o_response', '')
        
        if not question:
            continue
        
        console.print(f"[{i}/{len(manual_pairs)}] {question[:60]}...")
        
        # Si ya tiene respuesta Sonnet, usarla
        if pair.get('sonnet_response') and pair.get('sonnet_response') != "COMPLETAR CON RESPUESTA DE SONNET":
            sonnet_response = pair['sonnet_response']
            latency_ms = pair.get('sonnet_latency_ms', 0)
        else:
            # Generar nueva
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
            except Exception as e:
                console.print(f"  [red]✗ Error:[/red] {e}")
                continue
        
        paired = {
            "question": question,
            "gpt4o_response": gpt4o_response,
            "sonnet_response": sonnet_response,
            "gpt4o_latency_ms": pair.get('gpt4o_latency_ms', 0),
            "sonnet_latency_ms": round(latency_ms, 2) if latency_ms else 0,
            "source": pair.get('source', 'manual'),
            "timestamp": datetime.now().isoformat()
        }
        
        paired_responses.append(paired)
        console.print(f"  [green]✓ Sonnet:[/green] {len(sonnet_response)} chars\n")
        
        time.sleep(1)
    
    output_path = "data/raw/paired_responses.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(paired_responses, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[bold green]✅ GUARDADO EN: {output_path}[/bold green]")
    console.print(f"[bold green]📊 Total: {len(paired_responses)} pares[/bold green]")

if __name__ == "__main__":
    main()
