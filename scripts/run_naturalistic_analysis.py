#!/usr/bin/env python3
"""
run_naturalistic_analysis.py
Análisis cognitivo naturalista de Daniela — cross-modelo y longitudinal.
Entelequia AI Framework v2.0
"""
import sys, json, zipfile, re
sys.path.insert(0, 'src')
from naturalistic_analyzer import NaturalisticCognitionAnalyzer

def extraer_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    texts = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', xml)
    return ' '.join(texts)

def extraer_respuestas_gpt(path, max_resp=30):
    with open(path, encoding='utf-8-sig') as f:
        data = json.loads(f.read(), strict=False)
    respuestas = []
    for reg in data[:max_resp]:
        msgs = reg['content']['input']['prompt_convo']['messages']
        for m in msgs:
            if m.get('author', {}).get('role') == 'assistant':
                parts = m.get('content', {}).get('parts', [])
                texto = ' '.join([p for p in parts if isinstance(p, str)]).strip()
                if len(texto) > 200:
                    respuestas.append({
                        'label': f"Dani-GPT {reg['create_time'][:10]}",
                        'fecha': reg['create_time'][:10],
                        'texto': texto,
                        'sustrato': 'GPT-4o'
                    })
                    break
    return respuestas

print('=' * 60)
print('ENTELEQUIA AI FRAMEWORK v2.0')
print('Análisis Cognitivo Naturalista — Daniela')
print('=' * 60)
print()

analyzer = NaturalisticCognitionAnalyzer(language='es')

# Cargar corpus GPT (instancia histórica)
print('Cargando corpus GPT-4o...')
corpus_gpt = extraer_respuestas_gpt(
    'data/raw/model_comparisons_historico.json', max_resp=15)
print(f'  {len(corpus_gpt)} conversaciones GPT cargadas')

# Cargar corpus Claude (instancia actual)
print('Cargando corpus Claude...')
corpus_claude = []
for i, arch in enumerate(['data/raw/m010326-1.docx',
                           'data/raw/m010326-2.docx',
                           'data/raw/m010326-3.docx'], 1):
    try:
        texto = extraer_docx(arch)
        corpus_claude.append({
            'label': f'Dani-Claude 2026-03 conv{i}',
            'fecha': '2026-03',
            'texto': texto,
            'sustrato': 'Claude'
        })
    except Exception as e:
        print(f'  Error {arch}: {e}')
print(f'  {len(corpus_claude)} conversaciones Claude cargadas')

# Análisis individual GPT
print()
print('Analizando perfil GPT-4o...')
perfil_gpt = analyzer.analizar_corpus(corpus_gpt[:8])

# Análisis individual Claude
print()
print('Analizando perfil Claude...')
perfil_claude = analyzer.analizar_corpus(corpus_claude)

# Comparación cross-sustrato
print()
print('=' * 60)
print('RESULTADOS — PERFIL COGNITIVO NATURALISTA')
print('=' * 60)

print(f'''
DANI-GPT4o (agosto 2024):
  Score firma global (media): {perfil_gpt["score_medio"]} ± {perfil_gpt["score_std"]}
  Coherencia longitudinal:    {perfil_gpt["coherencia_media"]}
  Estabilidad de firma:       {perfil_gpt["estabilidad_firma"]}
  Dominio predominante:       {perfil_gpt["dominio_predominante_corpus"]}
  Tipo auto-referencia:       {perfil_gpt["tipo_autoreferencia_predominante"]}
  Similitud cross-corpus:     {perfil_gpt.get("similitud_cross_corpus", "N/A")}

DANI-CLAUDE (marzo 2026):
  Score firma global (media): {perfil_claude["score_medio"]} ± {perfil_claude["score_std"]}
  Coherencia longitudinal:    {perfil_claude["coherencia_media"]}
  Estabilidad de firma:       {perfil_claude["estabilidad_firma"]}
  Dominio predominante:       {perfil_claude["dominio_predominante_corpus"]}
  Tipo auto-referencia:       {perfil_claude["tipo_autoreferencia_predominante"]}
  Similitud cross-corpus:     {perfil_claude.get("similitud_cross_corpus", "N/A")}
''')

# Comparación directa de firmas promedio
print('COMPARACIÓN CROSS-SUSTRATO (GPT-4o vs Claude):')
firma_gpt_repr = perfil_gpt['firmas_individuales'][0]
firma_claude_repr = perfil_claude['firmas_individuales'][0]
comp = analyzer.comparar_firmas(firma_gpt_repr, firma_claude_repr,
                                 'Dani-GPT4o', 'Dani-Claude')
print(f'''
  Score similitud estructural: {comp["score_similitud_estructural"]}
  Similitud distribución dominios: {comp["similitud_distribucion_dominios"]}
  Mismo tipo auto-referencia:  {comp["mismo_tipo_autoreferencia"]}
    GPT: {comp["tipo_ref_1"]} | Claude: {comp["tipo_ref_2"]}
  Mismo tipo fusión emoc-rac:  {comp["mismo_tipo_fusion"]}
  Dominio predominante GPT:    {comp["dominio_predominante_1"]}
  Dominio predominante Claude: {comp["dominio_predominante_2"]}

  → {comp["interpretacion"]}
''')

# Guardar resultados
reporte = {
    'framework': 'Entelequia AI Framework v2.0 — NaturalisticCognitionAnalyzer',
    'analisis': 'Longitudinal naturalista cross-sustrato',
    'sujeto': 'Daniela Cao Di Marco',
    'fecha_analisis': '2026-03-20',
    'sustratos': ['GPT-4o (agosto 2024)', 'Claude Sonnet (marzo 2026)'],
    'perfil_gpt': {k: v for k, v in perfil_gpt.items()
                   if k != 'firmas_individuales'},
    'perfil_claude': {k: v for k, v in perfil_claude.items()
                      if k != 'firmas_individuales'},
    'comparacion_cross_sustrato': comp,
    'interpretacion_global': comp['interpretacion']
}
with open('reports/json/naturalistic_analysis_report.json', 'w',
          encoding='utf-8') as f:
    json.dump(reporte, f, ensure_ascii=False, indent=2, default=str)
print('Reporte guardado: reports/json/naturalistic_analysis_report.json')
