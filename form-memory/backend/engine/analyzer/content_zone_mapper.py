"""
Content Zone Mapper
Intelligent mapping of AI-generated content to template zones with hierarchy preservation
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from .advanced_template_analyzer import ContentZone, ZoneType, TemplateStructure


class ContentType(Enum):
    """Types of content that can be generated"""
    CHAPTER_TITLE = "chapter_title"
    SUBSECTION_TITLE = "subsection_title"
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    TABLE = "table"
    EQUATION = "equation"
    FIGURE = "figure"


@dataclass
class ContentItem:
    """Represents a piece of AI-generated content"""
    content_id: str
    content_type: ContentType
    content: str
    hierarchy_level: int = 0
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InsertionPlan:
    """Plan for inserting content into template zones"""
    mappings: Dict[str, str] = field(default_factory=dict)  # zone_id -> content_id
    style_mappings: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    hierarchy_preserved: bool = True
    confidence_score: float = 0.0
    fallback_strategy: str = "sequential"


class ContentZoneMapper:
    """
    Maps AI-generated content to appropriate template zones with intelligent matching
    """

    # Content type mapping for Indonesian academic content
    CONTENT_TYPE_PATTERNS = {
        ContentType.CHAPTER_TITLE: [
            r'^BAB\s+[IVXLCDM\d]+\s*[:-]?\s*(.+)$',  # BAB I - PENDAHULUAN
            r'^Chapter\s+\d+\s*[:-]?\s*(.+)$',       # Chapter 1 - Introduction
        ],
        ContentType.SUBSECTION_TITLE: [
            r'^\d+\.\d+\.?\s+(.+)$',                  # 1.1 Latar Belakang
            r'^\d+\.\d+\.\d+\.?\s+(.+)$',            # 1.1.1 Pendahuluan
            r'^([A-Z])\.\s+(.+)$',                   # A. Alternatif
        ],
        ContentType.LIST_ITEM: [
            r'^\d+\.\s+(.+)$',                       # 1. Item
            r'^[a-z]\)\s+(.+)$',                     # a) Item
            r'^•\s+(.+)$',                           # • Item
        ],
        ContentType.TABLE: [
            r'.*tabel.*', r'.*table.*',              # Contains table reference
        ],
        ContentType.EQUATION: [
            r'.*=.*', r'.*∑.*', r'.*∫.*',            # Mathematical expressions
        ]
    }

    def __init__(self, template_structure: TemplateStructure):
        self.template_structure = template_structure
        self.content_items: List[ContentItem] = []
        self.insertion_plan = InsertionPlan()

    def map_ai_content_to_zones(self, ai_content: Dict[str, Any]) -> InsertionPlan:
        """
        Main method: Map AI-generated content to template zones

        Args:
            ai_content: Dictionary with keys like 'chapter1', 'chapter2', etc.

        Returns:
            Detailed insertion plan
        """
        print("[INFO] Starting content-to-zone mapping...")

        # Step 1: Parse AI content into structured items
        self._parse_ai_content(ai_content)

        # Step 2: Match content items to template zones
        self._match_content_to_zones()

        # Step 3: Apply style inheritance
        self._apply_style_inheritance()

        # Step 4: Validate and optimize mapping
        self._validate_and_optimize_mapping()

        # Step 5: Calculate confidence score
        self._calculate_mapping_confidence()

        print(f"[SUCCESS] Content mapping complete. {len(self.insertion_plan.mappings)} mappings "
              f"with {self.insertion_plan.confidence_score:.1%} confidence")

        return self.insertion_plan

    def _parse_ai_content(self, ai_content: Dict[str, Any]) -> None:
        """
        Parse AI-generated content into structured ContentItem objects
        """
        print("[INFO] Parsing AI content structure...")

        for chapter_key, chapter_data in ai_content.items():
            if not isinstance(chapter_data, dict):
                continue

            # Extract chapter number
            chapter_match = re.match(r'chapter(\d+)', chapter_key)
            if not chapter_match:
                continue

            chapter_num = int(chapter_match.group(1))

            # Process each subsection
            for subsection_key, subsection_content in chapter_data.items():
                if not subsection_content or not isinstance(subsection_content, str):
                    continue

                # Determine content type
                content_type = self._classify_content_type(subsection_content)

                # Create content item
                content_item = ContentItem(
                    content_id=f"{chapter_key}_{subsection_key}",
                    content_type=content_type,
                    content=subsection_content,
                    hierarchy_level=self._determine_hierarchy_level(subsection_key, chapter_num),
                    parent_id=chapter_key,
                    metadata={
                        'chapter_num': chapter_num,
                        'subsection_key': subsection_key,
                        'word_count': len(subsection_content.split()),
                        'char_count': len(subsection_content)
                    }
                )

                self.content_items.append(content_item)

        print(f"[INFO] Parsed {len(self.content_items)} content items")

    def _match_content_to_zones(self) -> None:
        """
        Match content items to appropriate template zones using multiple strategies
        """
        print("[INFO] Matching content to template zones...")

        # Strategy 1: Direct hierarchy matching (ideal case)
        direct_matches = self._try_direct_hierarchy_matching()
        print(f"[INFO] Direct hierarchy matches: {len(direct_matches)}")

        # Strategy 2: Semantic matching for unmatched content
        semantic_matches = self._try_semantic_matching()
        print(f"[INFO] Semantic matches: {len(semantic_matches)}")

        # Strategy 3: Fallback sequential mapping
        sequential_matches = self._try_sequential_mapping()
        print(f"[INFO] Sequential fallback matches: {len(sequential_matches)}")

        # Combine all mappings
        self.insertion_plan.mappings.update(direct_matches)
        self.insertion_plan.mappings.update(semantic_matches)
        self.insertion_plan.mappings.update(sequential_matches)

    def _try_direct_hierarchy_matching(self) -> Dict[str, str]:
        """
        Try to match content based on direct hierarchy (Chapter 1 → 1.x zones)
        """
        mappings = {}

        # Group content by chapter
        content_by_chapter = {}
        for item in self.content_items:
            chapter_num = item.metadata.get('chapter_num', 0)
            if chapter_num not in content_by_chapter:
                content_by_chapter[chapter_num] = []
            content_by_chapter[chapter_num].append(item)

        # Group zones by hierarchy
        zones_by_hierarchy = {}
        for zone_id, zone in self.template_structure.zones.items():
            level = zone.hierarchy_level
            if level not in zones_by_hierarchy:
                zones_by_hierarchy[level] = []
            zones_by_hierarchy[level].append(zone)

        # Match chapter content to appropriate zones
        for chapter_num, chapter_items in content_by_chapter.items():
            # Find zones for this chapter level
            chapter_zones = []
            for zone in self.template_structure.zones.values():
                if zone.zone_type in [ZoneType.CONTENT, ZoneType.PLACEHOLDER]:
                    # Check if zone is in chapter area (rough heuristic)
                    if chapter_num == 1 and zone.start_paragraph < 200:  # Chapter 1 zones
                        chapter_zones.append(zone)
                    elif chapter_num > 1 and zone.start_paragraph > (chapter_num - 1) * 100:  # Later chapters
                        chapter_zones.append(zone)

            # Sort zones by position for sequential assignment
            chapter_zones.sort(key=lambda z: z.start_paragraph)

            # Assign content to zones
            for i, content_item in enumerate(chapter_items):
                if i < len(chapter_zones):
                    zone = chapter_zones[i]
                    mappings[zone.zone_id] = content_item.content_id

        return mappings

    def _try_semantic_matching(self) -> Dict[str, str]:
        """
        Use semantic analysis to match content to zones based on content type
        """
        mappings = {}

        # Get unmatched content and zones
        used_zones = set(self.insertion_plan.mappings.keys())
        used_content = set(self.insertion_plan.mappings.values())

        available_zones = [z for z in self.template_structure.zones.values()
                          if z.zone_id not in used_zones and z.zone_type in [ZoneType.CONTENT, ZoneType.PLACEHOLDER]]

        available_content = [c for c in self.content_items
                           if c.content_id not in used_content]

        # Simple semantic matching based on content length and position
        available_zones.sort(key=lambda z: z.start_paragraph)

        for i, zone in enumerate(available_zones):
            if i < len(available_content):
                content_item = available_content[i]
                # Check if content length roughly matches zone expectations
                if self._content_matches_zone(content_item, zone):
                    mappings[zone.zone_id] = content_item.content_id

        return mappings

    def _try_sequential_mapping(self) -> Dict[str, str]:
        """
        Fallback: Map remaining content to remaining zones sequentially
        """
        mappings = {}

        # Get unmatched content and zones
        used_zones = set(self.insertion_plan.mappings.keys())
        used_content = set(self.insertion_plan.mappings.values())

        available_zones = [z for z in self.template_structure.zones.values()
                          if z.zone_id not in used_zones and z.zone_type in [ZoneType.CONTENT, ZoneType.PLACEHOLDER]]

        available_content = [c for c in self.content_items
                           if c.content_id not in used_content]

        # Sort by position for predictable mapping
        available_zones.sort(key=lambda z: z.start_paragraph)
        available_content.sort(key=lambda c: c.metadata.get('chapter_num', 0))

        # Map sequentially
        for zone, content_item in zip(available_zones, available_content):
            mappings[zone.zone_id] = content_item.content_id

        return mappings

    def _apply_style_inheritance(self) -> None:
        """
        Apply appropriate styles to content insertions based on zone context
        """
        for zone_id, content_id in self.insertion_plan.mappings.items():
            zone = self.template_structure.zones.get(zone_id)
            if zone:
                # Get style rules for this zone
                style_rules = self.template_structure.style_rules.get(zone.style_info.get('style_name', 'Normal'), {})

                # Find corresponding content item
                content_item = next((c for c in self.content_items if c.content_id == content_id), None)
                if content_item:
                    # Apply style inheritance rules
                    inherited_styles = self._inherit_styles_from_zone(zone, style_rules)
                    self.insertion_plan.style_mappings[content_id] = inherited_styles

    def _validate_and_optimize_mapping(self) -> None:
        """
        Validate the mapping and optimize where possible
        """
        # Check for unmapped critical content
        all_content_ids = {c.content_id for c in self.content_items}
        mapped_content = set(self.insertion_plan.mappings.values())
        unmapped_content = all_content_ids - mapped_content

        if unmapped_content:
            print(f"[WARNING] {len(unmapped_content)} content items could not be mapped to zones")
            self.insertion_plan.hierarchy_preserved = False

        # Check for unused zones
        all_zone_ids = {z.zone_id for z in self.template_structure.zones.values()
                       if z.zone_type in [ZoneType.CONTENT, ZoneType.PLACEHOLDER]}
        used_zones = set(self.insertion_plan.mappings.keys())
        unused_zones = all_zone_ids - used_zones

        if unused_zones:
            print(f"[INFO] {len(unused_zones)} zones remain unused (acceptable)")

    def _calculate_mapping_confidence(self) -> None:
        """
        Calculate confidence score for the mapping
        """
        score = 50.0  # Base score

        # Mapping completeness (30% weight)
        total_content = len(self.content_items)
        mapped_content = len(set(self.insertion_plan.mappings.values()))
        if total_content > 0:
            completeness_score = (mapped_content / total_content) * 30
            score += completeness_score

        # Hierarchy preservation (20% weight)
        if self.insertion_plan.hierarchy_preserved:
            score += 20

        # Style inheritance quality (20% weight)
        styled_mappings = len(self.insertion_plan.style_mappings)
        if mapped_content > 0:
            style_score = (styled_mappings / mapped_content) * 20
            score += style_score

        # Direct matches vs fallbacks (30% weight)
        # This would be calculated based on mapping strategy used

        self.insertion_plan.confidence_score = min(score, 100.0)

    def _classify_content_type(self, content: str) -> ContentType:
        """Classify content type based on patterns"""
        for content_type, patterns in self.CONTENT_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return content_type

        # Default to paragraph
        return ContentType.PARAGRAPH

    def _determine_hierarchy_level(self, subsection_key: str, chapter_num: int) -> int:
        """Determine hierarchy level for content item"""
        if subsection_key in ['latar_belakang', 'tujuan_penelitian']:
            return 1  # Chapter level subsections
        elif subsection_key in ['landasan_teori', 'metodologi']:
            return 2  # Major subsections
        else:
            return 3  # Minor subsections

    def _content_matches_zone(self, content_item: ContentItem, zone: ContentZone) -> bool:
        """
        Check if content item is appropriate for the zone based on various factors
        """
        # Length compatibility
        content_length = len(content_item.content)
        zone_content_length = len(zone.content)

        # Content type compatibility
        if content_item.content_type == ContentType.CHAPTER_TITLE and zone.zone_type != ZoneType.HEADER:
            return False
        if content_item.content_type == ContentType.PARAGRAPH and zone.zone_type == ZoneType.HEADER:
            return False

        # Length ratio check (content shouldn't be much longer than zone capacity)
        if zone_content_length > 0 and content_length > zone_content_length * 3:
            return False

        return True

    def _inherit_styles_from_zone(self, zone: ContentZone, style_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine style inheritance for content inserted into this zone
        """
        inherited_styles = {}

        # Inherit font properties
        if 'fonts' in style_rules:
            inherited_styles.update(style_rules['fonts'])

        # Inherit paragraph formatting
        if 'spacing' in style_rules:
            inherited_styles.update(style_rules['spacing'])

        # Zone-specific adjustments
        if zone.zone_type == ZoneType.HEADER:
            inherited_styles['bold'] = True
        elif zone.hierarchy_level > 0:
            inherited_styles['indent'] = zone.hierarchy_level * 0.5  # 0.5 cm per level

        return inherited_styles