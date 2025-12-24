"""
Graph-Based Recommendation Engine

This module implements a graph-based recommendation system that leverages
the concept dependency graph to generate intelligent content recommendations.
The engine uses various graph traversal algorithms and centrality measures
to identify optimal learning paths and related content.

The graph-based approach captures the structural relationships between
concepts, enabling recommendations that respect prerequisite relationships
and identify interconnected topics.
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import deque
import logging
import math

from ..schemas import (
    StudentProfile,
    ContentItem,
    ConceptNode,
    LearningPath,
    RecommendationReason
)


logger = logging.getLogger(__name__)


class TraversalStrategy(Enum):
    """Enumeration of graph traversal strategies."""
    BFS = "breadth_first"  # Breadth-first for exploration
    DFS = "depth_first"    # Depth-first for deep dives
    DIJKSTRA = "dijkstra"  # Weighted shortest path
    A_STAR = "a_star"      # Heuristic-based pathfinding
    TOPOLOGICAL = "topological"  # For prerequisite chains


@dataclass
class GraphNode:
    """Represents a node in the concept dependency graph."""
    concept_id: str
    concept: ConceptNode
    neighbors: Dict[str, float] = field(default_factory=dict)  # concept_id -> weight
    incoming_edges: Dict[str, float] = field(default_factory=dict)  # prerequisite_id -> weight
    centrality_score: float = 0.0
    cluster_id: Optional[str] = None


@dataclass
class GraphEdge:
    """Represents an edge in the concept dependency graph."""
    source_concept_id: str
    target_concept_id: str
    relationship_type: str  # "prerequisite", "related", "similar", "extension"
    weight: float = 1.0
    strength: float = 1.0  # Semantic relationship strength


class ConceptDependencyGraph:
    """
    Represents the concept dependency graph for the learning domain.
    
    This class manages the graph structure and provides methods for
    building, updating, and querying the concept relationships.
    """
    
    def __init__(self):
        """Initialize an empty concept dependency graph."""
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.clusters: Dict[str, Set[str]] = {}
    
    def add_concept(self, concept: ConceptNode):
        """
        Add a concept node to the graph.
        
        Args:
            concept: The concept to add
        """
        if concept.concept_id not in self.nodes:
            self.nodes[concept.concept_id] = GraphNode(
                concept_id=concept.concept_id,
                concept=concept
            )
            logger.debug(f"Added concept node: {concept.concept_id}")
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "prerequisite",
        weight: float = 1.0
    ) -> bool:
        """
        Add an edge between two concept nodes.
        
        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            relationship_type: Type of relationship
            weight: Edge weight
            
        Returns:
            True if edge was added successfully
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"Cannot add edge: nodes not found ({source_id}, {target_id})")
            return False
        
        # Add edge to adjacency lists
        self.nodes[source_id].neighbors[target_id] = weight
        self.nodes[target_id].incoming_edges[source_id] = weight
        
        # Store edge metadata
        edge = GraphEdge(
            source_concept_id=source_id,
            target_concept_id=target_id,
            relationship_type=relationship_type,
            weight=weight
        )
        self.edges.append(edge)
        
        logger.debug(f"Added edge: {source_id} -> {target_id} ({relationship_type})")
        return True
    
    def build_from_concepts(self, concepts: List[ConceptNode]):
        """
        Build the graph from a list of concept nodes.
        
        Args:
            concepts: List of concepts to add
        """
        # Add all concepts
        for concept in concepts:
            self.add_concept(concept)
        
        # Add edges based on prerequisites
        for concept in concepts:
            if concept.prerequisites:
                for prereq_id in concept.prerequisites:
                    self.add_edge(prereq_id, concept.concept_id, "prerequisite", 1.0)
        
        # Add similarity edges if available
        for concept in concepts:
            if hasattr(concept, "related_concepts") and concept.related_concepts:
                for related_id in concept.related_concepts:
                    if related_id in self.nodes and related_id != concept.concept_id:
                        self.add_edge(
                            concept.concept_id,
                            related_id,
                            "related",
                            0.5
                        )
        
        # Calculate centrality scores
        self._calculate_centrality_scores()
        
        logger.info(f"Built graph with {len(self.nodes)} nodes and {len(self.edges)} edges")
    
    def _calculate_centrality_scores(self):
        """Calculate centrality scores for all nodes using PageRank-like algorithm."""
        # Simple degree centrality as starting point
        max_degree = 0
        
        for node in self.nodes.values():
            degree = len(node.neighbors) + len(node.incoming_edges)
            node.centrality_score = degree
            max_degree = max(max_degree, degree)
        
        # Normalize scores
        if max_degree > 0:
            for node in self.nodes.values():
                node.centrality_score /= max_degree
    
    def get_prerequisites(self, concept_id: str) -> List[str]:
        """
        Get all prerequisite concepts for a given concept.
        
        Uses BFS to find all ancestors in the dependency tree.
        
        Args:
            concept_id: The target concept ID
            
        Returns:
            List of prerequisite concept IDs
        """
        if concept_id not in self.nodes:
            return []
        
        prerequisites = set()
        queue = deque([concept_id])
        
        while queue:
            current = queue.popleft()
            for prereq_id in self.nodes[current].incoming_edges:
                if prereq_id not in prerequisites:
                    prerequisites.add(prereq_id)
                    queue.append(prereq_id)
        
        return list(prerequisites)
    
    def get_dependents(self, concept_id: str) -> List[str]:
        """
        Get all concepts that depend on the given concept.
        
        Args:
            concept_id: The source concept ID
            
        Returns:
            List of dependent concept IDs
        """
        if concept_id not in self.nodes:
            return []
        
        dependents = set()
        queue = deque([concept_id])
        
        while queue:
            current = queue.popleft()
            for neighbor_id in self.nodes[current].neighbors:
                if neighbor_id not in dependents:
                    dependents.add(neighbor_id)
                    queue.append(neighbor_id)
        
        return list(dependents)
    
    def find_learning_path(
        self,
        start_concepts: List[str],
        target_concepts: List[str],
        strategy: TraversalStrategy = TraversalStrategy.DIJKSTRA
    ) -> List[str]:
        """
        Find an optimal learning path from start to target concepts.
        
        Args:
            start_concepts: Starting concept IDs
            target_concepts: Target concept IDs
            strategy: Traversal strategy to use
            
        Returns:
            Ordered list of concept IDs representing the learning path
        """
        if strategy == TraversalStrategy.TOPOLOGICAL:
            return self._topological_path(start_concepts, target_concepts)
        elif strategy == TraversalStrategy.DIJKSTRA:
            return self._dijkstra_path(start_concepts, target_concepts)
        elif strategy == TraversalStrategy.A_STAR:
            return self._a_star_path(start_concepts, target_concepts)
        elif strategy == TraversalStrategy.BFS:
            return self._bfs_path(start_concepts, target_concepts)
        else:
            return self._dfs_path(start_concepts, target_concepts)
    
    def _bfs_path(self, start_concepts: List[str], target_concepts: List[str]) -> List[str]:
        """Find path using breadth-first search."""
        if not start_concepts or not target_concepts:
            return []
        
        queue = deque([(start_concepts[0], [start_concepts[0]])])
        visited = {start_concepts[0]}
        
        while queue:
            current, path = queue.popleft()
            
            if current in target_concepts:
                return path
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def _dfs_path(self, start_concepts: List[str], target_concepts: List[str]) -> List[str]:
        """Find path using depth-first search."""
        def dfs(current: str, path: List[str], visited: Set[str]) -> Optional[List[str]]:
            if current in target_concepts:
                return path
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor not in visited:
                    result = dfs(neighbor, path + [neighbor], visited | {neighbor})
                    if result:
                        return result
            
            return None
        
        if not start_concepts:
            return []
        
        return dfs(start_concepts[0], [start_concepts[0]], {start_concepts[0]}) or []
    
    def _dijkstra_path(
        self,
        start_concepts: List[str],
        target_concepts: List[str]
    ) -> List[str]:
        """Find shortest path using Dijkstra's algorithm."""
        import heapq
        
        if not start_concepts or not target_concepts:
            return []
        
        # Initialize distances and paths
        distances = {node_id: float('inf') for node_id in self.nodes}
        paths = {node_id: [] for node_id in self.nodes}
        
        # Priority queue: (distance, current_node, path)
        pq = []
        
        for start in start_concepts:
            if start in distances:
                distances[start] = 0
                paths[start] = [start]
                heapq.heappush(pq, (0, start, [start]))
        
        while pq:
            current_dist, current, current_path = heapq.heappop(pq)
            
            if current in target_concepts:
                return current_path
            
            if current_dist > distances[current]:
                continue
            
            for neighbor, weight in self.nodes[current].neighbors.items():
                distance = current_dist + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    new_path = current_path + [neighbor]
                    paths[neighbor] = new_path
                    heapq.heappush(pq, (distance, neighbor, new_path))
        
        return paths.get(target_concepts[0], [])
    
    def _a_star_path(
        self,
        start_concepts: List[str],
        target_concepts: List[str]
    ) -> List[str]:
        """Find path using A* algorithm with heuristic."""
        import heapq
        
        if not start_concepts or not target_concepts:
            return []
        
        def heuristic(node_id: str) -> float:
            """Simple heuristic: minimum distance to any target."""
            if not target_concepts:
                return 0
            
            min_dist = float('inf')
            for target in target_concepts:
                if target in self.nodes:
                    dist = self._graph_distance(node_id, target)
                    min_dist = min(min_dist, dist)
            
            return min_dist if min_dist != float('inf') else 100
        
        def graph_distance(node1: str, node2: str) -> float:
            """Calculate graph distance between two nodes."""
            queue = deque([(node1, 0)])
            visited = {node1}
            
            while queue:
                current, dist = queue.popleft()
                if current == node2:
                    return dist
                
                for neighbor in self.nodes[current].neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
            
            return float('inf')
        
        # Initialize
        open_set = []
        closed_set = set()
        
        for start in start_concepts:
            h = heuristic(start)
            heapq.heappush(open_set, (h, 0, start, [start]))
        
        g_scores = {start: 0 for start in start_concepts}
        
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            
            if current in target_concepts:
                return path
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor in closed_set:
                    continue
                
                tentative_g = g + self.nodes[current].neighbors[neighbor]
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h = heuristic(neighbor)
                    f_score = tentative_g + h
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor, path + [neighbor]))
        
        return []
    
    def _graph_distance(self, node1: str, node2: str) -> float:
        """Calculate the graph distance between two nodes."""
        if node1 == node2:
            return 0
        
        queue = deque([(node1, 0)])
        visited = {node1}
        
        while queue:
            current, dist = queue.popleft()
            
            for neighbor in self.nodes[current].neighbors:
                if neighbor == node2:
                    return dist + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return float('inf')
    
    def _topological_path(
        self,
        start_concepts: List[str],
        target_concepts: List[str]
    ) -> List[str]:
        """Generate path based on topological ordering."""
        # Get all prerequisites for target concepts
        all_prereqs = set()
        for target in target_concepts:
            all_prereqs.update(self.get_prerequisites(target))
        
        # Build dependency order
        path = list(start_concepts)
        visited = set(start_concepts)
        queue = deque(start_concepts)
        
        while queue:
            current = queue.popleft()
            
            for neighbor, weight in self.nodes[current].neighbors.items():
                if neighbor not in visited:
                    # Check if all prerequisites are in path
                    prereqs = self.get_prerequisites(neighbor)
                    if all(p in path for p in prereqs):
                        path.append(neighbor)
                        visited.add(neighbor)
                        queue.append(neighbor)
        
        return path
    
    def get_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Get concepts related to a given concept.
        
        Args:
            concept_id: The source concept ID
            max_depth: Maximum traversal depth
            relationship_types: Filter by relationship types
            
        Returns:
            List of (concept_id, distance) tuples
        """
        if concept_id not in self.nodes:
            return []
        
        if relationship_types is None:
            relationship_types = ["prerequisite", "related", "similar", "extension"]
        
        related = []
        queue = deque([(concept_id, 0)])
        visited = {concept_id}
        
        while queue:
            current, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            for neighbor, weight in self.nodes[current].neighbors.items():
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.append((neighbor, depth + 1))
                    queue.append((neighbor, depth + 1))
        
        # Sort by distance
        related.sort(key=lambda x: x[1])
        return related
    
    def get_central_concepts(self, top_n: int = 10) -> List[str]:
        """
        Get the most central concepts in the graph.
        
        Args:
            top_n: Number of concepts to return
            
        Returns:
            List of concept IDs sorted by centrality
        """
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.centrality_score,
            reverse=True
        )
        
        return [node.concept_id for node in sorted_nodes[:top_n]]
    
    def identify_clusters(self):
        """Identify concept clusters using connected components."""
        self.clusters = {}
        visited = set()
        
        for node_id in self.nodes:
            if node_id not in visited:
                # BFS to find connected component
                cluster = set()
                queue = deque([node_id])
                
                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    cluster.add(current)
                    
                    for neighbor in self.nodes[current].neighbors:
                        if neighbor not in visited:
                            queue.append(neighbor)
                
                cluster_id = f"cluster_{len(self.clusters)}"
                self.clusters[cluster_id] = cluster
                
                # Update nodes with cluster info
                for nid in cluster:
                    self.nodes[nid].cluster_id = cluster_id
        
        logger.info(f"Identified {len(self.clusters)} concept clusters")
        return self.clusters


class GraphBasedEngine:
    """
    Engine that generates recommendations using graph-based algorithms.
    
    This engine leverages the concept dependency graph to provide
    recommendations that respect prerequisite relationships and
    identify optimal learning paths through the curriculum.
    """
    
    def __init__(self, graph: Optional[ConceptDependencyGraph] = None):
        """
        Initialize the graph-based recommendation engine.
        
        Args:
            graph: Optional pre-built concept dependency graph
        """
        self.graph = graph or ConceptDependencyGraph()
        self.content_graph_mapping: Dict[str, List[str]] = {}  # content_id -> concept_ids
    
    def set_graph(self, graph: ConceptDependencyGraph):
        """
        Set the concept dependency graph.
        
        Args:
            graph: The concept dependency graph to use
        """
        self.graph = graph
    
    def build_content_mapping(self, content_items: List[ContentItem]):
        """
        Build mapping from content items to concepts.
        
        Args:
            content_items: List of content items with related concepts
        """
        for content in content_items:
            if hasattr(content, "related_concepts") and content.related_concepts:
                self.content_graph_mapping[content.content_id] = content.related_concepts
            else:
                self.content_graph_mapping[content.content_id] = []
        
        logger.info(
            f"Built content mapping for {len(self.content_graph_mapping)} items"
        )
    
    def recommend_based_on_concepts(
        self,
        profile: StudentProfile,
        available_content: List[ContentItem],
        max_results: int = 10,
        strategy: TraversalStrategy = TraversalStrategy.DIJKSTRA
    ) -> Tuple[List[ContentItem], List[RecommendationReason], Dict[str, Any]]:
        """
        Generate recommendations based on concept relationships.
        
        Args:
            profile: The student profile
            available_content: Available content items
            max_results: Maximum recommendations to return
            strategy: Graph traversal strategy
            
        Returns:
            Tuple of (recommended_items, reasons, metadata)
        """
        # Build content mapping if needed
        if not self.content_graph_mapping:
            self.build_content_mapping(available_content)
        
        # Identify target concepts from profile
        target_concepts = self._identify_target_concepts(profile)
        
        if not target_concepts:
            logger.info(f"No target concepts identified for student {profile.student_id}")
            return [], [], {"reason": "no_target_concepts"}
        
        # Find learning paths to target concepts
        start_concepts = list(profile.completed_concepts_ids) if profile.completed_concepts_ids else []
        
        if not start_concepts:
            # Start from foundational concepts
            start_concepts = self._find_foundational_concepts()
        
        # Generate paths
        all_path_concepts = set()
        for target in target_concepts:
            path = self.graph.find_learning_path(
                start_concepts or ["foundational"],
                [target],
                strategy
            )
            all_path_concepts.update(path)
        
        # Score content based on concept alignment
        scored_content = []
        
        for content in available_content:
            content_concepts = self.content_graph_mapping.get(content.content_id, [])
            
            # Calculate concept overlap
            overlap = len(set(content_concepts) & all_path_concepts)
            
            if overlap > 0:
                # Calculate additional factors
                priority_score = self._calculate_priority_score(
                    content, profile, content_concepts, target_concepts
                )
                
                path_score = overlap / len(all_path_concepts) if all_path_concepts else 0
                
                total_score = (path_score * 0.4 + priority_score * 0.6)
                
                scored_content.append((content, total_score, content_concepts))
        
        # Sort by score
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        # Get top recommendations
        recommended_items = [item for item, _, _ in scored_content[:max_results]]
        
        # Generate reasons
        reasons = [
            RecommendationReason(
                rule_applied="graph_based_concept_recommendation",
                explanation=f"Content aligns with learning path to target concepts",
                confidence=0.8,
                factors=[
                    f"Concepts aligned: {len(set(self.content_graph_mapping.get(item.content_id, [])) & all_path_concepts)}",
                    f"Priority score: {score:.2f}"
                ]
            )
            for item, score, _ in scored_content[:max_results]
        ]
        
        metadata = {
            "target_concepts": target_concepts,
            "path_concepts_count": len(all_path_concepts),
            "strategy": strategy.value,
            "content_scored": len(scored_content)
        }
        
        return recommended_items, reasons, metadata
    
    def recommend_prerequisites(
        self,
        profile: StudentProfile,
        target_content: ContentItem,
        available_content: List[ContentItem]
    ) -> List[ContentItem]:
        """
        Recommend prerequisite content for target content.
        
        Args:
            profile: The student profile
            target_content: The content user wants to access
            available_content: Available content items
            
        Returns:
            List of prerequisite content items
        """
        target_concepts = self.content_graph_mapping.get(
            target_content.content_id, []
        )
        
        if not target_concepts:
            return []
        
        # Get all prerequisites for target concepts
        all_prereqs = set()
        for concept_id in target_concepts:
            prereqs = self.graph.get_prerequisites(concept_id)
            all_prereqs.update(prereqs)
        
        # Filter out already completed concepts
        missing_prereqs = all_prereqs - set(profile.completed_concepts_ids)
        
        # Find content for missing prerequisites
        prereq_content = []
        for content in available_content:
            content_concepts = self.content_graph_mapping.get(content.content_id, [])
            
            if set(content_concepts) & missing_prereqs:
                prereq_content.append(content)
        
        # Sort by prerequisite depth (most foundational first)
        prereq_content.sort(
            key=lambda c: self._calculate_concept_depth(
                self.content_graph_mapping.get(c.content_id, [])
            )
        )
        
        return prereq_content
    
    def recommend_extended_learning(
        self,
        profile: StudentProfile,
        completed_content: ContentItem,
        available_content: List[ContentItem],
        max_results: int = 5
    ) -> Tuple[List[ContentItem], Dict[str, Any]]:
        """
        Recommend extended learning content based on completed content.
        
        Args:
            profile: The student profile
            completed_content: Content the student just completed
            available_content: Available content items
            max_results: Maximum recommendations
            
        Returns:
            Tuple of (recommended_items, metadata)
        """
        completed_concepts = self.content_graph_mapping.get(
            completed_content.content_id, []
        )
        
        if not completed_concepts:
            return [], {"reason": "no_concept_mapping"}
        
        # Find related concepts
        related_concepts = []
        for concept_id in completed_concepts:
            related = self.graph.get_related_concepts(
                concept_id,
                max_depth=2,
                relationship_types=["extension", "related", "similar"]
            )
            related_concepts.extend([r[0] for r in related])
        
        # Remove already completed concepts
        available_related = [
            c for c in set(related_concepts)
            if c not in profile.completed_concepts_ids
        ]
        
        # Find content for related concepts
        extended_content = []
        for content in available_content:
            content_concepts = self.content_graph_mapping.get(content.content_id, [])
            
            if set(content_concepts) & set(available_related):
                if content.content_id not in profile.completed_content_ids:
                    extended_content.append(content)
        
        # Sort by centrality (most connected concepts first)
        extended_content.sort(
            key=lambda c: self._calculate_concept_centrality(
                self.content_graph_mapping.get(c.content_id, [])
            ),
            reverse=True
        )
        
        return extended_content[:max_results], {
            "completed_concepts": completed_concepts,
            "related_concepts_found": len(available_related),
            "recommendations_count": len(extended_content[:max_results])
        }
    
    def generate_learning_path(
        self,
        profile: StudentProfile,
        target_concepts: List[str],
        available_content: List[ContentItem]
    ) -> LearningPath:
        """
        Generate a complete learning path to target concepts.
        
        Args:
            profile: The student profile
            target_concepts: Target concept IDs
            available_content: Available content items
            
        Returns:
            LearningPath with ordered content recommendations
        """
        # Build content mapping
        self.build_content_mapping(available_content)
        
        # Find paths to target concepts
        start_concepts = list(profile.completed_concepts_ids) if profile.completed_concepts_ids else []
        
        if not start_concepts:
            start_concepts = self._find_foundational_concepts()
        
        # Collect all concepts in paths
        all_path_concepts = set()
        concept_to_content = {}
        
        for target in target_concepts:
            path = self.graph.find_learning_path(
                start_concepts,
                [target],
                TraversalStrategy.TOPOLOGICAL
            )
            all_path_concepts.update(path)
            
            # Map each concept to best content
            for concept_id in path:
                if concept_id not in concept_to_content:
                    concept_to_content[concept_id] = []
                
                for content in available_content:
                    content_concepts = self.content_graph_mapping.get(
                        content.content_id, []
                    )
                    if concept_id in content_concepts:
                        if content not in concept_to_content[concept_id]:
                            concept_to_content[concept_id].append(content)
        
        # Build ordered path
        path_items = []
        reasons = []
        
        for concept_id in sorted(
            all_path_concepts,
            key=lambda c: self._calculate_concept_depth([c])
        ):
            if concept_id in concept_to_content:
                # Select best content for this concept
                best_content = self._select_best_content(
                    concept_to_content[concept_id],
                    profile
                )
                if best_content:
                    path_items.append(best_content)
                    
                    reason = RecommendationReason(
                        rule_applied="learning_path_generation",
                        explanation=f"Step in path to target concepts",
                        confidence=0.85,
                        factors=[
                            f"Concept: {concept_id}",
                            f"Content: {best_content.title}",
                            f"Type: {best_content.content_type}"
                        ]
                    )
                    reasons.append(reason)
        
        learning_path = LearningPath(
            path_id=f"gplp_{profile.student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            student_id=profile.student_id,
            items=path_items,
            total_duration=sum(c.estimated_duration for c in path_items),
            reasons=reasons,
            created_at=datetime.now()
        )
        
        return learning_path
    
    def _identify_target_concepts(self, profile: StudentProfile) -> List[str]:
        """Identify target concepts based on student profile."""
        targets = []
        
        # Add incomplete prerequisites from profile
        if profile.incomplete_prerequisites_ids:
            targets.extend(profile.incomplete_prerequisites_ids)
        
        # Add topics from learning goals
        if hasattr(profile, "learning_goals") and profile.learning_goals:
            for goal in profile.learning_goals:
                if hasattr(goal, "target_concepts"):
                    targets.extend(goal.target_concepts)
        
        # Add concepts with low mastery
        if profile.mastery_states:
            for concept_id, mastery in profile.mastery_states.items():
                if mastery < 0.7:
                    targets.append(concept_id)
        
        return list(set(targets))
    
    def _find_foundational_concepts(self) -> List[str]:
        """Find foundational concepts (those with no prerequisites)."""
        foundational = []
        
        for node_id, node in self.graph.nodes.items():
            if not node.incoming_edges:
                foundational.append(node_id)
        
        return foundational
    
    def _calculate_priority_score(
        self,
        content: ContentItem,
        profile: StudentProfile,
        content_concepts: List[str],
        target_concepts: List[str]
    ) -> float:
        """Calculate priority score for content."""
        score = 0.5
        
        # Boost for content directly targeting needed concepts
        direct_targets = set(content_concepts) & set(target_concepts)
        score += len(direct_targets) * 0.15
        
        # Boost for content in progress
        if hasattr(profile, "in_progress_content_ids"):
            if content.content_id in profile.in_progress_content_ids:
                score += 0.2
        
        # Boost for high-quality content
        if hasattr(content, "quality_score"):
            score += content.quality_score * 0.1
        
        # Adjust for difficulty
        difficulty_map = {
            "foundational": 1.0,
            "intermediate": 2.0,
            "advanced": 3.0
        }
        difficulty_level = difficulty_map.get(content.difficulty_level, 2.0)
        
        # Match difficulty to student level
        if profile.average_score:
            student_level = 1 + profile.average_score * 2
            difficulty_diff = abs(difficulty_level - student_level)
            if difficulty_diff < 0.5:
                score += 0.1
            elif difficulty_diff > 1.5:
                score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    def _calculate_concept_depth(self, concept_ids: List[str]) -> int:
        """Calculate maximum depth of concepts from foundational level."""
        max_depth = 0
        
        for concept_id in concept_ids:
            prereqs = self.graph.get_prerequisites(concept_id)
            depth = len(prereqs)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_concept_centrality(self, concept_ids: List[str]) -> float:
        """Calculate average centrality of concepts."""
        if not concept_ids:
            return 0.0
        
        centralities = [
            self.graph.nodes.get(cid, GraphNode(cid, ConceptNode(cid, ""))).centrality_score
            for cid in concept_ids
            if cid in self.graph.nodes
        ]
        
        return sum(centralities) / len(centralities) if centralities else 0.0
    
    def _select_best_content(
        self,
        content_list: List[ContentItem],
        profile: StudentProfile
    ) -> Optional[ContentItem]:
        """Select the best content item from a list."""
        if not content_list:
            return None
        
        scored = []
        for content in content_list:
            # Prefer content student hasn't seen
            if content.content_id in profile.completed_content_ids:
                score = 0.3
            else:
                score = 0.7
            
            # Factor in quality
            if hasattr(content, "quality_score"):
                score += content.quality_score * 0.3
            
            scored.append((content, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None
