"""
logic_engine.py
Knowledge Base and Forward Chaining Inference Engine for Intelligent Agents
Part 1 & 2: Implementing the Knowledge Base (KB) and Forward Chaining Algorithm
"""


class KnowledgeBase:
    """
    A declarative Knowledge Base that stores facts and rules using propositional logic.
    Uses forward chaining inference to deduce new facts from existing facts and rules.
    
    Attributes:
        facts (set): A set of unique fact strings representing current knowledge
        rules (list): A list of tuples (premises, conclusion) representing Horn clauses
    """
    
    def __init__(self):
        """Initialize an empty Knowledge Base with no facts or rules."""
        self.facts = set()
        self.rules = list()
    
    def tell_fact(self, fact_string: str):
        """
        Add a fact to the Knowledge Base.
        
        Args:
            fact_string (str): A string representing a fact (e.g., 'TargetVisible')
        """
        self.facts.add(fact_string)
    
    def tell_rule(self, premise_list: list, conclusion_string: str):
        """
        Add a rule (Horn Clause) to the Knowledge Base.
        A rule is a tuple of (premises, conclusion) where:
        - premises is a list of fact strings that must ALL be true
        - conclusion is a single fact string that is derived if all premises are true
        
        Example: tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        This creates the rule: TargetVisible ∧ HasDust ⇒ SafeToEngage
        
        Args:
            premise_list (list): List of premise fact strings
            conclusion_string (str): The conclusion fact string
        """
        self.rules.append((premise_list, conclusion_string))
    
    def clear_facts(self):
        """Remove all facts from the Knowledge Base, keeping rules intact."""
        self.facts.clear()
    
    def forward_chain(self):
        """
        Execute forward chaining inference algorithm.
        This is a data-driven approach that iteratively applies rules to known facts
        until no new facts can be deduced (fixed point reached).
        
        Algorithm (Modus Ponens):
        1. Initialize new_facts_added = TRUE
        2. WHILE new_facts_added == TRUE:
           a. Set new_facts_added = FALSE
           b. For each rule (premises, conclusion):
              - If conclusion is NOT already known:
                - If ALL premises are known:
                  - Add conclusion to facts
                  - Set new_facts_added = TRUE
        3. Loop terminates when a full pass produces no new facts (fixed point)
        
        This implements the logical inference rule Modus Ponens:
        If (P1 ∧ P2 ∧ ... ∧ Pn ⇒ Q) and (P1, P2, ..., Pn are all true)
        Then Q must be true.
        """
        new_facts_added = True
        
        while new_facts_added:
            new_facts_added = False
            
            for premises, conclusion in self.rules:
                # Only process if the conclusion hasn't been deduced yet
                if conclusion not in self.facts:
                    # Modus Ponens Check: ALL premises must be in facts
                    if all(premise in self.facts for premise in premises):
                        # All premises satisfied, so conclusion must be true
                        self.facts.add(conclusion)
                        new_facts_added = True
    
    def query(self, fact_string: str) -> bool:
        """
        Query the Knowledge Base to check if a fact is known.
        
        Args:
            fact_string (str): The fact to query for
            
        Returns:
            bool: True if the fact is known, False otherwise
        """
        return fact_string in self.facts
    
    def __str__(self) -> str:
        """String representation of the Knowledge Base state."""
        return f"KnowledgeBase(facts={self.facts}, rules={self.rules})"
