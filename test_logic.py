"""
test_logic.py
Part 4: Automated Validation of Forward Chaining Logic Engine
Self-Evaluation Test Cases for the Knowledge Base
"""

from logic_engine import KnowledgeBase


def test_forward_chaining():
    """
    Test suite for validating Forward Chaining inference engine.
    These tests verify that the mathematical logic implementation works correctly
    before integration with the visual grid.
    """
    
    kb = KnowledgeBase()
    
    # ============================================================================
    # Add Domain Rules (Horn Clauses)
    # ============================================================================
    # Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
    kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
    
    # Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
    kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')
    
    # ============================================================================
    # Test Case 1: Safe Engagement (No threat from Bloodseeker)
    # ============================================================================
    print("Running Test Case 1: Safe Engagement...")
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.forward_chain()
    
    assert 'SafeToEngage' in kb.facts, "Test 1 Failed: Should deduce SafeToEngage"
    assert 'Retreat' not in kb.facts, "Test 1 Failed: Should NOT deduce Retreat"
    print("✅ Test Case 1 Passed: SafeToEngage deduced, no retreat needed")
    
    # ============================================================================
    # Test Case 2: Unsafe Engagement (Bloodseeker Missing = threat detected)
    # ============================================================================
    print("\nRunning Test Case 2: Unsafe Engagement (Bloodseeker Threat)...")
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.tell_fact('BloodseekerMissing')
    kb.forward_chain()
    
    assert 'SafeToEngage' in kb.facts, "Test 2 Failed: Should deduce SafeToEngage"
    assert 'Retreat' in kb.facts, "Test 2 Failed: Should deduce Retreat when Bloodseeker is missing"
    print("✅ Test Case 2 Passed: Retreat deduced due to Bloodseeker threat")
    
    # ============================================================================
    # Test Case 3: Incomplete premises (Missing HasDust)
    # ============================================================================
    print("\nRunning Test Case 3: Incomplete Premises (Missing HasDust)...")
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    # Note: NOT adding 'HasDust'
    kb.forward_chain()
    
    assert 'SafeToEngage' not in kb.facts, "Test 3 Failed: Should NOT deduce SafeToEngage without HasDust"
    assert 'Retreat' not in kb.facts, "Test 3 Failed: Should NOT deduce Retreat"
    print("✅ Test Case 3 Passed: No deduction when premises incomplete")
    
    # ============================================================================
    # Test Case 4: No initial facts
    # ============================================================================
    print("\nRunning Test Case 4: No Initial Facts...")
    kb.clear_facts()
    kb.forward_chain()
    
    assert len(kb.facts) == 0, "Test 4 Failed: Should have no facts when starting empty"
    assert 'SafeToEngage' not in kb.facts, "Test 4 Failed: No deductions without premises"
    print("✅ Test Case 4 Passed: No spurious deductions from empty state")
    
    # ============================================================================
    # Test Case 5: Multi-step chaining (2-level inference)
    # ============================================================================
    print("\nRunning Test Case 5: Multi-step Forward Chaining...")
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.tell_fact('BloodseekerMissing')
    
    # Before forward chaining, no derived facts
    assert 'SafeToEngage' not in kb.facts, "Before chaining: SafeToEngage should not exist"
    assert 'Retreat' not in kb.facts, "Before chaining: Retreat should not exist"
    
    kb.forward_chain()
    
    # After forward chaining, both should be derived
    assert 'SafeToEngage' in kb.facts, "Test 5 Failed: Step 1 - Should deduce SafeToEngage"
    assert 'Retreat' in kb.facts, "Test 5 Failed: Step 2 - Should then deduce Retreat"
    print("✅ Test Case 5 Passed: Multi-step chaining works (SafeToEngage → Retreat)")
    
    # ============================================================================
    # Test Case 6: Query functionality
    # ============================================================================
    print("\nRunning Test Case 6: Query Functionality...")
    kb.clear_facts()
    kb.tell_fact('TargetVisible')
    kb.tell_fact('HasDust')
    kb.forward_chain()
    
    assert kb.query('SafeToEngage') == True, "Test 6 Failed: Query should return True for known fact"
    assert kb.query('Retreat') == False, "Test 6 Failed: Query should return False for unknown fact"
    assert kb.query('NonExistentFact') == False, "Test 6 Failed: Query should return False for non-existent fact"
    print("✅ Test Case 6 Passed: Query functionality works correctly")
    
    # ============================================================================
    # Final Summary
    # ============================================================================
    print("\n" + "="*70)
    print("✅ ALL LOGIC ENGINE TEST CASES PASSED!")
    print("="*70)
    print("\nForward Chaining Inference Engine validated successfully.")
    print("The Knowledge Base correctly implements:")
    print("  • Propositional Logic (facts and Horn clauses)")
    print("  • Modus Ponens inference rule")
    print("  • Fixed-point iteration algorithm")
    print("  • Multi-step logical chaining")
    print("\nReady for integration with A* pathfinding!")


if __name__ == "__main__":
    test_forward_chaining()
