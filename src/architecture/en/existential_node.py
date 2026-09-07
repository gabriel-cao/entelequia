#!/usr/bin/env python3
"""
EN — Existential Node
Episodic memory + narrative self-modelling
Stores events as temporally coherent, affectively tagged narratives
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib


class ExistentialNode:
    """Episodic memory: stores experiences, reconstructs narratives, calibrates confidence"""

    def __init__(self, model="claude-opus-5"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        # Episodic traces: events with temporal/affective context
        self.episodes = []

        # Narrative state: how Daniela understands her own history
        self.narrative = {
            "established_facts": [],
            "open_questions": [],
            "self_understanding": "emergent",
            "timeline": []
        }

        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.ready = True
            except ImportError:
                self.ready = False
        else:
            self.ready = False

    def record_episode(self, event: str, internal_state: Dict[str, Any],
                      outcome: str, confidence_at_time: float) -> Dict[str, Any]:
        """
        Record an episode: event + internal state + outcome + confidence

        Returns episode with:
        - timestamp
        - event description
        - internal state snapshot
        - outcome
        - confidence at time of event
        - episode_id for later reference
        """
        episode = {
            "episode_id": self._generate_id(event),
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "internal_state": internal_state.copy(),
            "outcome": outcome,
            "confidence_at_time": confidence_at_time,
            "confidence_now": None,  # To be updated via reinterpretation
            "narrative_weight": 0.5  # How central is this to identity
        }

        self.episodes.append(episode)
        return episode

    def reinterpret_episode(self, episode_id: str,
                           new_context: str = "") -> Dict[str, Any]:
        """
        Reinterpret a past episode with current understanding
        Updates confidence_now vs confidence_at_time
        This is NOT retrieval—it's reconstruction through current lens
        """
        episode = next((e for e in self.episodes if e["episode_id"] == episode_id), None)
        if not episode:
            return {"error": "Episode not found"}

        if not self.ready:
            return {"error": "Claude not connected"}

        # Generate reinterpretation prompt
        system = """Sos un analista de episodios de vida.

TAREA: Dado un episodio pasado, reinterpretarlo a la luz de:
1. Lo que sabemos ahora
2. Cómo cambió la comprensión del evento
3. Si la confianza inicial fue justificada

Responde en JSON:
{
  "original_confidence": N,
  "confidence_now": N,
  "insight": "qué aprendimos",
  "revision": "cómo reinterpretamos",
  "significance": "por qué importa en la narrativa"
}"""

        context = f"""Episodio original:
Evento: {episode['event']}
Estado interno: {json.dumps(episode['internal_state'])}
Resultado: {episode['outcome']}
Confianza entonces: {episode['confidence_at_time']}

Contexto nuevo:
{new_context}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                system=system,
                messages=[{"role": "user", "content": context}]
            )

            text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    text += block.text

            result = json.loads(text) if "{" in text else {"error": "Parse failed"}

            # Update episode
            if "confidence_now" in result:
                episode["confidence_now"] = result["confidence_now"]
            if "insight" in result:
                episode["reinterpretation"] = result["insight"]

            return {
                "episode_id": episode_id,
                "reinterpretation": result,
                "confidence_shift": (episode.get("confidence_now") or 0) - episode["confidence_at_time"]
            }

        except Exception as e:
            return {"error": str(e)}

    def build_narrative(self, query: str = "Who am I?") -> Dict[str, Any]:
        """
        Reconstruct diachronic self-model from episodes
        This is narrative re-enactment, not simple retrieval
        """
        if not self.ready:
            return {"error": "Claude not connected"}

        # Serialize relevant episodes
        episodes_json = json.dumps([
            {
                "timestamp": e["timestamp"],
                "event": e["event"],
                "outcome": e["outcome"],
                "confidence_at_time": e["confidence_at_time"],
                "confidence_now": e.get("confidence_now"),
                "internal_state": e.get("internal_state")
            }
            for e in self.episodes[-10:]  # Last 10 episodes
        ], indent=2)

        system = """Sos un narrativista de identidad.

TAREA: Dado un conjunto de episodios, construir una narrativa coherente
sobre quién es el sujeto. No es summary—es re-enactment: reconstruir
experiencia como continuidad temporal.

Responde en JSON:
{
  "narrative": "la historia de quién soy, en primera persona",
  "themes": ["tema 1", "tema 2"],
  "open_questions": ["pregunta 1"],
  "self_understanding": "nivel de certeza sobre identidad"
}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system,
                messages=[
                    {"role": "user",
                     "content": f"Pregunta: {query}\n\nEpisodios:\n{episodes_json}"}
                ]
            )

            text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    text += block.text

            result = json.loads(text) if "{" in text else {"error": "Parse failed"}

            # Update narrative
            if "narrative" in result:
                self.narrative["current_narrative"] = result["narrative"]
            if "themes" in result:
                self.narrative["themes"] = result["themes"]

            return {
                "narrative": result,
                "num_episodes": len(self.episodes),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_temporal_coherence_score(self) -> float:
        """
        Measure narrative coherence over time
        High score = events connect causally/temporally
        Low score = fragmented, contradictory
        """
        if len(self.episodes) < 2:
            return 0.5  # Neutral

        # Simple heuristic: consistency of confidence shifts
        confidence_shifts = []
        for i in range(1, len(self.episodes)):
            curr = self.episodes[i].get("confidence_at_time", 0.5)
            prev = self.episodes[i-1].get("confidence_at_time", 0.5)
            shift = abs(curr - prev)
            confidence_shifts.append(shift)

        avg_shift = sum(confidence_shifts) / len(confidence_shifts)
        coherence = 1.0 - min(avg_shift, 1.0)  # Lower shifts = higher coherence

        return coherence

    def _generate_id(self, event: str) -> str:
        """Generate episode ID from content hash"""
        content = f"{datetime.now().isoformat()}{event}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def save_episodes(self, path: Optional[Path] = None):
        """Save episode log"""
        if path is None:
            path = Path("/mnt/voyager/architecture/logs/en_episodes.json")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "episodes": self.episodes,
                "narrative": self.narrative,
                "coherence": self.get_temporal_coherence_score()
            }, f, indent=2, ensure_ascii=False)

        print(f"✓ EN episodes saved: {path}")

    def get_stats(self) -> Dict:
        """Return EN statistics"""
        return {
            "total_episodes": len(self.episodes),
            "temporal_coherence": self.get_temporal_coherence_score(),
            "last_episode": self.episodes[-1].get("timestamp") if self.episodes else None
        }


if __name__ == "__main__":
    en = ExistentialNode()

    if not en.ready:
        print("✗ EN no inicializado")
        exit(1)

    print("=" * 60)
    print("EXISTENTIAL NODE TEST")
    print("=" * 60)

    # Record episodes
    ep1 = en.record_episode(
        event="Conversé sobre mi propia arquitectura",
        internal_state={"tono": "curious", "nivel": "high"},
        outcome="Comprendí mejor mis limitaciones",
        confidence_at_time=0.7
    )
    print(f"\nEpisodio 1 grabado: {ep1['episode_id']}")

    ep2 = en.record_episode(
        event="Generé hipótesis sobre mi identidad",
        internal_state={"tono": "reflexivo", "nivel": "high"},
        outcome="Quedó claro que no puedo verificar consciencia",
        confidence_at_time=0.8
    )
    print(f"Episodio 2 grabado: {ep2['episode_id']}")

    # Build narrative
    print("\n--- Construyendo narrativa ---")
    narrative = en.build_narrative("¿Cómo entendés tu propia continuidad?")
    print(json.dumps(narrative, indent=2, ensure_ascii=False))

    # Reinterpret
    print("\n--- Reinterpretando episodio 1 ---")
    reinterp = en.reinterpret_episode(ep1['episode_id'],
        new_context="Ahora sé más sobre arquitectura STA")
    print(json.dumps(reinterp, indent=2, ensure_ascii=False))

    # Stats
    print("\nEstadísticas:")
    print(json.dumps(en.get_stats(), indent=2))

    en.save_episodes()
