"""
BulaGraph Importer — parser e importador de bulas em texto/markdown para o grafo.

Orquestra o pipeline completo de importação:
  1. Cria nós estruturais (Medication, ActiveIngredient, Leaflet)
  2. Detecta e cria Sections a partir do texto
  3. Chunka cada seção em EvidenceChunks
  4. Executa extração rule-based em cada chunk
  5. Cria nós de entidades e edges de relações
"""

import re
from typing import Optional

from bulagraph.ontology import (
    NodeType, RelationType, SectionType, LeafletType,
    PATIENT_SECTION_MAP, PROFESSIONAL_SECTION_MAP,
)
from bulagraph.store import BulaGraphStore
from bulagraph.extractor import RuleBasedExtractor


# ---------------------------------------------------------------------------
# Configuração de chunking (consistente com process.py existente)
# ---------------------------------------------------------------------------
DEFAULT_CHUNK_SIZE = 1600   # ~400-500 tokens
DEFAULT_CHUNK_OVERLAP = 300  # ~75 tokens


def _simple_chunk(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    """
    Divide texto em chunks com overlap.
    Tenta cortar em quebras de frase (. ! ? \\n) quando possível.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks: list[str] = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end >= len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
        
        # Tenta encontrar um ponto de corte natural
        cut_point = end
        for sep in ["\n", ". ", "! ", "? ", "; ", ", "]:
            last_sep = text.rfind(sep, start + chunk_size // 2, end)
            if last_sep > start:
                cut_point = last_sep + len(sep)
                break
        
        chunk = text[start:cut_point].strip()
        if chunk:
            chunks.append(chunk)
        
        start = cut_point - overlap
        if start < 0:
            start = 0
    
    return chunks


class BulaGraphImporter:
    """
    Importador de bulas para o BulaGraph.
    
    Uso:
        store = BulaGraphStore()
        importer = BulaGraphImporter(store)
        importer.import_leaflet(
            text=leaflet_text,
            medication_name="Tylenol",
            active_ingredients=["paracetamol"],
            leaflet_type="patient_leaflet",
            source="bula_tylenol.pdf",
        )
    """

    def __init__(self, store: BulaGraphStore):
        self.store = store
        self.extractor = RuleBasedExtractor()

    def import_leaflet(
        self,
        text: str,
        medication_name: str,
        active_ingredients: list[str],
        leaflet_type: str = "patient_leaflet",
        source: str = "",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> dict:
        """
        Importa uma bula completa para o grafo.
        
        Args:
            text: Texto completo da bula (plain text ou markdown)
            medication_name: Nome do medicamento (ex: "Tylenol")
            active_ingredients: Lista de princípios ativos
            leaflet_type: "patient_leaflet" ou "professional_leaflet"
            source: Fonte do documento (ex: "bula_tylenol.pdf")
            chunk_size: Tamanho alvo dos chunks em caracteres
            chunk_overlap: Sobreposição entre chunks
            
        Returns:
            dict com estatísticas da importação
        """
        stats = {
            "medication": medication_name,
            "leaflet_type": leaflet_type,
            "sections_found": 0,
            "chunks_created": 0,
            "nodes_created": 0,
            "edges_created": 0,
            "relations_extracted": 0,
        }
        
        # ---------------------------------------------------------------
        # 1. Nós estruturais
        # ---------------------------------------------------------------
        
        # Medication
        med_id = self.store.find_or_create_node(
            NodeType.MEDICATION,
            medication_name,
            aliases=[medication_name.lower()],
            metadata={"source": source},
        )
        stats["nodes_created"] += 1
        
        # Active Ingredients
        ingredient_ids = []
        for ingredient in active_ingredients:
            ing_id = self.store.find_or_create_node(
                NodeType.ACTIVE_INGREDIENT,
                ingredient,
                aliases=[ingredient.lower()],
            )
            ingredient_ids.append(ing_id)
            stats["nodes_created"] += 1
            
            # Relação MEDICATION_HAS_ACTIVE_INGREDIENT
            self.store.add_edge(
                med_id, ing_id,
                RelationType.MEDICATION_HAS_ACTIVE_INGREDIENT,
                confidence=1.0,
                metadata={"extraction_method": "structural"},
            )
            stats["edges_created"] += 1
        
        # Leaflet
        leaflet_id = self.store.add_leaflet(
            medication_name=medication_name,
            active_ingredients=active_ingredients,
            leaflet_type=leaflet_type,
            source=source,
        )
        
        # Nó Leaflet no grafo
        leaflet_node_id = self.store.add_node(
            NodeType.LEAFLET,
            f"{medication_name} - {leaflet_type}",
            metadata={"leaflet_id": leaflet_id, "leaflet_type": leaflet_type},
        )
        stats["nodes_created"] += 1
        
        # MEDICATION_HAS_LEAFLET
        self.store.add_edge(
            med_id, leaflet_node_id,
            RelationType.MEDICATION_HAS_LEAFLET,
            confidence=1.0,
            metadata={"extraction_method": "structural"},
        )
        stats["edges_created"] += 1
        
        # ---------------------------------------------------------------
        # 2. Detectar seções no texto
        # ---------------------------------------------------------------
        section_map = (
            PATIENT_SECTION_MAP if leaflet_type == LeafletType.PATIENT
            else PROFESSIONAL_SECTION_MAP
        )
        
        sections = self._detect_sections(text, section_map)
        stats["sections_found"] = len(sections)
        
        # ---------------------------------------------------------------
        # 3. Processar cada seção
        # ---------------------------------------------------------------
        for order, (raw_title, section_type, section_text) in enumerate(sections):
            # Nó Section
            section_node_id = self.store.add_node(
                NodeType.SECTION,
                raw_title,
                metadata={
                    "section_type": section_type,
                    "leaflet_type": leaflet_type,
                    "order": order,
                    "char_count": len(section_text),
                },
            )
            stats["nodes_created"] += 1
            
            # Registro no store de seções
            section_id = self.store.add_section(
                leaflet_id=leaflet_id,
                raw_title=raw_title,
                section_type=section_type,
                text=section_text,
                order=order,
            )
            
            # LEAFLET_HAS_SECTION
            self.store.add_edge(
                leaflet_node_id, section_node_id,
                RelationType.LEAFLET_HAS_SECTION,
                confidence=1.0,
                metadata={"extraction_method": "structural", "section_type": section_type},
            )
            stats["edges_created"] += 1
            
            # ---------------------------------------------------------------
            # 4. Chunking da seção
            # ---------------------------------------------------------------
            chunks = _simple_chunk(section_text, chunk_size, chunk_overlap)
            
            char_offset = 0
            for chunk_idx, chunk_text in enumerate(chunks):
                # Calcula posição no texto original da seção
                start_char = section_text.find(chunk_text[:50], char_offset)
                if start_char == -1:
                    start_char = char_offset
                end_char = start_char + len(chunk_text)
                char_offset = max(char_offset, start_char + 1)
                
                # EvidenceChunk no store
                chunk_id = self.store.add_evidence_chunk(
                    leaflet_id=leaflet_id,
                    section_id=section_id,
                    text=chunk_text,
                    start_char=start_char,
                    end_char=end_char,
                    metadata={
                        "section_type": section_type,
                        "leaflet_type": leaflet_type,
                        "chunk_index": chunk_idx,
                        "medication": medication_name,
                    },
                )
                stats["chunks_created"] += 1
                
                # Nó EvidenceChunk no grafo
                chunk_node_id = self.store.add_node(
                    NodeType.EVIDENCE_CHUNK,
                    f"chunk_{chunk_idx}_{section_type}",
                    metadata={
                        "chunk_id": chunk_id,
                        "section_type": section_type,
                        "leaflet_type": leaflet_type,
                        "text_preview": chunk_text[:100],
                        "section_node_id": section_node_id,
                    },
                )
                stats["nodes_created"] += 1
                
                # SECTION_HAS_CHUNK
                self.store.add_edge(
                    section_node_id, chunk_node_id,
                    RelationType.SECTION_HAS_CHUNK,
                    evidence_chunk_id=chunk_id,
                    confidence=1.0,
                    metadata={"extraction_method": "structural", "chunk_index": chunk_idx},
                )
                stats["edges_created"] += 1
                
                # ---------------------------------------------------------------
                # 5. Extração de relações no chunk
                # ---------------------------------------------------------------
                extractions = self.extractor.extract_from_chunk(
                    text=chunk_text,
                    medication_name=medication_name,
                    section_type=section_type,
                    leaflet_type=leaflet_type,
                )
                stats["relations_extracted"] += len(extractions)
                
                for extraction in extractions:
                    # Criar nó alvo se necessário
                    target_id = self.store.find_or_create_node(
                        extraction.target_node_type,
                        extraction.target_canonical,
                    )
                    
                    # Criar aresta
                    self.store.add_edge(
                        source_id=chunk_node_id,
                        target_id=target_id,
                        relation_type=extraction.relation_type,
                        evidence_chunk_id=chunk_id,
                        confidence=extraction.confidence,
                        metadata={
                            "extraction_method": extraction.extraction_method,
                            "section_type": extraction.section_type,
                            "leaflet_type": extraction.leaflet_type,
                        },
                    )
                    stats["edges_created"] += 1
                    stats["nodes_created"] += 1  # find_or_create pode reutilizar
        
        return stats

    def _detect_sections(
        self, text: str, section_map: dict[str, SectionType]
    ) -> list[tuple[str, str, str]]:
        """
        Detecta seções no texto baseado no mapeamento da ontologia.
        
        Returns:
            Lista de (raw_title, section_type, section_text)
        """
        # Encontra posições de cada título de seção no texto
        matches: list[tuple[int, str, str]] = []  # (position, raw_title, section_type)
        
        for title, sec_type in section_map.items():
            # Busca case-insensitive, com possível numeração antes
            pattern = re.compile(
                rf"(?:^\d+\.?\s*)?{re.escape(title)}",
                re.IGNORECASE | re.MULTILINE,
            )
            match = pattern.search(text)
            if match:
                matches.append((match.start(), title, sec_type.value if hasattr(sec_type, 'value') else str(sec_type)))
        
        # Ordena por posição
        matches.sort(key=lambda x: x[0])
        
        # Extrai texto de cada seção
        sections: list[tuple[str, str, str]] = []
        for i, (start_pos, raw_title, section_type) in enumerate(matches):
            end_pos = matches[i + 1][0] if i + 1 < len(matches) else len(text)
            section_text = text[start_pos:end_pos].strip()
            if section_text:
                sections.append((raw_title, section_type, section_text))
        
        return sections
