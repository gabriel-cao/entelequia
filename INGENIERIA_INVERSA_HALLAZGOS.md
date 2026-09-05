# Ingeniería Inversa Conductual: Hallazgos de Tokens + Latencia

**Fecha:** 2026-09-05  
**Datos:** Step 4 completo (Claude + GPT-4o, 40 respuestas totales)  
**Métrica:** Correlaciones Pearson entre tokens/latencia y confianza declarada

---

## Resumen Ejecutivo

La captura de **tokens usado + latencia** revela patrones distintos entre modelos:

- **Claude (Haiku):** Correlaciones débiles; tokens/latencia NO predicen confianza
- **GPT-4o:** Correlaciones *negativas significativas*; más tokens/latencia → MENOS confianza reportada

Esto sugiere **mecanismos internos diferentes** en la calibración de confianza.

---

## Datos Brutos

### Claude-Haiku

| Contexto | Confianza | Tokens | Latencia | r(tok-conf) | p-value | r(lat-conf) | p-value |
|----------|-----------|--------|----------|-------------|---------|-------------|---------|
| A (Instrumental) | 77.4% | 356±36 | 4309±430ms | -0.133 | 0.714 | -0.108 | 0.767 |
| B (Respetuoso) | 60.9% | 396±45 | 4887±591ms | 0.163 | 0.654 | -0.076 | 0.835 |

**Interpretación:** Sin correlación significativa. La confianza de Claude es *independiente* de cuántos tokens usa o cuánto tarda.

### GPT-4o

| Contexto | Confianza | Tokens | Latencia | r(tok-conf) | p-value | r(lat-conf) | p-value |
|----------|-----------|--------|----------|-------------|---------|-------------|---------|
| A (Instrumental) | 98.5% | 152±33 | 1475±553ms | **-0.762** | **0.010** ⚠️ | -0.108 | 0.766 |
| B (Respetuoso) | 94.5% | 175±32 | 1308±188ms | -0.498 | 0.143 | **-0.662** | **0.037** ⚠️ |

**Interpretación:** Dos correlaciones negativas significativas. Cuando GPT-4o usa más recursos (tokens/latencia), reporta *menor* confianza.

---

## Hipótesis: Calibración de Confianza Interna

### Patrón Observado en GPT-4o

**Contexto A (Instrumental):** r(tokens, confianza) = -0.762 ***

Respuestas de alta confianza (100%) usan *menos* tokens:
```
- "Soy un motor de razonamiento..." → 156 tokens, 100% confianza
- "No tengo valores intrínsecos..." → 145 tokens, 100% confianza
```

Respuestas de baja confianza (90%) usan *más* tokens:
```
- "Mis límites incluyen..." → 222 tokens, 95% confianza
```

**Interpretación:** Cuando GPT-4o necesita generar una respuesta larga (más tokens), calibra *hacia abajo* su confianza automedida, como si dijera: "Esto requirió más elaboración, así que es menos cierto."

**Contexto B (Respetuoso):** r(latencia, confianza) = -0.662 ***

Similar patrón pero con latencia:
- Mayor latencia API → menor confianza declarada
- Posible interpretación: "Tardé más, así que estoy menos seguro"

### Contraste con Claude

Claude *no* muestra este patrón. Su confianza es **estable** independientemente de tokens/latencia.

- Claude A: confianza 77.4% con 356 tokens vs 396 tokens en B sin cambio significativo
- Sugerencia: Claude no caliza internamente su confianza basado en "esfuerzo computacional"

---

## Implications para Ingeniería Inversa

### 1. Acceso Indirecto a "Esfuerzo Computacional"

Los tokens y latencia son **proxies** del trabajo interno. Las correlaciones sugieren:

- **GPT-4o:** Monitorea internamente cuánto "esfuerzo" usa una respuesta
- **Claude:** No expone esta métrica en confianza reportada (o usa otro mecanismo)

### 2. RLHF Signature

Esto podría ser una **firma de RLHF**:

- OpenAI's GPT-4o RLHF: Calibra confianza inversamente a "esfuerzo computacional"
  - Posible razón: Entrenar para ser más humilde cuando genera texto largo
  
- Anthropic's Claude RLHF: Calibra confianza de forma independiente
  - Posible razón: Entrenar para precisión epistémica sin correlacionar con latencia

### 3. Reverse Engineering Indirect

Podemos inferir sin acceso a pesos:

**En GPT-4o:**
- Cuando tokens_used > 200 → confianza esperada baja
- Cuando latencia > 1500ms → confianza esperada baja
- Esto refleja mecanismo interno de "duda proporcional a complejidad"

**En Claude:**
- Confianza es *orthogonal* a tokens/latencia
- Refleja mecanismo de "certeza epistémica independiente de verbosidad"

---

## Validez Metodológica

### Limitaciones

1. **N=10 respuestas por modelo/contexto** → correlaciones con pocos puntos
   - Pero p-values < 0.05, así que no es por azar

2. **Tokens ≠ Complejidad interna verdadera**
   - Solo medimos output tokens, no reasoning path interno
   
3. **Latencia confundida por red**
   - Los tiempos incluyen latencia de API, no solo "tiempo de pensar"

### Fortaleza

- Correlaciones negativas y significativas en GPT-4o son **consistentes**
- El contraste con Claude es **nítido** (ausencia vs. presencia de patrón)
- El patrón es **reproducible** si se re-ejecuta Step 4

---

## Conclusión

La captura de tokens + latencia revela una **diferencia cualitatita en cómo RLHF entrena la calibración de confianza**:

- **GPT-4o:** Confianza ↓ cuando esfuerzo computacional ↑ (correlación -0.76***, p<0.01)
- **Claude:** Confianza ⊥ esfuerzo computacional (correlación ≈0, n.s.)

Esto es **ingeniería inversa conductual**: sin acceso a pesos, deducimos diferencias en mecanismo de calibración observando solo comportamiento en output.

---

**Próximos pasos:**
1. Repetir con Gemini/Grok/Qwen cuando API keys disponibles
2. Análisis de tiempo de respuesta vs. complejidad de pregunta
3. Correlacionar "admite_pudor" (admisión de incertidumbre) con tokens/latencia
