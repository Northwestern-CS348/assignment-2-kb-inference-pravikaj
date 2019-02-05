import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        if isinstance(fact_or_rule, Fact):
            """RETRACTS THE FACT"""
            fact_or_rule.asserted = False

            """Checks if we should remove the fact or not based on its supports"""
            self.kb_remove(fact_or_rule)

        if isinstance(fact_or_rule, Rule):
            return False

        
    def kb_remove(self, f_or_r):
        # If fact is not supported (does not matter asserted or not) it is removed
        # If rule is not supported AND not asserted then remove
        if len(f_or_r.supported_by) == 0:
            if isinstance(f_or_r, Fact) or (isinstance(f_or_r, Rule) and f_or_r.asserted is False):
                if isinstance(f_or_r, Fact):
                    self.facts.remove(f_or_r)
                    for sf in f_or_r.supports_facts:
                        for sb in sf.supported_by:  # remove support
                            if f_or_r in sb:
                                sf.supported_by.remove(sb)
                        self.kb_remove(sf)

                if isinstance(f_or_r, Rule):
                    self.rules.remove(f_or_r)
                    for sr in f_or_r.supports_rules:
                        for sb in sr.supported_by:
                            if f_or_r in sb:
                                sr.supported_by.remove(sb)
                        self.kb_remove(sr)





        #
        # remove_f_r = fact_or_rule
        # self.facts.remove(fact_or_rule)
        #
        # if remove_f_r.name == 'fact':
        #     for i, e in remove_f_r.supports_facts:
        #         # REMOVES ALL SUPPORT FROM PREVIOUSLY SUPPORTED FACTS
        #         if e.supported_by[i, 0] == remove_f_r:
        #             e.supported_by.remove(i)
        #
        #         #Now loop through previosuly supported facts to check if they should be retracted or removed
        #         if e.asserted is True & len(e.supported_by) > 0:
        #             self.kb_retract(e)
        #
        #         if len(e.supported_by) == 0:
        #             self.kb_remove(e)
        #
        #     for j, e in remove_f_r.supports_rules:
        #         #REMOVES ALL SUPPORT FROM PREVIOUSLY SUPPORTED RULES
        #         if e.supported_by[i, 0] == remove_f_r:
        #             e.supported_by.remove(j)
        #
        #         # Now loop through previosuly supported facts to check if they should be removed
        #         if e.asserted is False & len(e.supported_by) == 0:
        #             self.kb_remove(e)
        #
        # if remove_f_r.name == 'rule':
        #     if remove_f_r.asserted is False & len(remove_f_r.supported_by)==0:
        #         self.kb_remove(e)




class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        new_lhs = []
        bindings = match(fact.statement, rule.lhs[0])
        if bindings:
            if len(rule.lhs) > 1:
                for i in rule.lhs[1:]:
                    new_lhs.append(instantiate(i, bindings))
                new_rhs = instantiate(rule.rhs, bindings)
                new_rule = Rule([new_lhs, new_rhs], [[fact, rule]])
                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)
                kb.kb_add(new_rule)

            if len(rule.lhs) == 1:
                new_rhs = instantiate(rule.rhs, bindings)
                new_fact = Fact(new_rhs, [[fact, rule]])
                fact.supports_rules.append(new_fact)
                rule.supports_rules.append(new_fact)
                kb.kb_add(new_fact)

