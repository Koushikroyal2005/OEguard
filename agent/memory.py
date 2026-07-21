"""
Memory Module using Chroma DB
Stores historical behavior patterns for better decisions
"""

import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime
import json
from typing import List, Dict, Any

class GuardianMemory:
    """Vector memory for tracking child's behavior patterns"""
    
    def __init__(self, persist_directory="./chroma-data"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use sentence transformer for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="guardian_memory",
            embedding_function=self.embedding_fn,
            metadata={"description": "Screen time guardian behavior memory"}
        )
        
    def store_event(self, event_data: Dict[str, Any]):
        """Store an event in memory"""
        event_id = f"event_{datetime.now().timestamp()}"
        
        # Create a descriptive text for embedding
        text = f"""
        Time: {event_data.get('timestamp')}
        Blink Rate: {event_data.get('blink_rate')}/min
        Action: {event_data.get('action')}
        Child's Reaction: {event_data.get('reaction')}
        Defiance Level: {event_data.get('defiance_score')}
        Outcome: {event_data.get('outcome')}
        """
        
        self.collection.add(
            documents=[text],
            metadatas=[event_data],
            ids=[event_id]
        )
        
    def query_similar_events(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find similar past events"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        events = []
        if results['metadatas']:
            for metadata in results['metadatas'][0]:
                events.append(metadata)
                
        return events
    
    def get_recent_history(self, minutes: int = 30) -> List[Dict]:
        """Get events from recent time window"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        
        # Query all events (in production, use time-based filtering)
        results = self.collection.get()
        
        recent = []
        if results['metadatas']:
            for metadata in results['metadatas']:
                try:
                    event_time = datetime.fromisoformat(metadata['timestamp']).timestamp()
                    if event_time > cutoff_time:
                        recent.append(metadata)
                except:
                    continue
                    
        return recent
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze behavior patterns from memory"""
        recent = self.get_recent_history(60)
        
        if not recent:
            return {"message": "No recent history available"}
        
        # Calculate patterns
        warnings_count = len([e for e in recent if e.get('action') == 'WARNING'])
        compliance_count = len([e for e in recent if e.get('reaction') == 'complied'])
        defiance_count = len([e for e in recent if e.get('action') == 'DEFIANCE'])
        
        total = len(recent)
        compliance_rate = (compliance_count / total * 100) if total > 0 else 0
        
        return {
            "total_events": total,
            "warnings_sent": warnings_count,
            "compliance_rate": round(compliance_rate, 1),
            "defiance_incidents": defiance_count,
            "risk_level": "HIGH" if defiance_count > 2 else "MEDIUM" if warnings_count > 3 else "LOW",
            "recommendation": self._generate_recommendation(compliance_rate, defiance_count)
        }
    
    def _generate_recommendation(self, compliance_rate: float, defiance_count: int) -> str:
        """Generate recommendation based on patterns"""
        if defiance_count > 3:
            return "Consider stricter rules and parent intervention"
        elif compliance_rate < 50:
            return "Try more engaging warning messages with favorite characters"
        elif compliance_rate > 80:
            return "Great compliance! Maintain current approach with positive reinforcement"
        else:
            return "Continue monitoring and adjust warning timing"
    
    def clear_memory(self):
        """Clear all memory (use with caution)"""
        self.client.delete_collection("guardian_memory")
        self.collection = self.client.create_collection(
            name="guardian_memory",
            embedding_function=self.embedding_fn
        )

# Test memory functionality
if __name__ == "__main__":
    memory = GuardianMemory()
    
    # Store a test event
    memory.store_event({
        "timestamp": datetime.now().isoformat(),
        "blink_rate": 8,
        "action": "WARNING",
        "reaction": "ignored",
        "defiance_score": 0.3,
        "outcome": "Second warning sent"
    })
    
    # Query similar events
    similar = memory.query_similar_events("child ignored warning")
    print(f"Found {len(similar)} similar events")
    
    # Analyze patterns
    patterns = memory.analyze_patterns()
    print(f"Behavior patterns: {patterns}")
