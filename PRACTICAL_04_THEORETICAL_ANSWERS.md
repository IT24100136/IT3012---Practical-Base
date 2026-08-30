"""
PRACTICAL 04 - THEORY-TO-IMPLEMENTATION MAPPING
Part 5: Analytical Questions and Answers
Module: IT3012 Intelligent Agents
"""

# =============================================================================
# Question 1: Reachability vs. Feasibility (Apply)
# =============================================================================

"""
QUESTION 1: Reachability vs. Feasibility (Apply)

In Step 3.2, you modified the A* algorithm's neighbor-generation loop. How does 
your new code differentiate between checking if a node is "Reachable" (like a 
wall collision) versus checking if it is "Feasible"? Explain how the Knowledge 
Base enforces feasibility.

---

ANSWER 1: Reachability vs. Feasibility

The implementation introduces a TWO-LAYER validation system in A* neighbor expansion:

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: REACHABILITY CHECK (Physical Constraints)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Checked FIRST in the neighbor loop:                                         │
│                                                                             │
│  if 0 <= next_x < width and 0 <= next_y < height:                         │
│      if (next_x, next_y) not in walls_set and (next_x, next_y) not in     │
│         reached_states:                                                     │
│          # Node is PHYSICALLY REACHABLE                                    │
│                                                                             │
│ This answers: "Can we move there?" (Collision, boundary checks)            │
│ Outcome: Only REACHABLE nodes proceed to Layer 2                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: FEASIBILITY CHECK (Logical Constraints via Knowledge Base)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ Checked AFTER reachability, before adding to open_list:                    │
│                                                                             │
│  self.kb.clear_facts()                     # Reset for this tile           │
│  self.kb.tell_fact('TargetVisible')        # Feed tile-specific percepts  │
│  self.kb.tell_fact('HasDust')                                             │
│  self.kb.tell_fact('BloodseekerMissing')   # If threats detected          │
│  self.kb.forward_chain()                   # Logical inference            │
│                                                                             │
│  if 'Retreat' in self.kb.facts:            # Safety conclusion             │
│      continue                              # SKIP this tile               │
│                                                                             │
│ This answers: "Should we move there?" (Safety, game rules)                │
│ Outcome: REACHABLE nodes become FEASIBLE only if 'Retreat' NOT deduced   │
└─────────────────────────────────────────────────────────────────────────────┘

KEY DIFFERENCE:

┌──────────────────────────────────────────────────────────────────────────┐
│  REACHABILITY:  Can the agent's body move to this tile?                  │
│  └─ Determined by: Physics (walls, boundaries), geometry                │
│  └─ Checked by: Boundary and wall collision logic                       │
│  └─ Data type: Boolean from set membership tests                        │
│                                                                           │
│  FEASIBILITY:   Should the agent's mind move to this tile?              │
│  └─ Determined by: Safety rules, game logic, tactical intelligence      │
│  └─ Checked by: Forward Chaining inference engine                       │
│  └─ Data type: Boolean from logical deduction ('Retreat' in facts)      │
└──────────────────────────────────────────────────────────────────────────┘

PRACTICAL EXAMPLE:

Scenario: Agent at (2,2), goal at (3,3), neighbor (3,2) is physically adjacent.

Case A - REACHABLE but NOT FEASIBLE:
  ✓ (3,2) is within grid boundaries     → REACHABLE
  ✓ (3,2) has no wall                   → REACHABLE
  ✗ KB deduces 'Retreat' (Bloodseeker threat)  → NOT FEASIBLE
  → A* SKIPS this tile (even though you could move there)

Case B - REACHABLE AND FEASIBLE:
  ✓ (3,2) is within grid boundaries     → REACHABLE
  ✓ (3,2) has no wall                   → REACHABLE
  ✓ KB does NOT deduce 'Retreat'        → FEASIBLE
  → A* ADDS this tile to open_list

HOW THE KNOWLEDGE BASE ENFORCES FEASIBILITY:

The KB enforces feasibility through PROPOSITIONAL LOGIC and the MODUS PONENS 
inference rule:

  Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
  Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat

When facts are fed into the KB for a specific tile:
  • If TargetVisible AND HasDust are both true → SafeToEngage is DEDUCED
  • If SafeToEngage AND BloodseekerMissing are both true → Retreat is DEDUCED
  
If 'Retreat' is deduced, the tile fails the feasibility check, regardless of 
physical reachability.

This creates a TWO-LEVEL DECISION TREE:

                     ┌─────────────┐
                     │  Neighbor   │
                     │    Tile     │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │  Reachable? │ (Physics)
                     └──────┬──────┘
                    Yes  /      \  No
                        /        \
                   ┌───▼─────┐   SKIP
                   │ Feasible?│ (Logic)
                   └───┬─────┘
                  Yes / \ No
                     /   \
                  ADD    SKIP
                to PQ
"""

# =============================================================================
# Question 2: Declarative vs. Procedural Paradigms (Analyze)
# =============================================================================

"""
QUESTION 2: Declarative vs. Procedural Paradigms (Analyze)

Why did we build a KnowledgeBase class with a forward_chain() loop instead 
of simply writing if 'TargetVisible' in percepts and 'HasDust' in 
percepts: directly inside the agent's movement code? What happens to the 
agent's code complexity if we add 50 new game rules?

---

ANSWER 2: Declarative vs. Procedural Paradigms

PROCEDURAL APPROACH (What We Avoided):
────────────────────────────────────────────

Hardcoding conditions directly in the agent:

    def sense_and_act(self, percept):
        if percept['TargetVisible'] and percept['HasDust']:
            return 'Engage'
        
        if percept['Engagement'] and percept['BloodseekerMissing']:
            return 'Retreat'
        
        if percept['Engagement'] and percept['AllyNearby']:
            return 'Hold'
        
        # ... 47 more rules ...
        
        if percept['Rule47Condition1'] and percept['Rule47Condition2']:
            return 'Action47'
        
        return 'DefaultAction'

PROBLEMS with procedural approach:
  ✗ Code becomes UNREADABLE (47 nested if-statements = spaghetti logic)
  ✗ Hard to MODIFY (changing Rule 10 requires finding it in the mess)
  ✗ Easy to CREATE BUGS (edge cases, interaction effects)
  ✗ No SEPARATION OF CONCERNS (logic mixed with execution)
  ✗ UNMAINTAINABLE (future developers need code archaeology)

---

DECLARATIVE APPROACH (What We Implemented):
──────────────────────────────────────────────

Separating DATA (facts/rules) from LOGIC (inference engine):

    def __init__(self):
        self.kb = KnowledgeBase()
        
        # DECLARE rules once, as data
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')
        self.kb.tell_rule(['SafeToEngage', 'AllyNearby'], 'Hold')
        # ... 47 more rules ...
    
    def sense_and_act(self, percept):
        # Feed facts once
        self.kb.clear_facts()
        self.kb.tell_fact('TargetVisible')
        self.kb.tell_fact('HasDust')
        # ...
        
        # Apply inference engine (same for ALL domains)
        self.kb.forward_chain()
        
        # Query result
        if self.kb.query('Retreat'):
            return 'Retreat'

ADVANTAGES of declarative approach:
  ✓ Code is READABLE (rules are just data, clearly separated from inference)
  ✓ Easy to MODIFY (add/remove rules without touching inference logic)
  ✓ Reduces BUGS (inference engine is generic, tested once)
  ✓ SEPARATION OF CONCERNS (domain knowledge ≠ reasoning mechanism)
  ✓ REUSABLE (same engine works for ANY propositional logic domain)

---

COMPLEXITY ANALYSIS: 50 NEW RULES
──────────────────────────────────

PROCEDURAL COMPLEXITY (Direct if-statements):
┌────────────────────────────────────────────────────────────────────┐
│ O(n) rules → O(n) nested if-statements in code                    │
│                                                                    │
│ 2 rules:   ~20 lines, 1 level of nesting (READABLE)              │
│ 10 rules:  ~100 lines, 4 levels of nesting (HARD TO READ)        │
│ 50 rules:  ~500 lines, 8 levels of nesting (UNMAINTAINABLE) ❌   │
│                                                                    │
│ CYCLOMATIC COMPLEXITY = 50 (extremely high - difficult to test)  │
│ CODE MODIFICATIONS required in 3-5 different places               │
│ RISK OF BREAKING EXISTING LOGIC = VERY HIGH                      │
└────────────────────────────────────────────────────────────────────┘

DECLARATIVE COMPLEXITY (Knowledge Base):
┌────────────────────────────────────────────────────────────────────┐
│ O(n) rules → O(n) tell_rule() calls in __init__                  │
│                                                                    │
│ 2 rules:   2 tell_rule() calls  (CLEAR)                          │
│ 10 rules:  10 tell_rule() calls (VERY CLEAR)                     │
│ 50 rules:  50 tell_rule() calls (STILL VERY CLEAR) ✓             │
│                                                                    │
│ AGENT CODE STAYS THE SAME (sense_and_act is unchanged)           │
│ CYCLOMATIC COMPLEXITY = 1 (forward_chain() is tested once)        │
│ CODE MODIFICATIONS: Only add rules, never modify engine           │
│ RISK OF BREAKING EXISTING LOGIC = VERY LOW                       │
└────────────────────────────────────────────────────────────────────┘

VISUAL COMPARISON:

Procedural (50 rules):
    
    def sense_and_act(self):
        if cond1 and cond2:
            if cond3:
                if cond4:
                    if cond5:
                        if ... (deeply nested, impossible to follow)
                        return action5
    
    Lines of code: ~500+
    Nesting depth: 8+
    Cyclomatic complexity: 50+
    Maintenance cost: EXPONENTIAL

Declarative (50 rules):

    def __init__(self):
        # 50 simple tell_rule() calls
        for rule in domain_rules:
            self.kb.tell_rule(rule['premises'], rule['conclusion'])
    
    def sense_and_act(self):
        self.kb.clear_facts()
        for fact in percept:
            self.kb.tell_fact(fact)
        self.kb.forward_chain()
        return query_result(self.kb)
    
    Lines of code: ~20
    Nesting depth: 1
    Cyclomatic complexity: 1
    Maintenance cost: CONSTANT

---

WHAT HAPPENS WHEN WE ADD 50 NEW RULES:

Procedural Approach:
    1. Add 50 new if-statements to sense_and_act()
    2. Risk: Accidentally change indentation → bugs
    3. Risk: Interaction with existing 2 rules → unpredictable behavior
    4. Testing: Need to test all 2^50 combinations (impossible)
    5. Developer sanity: ❌

Declarative Approach:
    1. Add 50 new tell_rule() calls to __init__()
    2. Risk: Minimal (each rule is isolated)
    3. Risk: Forward chaining handles all interactions automatically
    4. Testing: Test forward_chain() ONCE, then add rules freely
    5. Developer sanity: ✓

---

CONCLUSION: Separation of Knowledge from Reasoning

By using a declarative Knowledge Base:
  • The INFERENCE ENGINE (forward_chain) is generic and reusable
  • The DOMAIN KNOWLEDGE (rules) is data, not code
  • Adding 50 rules is TRIVIAL (50 more data entries)
  • The agent code remains UNCHANGED and CLEAN
  • Maintenance complexity becomes LINEAR instead of EXPONENTIAL
  
This is the fundamental principle behind Expert Systems, which handle domains 
with THOUSANDS of rules using the same forward-chaining engine.

Architecture Summary:
┌─────────────────────────────────────────────────────────────────────────┐
│                   AGENT (remains simple)                               │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ sense_and_act():                                               │   │
│  │   - Query KB for decisions                                     │   │
│  │   - NO rule logic here                                         │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                              ↑                                         │
│                    (queries for decisions)                            │
│                              │                                        │
├──────────────────────────────┼──────────────────────────────────────┤
│                              │                                        │
│                 KNOWLEDGE BASE + INFERENCE ENGINE                    │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ Rules (Data):                                                  │   │
│  │   - Rule 1: P₁ ∧ P₂ ⇒ Q₁                                       │   │
│  │   - Rule 2: Q₁ ∧ P₃ ⇒ Q₂                                       │   │
│  │   - ... (50 more rules as data)                                │   │
│  │                                                                │   │
│  │ Inference (Logic):                                            │   │
│  │   - forward_chain() applies Modus Ponens uniformly            │   │
│  │   - No rule-specific code                                     │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Result: Code complexity stays O(1) while knowledge grows to O(n).
"""

# =============================================================================
# Question 3: Modus Ponens & Horn Clauses (Understand)
# =============================================================================

"""
QUESTION 3: Modus Ponens & Horn Clauses (Understand)

The rule ['TargetVisible', 'HasDust'] ⇒ 'SafeToEngage' is formally known 
as a Horn Clause. Briefly explain how your Python implementation of the 
forward_chain() while loop acts as a mathematical execution of the Modus 
Ponens inference rule.

---

ANSWER 3: Modus Ponens & Horn Clauses

MODUS PONENS (Logical Inference Rule):
──────────────────────────────────────

Definition: If we know that "P implies Q" (P → Q) and we know that "P is true",
then we can DEDUCE that "Q must be true".

Formal notation:
    P → Q      (Major premise: "If P then Q")
    P          (Minor premise: "P is true")
    ─────      
    ∴ Q        (Conclusion: "Therefore Q is true")

Example in our domain:
    TargetVisible ∧ HasDust → SafeToEngage  (Rule)
    TargetVisible ∧ HasDust                 (Facts)
    ─────────────────────────────────────────
    ∴ SafeToEngage                          (Deduced)

---

HORN CLAUSE:
────────────

A Horn Clause is a disjunction (OR) of literals where AT MOST ONE is positive:
    ¬P₁ ∨ ¬P₂ ∨ ¬P₃ ∨ Q

Which is logically equivalent to the implication:
    P₁ ∧ P₂ ∧ P₃ → Q

Horn Clauses are the basis of logic programming (Prolog, our forward chaining):
  • Premises (P₁, P₂, P₃): Conjunction of antecedents (AND)
  • Conclusion (Q): Single consequent
  • Implication: All premises must be true for conclusion to follow

Our rule in Horn Clause form:
    tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
    
    Implication: TargetVisible ∧ HasDust → SafeToEngage
    Disjunctive: ¬TargetVisible ∨ ¬HasDust ∨ SafeToEngage

---

FORWARD CHAINING AS MODUS PONENS EXECUTION:
─────────────────────────────────────────────

The forward_chain() method IS the algorithmic implementation of Modus Ponens.

Here's the code with Modus Ponens annotations:

    def forward_chain(self):
        new_facts_added = True
        
        while new_facts_added:
            new_facts_added = False
            
            for premises, conclusion in self.rules:  # For each rule (Horn Clause)
                if conclusion not in self.facts:     # If Q not already known
                    
                    # MODUS PONENS CHECK:
                    if all(premise in self.facts for premise in premises):
                        #     ▲ Check ALL premises are true
                        #     └─ This is the MODUS PONENS condition
                        #
                        # If we reach here:
                        #   P₁ ∧ P₂ ∧ ... ∧ Pₙ are ALL in facts (premises are true)
                        #   P₁ ∧ P₂ ∧ ... ∧ Pₙ → Q is a rule (implication exists)
                        #   Therefore, by Modus Ponens: Q MUST BE TRUE
                        
                        self.facts.add(conclusion)
                        #   ▲ Deduce Q (conclusion)
                        
                        new_facts_added = True
                        #   ▲ Flag that new knowledge was derived

STEP-BY-STEP EXECUTION OF MODUS PONENS:
─────────────────────────────────────────

Iteration 1:
  Facts: {TargetVisible, HasDust}
  Rule:  ['TargetVisible', 'HasDust'] → 'SafeToEngage'
  
  CHECK:  all([TargetVisible ∈ facts, HasDust ∈ facts])
  RESULT: TRUE
  ACTION: Add 'SafeToEngage' to facts
  
  Facts NOW: {TargetVisible, HasDust, SafeToEngage}
  
  ✓ MODUS PONENS APPLIED:
    - Major premise: TargetVisible ∧ HasDust → SafeToEngage
    - Minor premise: TargetVisible and HasDust are in facts
    - Conclusion: SafeToEngage is deduced

Iteration 2 (if BloodseekerMissing is a fact):
  Facts: {TargetVisible, HasDust, SafeToEngage, BloodseekerMissing}
  Rule:  ['SafeToEngage', 'BloodseekerMissing'] → 'Retreat'
  
  CHECK:  all([SafeToEngage ∈ facts, BloodseekerMissing ∈ facts])
  RESULT: TRUE
  ACTION: Add 'Retreat' to facts
  
  Facts NOW: {TargetVisible, HasDust, SafeToEngage, BloodseekerMissing, Retreat}
  
  ✓ MODUS PONENS APPLIED AGAIN:
    - Major premise: SafeToEngage ∧ BloodseekerMissing → Retreat
    - Minor premise: SafeToEngage and BloodseekerMissing are in facts
    - Conclusion: Retreat is deduced

---

HOW THE WHILE LOOP IMPLEMENTS COMPLETENESS:
─────────────────────────────────────────────

The outer while loop ensures we reach the FIXED POINT (no new derivations):

    PASS 1: Apply Modus Ponens once to all rules
            ✓ SafeToEngage deduced
            new_facts_added = TRUE → Continue

    PASS 2: Apply Modus Ponens again (now SafeToEngage is available)
            ✓ Retreat deduced (using newly derived SafeToEngage)
            new_facts_added = TRUE → Continue

    PASS 3: Apply Modus Ponens again
            ✗ No new conclusions possible
            new_facts_added = FALSE → EXIT

Result: ALL possible logical consequences have been computed.

This implements the CLOSED WORLD ASSUMPTION: If a fact cannot be deduced 
from the KB, it is assumed to be FALSE.

---

FORMAL PROOF OF CORRECTNESS:
─────────────────────────────

Claim: forward_chain() computes exactly the logical closure of the KB.

Proof by induction on number of derivation steps:

Base case (k=0):
  - Facts = explicitly told facts
  - No rules can apply yet
  - True by definition

Inductive step (assume k → k+1):
  - At iteration k, some fact Q is deduced via Modus Ponens
  - By definition of Modus Ponens: Q logically follows from premises
  - At iteration k+1, Q is in facts, enabling further derivations
  - All subsequent derivations are valid by Modus Ponens
  
Termination:
  - Facts can only grow (monotonic)
  - Finite set of possible facts (bounded)
  - Eventually no new facts can be added
  - Loop terminates with complete closure

∴ forward_chain() is a complete, correct implementation of logical closure 
  using Modus Ponens.

---

COMPARISON: MODUS PONENS vs FORWARD CHAINING
─────────────────────────────────────────────

Modus Ponens (Logical Principle):
  • A single inference step
  • Applied manually by a logician
  • One fact deduced at a time
  • Must track what you've tried
  
Forward Chaining (Algorithmic Implementation):
  • Automated Modus Ponens
  • Applied repeatedly by a computer
  • Multiple facts deduced per iteration
  • Automatically tracks fixed point
  • Scales to thousands of rules

Our code makes this explicit:

    # Line-by-line Modus Ponens application:
    if all(premise in self.facts for premise in premises):
        #   ▲ Premises are true (Minor premise of Modus Ponens)
        #   ▲ Rule exists (Major premise of Modus Ponens)
        
        self.facts.add(conclusion)
        #   ▲ Therefore conclusion is true (Modus Ponens conclusion)

The while loop automates this for ALL rules and ALL iterations:
  • First while loop: Tries to find ANY rule that applies
  • Inner for loop: Tests each rule
  • If line: Checks Modus Ponens condition
  • All() function: Verifies ALL premises (AND operation)
  • Repeat: Until no new facts (fixed point)

---

CONCLUSION:

forward_chain() is not just inspired by Modus Ponens—it IS Modus Ponens
executed algorithmically and iteratively on a set of Horn Clauses until
all logical consequences are derived.

This single method implements:
  ✓ The Modus Ponens inference rule
  ✓ Automated logical reasoning
  ✓ The fixed-point algorithm for logical closure
  ✓ The basis of inference engines used in Expert Systems worldwide
"""

# =============================================================================
# IMPLEMENTATION SUMMARY
# =============================================================================

"""
SUMMARY: Theory to Implementation in Practical 04

Three Layers of Integration:

1. LOGICAL LAYER (logic_engine.py):
   - KnowledgeBase: Data structure for facts and rules
   - forward_chain(): Algorithm implementing Modus Ponens
   - Result: Automated logical reasoning system

2. ALGORITHMIC LAYER (Modified agent.py):
   - Separation of Reachability (physics) from Feasibility (logic)
   - A* integrates KB consultation for safety checking
   - Result: Intelligent pathfinding that respects game rules

3. THEORETICAL LAYER (This document):
   - Reachability vs Feasibility: Two-layer decision making
   - Declarative vs Procedural: Separation of knowledge from reasoning
   - Modus Ponens & Horn Clauses: Mathematical foundation of inference
   - Result: Understanding why this architecture is superior

The implementation demonstrates:
  ✓ Propositional Logic in code (facts, rules)
  ✓ Inference algorithms (forward chaining)
  ✓ Search integration (A* + KB)
  ✓ Software engineering principles (separation of concerns)
  ✓ Scalability (adding rules doesn't break the system)
  ✓ Maintainability (clean, testable architecture)

This is the foundation of Knowledge Representation and Reasoning in AI.
"""
