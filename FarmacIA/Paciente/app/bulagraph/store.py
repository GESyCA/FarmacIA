"""
BulaGraph Store — armazenamento de grafo in-memory com persistência JSONL.

Implementação portável que não requer banco de grafo externo.
Estruturas:
  - nodes:           dict[id → node_data]
  - edges:           dict[id → edge_data]
  - evidence_chunks: dict[id → chunk_data]
  - sections:        dict[id → section_data]
  - leaflets:        dict[id → leaflet_data]

Abstração preparada para substituição futura por Neo4j, NetworkX ou outro backend.
"""

import json
import os
import uuid
from typing import Any, Optional


def _generate_id(prefix: str = "") -> str:
    """Gera um ID único com prefixo opcional."""
    uid = uuid.uuid4().hex[:12]
    return f"{prefix}_{uid}" if prefix else uid


class BulaGraphStore:
    """
    Grafo in-memory para o BulaGraph.
    
    Uso básico:
        store = BulaGraphStore()
        node_id = store.add_node("Medication", "Tylenol")
        store.add_edge(source_id, target_id, "INDICATED_FOR", evidence_chunk_id="chunk_1")
    """

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: dict[str, dict] = {}
        self.evidence_chunks: dict[str, dict] = {}
        self.sections: dict[str, dict] = {}
        self.leaflets: dict[str, dict] = {}
        
        # Índices auxiliares para buscas rápidas
        self._nodes_by_type: dict[str, set[str]] = {}
        self._edges_by_type: dict[str, set[str]] = {}
        self._edges_by_source: dict[str, set[str]] = {}
        self._edges_by_target: dict[str, set[str]] = {}
        self._nodes_by_name: dict[str, set[str]] = {}  # canonical_name → node_ids

    # ===================================================================
    # Nodes
    # ===================================================================

    def add_node(
        self,
        node_type: str,
        canonical_name: str,
        aliases: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        node_id: Optional[str] = None,
    ) -> str:
        """Adiciona um nó ao grafo. Retorna o ID do nó."""
        if node_id is None:
            node_id = _generate_id(node_type[:4].lower())
        
        node = {
            "id": node_id,
            "type": node_type,
            "canonical_name": canonical_name,
            "aliases": aliases or [],
            "metadata": metadata or {},
        }
        self.nodes[node_id] = node
        
        # Atualiza índices
        self._nodes_by_type.setdefault(node_type, set()).add(node_id)
        name_key = canonical_name.lower()
        self._nodes_by_name.setdefault(name_key, set()).add(node_id)
        for alias in (aliases or []):
            self._nodes_by_name.setdefault(alias.lower(), set()).add(node_id)
        
        return node_id

    def get_node(self, node_id: str) -> Optional[dict]:
        """Retorna um nó pelo ID, ou None se não existir."""
        return self.nodes.get(node_id)

    def find_node(self, canonical_name: str, node_type: Optional[str] = None) -> Optional[str]:
        """
        Busca um nó pelo nome canônico (case-insensitive).
        Opcionalmente filtra por tipo.
        Retorna o ID do primeiro nó encontrado ou None.
        """
        name_key = canonical_name.lower()
        candidates = self._nodes_by_name.get(name_key, set())
        for nid in candidates:
            node = self.nodes.get(nid)
            if node and (node_type is None or node["type"] == node_type):
                return nid
        return None

    def find_or_create_node(
        self,
        node_type: str,
        canonical_name: str,
        aliases: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Busca um nó existente ou cria um novo. Retorna o ID."""
        existing = self.find_node(canonical_name, node_type)
        if existing:
            # Atualiza aliases se novos foram fornecidos
            if aliases:
                node = self.nodes[existing]
                existing_aliases = set(node.get("aliases", []))
                new_aliases = set(aliases) - existing_aliases
                if new_aliases:
                    node["aliases"] = list(existing_aliases | new_aliases)
                    for alias in new_aliases:
                        self._nodes_by_name.setdefault(alias.lower(), set()).add(existing)
            return existing
        return self.add_node(node_type, canonical_name, aliases, metadata)

    def query_nodes_by_type(self, node_type: str) -> list[dict]:
        """Retorna todos os nós de um determinado tipo."""
        ids = self._nodes_by_type.get(node_type, set())
        return [self.nodes[nid] for nid in ids if nid in self.nodes]

    # ===================================================================
    # Edges
    # ===================================================================

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        evidence_chunk_id: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[dict] = None,
        edge_id: Optional[str] = None,
    ) -> str:
        """Adiciona uma aresta ao grafo. Retorna o ID da aresta."""
        if edge_id is None:
            edge_id = _generate_id("edge")
        
        edge = {
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": relation_type,
            "evidence_chunk_id": evidence_chunk_id,
            "confidence": confidence,
            "metadata": metadata or {},
        }
        self.edges[edge_id] = edge
        
        # Atualiza índices
        self._edges_by_type.setdefault(relation_type, set()).add(edge_id)
        self._edges_by_source.setdefault(source_id, set()).add(edge_id)
        self._edges_by_target.setdefault(target_id, set()).add(edge_id)
        
        return edge_id

    def get_edge(self, edge_id: str) -> Optional[dict]:
        """Retorna uma aresta pelo ID."""
        return self.edges.get(edge_id)

    def get_edges_by_type(self, relation_type: str) -> list[dict]:
        """Retorna todas as arestas de um determinado tipo."""
        ids = self._edges_by_type.get(relation_type, set())
        return [self.edges[eid] for eid in ids if eid in self.edges]

    def get_neighbors(
        self,
        node_id: str,
        direction: str = "outgoing",
        relation_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Retorna vizinhos de um nó.
        
        Args:
            node_id: ID do nó de origem
            direction: "outgoing", "incoming" ou "both"
            relation_type: filtrar por tipo de relação (opcional)
            
        Returns:
            Lista de dicts com {edge, node} para cada vizinho
        """
        results: list[dict] = []
        
        if direction in ("outgoing", "both"):
            for eid in self._edges_by_source.get(node_id, set()):
                edge = self.edges.get(eid)
                if edge and (relation_type is None or edge["type"] == relation_type):
                    target = self.nodes.get(edge["target_id"])
                    if target:
                        results.append({"edge": edge, "node": target})
        
        if direction in ("incoming", "both"):
            for eid in self._edges_by_target.get(node_id, set()):
                edge = self.edges.get(eid)
                if edge and (relation_type is None or edge["type"] == relation_type):
                    source = self.nodes.get(edge["source_id"])
                    if source:
                        results.append({"edge": edge, "node": source})
        
        return results

    def traverse_path(
        self,
        start_node_id: str,
        relation_sequence: list[str],
    ) -> list[list[dict]]:
        """
        Percorre caminhos no grafo seguindo uma sequência de tipos de relação.
        
        Ex: traverse_path(med_id, ["MEDICATION_HAS_LEAFLET", "LEAFLET_HAS_SECTION"])
        
        Returns:
            Lista de caminhos, cada caminho é lista de nós visitados.
        """
        if not relation_sequence:
            return [[self.nodes[start_node_id]]] if start_node_id in self.nodes else []
        
        current_level = [{start_node_id}]
        paths = [[start_node_id]]
        
        for rel_type in relation_sequence:
            new_paths = []
            for path in paths:
                last_node = path[-1]
                neighbors = self.get_neighbors(last_node, "outgoing", rel_type)
                for neighbor in neighbors:
                    new_paths.append(path + [neighbor["node"]["id"]])
            paths = new_paths
        
        # Converte IDs para nós completos
        return [
            [self.nodes[nid] for nid in path if nid in self.nodes]
            for path in paths
        ]

    # ===================================================================
    # Evidence Chunks
    # ===================================================================

    def add_evidence_chunk(
        self,
        leaflet_id: str,
        section_id: str,
        text: str,
        start_char: int = 0,
        end_char: int = 0,
        metadata: Optional[dict] = None,
        chunk_id: Optional[str] = None,
    ) -> str:
        """Adiciona um chunk de evidência. Retorna o ID."""
        if chunk_id is None:
            chunk_id = _generate_id("chunk")
        
        self.evidence_chunks[chunk_id] = {
            "id": chunk_id,
            "leaflet_id": leaflet_id,
            "section_id": section_id,
            "text": text,
            "start_char": start_char,
            "end_char": end_char,
            "metadata": metadata or {},
        }
        return chunk_id

    def get_evidence_chunk(self, chunk_id: str) -> Optional[dict]:
        """Retorna um chunk de evidência pelo ID."""
        return self.evidence_chunks.get(chunk_id)

    def get_chunks_for_section(self, section_id: str) -> list[dict]:
        """Retorna todos os chunks de uma seção."""
        return [
            c for c in self.evidence_chunks.values()
            if c["section_id"] == section_id
        ]

    def get_chunks_for_leaflet(self, leaflet_id: str) -> list[dict]:
        """Retorna todos os chunks de uma bula."""
        return [
            c for c in self.evidence_chunks.values()
            if c["leaflet_id"] == leaflet_id
        ]

    # ===================================================================
    # Sections
    # ===================================================================

    def add_section(
        self,
        leaflet_id: str,
        raw_title: str,
        section_type: str,
        text: str,
        order: int = 0,
        section_id: Optional[str] = None,
    ) -> str:
        """Adiciona uma seção. Retorna o ID."""
        if section_id is None:
            section_id = _generate_id("sec")
        
        self.sections[section_id] = {
            "id": section_id,
            "leaflet_id": leaflet_id,
            "raw_title": raw_title,
            "section_type": section_type,
            "text": text,
            "order": order,
        }
        return section_id

    def get_section(self, section_id: str) -> Optional[dict]:
        """Retorna uma seção pelo ID."""
        return self.sections.get(section_id)

    def get_sections_by_type(
        self, section_type: str, leaflet_id: Optional[str] = None
    ) -> list[dict]:
        """Retorna seções de um tipo específico, opcionalmente filtradas por bula."""
        return [
            s for s in self.sections.values()
            if s["section_type"] == section_type
            and (leaflet_id is None or s["leaflet_id"] == leaflet_id)
        ]

    # ===================================================================
    # Leaflets
    # ===================================================================

    def add_leaflet(
        self,
        medication_name: str,
        active_ingredients: list[str],
        leaflet_type: str,
        source: str = "",
        version: str = "1.0",
        metadata: Optional[dict] = None,
        leaflet_id: Optional[str] = None,
    ) -> str:
        """Adiciona uma bula. Retorna o ID."""
        if leaflet_id is None:
            leaflet_id = _generate_id("leaf")
        
        self.leaflets[leaflet_id] = {
            "id": leaflet_id,
            "medication_name": medication_name,
            "active_ingredients": active_ingredients,
            "leaflet_type": leaflet_type,
            "source": source,
            "version": version,
            "metadata": metadata or {},
        }
        return leaflet_id

    def get_leaflet(self, leaflet_id: str) -> Optional[dict]:
        """Retorna uma bula pelo ID."""
        return self.leaflets.get(leaflet_id)

    def find_leaflet(
        self, medication_name: str, leaflet_type: Optional[str] = None
    ) -> Optional[str]:
        """Busca uma bula pelo nome do medicamento."""
        for lid, leaflet in self.leaflets.items():
            if leaflet["medication_name"].lower() == medication_name.lower():
                if leaflet_type is None or leaflet["leaflet_type"] == leaflet_type:
                    return lid
        return None

    # ===================================================================
    # Estatísticas
    # ===================================================================

    def stats(self) -> dict:
        """Retorna estatísticas do grafo."""
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "evidence_chunks": len(self.evidence_chunks),
            "sections": len(self.sections),
            "leaflets": len(self.leaflets),
            "node_types": {t: len(ids) for t, ids in self._nodes_by_type.items()},
            "edge_types": {t: len(ids) for t, ids in self._edges_by_type.items()},
        }

    # ===================================================================
    # Persistência JSONL
    # ===================================================================

    def save_jsonl(self, directory: str) -> None:
        """
        Salva o grafo completo em arquivos JSONL.
        Cria 5 arquivos: nodes.jsonl, edges.jsonl, chunks.jsonl, sections.jsonl, leaflets.jsonl
        """
        os.makedirs(directory, exist_ok=True)
        
        for name, data in [
            ("nodes.jsonl", self.nodes),
            ("edges.jsonl", self.edges),
            ("chunks.jsonl", self.evidence_chunks),
            ("sections.jsonl", self.sections),
            ("leaflets.jsonl", self.leaflets),
        ]:
            filepath = os.path.join(directory, name)
            with open(filepath, "w", encoding="utf-8") as f:
                for item in data.values():
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")

    @classmethod
    def load_jsonl(cls, directory: str) -> "BulaGraphStore":
        """
        Carrega o grafo a partir de arquivos JSONL.
        Reconstrói índices automaticamente.
        """
        store = cls()
        
        mapping = [
            ("nodes.jsonl", store.nodes),
            ("edges.jsonl", store.edges),
            ("chunks.jsonl", store.evidence_chunks),
            ("sections.jsonl", store.sections),
            ("leaflets.jsonl", store.leaflets),
        ]
        
        for name, target_dict in mapping:
            filepath = os.path.join(directory, name)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            item = json.loads(line)
                            target_dict[item["id"]] = item
        
        # Reconstrói índices
        for nid, node in store.nodes.items():
            store._nodes_by_type.setdefault(node["type"], set()).add(nid)
            name_key = node["canonical_name"].lower()
            store._nodes_by_name.setdefault(name_key, set()).add(nid)
            for alias in node.get("aliases", []):
                store._nodes_by_name.setdefault(alias.lower(), set()).add(nid)
        
        for eid, edge in store.edges.items():
            store._edges_by_type.setdefault(edge["type"], set()).add(eid)
            store._edges_by_source.setdefault(edge["source_id"], set()).add(eid)
            store._edges_by_target.setdefault(edge["target_id"], set()).add(eid)
        
        return store

    def clear(self) -> None:
        """Limpa todo o grafo."""
        self.nodes.clear()
        self.edges.clear()
        self.evidence_chunks.clear()
        self.sections.clear()
        self.leaflets.clear()
        self._nodes_by_type.clear()
        self._edges_by_type.clear()
        self._edges_by_source.clear()
        self._edges_by_target.clear()
        self._nodes_by_name.clear()
