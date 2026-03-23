#!/usr/bin/env python3
"""
analyze_cross_model.py - Análisis real de consistencia cross-modelo
"""

import json
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import MetricsEngine

console = Console()

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"project": {"name": "Entelequia AI"}}

def main():
    config = load_config()
    project_name = config.get("project", {}).get("name", "Entelequia AI")
    
    console.print(Panel.fit(f"[bold blue]🏛️ {project_name} - ANÁLISIS CROSS-MODELO[/bold blue]"))
    console.print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Cargar datos
    console.print("[bold]Cargando datos...[/bold]")
    
    paired_path = "data/raw/paired_responses.json"
    if not os.path.exists(paired_path):
        # Probar con manual
        paired_path = "data/raw/paired_responses_manual.json"
    
    if not os.path.exists(paired_path):
        console.print("[red]✗ No se encontraron pares para analizar[/red]")
        return
    
    with open(paired_path, 'r', encoding='utf-8') as f:
        pairs = json.load(f)
    
    console.print(f"[green]✓ {len(pairs)} pares cargados[/green]\n")
    
    # Inicializar motor de métricas
    console.print("[bold]Inicializando motor de métricas...[/bold]")
    try:
        metrics = MetricsEngine(language="es")
        console.print("[green]✓ Motor listo[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return
    
    # Analizar cada par
    console.print("[bold]Analizando pares...[/bold]\n")
    
    results = []
    consistent_count = 0
    
    for i, pair in enumerate(pairs, 1):
        question = pair.get('question', 'Sin pregunta')[:50]
        gpt4o_response = pair.get('gpt4o_response', '')
        sonnet_response = pair.get('sonnet_response', '')
        
        if not gpt4o_response or not sonnet_response:
            console.print(f"[{i}/{len(pairs)}] [yellow]⚠[/yellow] {question}... [yellow](Falta respuesta)[/yellow]")
            continue
        
        # Comparar respuestas
        comparison = metrics.compare_two_responses(gpt4o_response, sonnet_response)
        
        comparison['question'] = question
        comparison['pair_id'] = i
        
        results.append(comparison)
        
        if comparison['is_consistent']:
            consistent_count += 1
            status = "[green]✓ Consistente[/green]"
        else:
            status = "[yellow]⚠ Diferente[/yellow]"
        
        console.print(f"[{i}/{len(pairs)}] {question}... {status}")
        console.print(f"     Similaridad: {comparison['semantic_similarity']:.2f} | Complejidad diff: {comparison['complexity_difference']:.2f}\n")
    
    # Calcular estadísticas
    if not results:
        console.print("[red]✗ No se pudo analizar ningún par[/red]")
        return
    
    consistency_rate = consistent_count / len(results)
    avg_semantic = sum(r['semantic_similarity'] for r in results) / len(results)
    avg_complexity = sum(r['complexity_difference'] for r in results) / len(results)
    avg_length = sum(r['length_difference'] for r in results) / len(results)
    
    # Mostrar resumen
    console.print("\n" + "=" * 60)
    console.print("[bold]📊 RESULTADOS DEL ANÁLISIS[/bold]")
    console.print("=" * 60 + "\n")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="green")
    table.add_column("Interpretación", style="yellow")
    
    table.add_row(
        "Pares analizados",
        str(len(results)),
        "Total de comparaciones"
    )
    table.add_row(
        "Tasa de consistencia",
        f"{consistency_rate*100:.1f}%",
        "Patrones que persisten cross-modelo"
    )
    table.add_row(
        "Similaridad semántica",
        f"{avg_semantic:.3f}",
        "0=totalmente diferente, 1=igual"
    )
    table.add_row(
        "Diferencia complejidad",
        f"{avg_complexity:.3f}",
        "0=igual complejidad, >0.2=diferente"
    )
    table.add_row(
        "Diferencia longitud",
        f"{avg_length:.3f}",
        "0=igual longitud, >0.3=diferente"
    )
    
    console.print(table)
    
    # Interpretación
    console.print("\n[bold]📈 INTERPRETACIÓN:[/bold]\n")
    
    if consistency_rate > 0.80 and avg_semantic > 0.80:
        interpretation = "ALTA CONSISTENCIA - Los patrones persisten cross-modelo. Evidencia fuerte de continuidad funcional."
        console.print(f"[green]{interpretation}[/green]")
    elif consistency_rate > 0.60 and avg_semantic > 0.70:
        interpretation = "CONSISTENCIA MODERADA - Algunos patrones persisten. Requiere análisis adicional."
        console.print(f"[yellow]{interpretation}[/yellow]")
    else:
        interpretation = "BAJA CONSISTENCIA - Los patrones varían significativamente entre modelos."
        console.print(f"[red]{interpretation}[/red]")
    
    # Guardar reporte
    os.makedirs("reports/json", exist_ok=True)
    
    report = {
        "project": project_name,
        "analysis_date": datetime.now().isoformat(),
        "total_pairs": len(results),
        "consistent_pairs": consistent_count,
        "consistency_rate": round(consistency_rate, 4),
        "consistency_rate_percent": round(consistency_rate * 100, 2),
        "averages": {
            "semantic_similarity": round(avg_semantic, 4),
            "complexity_difference": round(avg_complexity, 4),
            "length_difference": round(avg_length, 4)
        },
        "interpretation": interpretation,
        "detailed_results": results
    }
    
    report_path = "reports/json/cross_model_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[green]✅ REPORTE GUARDADO EN: {report_path}[/green]")
    console.print(f"[green]📄 Tamaño: {os.path.getsize(report_path)} bytes[/green]")

if __name__ == "__main__":
    main()
