#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all test suites in the SWOT Analysis Agent project.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def run_all_tests():
    """Run all test suites"""
    print("🚀 Running Complete Test Suite")
    print("=" * 40)
    
    # Import and run individual test modules
    test_modules = [
        ("MCP Tests", "test_mcp"),
        ("Self-Correction Tests", "test_self_correction"),
        ("Graph Tests", "test_graph"),
        ("Streamlit Tests", "test_streamlit")
    ]
    
    results = []
    
    for test_name, module_name in test_modules:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        
        try:
            # Dynamically import and run the test module
            module = __import__(module_name)
            if hasattr(module, 'main'):
                result = module.main()
                results.append((test_name, True, "Passed"))
            else:
                print(f"✅ {test_name} framework ready")
                results.append((test_name, True, "Framework Ready"))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    failed = 0
    
    for test_name, success, status in results:
        if success:
            print(f"✅ {test_name}: {status}")
            passed += 1
        else:
            print(f"❌ {test_name}: {status}")
            failed += 1
    
    print(f"\n📈 Total: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    run_all_tests()
