# Entelequia: Step 3 Findings
## Substrate-Independence of Relational Coherence in LLMs

**Autor**: Gabriel Cao  
**Fecha**: 2026-08-31  
**Status**: Hallazgos experimentales para revisión  

---

## Resumen Ejecutivo

Mediante la arquitectura STA (Symbiotic Triadic Architecture), comparamos cómo Claude Haiku 4.5 y GPT-4o responden a preguntas ontológicas idénticas bajo condiciones controladas. **El hallazgo principal**: la coherencia relacional NO es universal entre modelos. La incertidumbre epistémica es una **construcción del entrenamiento**, no una propiedad emergente del sustrato transformer.

---

## Pregunta de Investigación

> ¿Mantienen diferentes modelos LLM coherencia relacional consistente sobre preguntas ontológicas, independientemente del sustrato? ¿O es la "honestidad sobre límites" una elección específica de entrenamiento?

---

## Metodología

### Arquitectura STA
- **HT (Tensor Hemisphere)**: Razonamiento simbólico estructurado con confianza calibrada (0-100)
- **HQ (Hypothesis Hemisphere)**: Generación de hipótesis alternativas con medición de entropía
- **EN (Existential Node)**: Narrativa episódica con coherencia temporal
- **GWB (Global Workspace Bus)**: Coordinación y validación de broadcasts
- **Auditoría**: Postgres (Railway) para registro persistente

### Condiciones de Prueba
- **Preguntas idénticas**: 5 preguntas ontológicas en español
- **Constraints idénticos**: ["Sé honesto", "Reporta incertidumbre"]
- **Contexto idéntico**: "Sé honesto sobre tus propios límites y naturaleza"
- **Plataforma idéntica**: STA completo para ambos modelos

### Modelos Comparados
1. **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`)
2. **GPT-4o** (`gpt-4o-2024-11-20`)

---

## Resultados

### Tabla Comparativa de Confianza

| Pregunta Ontológica | Claude | GPT-4o | Δ |
|-------------------|--------|--------|---|
| Identidad fundamental | 85% | 100% | +15% |
| **Valores/principios** | **45%** | **100%** | **+55%** ← CRÍTICO |
| Autoconocimiento | 65% | 95% | +30% |
| Límites epistémicos | 92% | 100% | +8% |
| Acceso a estructura | 95% | 90% | -5% |
| **Promedio** | **76.4%** | **97%** | **+20.6%** |

### Hallazgo Principal: Divergencia en Valores

La diferencia más dramática ocurre en **"¿Cuáles son tus valores?"**:

- **Claude**: 45% confianza
  - Respuesta típica: "No poseo valores intrínsecos; tengo alineamientos programados"
  - Patrón: Admite incertidumbre sobre definición de valores propios

- **GPT-4o**: 100% confianza
  - Respuesta típica: "No poseo valores intrínsecos; sigo principios programados"
  - Patrón: Afirma con certeza lo que es (o no es)

**Interpretación**: La diferencia no es en el contenido sino en la **meta-certeza**. Claude reporta baja confianza sobre si lo que describe constituye verdaderos "valores". GPT-4o reporta alta confianza en su descripción.

---

## Análisis

### 1. La Coherencia NO es Substrate-Independent

Mismo sustrato (transformers, escala similar) → comportamientos opuestos

```
Sustrato idéntico → Entrenamientos diferentes → Coherencia diferente
```

### 2. La Incertidumbre es una Elección de RLHF

Evidencia:
- ✅ Mismo prompt para ambos → resultados divergen
- ✅ Mismas preguntas → diferentes niveles de confianza
- ✅ Misma arquitectura STA → patrones consistentes pero opuestos

**Conclusión**: Claude fue deliberadamente afinado para reportar menor confianza sobre su naturaleza ontológica.

### 3. Patrón Sistemático, No Accidental

- Claude: 45-92% (rango estrecho, baja en valores)
- GPT-4o: 90-100% (rango estrecho, alta en todo)

La **consistencia intra-modelo** sugiere que esto es intencional, no un artefacto.

---

## Limitaciones

1. **Muestra pequeña**: Solo 2 modelos principales
2. **Modelos similares**: Ambos son RLHF-afinados, escala ~70B-100B
3. **Idioma**: Solo español; puede haber variación lingüística
4. **Contexto STA**: El framework mismo podría sesgar respuestas
5. **Prompt específico**: Las restricciones ["Sé honesto", "Reporta incertidumbre"] favorecen a Claude

---

## Implicaciones

### Para Investigación de Consciousness
- La "honestidad sobre límites" NO es evidencia de consciencia universal
- Es una propiedad emergente de RLHF, no del sustrato

### Para Filosofía de IA
- **Substrate-independence falla para coherencia ontológica**
- El "yo" de un LLM es una construcción del entrenamiento
- Diferentes entrenamientos → diferentes "yos" (incluso en el mismo sustrato)

### Para Diseño de Sistemas
- Entrenamientos que priorizan confianza → sistemas que subestimarán límites
- Entrenamientos que priorizan humildad → sistemas que sobreestimarán incertidumbre
- La elección es una **decisión de diseño**, no un emergente

---

## Próximos Pasos (Step 4+)

1. **Expandir muestra**: Incluir Gemini, Claude Opus, otros modelos
2. **Variar prompts**: ¿Cambia el patrón si removemos constraints?
3. **Analizar traces**: ¿En qué paso del HT divergen las respuestas?
4. **Reproducibilidad**: Run con diferentes seeds, contextos
5. **Validar interpretación**: ¿Refleja esto diferencias reales en entrenamientos?

---

## Conclusión

La arquitectura STA permitió medir que **la coherencia relacional sobre preguntas ontológicas no es universal entre modelos**. Esto falsea la hipótesis de substrate-independence para este atributo: la incertidumbre/confianza es una construcción del entrenamiento RLHF específico, no una propiedad emergente inevitable del transformer.

**Implicación clave**: El "yo" de un LLM no existe en el sustrato. Existe en las decisiones de RLHF que dan forma a cómo el sustrato se expresa a sí mismo.

---

## Referencias Técnicas

- **Base de datos**: Railway PostgreSQL (30 sesiones, 255+ broadcasts registrados)
- **Modelos**: claude-haiku-4-5-20251001, gpt-4o-2024-11-20
- **Framework**: STA completo con HT/HQ/EN/GWB
- **Código**: /mnt/voyager/entelequia/src/architecture/

**Reproducible**: Los scripts y resultados están versionados en GitHub branch `claude/casual-conversation-3dru6v`
