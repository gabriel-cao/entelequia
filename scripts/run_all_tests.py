#!/usr/bin/env python3
"""
run_all_tests.py - Ejecución automatizada de todos los tests
"""

import json
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from metrics import MetricsEngine

console = Console()

def load_config():
    """Cargar configuración"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"project": {"name": "Entelequia AI"}}

def check_data_files():
    """Verificar archivos de datos"""
    files = {
        "baseline": "data/raw/baseline_interactions.json",
        "paired": "data/raw/paired_responses_manual.json"
    }
    
    status = {}
    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            status[name] = {"exists": True, "size": size, "path": path}
        else:
            status[name] = {"exists": False, "size": 0, "path": path}
    
    return status

def main():
    config = load_config()
    project_name = config.get("project", {}).get("name", "Entelequia AI")
    
    console.print(Panel.fit(f"[bold blue]🏛️ {project_name} - LABORATORIO LONGITUDINAL[/bold blue]"))
    console.print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Verificar datos
    console.print("[bold]Verificando datos...[/bold]")
    data_status = check_data_files()
    
    for name, status in data_status.items():
        if status["exists"]:
            console.print(f"  [green]✓[/green] {name}: {status['size']} bytes")
        else:
            console.print(f"  [yellow]⚠[/yellow] {name}: No encontrado")
    
    console.print()
    
    # Inicializar motor de métricas
    console.print("[bold]Inicializando motor de métricas...[/bold]")
    try:
        metrics = MetricsEngine(language="es")
        console.print("[green]✓ Motor listo[/green]\n")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print("[yellow]Ejecutá: python -m spacy download es_core_news_sm[/yellow]")
        return
    
    console.print("[green]✅ SISTEMA LISTO PARA USAR[/green]")
    console.print("\nPróximos pasos:")
    console.print("1. Completar 20 pares en data/raw/paired_responses_manual.json")
    console.print("2. Ejecutar tests específicos cuando tengas los datos")

if __name__ == "__main__":
    main()
