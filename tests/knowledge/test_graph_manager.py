"""
Tests for the graph manager component.
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from knowledge.graph_manager import GraphManager

class TestGraphManager(unittest.TestCase):
    """Test cases for the GraphManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph_manager = GraphManager()
    
    def test_find_entity_direct_match(self):
        """Test finding an entity with a direct match."""
        # Test with exact match
        result = self.graph_manager.find_entity("knowledge_graph")
        
        # Check that we got a result
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'knowledge_graph')
        self.assertEqual(result['name'], 'Knowledge Graph')
    
    def test_find_entity_case_insensitive(self):
        """Test finding an entity with case-insensitive matching."""
        # Test with mixed case
        result = self.graph_manager.find_entity("Knowledge Graph")
        
        # Check that we got a result
        self.assertIsNotNone(result)
        self.assertEqual(result['id'], 'knowledge_graph')
    
    def test_find_entity_not_found(self):
        """Test behavior when entity is not found."""
        # Test with non-existent entity
        result = self.graph_manager.find_entity("nonexistent_entity")
        
        # Check that we got no result
        self.assertIsNone(result)
    
    def test_get_relationships_outgoing(self):
        """Test getting outgoing relationships for an entity."""
        # Get outgoing relationships for knowledge_graph
        relationships = self.graph_manager.get_relationships("knowledge_graph", direction="outgoing")
        
        # Check that we got results
        self.assertGreater(len(relationships), 0)
        
        # Check that all are outgoing from knowledge_graph
        for rel in relationships:
            self.assertEqual(rel['source'], 'knowledge_graph')
    
    def test_get_relationships_incoming(self):
        """Test getting incoming relationships for an entity."""
        # Get incoming relationships for vector_embeddings
        relationships = self.graph_manager.get_relationships("vector_embeddings", direction="incoming")
        
        # Check that we got results
        self.assertGreater(len(relationships), 0)
        
        # Check that all are incoming to vector_embeddings
        for rel in relationships:
            self.assertEqual(rel['target'], 'vector_embeddings')
    
    def test_get_relationships_filtered(self):
        """Test getting relationships filtered by relationship type."""
        # Get RELATED_TO relationships for knowledge_graph
        relationships = self.graph_manager.get_relationships(
            "knowledge_graph",
            relationship_types=["RELATED_TO"],
            direction="both"
        )
        
        # Check that we got results
        self.assertGreater(len(relationships), 0)
        
        # Check that all are RELATED_TO type
        for rel in relationships:
            self.assertEqual(rel['type'], 'RELATED_TO')
    
    def test_find_related_entities(self):
        """Test finding related entities with traversal."""
        # Find entities related to knowledge_graph
        related = self.graph_manager.find_related_entities("knowledge_graph", max_depth=1)
        
        # Check that we got results
        self.assertGreater(len(related), 0)
        
        # Check that each has an entity and relationship
        for item in related:
            self.assertIn('entity', item)
            self.assertIn('relationship', item)
            self.assertIn('depth', item)
    
    def test_find_related_entities_with_depth(self):
        """Test finding related entities with multiple traversal depth."""
        # Find entities related to knowledge_graph with depth 2
        related = self.graph_manager.find_related_entities("knowledge_graph", max_depth=2)
        
        # Check that we got results
        self.assertGreater(len(related), 0)
        
        # Check that we have some items at depth 2
        has_depth_2 = any(item['depth'] == 2 for item in related)
        self.assertTrue(has_depth_2, "Should have found entities at depth 2")

if __name__ == "__main__":
    unittest.main() 