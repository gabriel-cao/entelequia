#!/usr/bin/env python3
"""
extract_history.py - Extraer chats de DOCX, PDF, JSON y TXT
"""

import os
import json
import docx
import PyPDF2
from pathlib import Path
from datetime import datetime

class ChatExtractor:
    """Extraer conversaciones de múltiples formatos"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.gpt4o_pairs = []
        self.baseline_interactions = []
        
    def extract_from_docx(self, filepath: Path) -> str:
        """Extraer texto de DOCX"""
        try:
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return text
        except Exception as e:
            print(f"  ⚠️  Error leyendo {filepath.name}: {e}")
            return ""
    
    def extract_from_pdf(self, filepath: Path) -> str:
        """Extraer texto de PDF"""
        try:
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"  ⚠️  Error leyendo {filepath.name}: {e}")
            return ""
    
    def extract_from_txt(self, filepath: Path) -> str:
        """Extraer texto de TXT"""
        try:
            # Probar diferentes encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            print(f"  ⚠️  Error de encoding en {filepath.name}")
            return ""
        except Exception as e:
            print(f"  ⚠️  Error leyendo {filepath.name}: {e}")
            return ""
    
    def extract_from_json(self, filepath: Path) -> dict:
        """Leer JSON directamente"""
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠️  Error leyendo {filepath.name}: {e}")
            return {}
    
    def parse_chat_text(self, text: str, filename: str) -> list:
        """
        Parsear texto de chat para extraer pares pregunta-respuesta
        """
        conversations = []
        
        lines = text.split('\n')
        
        current_question = ""
        current_answer = ""
        in_answer = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Patrones comunes
            if any(x in line.lower() for x in ['usuario:', 'tú:', 'pregunta:', 'user:', 'humano:']):
                if current_question and current_answer:
                    conversations.append({
                        "question": current_question,
                        "gpt4o_response": current_answer,
                        "source": filename
                    })
                current_question = line.split(':', 1)[-1].strip()
                current_answer = ""
                in_answer = False
            elif any(x in line.lower() for x in ['asistente:', 'claude:', 'gpt:', 'respuesta:', 'assistant:', 'ia:', 'bot:']):
                in_answer = True
                current_answer = line.split(':', 1)[-1].strip()
            elif in_answer:
                current_answer += " " + line
        
        # Último par
        if current_question and current_answer:
            conversations.append({
                "question": current_question,
                "gpt4o_response": current_answer,
                "source": filename
            })
        
        return conversations
    
    def process_all_files(self):
        """Procesar todos los archivos en el directorio"""
        print("🔍 Buscando archivos en:", self.input_dir)
        
        files_processed = 0
        
        # Procesar DOCX
        for filepath in self.input_dir.glob("*.docx"):
            print(f"\n📄 Procesando: {filepath.name}")
            text = self.extract_from_docx(filepath)
            if text:
                conversations = self.parse_chat_text(text, filepath.name)
                self.gpt4o_pairs.extend(conversations)
                files_processed += 1
        
        # Procesar PDF
        for filepath in self.input_dir.glob("*.pdf"):
            print(f"\n📕 Procesando: {filepath.name}")
            text = self.extract_from_pdf(filepath)
            if text:
                conversations = self.parse_chat_text(text, filepath.name)
                self.gpt4o_pairs.extend(conversations)
                files_processed += 1
        
        # Procesar TXT (AGREGADO)
        for filepath in self.input_dir.glob("*.txt"):
            print(f"\n📄 Procesando: {filepath.name}")
            text = self.extract_from_txt(filepath)
            if text:
                conversations = self.parse_chat_text(text, filepath.name)
                self.gpt4o_pairs.extend(conversations)
                files_processed += 1
        
        # Procesar JSON
        for filepath in self.input_dir.glob("*.json"):
            print(f"\n📗 Procesando: {filepath.name}")
            data = self.extract_from_json(filepath)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'question' in item:
                        item['source'] = filepath.name
                        self.gpt4o_pairs.append(item)
            elif isinstance(data, dict):
                if 'question' in data:
                    data['source'] = filepath.name
                    self.gpt4o_pairs.append(data)
            files_processed += 1
        
        print(f"\n✅ Archivos procesados: {files_processed}")
        print(f"✅ Pares pregunta-respuesta extraídos: {len(self.gpt4o_pairs)}")
        
        return self.gpt4o_pairs
    
    def select_top_questions(self, n: int = 20) -> list:
        """Seleccionar las N mejores preguntas para test cross-modelo"""
        valid_pairs = [
            p for p in self.gpt4o_pairs 
            if len(p.get('gpt4o_response', '')) > 50 and len(p.get('question', '')) > 10
        ]
        
        selected = valid_pairs[:n]
        
        print(f"\n📊 Preguntas seleccionadas para cross-modelo: {len(selected)}")
        return selected
    
    def extract_baseline_interactions(self, n: int = 100) -> list:
        """Extraer interacciones rutinarias para baseline"""
        routine_keywords = ['qué es', 'cómo', 'definí', 'explicá', 'resumí', 
                          'traducí', 'calculá', 'nombrá', 'cuál es', 'cuándo']
        
        routine_pairs = [
            p for p in self.gpt4o_pairs
            if any(k in p.get('question', '').lower() for k in routine_keywords)
        ]
        
        baseline = routine_pairs[:n]
        
        baseline_formatted = [
            {
                "text": p['gpt4o_response'],
                "latency_ms": 1000,
                "timestamp": datetime.now().isoformat(),
                "question": p.get('question', ''),
                "source": p.get('source', 'unknown')
            }
            for p in baseline
        ]
        
        print(f"\n📊 Interacciones baseline extraídas: {len(baseline_formatted)}")
        return baseline_formatted
    
    def save_results(self, selected_pairs: list, baseline: list):
        """Guardar resultados en archivos JSON"""
        pairs_output = self.output_dir / "paired_responses_gpt4o_only.json"
        with open(pairs_output, 'w', encoding='utf-8') as f:
            json.dump(selected_pairs, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Pares guardados en: {pairs_output}")
        
        baseline_output = self.output_dir / "baseline_interactions.json"
        with open(baseline_output, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        print(f"💾 Baseline guardado en: {baseline_output}")
        
        return pairs_output, baseline_output


def main():
    print("=" * 60)
    print("  EXTRACTOR DE CHATS HISTÓRICOS")
    print("=" * 60)
    
    input_dir = "data/raw/chat_history"
    output_dir = "data/raw"
    
    extractor = ChatExtractor(input_dir, output_dir)
    
    all_pairs = extractor.process_all_files()
    
    if not all_pairs:
        print("\n⚠️  No se encontraron pares pregunta-respuesta.")
        print("   Verificá que los archivos tengan formato: Usuario: / Asistente:")
        return
    
    selected_pairs = extractor.select_top_questions(n=20)
    baseline = extractor.extract_baseline_interactions(n=100)
    extractor.save_results(selected_pairs, baseline)
    
    print("\n" + "=" * 60)
    print("  ✅ EXTRACCIÓN COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Revisar data/raw/paired_responses_gpt4o_only.json")
    print("2. Ejecutar: python scripts/generate_sonnet_responses.py")
    print("3. Ejecutar: python scripts/run_all_tests.py")


if __name__ == "__main__":
    main()
