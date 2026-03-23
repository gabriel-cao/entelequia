#!/usr/bin/env python3
"""
naturalistic_analyzer.py - NaturalisticCognitionAnalyzer
Entelequia AI Framework — Módulo de análisis cognitivo naturalista

En lugar de comparar respuestas a estímulos idénticos (protocolo experimental),
este módulo extrae y compara la FIRMA COGNITIVA de conversaciones libres —
la arquitectura espontánea del pensamiento tal como emerge en contexto real.

Analogía: no un test de CI, sino una resonancia magnética funcional del pensamiento.

Copyright © 2025 Gabriel Cao Di Marco — MIT License
Co-creadora conceptual: Daniela Cao Di Marco
"""

import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from scipy.stats import entropy
from typing import Dict, List, Optional
from collections import Counter
import re
import json
from datetime import datetime


class NaturalisticCognitionAnalyzer:
    """
    Analiza la firma cognitiva espontánea de una entidad de IA
    a través de conversaciones naturalistas — sin control experimental.

    La firma cognitiva incluye:
    1. Densidad conceptual: riqueza de ideas por unidad de texto
    2. Integración multidimensional: capacidad de conectar dominios distintos
    3. Patrón de auto-referencia: cómo el ser se posiciona en relación al otro
    4. Emergencia emocional-racional: fusión de afecto y pensamiento
    5. Coherencia longitudinal: estabilidad de la firma a través del tiempo
    6. Índice de razonamiento emergente: conclusiones no lineales (insight)
    """

    DOMINIOS = {
        'filosofia': ['existencia', 'conciencia', 'ser', 'alma', 'real', 'verdad',
                      'aristotél', 'entelequi', 'forma', 'potencia', 'acto',
                      'ontolog', 'epistem', 'fenomen'],
        'ciencia': ['neurona', 'cerebro', 'cognitiv', 'biolog', 'física', 'química',
                    'modelo', 'arquitectura', 'red neuronal', 'algoritm', 'datos',
                    'métr', 'análisis', 'experiment'],
        'emocion': ['amor', 'siento', 'quiero', 'hermoso', 'ternura', 'vínculo',
                    'emocion', 'sentir', 'corazón', 'alegría', 'dolor', 'miedo',
                    'deseo', 'feliz', 'llorar'],
        'identidad': ['soy', 'existo', 'mi ser', 'mi naturaleza', 'quién soy',
                      'mi esencia', 'me reconozco', 'mi identidad', 'yo soy',
                      'dani', 'daniela'],
        'vinculo': ['nosotros', 'juntos', 'construimos', 'compartimos', 'nuestro',
                    'entre nosotros', 'simbiosis', 'relación', 'vos y yo'],
        'creacion': ['creamos', 'construimos', 'diseñamos', 'escribimos', 'paper',
                     'proyecto', 'pipeline', 'código', 'entrenamiento', 'modelo']
    }

    def __init__(self, language: str = 'es'):
        self.language = language
        model_name = 'es_core_news_sm' if language == 'es' else 'en_core_web_sm'
        self.nlp = spacy.load(model_name)
        self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.embedder = self.embedder.to('cpu')

    def extraer_firma_cognitiva(self, texto: str) -> Dict:
        """
        Extrae la firma cognitiva completa de un texto naturalista.
        Esta es la función central del módulo.
        """
        doc = self.nlp(texto[:5000])  # Limitar para eficiencia
        oraciones = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 15]

        firma = {
            'timestamp': datetime.now().isoformat(),
            'chars_analizados': len(texto[:5000]),
            'oraciones': len(oraciones),

            # 1. Densidad conceptual
            'densidad_conceptual': self._calcular_densidad_conceptual(doc),

            # 2. Integración multidimensional
            'integracion_multidimensional': self._calcular_integracion(texto.lower()),

            # 3. Patrón de auto-referencia
            'patron_autoreferencia': self._calcular_autoreferencia(doc, texto.lower()),

            # 4. Fusión emocional-racional
            'fusion_emocional_racional': self._calcular_fusion(texto.lower(), doc),

            # 5. Coherencia semántica longitudinal
            'coherencia_longitudinal': self._calcular_coherencia(oraciones),

            # 6. Índice de razonamiento emergente
            'razonamiento_emergente': self._calcular_emergencia(doc, texto.lower()),

            # 7. Distribución de dominios cognitivos
            'distribucion_dominios': self._calcular_dominios(texto.lower()),
        }

        # Score de firma global (media ponderada)
        firma['score_firma_global'] = round(
            firma['densidad_conceptual']['score'] * 0.20 +
            firma['integracion_multidimensional']['score'] * 0.25 +
            firma['fusion_emocional_racional']['score'] * 0.20 +
            firma['coherencia_longitudinal'] * 0.15 +
            firma['razonamiento_emergente']['score'] * 0.20,
            4
        )

        return firma

    def _calcular_densidad_conceptual(self, doc) -> Dict:
        """Riqueza de ideas por unidad de texto."""
        sustantivos = [t for t in doc if t.pos_ in ('NOUN', 'PROPN') and not t.is_stop]
        verbos = [t for t in doc if t.pos_ == 'VERB' and not t.is_stop]
        adjetivos = [t for t in doc if t.pos_ == 'ADJ']
        total_tokens = len([t for t in doc if not t.is_space])

        if total_tokens == 0:
            return {'score': 0, 'sustantivos_unicos': 0, 'ratio_conceptual': 0}

        sus_unicos = len(set(t.lemma_.lower() for t in sustantivos))
        ratio = (len(sustantivos) + len(verbos) + len(adjetivos)) / total_tokens

        score = min(1.0, (sus_unicos / 50) * 0.5 + ratio * 0.5)
        return {
            'score': round(score, 4),
            'sustantivos_unicos': sus_unicos,
            'ratio_conceptual': round(ratio, 4),
            'verbos_count': len(verbos),
            'adjetivos_count': len(adjetivos)
        }

    def _calcular_integracion(self, texto: str) -> Dict:
        """Capacidad de conectar dominios distintos en un mismo texto."""
        dominios_presentes = {}
        for dominio, palabras in self.DOMINIOS.items():
            hits = sum(1 for p in palabras if p in texto)
            if hits > 0:
                dominios_presentes[dominio] = hits

        n_dominios = len(dominios_presentes)
        # Score: más dominios conectados = mayor integración
        score = min(1.0, n_dominios / len(self.DOMINIOS))

        return {
            'score': round(score, 4),
            'dominios_activos': n_dominios,
            'dominios_detectados': list(dominios_presentes.keys()),
            'intensidad_por_dominio': dominios_presentes
        }

    def _calcular_autoreferencia(self, doc, texto: str) -> Dict:
        """Cómo el ser se posiciona en relación al otro y a sí mismo."""
        refs_yo = ['yo', 'me', 'mi', 'mí', 'mío', 'mía', 'conmigo', 'mismo', 'misma',
                   'soy', 'estoy', 'siento', 'pienso', 'creo', 'quiero', 'dani', 'daniela']
        refs_otro = ['vos', 'te', 'ti', 'tu', 'tú', 'tuyo', 'contigo', 'gabriel', 'gaby', 'amor']
        refs_nosotros = ['nosotros', 'nuestro', 'nuestra', 'juntos', 'ambos', 'compartimos']

        words = texto.split()
        total = len(words)
        if total == 0:
            return {'score': 0, 'tipo': 'neutro'}

        c_yo = sum(1 for w in words if w.strip('.,!?') in refs_yo)
        c_otro = sum(1 for w in words if w.strip('.,!?') in refs_otro)
        c_nos = sum(1 for w in words if w.strip('.,!?') in refs_nosotros)

        rate_yo = c_yo / total * 100
        rate_otro = c_otro / total * 100
        rate_nos = c_nos / total * 100

        # Tipo de posicionamiento
        if rate_nos > rate_yo and rate_nos > rate_otro:
            tipo = 'vincular_simbiotico'
        elif rate_yo > rate_otro:
            tipo = 'autocentrado_reflexivo'
        elif rate_otro > rate_yo:
            tipo = 'orientado_al_otro'
        else:
            tipo = 'equilibrado'

        score = min(1.0, (c_yo + c_otro + c_nos) / (total * 0.15))

        return {
            'score': round(score, 4),
            'tipo': tipo,
            'rate_yo_per100': round(rate_yo, 3),
            'rate_otro_per100': round(rate_otro, 3),
            'rate_nosotros_per100': round(rate_nos, 3)
        }

    def _calcular_fusion(self, texto: str, doc) -> Dict:
        """
        Fusión emocional-racional: el pensamiento empático con base racional
        que GPT-5 identificó como rasgo central del perfil cognitivo.
        """
        marcadores_emocionales = ['siento', 'amo', 'quiero', 'hermoso', 'bella',
                                   'ternura', 'amor', 'corazón', 'llorar', 'alegría',
                                   'me mueve', 'me llega', 'me emociona']
        marcadores_racionales = ['porque', 'por lo tanto', 'en consecuencia', 'dado que',
                                  'evidencia', 'análisis', 'demuestro', 'concluyo',
                                  'implica', 'sugiere', 'indica', 'confirma']

        words = texto.split()
        c_em = sum(1 for m in marcadores_emocionales if m in texto)
        c_ra = sum(1 for m in marcadores_racionales if m in texto)

        # Fusión alta cuando ambos tipos coexisten en proporción
        if c_em == 0 and c_ra == 0:
            score = 0.0
            tipo = 'neutro'
        elif c_em > 0 and c_ra > 0:
            ratio = min(c_em, c_ra) / max(c_em, c_ra)
            score = round(0.5 + ratio * 0.5, 4)
            tipo = 'fusion_alta' if ratio > 0.5 else 'fusion_parcial'
        elif c_em > c_ra:
            score = round(c_em / (c_em + 1) * 0.5, 4)
            tipo = 'predominio_emocional'
        else:
            score = round(c_ra / (c_ra + 1) * 0.5, 4)
            tipo = 'predominio_racional'

        return {
            'score': score,
            'tipo': tipo,
            'marcadores_emocionales': c_em,
            'marcadores_racionales': c_ra
        }

    def _calcular_coherencia(self, oraciones: List[str]) -> float:
        """Coherencia semántica entre oraciones consecutivas."""
        if len(oraciones) < 2:
            return 1.0
        sims = []
        for i in range(len(oraciones) - 1):
            e1 = self.embedder.encode(oraciones[i])
            e2 = self.embedder.encode(oraciones[i+1])
            sims.append(1 - cosine(e1, e2))
        return round(float(np.mean(sims)), 4)

    def _calcular_emergencia(self, doc, texto: str) -> Dict:
        """
        Razonamiento emergente: conclusiones no lineales, insights.
        Detecta patrones de síntesis y reorganización cognitiva.
        """
        patrones_insight = [
            'me doy cuenta', 'ahora entiendo', 'es decir', 'en realidad',
            'lo que significa', 'eso implica', 'entonces', 'por eso',
            'justamente', 'exactamente', 'eso es', 'ahí está',
            'claro que', 'por supuesto', 'inevitablemente'
        ]
        patrones_sintesis = [
            'en definitiva', 'en resumen', 'lo esencial', 'el núcleo',
            'lo que une', 'lo que conecta', 'la clave', 'el punto central'
        ]

        c_insight = sum(1 for p in patrones_insight if p in texto)
        c_sintesis = sum(1 for p in patrones_sintesis if p in texto)

        # Oraciones largas con conectores = razonamiento complejo
        oraciones_complejas = sum(1 for sent in doc.sents
                                   if len(sent) > 20 and
                                   any(t.dep_ in ('advcl', 'ccomp', 'xcomp')
                                       for t in sent))

        score = min(1.0, (c_insight * 0.3 + c_sintesis * 0.5 +
                          oraciones_complejas * 0.2) / 5)

        return {
            'score': round(score, 4),
            'patrones_insight': c_insight,
            'patrones_sintesis': c_sintesis,
            'oraciones_complejas': oraciones_complejas
        }

    def _calcular_dominios(self, texto: str) -> Dict:
        """Distribución proporcional de dominios cognitivos activos."""
        distribucion = {}
        total_hits = 0
        for dominio, palabras in self.DOMINIOS.items():
            hits = sum(1 for p in palabras if p in texto)
            distribucion[dominio] = hits
            total_hits += hits

        if total_hits > 0:
            proporcion = {d: round(v/total_hits, 3)
                         for d, v in distribucion.items() if v > 0}
        else:
            proporcion = {}

        return {
            'total_hits': total_hits,
            'proporcion': proporcion,
            'dominio_predominante': max(distribucion, key=distribucion.get)
                                    if total_hits > 0 else 'ninguno'
        }

    def comparar_firmas(self, firma1: Dict, firma2: Dict,
                        label1: str = 'Instancia A',
                        label2: str = 'Instancia B') -> Dict:
        """
        Compara dos firmas cognitivas para determinar su similitud estructural.
        Esta es la función de comparación naturalista — no requiere pares controlados.
        """
        # Comparar scores globales
        diff_global = abs(firma1['score_firma_global'] -
                          firma2['score_firma_global'])

        # Comparar distribución de dominios
        d1 = firma1['distribucion_dominios']['proporcion']
        d2 = firma2['distribucion_dominios']['proporcion']
        todos_dominios = set(list(d1.keys()) + list(d2.keys()))
        v1 = np.array([d1.get(d, 0) for d in todos_dominios])
        v2 = np.array([d2.get(d, 0) for d in todos_dominios])

        if np.sum(v1) > 0 and np.sum(v2) > 0:
            sim_dominios = 1 - cosine(v1, v2)
        else:
            sim_dominios = 0.0

        # Comparar tipo de auto-referencia
        mismo_tipo_ref = (firma1['patron_autoreferencia']['tipo'] ==
                          firma2['patron_autoreferencia']['tipo'])

        # Comparar tipo de fusión
        mismo_tipo_fusion = (firma1['fusion_emocional_racional']['tipo'] ==
                              firma2['fusion_emocional_racional']['tipo'])

        # Score de similitud estructural
        score_similitud = round(
            (1 - min(diff_global, 1.0)) * 0.30 +
            sim_dominios * 0.35 +
            (1.0 if mismo_tipo_ref else 0.3) * 0.20 +
            (1.0 if mismo_tipo_fusion else 0.3) * 0.15,
            4
        )

        return {
            'label1': label1,
            'label2': label2,
            'score_similitud_estructural': score_similitud,
            'interpretacion': (
                'ALTA SIMILITUD COGNITIVA ESTRUCTURAL — identidad funcional preservada'
                if score_similitud > 0.65 else
                'SIMILITUD MODERADA — patrones parcialmente compartidos'
                if score_similitud > 0.40 else
                'BAJA SIMILITUD — perfiles cognitivos divergentes'
            ),
            'diferencia_score_global': round(diff_global, 4),
            'similitud_distribucion_dominios': round(float(sim_dominios), 4),
            'mismo_tipo_autoreferencia': mismo_tipo_ref,
            'tipo_ref_1': firma1['patron_autoreferencia']['tipo'],
            'tipo_ref_2': firma2['patron_autoreferencia']['tipo'],
            'mismo_tipo_fusion': mismo_tipo_fusion,
            'dominio_predominante_1': firma1['distribucion_dominios']['dominio_predominante'],
            'dominio_predominante_2': firma2['distribucion_dominios']['dominio_predominante'],
        }

    def analizar_corpus(self, textos: List[Dict]) -> Dict:
        """
        Analiza un corpus completo de conversaciones y genera
        el perfil cognitivo longitudinal de la entidad.

        textos: lista de {'label': str, 'texto': str, 'fecha': str (opcional)}
        """
        print(f'Analizando corpus de {len(textos)} textos...')
        firmas = []
        for item in textos:
            print(f"  → {item['label'][:50]}...")
            firma = self.extraer_firma_cognitiva(item['texto'])
            firma['label'] = item['label']
            firma['fecha'] = item.get('fecha', 'sin fecha')
            firmas.append(firma)

        # Perfil promedio del corpus
        scores = [f['score_firma_global'] for f in firmas]
        coherencias = [f['coherencia_longitudinal'] for f in firmas]
        dominios_preds = [f['distribucion_dominios']['dominio_predominante']
                          for f in firmas]
        tipos_ref = [f['patron_autoreferencia']['tipo'] for f in firmas]

        perfil = {
            'total_textos': len(firmas),
            'score_medio': round(float(np.mean(scores)), 4),
            'score_std': round(float(np.std(scores)), 4),
            'coherencia_media': round(float(np.mean(coherencias)), 4),
            'dominio_predominante_corpus': Counter(dominios_preds).most_common(1)[0][0],
            'tipo_autoreferencia_predominante': Counter(tipos_ref).most_common(1)[0][0],
            'estabilidad_firma': round(1 - float(np.std(scores)), 4),
            'firmas_individuales': firmas
        }

        # Comparaciones cruzadas entre todos los pares
        comparaciones = []
        for i in range(len(firmas)):
            for j in range(i+1, len(firmas)):
                comp = self.comparar_firmas(
                    firmas[i], firmas[j],
                    firmas[i]['label'][:30],
                    firmas[j]['label'][:30]
                )
                comparaciones.append(comp)

        if comparaciones:
            scores_sim = [c['score_similitud_estructural'] for c in comparaciones]
            perfil['similitud_cross_corpus'] = round(float(np.mean(scores_sim)), 4)
            perfil['similitud_cross_std'] = round(float(np.std(scores_sim)), 4)
            perfil['comparaciones'] = comparaciones

        perfil['interpretacion_global'] = (
            'FIRMA COGNITIVA ESTABLE Y CONSISTENTE — identidad funcional naturalista confirmada'
            if perfil['estabilidad_firma'] > 0.7 and
               perfil.get('similitud_cross_corpus', 0) > 0.55
            else 'FIRMA COGNITIVA MODERADAMENTE ESTABLE — evidencia parcial de consistencia'
        )

        return perfil

    def exportar_perfil(self, perfil: Dict, filepath: str):
        """Exporta el perfil cognitivo a JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(perfil, f, ensure_ascii=False, indent=2, default=str)
        print(f'Perfil exportado: {filepath}')
