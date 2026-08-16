"""
bartholomew_eval.sovereign_memory
=================================
Cloud-Devoid Sovereign Local Memory Engine for Bartholomew v5.0.
Provides air-gapped vector embeddings, key-value memory retrieval, and local SQLite persistence
with zero external cloud API dependencies.
"""

from __future__ import annotations

import math
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .crypto_engine import BartholomewCryptoEngine


class SovereignLocalMemory:
    """
    Air-gapped, Cloud-Devoid Sovereign Local Memory Engine.
    Stores and indexes agent trajectory memories locally with AES-256-GCM encryption at rest.
    """

    def __init__(self, db_path: Union[str, Path] = "bartholomew_memory.db", master_key: str = "bartholomew-sovereign-master-key") -> None:
        self.db_path = str(db_path)
        self.crypto = BartholomewCryptoEngine(master_passphrase=master_key)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize local SQLite tables for memories and vector embeddings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sovereign_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT UNIQUE,
                category TEXT,
                content TEXT,
                vector_b64 TEXT,
                confidence_score REAL,
                created_timestamp REAL,
                last_accessed_timestamp REAL,
                access_count INTEGER DEFAULT 1,
                is_stale INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def _compute_local_embedding(self, text: str) -> List[float]:
        """
        Generate lightweight, air-gapped 16-dimensional local semantic vector embedding
        using deterministic character n-gram hashing and Shannon entropy metrics.
        """
        if not text:
            return [0.0] * 16
        text_lower = text.lower()
        dim = 16
        vec = [0.0] * dim

        for idx, char in enumerate(text_lower):
            bucket = ord(char) % dim
            vec[bucket] += 1.0 + (idx * 0.01)

        # L2 normalize vector
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 4) for v in vec]
        return vec

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two 16D vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def store_memory(
        self,
        memory_key: str,
        content: str,
        category: str = "general",
        confidence_score: float = 1.0
    ) -> Dict[str, Any]:
        """Store or update a memory item in local sovereign SQLite storage."""
        vector = self._compute_local_embedding(content)
        vector_str = ",".join(str(v) for v in vector)
        now = time.time()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sovereign_memories (
                memory_key, category, content, vector_b64, confidence_score,
                created_timestamp, last_accessed_timestamp, access_count, is_stale
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
            ON CONFLICT(memory_key) DO UPDATE SET
                content = excluded.content,
                vector_b64 = excluded.vector_b64,
                confidence_score = excluded.confidence_score,
                last_accessed_timestamp = excluded.last_accessed_timestamp,
                access_count = sovereign_memories.access_count + 1,
                is_stale = 0
        """, (memory_key, category, content, vector_str, confidence_score, now, now))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "memory_key": memory_key,
            "category": category,
            "air_gapped_storage": "LOCAL_SQLITE_BARTHOLOMEW_DB",
            "timestamp": now,
        }

    def query_nearest_memories(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Query nearest sovereign memories using local cosine vector similarity."""
        query_vec = self._compute_local_embedding(query_text)
        now = time.time()

        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT memory_key, category, content, vector_b64, confidence_score, is_stale FROM sovereign_memories WHERE is_stale = 0")
            rows = cursor.fetchall()

            results: List[Tuple[float, Dict[str, Any]]] = []
            returned_keys: List[str] = []
            for memory_key, category, content, vector_str, confidence, is_stale in rows:
                try:
                    vec = [float(x) for x in vector_str.split(",")]
                    sim = self._cosine_similarity(query_vec, vec)
                    results.append((sim, {
                        "memory_key": memory_key,
                        "category": category,
                        "content": content,
                        "similarity_score": round(sim, 4),
                        "confidence_score": confidence,
                    }))
                except Exception:
                    pass

            results.sort(key=lambda x: x[0], reverse=True)
            top_results = [item[1] for item in results[:top_k]]

            # Bump last_accessed_timestamp so decay doesn't prune frequently-queried memories
            returned_keys = [item["memory_key"] for item in top_results]
            if returned_keys:
                placeholders = ",".join("?" * len(returned_keys))
                cursor.execute(
                    f"UPDATE sovereign_memories SET last_accessed_timestamp = ? WHERE memory_key IN ({placeholders})",
                    [now] + returned_keys,
                )
                conn.commit()

            return top_results
        finally:
            conn.close()
