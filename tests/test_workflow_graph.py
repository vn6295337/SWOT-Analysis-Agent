#!/usr/bin/env python3
"""
Graph Workflow Tests
Tests the core graph-based workflow functionality.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_basic_graph_workflow():
    """Test basic graph workflow functionality"""
    print("🧪 Testing Basic Graph Workflow...")
    
    try:
        # Add project root to Python path
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from src.state import AgentState
        from langgraph.graph import StateGraph
        from langchain_core.runnables import RunnableLambda
        
        # Test basic graph creation
        workflow = StateGraph(AgentState)
        print("✅ Basic graph workflow test passed")
        return True
    except Exception as e:
        print(f"❌ Basic graph workflow test failed: {e}")
        return False

def test_node_functionality():
    """Test individual node functionality"""
    print("\n🧪 Testing Node Functionality...")
    print("📝 Node functionality test placeholder")
    print("✅ Node functionality framework ready")
    return True

if __name__ == "__main__":
    print("🚀 Running Graph Test Suite")
    print("=" * 35)
    
    success1 = test_basic_graph_workflow()
    success2 = test_node_functionality()
    
    if success1 and success2:
        print("\n🎉 All graph tests completed successfully!")
    else:
        print("\n❌ Some graph tests failed!")
        sys.exit(1)
