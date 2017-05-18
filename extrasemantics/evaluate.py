"""
Model of IDPL
"""

import collections
from itertools import chain, combinations, product

import nltk as nltk
from nltk.sem import (Valuation, Undefined)
from extrasemantics.expressions import (AbstractVariableExpression, AllExpression, BangExpression, Expression, EqualityExpression,
                            AndExpression, ApplicationExpression,
                            ExistsExpression, ImpExpression,
                            NegatedExpression, OrExpression, QuestionExpression, ExhExpression)

class Assignment(nltk.Assignment):
    """
    An assignment in CorMod can be seen as a special type of dictionary:\
            one that assigns entities to numbers (pegs).
    """

    def __init__(self, values=None):
        if values:
            assign = [("".join(["p", str(i)]), j) for i, j in enumerate(values)]
            domain = list(values)
            self.values = list(values)
        else:
            assign = None
            domain = list()
            self.values = []
        super(Assignment, self).__init__(domain=domain, assign=assign)

    def add(self, value, peg=None):
        """
        Add a new value to Assignment. The original assignment cannot be changed, but a new assignment is created with the new value.
        If peg specified, the value will be added at a particular peg. peg appears either as a number or a string "p+number"
        """
        temp_values = list(self.values)
        if peg:
            try:
                temp_values.insert(peg, value)
            except TypeError:
                temp_values.insert(int(peg[1:]), value)
        else:
            temp_values.append(value)
        new_assignment = Assignment(temp_values)
        return new_assignment

    def copy(self):
        """
        Copying an assignment -- this raises an error because Assignments are immutable, so there is no need for copying.
        """
        raise AttributeError("Assignment is immutable so there is no need to copy it.")

    def purge(self, var=None):
        """
        Return Assignment with one or all keys deleted. The latter option is used if no var is specified.
        """
        temp_values = list(self.values)
        if var:
            try:
                temp_values.pop(var)
            except TypeError:
                temp_values.pop(int(var[1:]))
            new_assignment = Assignment(list(temp_values))
            return new_assignment
        else:
            return Assignment()


class ReferentSystem(nltk.Assignment):
    """
    A referent system in CorMod can be seen as a special type of dictionary:\
            one that has variables as its domain and pegs as its range.
    """

    def __init__(self, variables=None):
        if variables:
            assign = [(j, "".join(["p", str(i)])) for i, j in enumerate(variables)]
            domain = set([x[1] for x in assign])
            self.variables = list(variables)
        else:
            assign = None
            domain = set()
            self.variables = []
        super(ReferentSystem, self).__init__(domain=domain, assign=assign)

    def add(self, variable):
        """
        Add a new value to Referent System. The original referent system cannot be changed, but a new one is created with the new value.
        """
        temp_variables = list(self.variables)
        temp_variables.append(variable)
        new_referentsystem = ReferentSystem(temp_variables)
        return new_referentsystem

    def copy(self):
        """
        Copying a referent system -- this raises an error because Referent Systems are immutable, so there is no need for copying.
        """
        raise AttributeError("Referent System is immutable so there is no need to copy it.")

    def purge(self, var=None):
        """
        Return ReferentSystem with one or all keys deleted. The latter option is used if no var is specified.
        """
        if var:
            self.variables.remove(var)
            new_referentsystem = ReferentSystem(list(self.variables))
            return new_referentsystem
        else:
            return ReferentSystem()

class World(nltk.Model):
    """
    World is a valuation, domain pair.
    """
    def __init__(self, valuation, domain=None):
        if not domain:
            domain = set(valuation.keys())
        super(World, self).__init__(domain=domain, valuation=valuation)

class Possibility(collections.Sequence):
    """

    :type possibilities: list of triples [r, g, w], where:
    r -- ReferentSystem
    g -- Assignment
    w -- World

    """

    def __init__(self, referentsystem, assignment, world):
        if not isinstance(referentsystem, ReferentSystem):
            raise TypeError("The first argument of a possibility has to be a ReferentSystem")
        if not isinstance(assignment, Assignment):
            raise TypeError("The 2nd argument of a possibility has to be an Assignment")
        if not isinstance(world, World):
            raise TypeError("The last argument of a possibility has to be a World")
        self.referentsystem = referentsystem
        self.assignment = assignment
        self.world = world

    def __hash__(self):
        #hash referent system items, assignment items, valuation items
        return hash(tuple([frozenset(self.referentsystem.items()), frozenset(self.assignment.items()), frozenset((x[0], frozenset(x[1])) for x in self.world.valuation.items())]))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __getitem__(self, item):
        if item == 0:
            return self.referentsystem
        if item == 1:
            return self.assignment
        if item == 2:
            return self.world

    def __len__(self):
        return 3

    def __le__(self, other):
        return self == other or self < other

    def __lt__(self, other):
        #self.referentsystem and self.assignment must be subsets of the other r and g
        if frozenset(self.referentsystem.items()).issubset(frozenset(other.referentsystem.items())) and frozenset(self.assignment.items()).issubset(frozenset(other.assignment.items())):
            #worlds must be identical
            if frozenset((x[0], frozenset(x[1])) for x in self.world.valuation.items()) == frozenset((x[0], frozenset(x[1])) for x in other.world.valuation.items()) and self != other:
                return True
        return False

    def __repr__(self):
        vals = " "
        for x in self.referentsystem:
            try:
                vals = " ".join([vals, "->".join([x, self.assignment[self.referentsystem[x]]])])
            except nltk.Undefined:
                vals = " ".join([vals])
        return " ".join([vals, "w:", repr(self.world.valuation), "\n"])

    def subsists(self, informationstate):
        """
        Check whether the possibility subsists in information state s.
        This happens if for some possibility i in s, self <= i.
        Return the subsisted possibilities.
        """
        subsisted_possibilities = set()
        for possibility in informationstate:
            if self <= possibility:
                subsisted_possibilities.add(possibility)
        return subsisted_possibilities

class InformationState(collections.Set):
    """
    Information state is a set of possibilities, where a possibility -- <r, g, w>;\
            information state has the same referent system in all its possibilities.

    :type domain: set
    :param domain: A set of entities representing the domain of discourse of the information state.

    possibilities: triples [r, g, w], where:
    r -- ReferentSystem
    g -- Assignment
    w -- World/Valuation

    """

    def __init__(self, domain, possibilities):
        assert len(set([tuple(x[0]) for x in possibilities])) <= 1,\
                "Referent systems are not identical in all possibilities of one information state"
        self.referentsystem = None
        self.possibilities = set()
        self.domain = domain
        worlds = set()
        #below -- run type checks & add each possibility into self.possibilities
        for possibility in possibilities:
            if not self.referentsystem:
                self.referentsystem = possibility[0]
            if not isinstance(possibility, collections.Iterable) or not len(possibility) == 3:
                raise TypeError("Possibilities added to Information State must be iterables of length 3.")
            assignment = possibility[1]
            if isinstance(possibility[2], Valuation):
                world = World(possibility[2], self.domain)
            elif isinstance(possibility[2], World):
                if possibility[2].domain == self.domain:
                    world = possibility[2]
                else:
                    raise ValueError("The domains of different worlds within one information state do not match")
            worlds.add(world)
            poss = Possibility(self.referentsystem, assignment, world)
            self.possibilities.add(poss)
        self.worlds = frozenset(worlds)
        self.possibilities = frozenset(self.possibilities)

    def __contains__(self, item):
        if not isinstance(item, collections.Iterable) or not len(item) == 3:
            raise TypeError("Possibilities in Information State must be iterables of length 3")
        return item[0] == self.referentsystem and Possibility(item[0], item[1], item[2]) in self.possibilities

    def __hash__(self):
        return hash(self.possibilities)

    def __iter__(self):
        for elem in self.possibilities:
            yield elem

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(self.possibilities)

    def __le__(self, other):
        return self == other or self < other

    def __lt__(self, other):
        if self == other:
            return False
        for poss2 in other:
            for poss in self:
                if poss <= poss2:
                    break
            else:
                return False
        return True
    
    def __repr__(self):
        if not self.referentsystem:
            string = ""
        else:
            string = "{"
        for poss in self.possibilities:
            poss_string = repr(poss)
            string = " ".join([string, poss_string])
        if self.referentsystem:
            string = "".join([string, "}"])
        return string

    def expand(self, possibility):
        """
        Create a new information state with a new possibility added to the new information state.
        :type possibilities: list of triples [r, g, w], where:
        r -- ReferentSystem
        g -- Assignment
        w -- World/Valuation
        The original information state is not changed.
        """
        poss_list = []
        for each in self.possibilities:
            poss_list.append([each.referentsystem, each.assignment, each.world])
        poss_list.append(possibility)
        return InformationState(self.domain, poss_list)

    def issubset(self, other):
        """
        Check that one state is subset of another.
        """
        return self.possibilities.issubset(other.possibilities)

    def shrink(self, possibility):
        """
        Create a new information state with one possibility removed. If the possibility is not present, nothing is changed.

        :type possibilities: list of triples [r, g, w], where:
        r -- ReferentSystem
        g -- Assignment
        w -- World/Valuation

        The original information state is not changed.
        """
        #change Valuation into World
        if isinstance(possibility[2], Valuation):
            possibility[2] = World(possibility[2], self.domain)
        elif isinstance(possibility[2], World):
            if possibility[2].domain == self.domain:
                pass
            else:
                raise ValueError("The domains of different worlds within one information state do not match")
        possibility = Possibility(possibility[0], possibility[1], possibility[2])
        poss_list = []
        for each in self.possibilities:
            if not possibility == each:
                poss_list.append([each.referentsystem, each.assignment, each.world])
        return InformationState(self.domain, poss_list)

    def subsists(self, element):
        """
        Check whether the information state subsists in information state s or inquisitive state S.
        For information state: this happens if for every possibility i in self, i subsists in s.
        For inquisitive state: this happens if self subsists in one or more s in S.
        For inquisitive state: return the subsisted possibilities.
        """
        if isinstance(element, InformationState):
            for possibility in self:
                if not possibility.subsists(element):
                    return False
            return True
        elif isinstance(element, DynamicInquisitiveState):
            subsisted_infostates = set()
            for info in element:
                if self.subsists(info):
                    subsisted_infostates.add(info)
            return subsisted_infostates
        else:
            raise TypeError("Subsisting is checked on wrong types! Only InformationState and DynamicInquisitiveState can be used.")

    def yieldsubsets(self, emptyset_included=True):
        """
        Yield all subsets of an info state.
        """
        for elem in chain.from_iterable(combinations(self.possibilities, r) for r in range(len(self.possibilities)+1)):
            info = InformationState(self.domain, [[poss.referentsystem, poss.assignment, poss.world] for poss in elem])
            if emptyset_included:
                yield info
            elif info:
                yield info

    def evaluate(self, expr):
        """
        Read input expressions, and provide a handler for ``satisfy``
        that blocks further propagation of the ``Undefined`` error.
        :param expr: An ``Expression`` of ``logic``.
        """
        try:
            parsed = Expression.fromstring(expr)
            return self.satisfy(parsed)
        except Undefined:
            return 'Undefined'
            #raise TypeError("Undefined")

    def satisfy(self, parsed):
        """
        Recursive interpretation function for a formula of CorMod (DPL).

        Raises an ``Undefined`` error when ``parsed`` is an atomic string
        but is not a symbol or an individual variable.

        :return: Returns a new model (sets of possibilities).
        
        :param parsed: An expression of ``logic``.
        """

        if isinstance(parsed, ApplicationExpression):
            function, arguments = parsed.uncurry()
            if isinstance(function, AbstractVariableExpression):
                #It's a predicate expression ("P(x,y)"), so used uncurried arguments
                #check each infostate, if there is any possibility that's not satisfied, delete the whole info state -- the check is done by possibility.world.satisfy (defined in nltk.sem.Model)
                possibilities = [[p.referentsystem, p.assignment, p.world] for p in self if p.world.satisfy(parsed, nltk.Assignment(p.assignment.domain, [(x, p.assignment[p.referentsystem[x]]) for x in p.referentsystem]))] #set comprehension to match conditions written out in dpl/cormod -- possibilities for which the condition holds are kept
                return InformationState(self.domain, possibilities)

        elif isinstance(parsed, AndExpression):
            return self.satisfy(parsed.first).satisfy(parsed.second)

        elif isinstance(parsed, NegatedExpression):
            pos_possibilities = self.satisfy(parsed.term)
            neg_possibilities = [[p.referentsystem, p.assignment, p.world] for p in self if not p.subsists(pos_possibilities)]
            return InformationState(self.domain, neg_possibilities)

        elif isinstance(parsed, ExistsExpression):
            temp_referentsystem = self.referentsystem.add(parsed.variable.name) #1 rs, so this can be stated just once
            possibilities = []
            #for each indiv add all possibilities in which that individual is added
            for indiv in self.domain:
                possibilities += [[temp_referentsystem, poss.assignment.add(indiv), poss.world] for poss in self]
            temp_infostate = InformationState(self.domain, possibilities)
            return temp_infostate.satisfy(parsed.term)

        elif isinstance(parsed, OrExpression):
            possibilities = [[p.referentsystem, p.assignment, p.world] for p in self if p.subsists(self.satisfy(parsed.first)) or p.subsists(self.satisfy(NegatedExpression(parsed.first)).satisfy(parsed.second))]
            return InformationState(self.domain, possibilities)

        elif isinstance(parsed, ImpExpression):
            if_possibilities = set([poss for poss in self if all(x.subsists(self.satisfy(parsed.first).satisfy(parsed.second)) for x in poss.subsists(self.satisfy(parsed.first)))])
            return InformationState(self.domain, if_possibilities)

        elif isinstance(parsed, AllExpression):
            temp_referentsystem = self.referentsystem.add(parsed.variable.name) #1 rs, so this can be stated just once
            possibilities = set([poss for poss in self if all(poss.subsists(InformationState(self.domain, [[temp_referentsystem, p.assignment.add(indiv), p.world] for p in self]).satisfy(parsed.term)) for indiv in self.domain)])
            return InformationState(self.domain, possibilities)

class DynamicInquisitiveState(collections.MutableSet):
    """
    Dynamic Inquisitive state is a downward-closed set of information states.

    You may specify just the maximal elements (alternatives), initialization will take care of the downward-closed property. If you want to specify every infostate, set only_maximal=False.

    You have to specify a set/list of infostates. Each infostate is a set of triples:
    [r, g, w]

    referentsystem and domain are normally taken from infostates (referentystem is present as the first argument, domain is in world). However, you can specify both elements when initializing the dynamic inq state.
    """
    
    def __init__(self, infostates, only_maximal=True, referentsystem=None, domain=None):
        assert  isinstance(infostates, collections.Iterable), "The argument infostates has to be an iterable"
        self.infostates = set()
        if not domain:
            domain = set()
        for info in infostates:
            if info and referentsystem and referentsystem != info.referentsystem:
                raise ValueError("Referent systems in different information states are not identical. This is not allowed.")
            if referentsystem and info.referentsystem and info.referentsystem != referentsystem:
                raise ValueError("Referent systems in different information states are not identical. This is not allowed.")
            if info.referentsystem:
                referentsystem = info.referentsystem
            if domain and domain != info.domain:
                raise ValueError("Domains in different information states are not identical. This is not allowed.")
            if not domain:
                domain = info.domain
            if only_maximal:
                subinfostates = []
                for elem in info.yieldsubsets():
                    self.add(elem)
                    subinfostates.append(elem)
            else:
                temp_info = InformationState(domain, [[poss.referentsystem, poss.assignment, poss.world] for poss in info])
                #self.infostates.add(temp_info)
                self.add(temp_info)

        self.domain = domain #the same individuals in all worlds, so we can have one domain as an attribute of the whole inqstate
        self.referentsystem = referentsystem #one referent system

    def __contains__(self, item):
        return item in self.infostates

    def __eq__(self, other):
        return self.infostates == other.infostates

    def __le__(self, other):
        return self == other or self < other

    def __lt__(self, other):
        for info2 in other:
            for info in self:
                if info <= info2:
                    break
            else:
                return False
        return True
    
    def __iter__(self):
        for item in self.infostates:
            yield item

    def __len__(self):
        return len(self.infostates)

    def __repr__(self):
        maximal_infostates = self.find_maximal()
        #print max_info
        string = "Only maximal elements (alternatives) printed:"
        for subinfostate in maximal_infostates:
            if subinfostate:
                string = "\n".join([string, "Alternative:", repr(subinfostate)])
            else:
                string = "\n".join([string,"{}"])
        return string

    def add(self, infostate, check_maximal=False):
        """
        Add an infostate. check_maximal -- find whether the added element changes what maximal infostates (alternatives) there are.
        """
        self.infostates.add(infostate)
        #if check_maximal:
        #    temp_set = self.maximal_infostates.copy()
        #    if not temp_set:
        #        self.maximal_infostates.add(infostate)
        #    for subinfostate in temp_set:
        #        if subinfostate in set(infostate.yieldsubsets()): 
        #           self.maximal_infostates.remove(subinfostate)
        #            self.maximal_infostates.add(infostate)
        #    temp_set = self.maximal_infostates.copy()
        #    for subinfostate in temp_set:
        #        if subinfostate <= infostate:
        #            break
        #    else:
        #        self.maximal_infostates.add(infostate)

    def copy(self):
        """
        Copy DynamicInquisitiveState.
        """
        return DynamicInquisitiveState(self.infostates, only_maximal=False)

    def discard(self, infostate):
        """
        Discards an infostate.
        """
        self.infostates.discard(infostate)
        #self.maximal_infostates.discard(infostate)

    def find_maximal(self):
        """
        Find maximal elements in InqState.
        """
        #find maximal elements
        maximal_infostates = set()
        for infostate in self.infostates:
            temp_set = maximal_infostates.copy()
            if not temp_set:
                maximal_infostates.add(infostate)
                continue
            for subinfostate in temp_set:
                if subinfostate in set(infostate.yieldsubsets()): 
                    maximal_infostates.remove(subinfostate)
                    maximal_infostates.add(infostate)
            temp_set = maximal_infostates.copy()
            for subinfostate in temp_set:
                if subinfostate <= infostate:
                    break
            else:
                maximal_infostates.add(infostate)

        #a sanity check that infostates match maximal_infostates in expected length
        testing_set = set()
        for info in maximal_infostates:
            for elem in chain.from_iterable(combinations(info, r) for r in range(len(info)+1)):
                test_d = {}
                for i in range(len(elem)):
                    test_d.setdefault(tuple(elem[i].assignment.items()), set()).add(elem[i].world)

                test = set()
                for i in test_d.values():
                    if test and test != i:
                        break
                    elif not test:
                        test = i
                else:
                    elem = frozenset(elem)
                    testing_set.add(elem)

                    if elem not in self:
                        raise AttributeError("There is something wrong in the attribute infostates and maximal_infostates. The following element should be but is not present in infostates. %s" % str(elem))

        if len(testing_set) != len(self): 
            raise AttributeError("There is something wrong in the attribute infostates and maximal_infostates. The length of one does not match the expected length. %s != %s" % (len(self), len(testing_set)))

        return maximal_infostates

    def issubset(self, other):
        """
        Check that one inquisitive state is subset of another.
        """
        return self.infostates.issubset(other.infostates)

    def subsists(self, element):
        """
        Check whether the inquisitive state subsists in the inquisitive state S.

        This happens if self subsists in for all info states in self, info state subsists in one or more s in S.
        """
        if isinstance(element, DynamicInquisitiveState):
            for info in self:
                if not info.subsists(element):
                    return False
            return True
        else:
            raise TypeError("Subsisting is checked on wrong types! Only DynamicInquisitiveState can be used.")


    def evaluate(self, expr):
        """
        Read input expressions, and provide a handler for ``satisfy``
        that blocks further propagation of the ``Undefined`` error.
        :param expr: An ``Expression`` of ``logic``.
        """
        try:
            parsed = Expression.fromstring(expr)
            return self.satisfy(parsed)
        except Undefined:
            return 'Undefined'
            #raise TypeError("Undefined")

    def satisfy(self, parsed):
        """
        Recursive interpretation function for a formula of InqBQD.

        Raises an ``Undefined`` error when ``parsed`` is an atomic string
        but is not a symbol or an individual variable.

        :return: Returns a new model (set of sets of possibilities).
        
        :param parsed: An expression of ``logic``.
        """

        if isinstance(parsed, ApplicationExpression):
            function, arguments = parsed.uncurry()
            if isinstance(function, AbstractVariableExpression):
                #It's a predicate expression ("P(x,y)"), so used uncurried arguments
                #check each infostate, if there is any possibility that's not satisfied, delete the whole info state -- the check is done by possibility.world.satisfy (defined in nltk.sem.Model)
                infostates = set([s for s in self if all(possibility.world.satisfy(parsed, nltk.Assignment(possibility.assignment.domain, [(x, possibility.assignment[possibility.referentsystem[x]]) for x in possibility.referentsystem])) for possibility in s)]) #set comprehension to match conditions written out in idpl -- infostate s has to be in the set of infostates and all its possibilities has to be satisfied
                return DynamicInquisitiveState(infostates, only_maximal=False)

        elif isinstance(parsed, EqualityExpression):
            infostates = set([s for s in self if all(possibility.world.satisfy(parsed, nltk.Assignment(possibility.assignment.domain, [(x, possibility.assignment[possibility.referentsystem[x]]) for x in possibility.referentsystem])) for possibility in s)]) #set comprehension to match conditions written out in idpl -- infostate s has to be in the set of infostates and all its possibilities has to be satisfied
            return DynamicInquisitiveState(infostates, only_maximal=False)

        elif isinstance(parsed, AndExpression):
            return self.satisfy(parsed.first).satisfy(parsed.second)

        elif isinstance(parsed, NegatedExpression):
            pos_inqstate = self.satisfy(parsed.term)
            neg_infostates = set([s for s in self if not any(subinfo.subsists(pos_inqstate) for subinfo in s.yieldsubsets(emptyset_included=False))])
            inq_state = DynamicInquisitiveState(neg_infostates, only_maximal=False)
            return inq_state

        elif isinstance(parsed, ExistsExpression):
            temp_referentsystem = self.referentsystem.add(parsed.variable.name) #1 rs, so this can be stated just once
            infostates = set()
            #for each indiv add all information states in which that individual is added
            subdomains = set()
            for elem in chain.from_iterable(combinations(self.domain, r) for r in range(len(self.domain)+1)):
                if elem:
                    subdomains.add(elem)
            for infostate in self:
                for subdomain in subdomains:
                    infostates.update(set([InformationState(self.domain, [[temp_referentsystem, poss.assignment.add(indiv), poss.world] for indiv in subdomain for poss in infostate])]))
            temp_inqstate = DynamicInquisitiveState(infostates, only_maximal=False)
            t2 = temp_inqstate.satisfy(parsed.term)
            return temp_inqstate.satisfy(parsed.term)

        elif isinstance(parsed, OrExpression):
            infostates = set([s for s in self if s.subsists(self.satisfy(parsed.first)) or s.subsists(self.satisfy(NegatedExpression(parsed.first)).satisfy(parsed.second))])
            return DynamicInquisitiveState(infostates, only_maximal=False)

        elif isinstance(parsed, ImpExpression):
            antecedent = self.satisfy(parsed.first)
            ant_consequent = antecedent.satisfy(parsed.second)
            if_infostates = set()
            for infostate in self:
                for elem in infostate.yieldsubsets(emptyset_included=True):
                    descendants = set()
                    for info in elem.subsists(antecedent):
                        if elem <= info:
                            descendants.add(info)
                    for descendant in descendants:
                        if not descendant.subsists(ant_consequent):
                            break
                    else:
                        continue
                    break
                else:
                    if_infostates.add(infostate)
            return DynamicInquisitiveState(if_infostates, only_maximal=False)

        elif isinstance(parsed, AllExpression):
            var_name = parsed.variable.name
            temp_referentsystem = self.referentsystem.add(var_name) #1 rs, so this can be stated just once
            peg_name = int(temp_referentsystem[var_name][1:])
            infostates = set()
            #for each indiv add all information states in which that individual is added
            subdomains = set()
            for elem in chain.from_iterable(combinations(self.domain, r) for r in range(len(self.domain)+1)):
                if elem:
                    subdomains.add(elem)
            for infostate in self:
                for subdomain in subdomains:
                    infostates.update(set([InformationState(self.domain, [[temp_referentsystem, poss.assignment.add(indiv), poss.world] for indiv in subdomain for poss in infostate])]))
            temp_inqstate = DynamicInquisitiveState(infostates, only_maximal=False).satisfy(parsed.term)
            #check universal validity
            try:
                number_pegs = len(temp_inqstate.referentsystem)
            
            #when hitting the contradictory state
            except TypeError:
                number_pegs = 0                 
                peg_name = -1 #ignore peg_name, because nothing is changed in the contradictory state
            exindivsets = list(product(self.domain, repeat=number_pegs - peg_name-1))
            final_infostates = set()
            for state in temp_inqstate:
                #if indivs introduced in the scope of forall
                if exindivsets[0]:
                    count = 0
                    for indiv in self.domain:
                        for exindivs in exindivsets:
                            sub_individuals = tuple([indiv]) + exindivs
                            new_possibilities = []
                            for poss in state:
                                new_possg = poss.assignment
                                for i, exindiv in enumerate(sub_individuals):
                                    new_possg = new_possg.purge(peg_name+i).add(exindiv, peg_name+i)
                                new_possibilities.append([temp_inqstate.referentsystem, new_possg, poss.world])
                            temp_state = InformationState(self.domain, new_possibilities)
                            if temp_state in temp_inqstate:
                                count += 1
                                break
                    if count == len(self.domain):
                        final_infostates.update(set([InformationState(self.domain, [poss for poss in state])]))
                else:
                    for indiv in self.domain:
                        temp_state = InformationState(self.domain, [[temp_referentsystem, poss.assignment.purge(peg_name).add(indiv, peg_name), poss.world] for poss in state])
                        if temp_state not in temp_inqstate:
                            break
                    else:
                        final_infostates.update(set([InformationState(self.domain, [poss for poss in state])]))
            temp_inqstate = DynamicInquisitiveState(final_infostates, only_maximal=False)
            return temp_inqstate

        elif isinstance(parsed, BangExpression):
            return self.satisfy(NegatedExpression(NegatedExpression(parsed.term))) #Bang is just two negations stacked on top of each other
        elif isinstance(parsed, QuestionExpression):
            return self.satisfy(OrExpression(first=parsed.term, second=NegatedExpression(parsed.term)))
        elif isinstance(parsed, ExhExpression):
            temp_inqstate = self.satisfy(parsed.term)
            maximal_infostates = temp_inqstate.find_maximal()
            infostates = set()
            for s in temp_inqstate:
                for info in maximal_infostates:
                    if not s.worlds.issubset(info.worlds) and not s.worlds.isdisjoint(info.worlds): #like static version
                    #if not s.issubset(info) and not s.isdisjoint(info):
                        break
                else:
                    infostates.add(s)
            return DynamicInquisitiveState(infostates, only_maximal=False)


class InquisitiveState(DynamicInquisitiveState):
    """
    Inquisitive state is a downward-closed set of information states.

    You may specify just the maximal elements (alternatives), initialization will take care of the downward-closed property. If you want to specify every infostate, set only_maximal=False.

    You have to specify a set/list of infostates. Each infostate is a set of worlds. You also have to specify the domain of individuals.
    """

    def __init__(self, domain, infostates, only_maximal=True):
        new_infostates = []
        for infostate in infostates:
            temp_info = []
            for elem in infostate:
                if isinstance(elem, Valuation):
                    world = World(elem, domain)
                elif isinstance(elem, World):
                    if elem.domain == domain:
                        world = elem
                    else:
                        raise ValueError("Domains do not match.")
                else:
                    raise TypeError("Infostates have to consist only of worlds or Valuations.")
                temp_info.append([ReferentSystem(), Assignment(), world])
            new_infostates.append(InformationState(domain, temp_info))

        super(InquisitiveState, self).__init__(infostates=new_infostates, only_maximal=only_maximal)

    def __repr__(self):
        maximal_infostates = self.find_maximal()
        #print max_info
        string = "Only maximal elements (alternatives) printed:"
        for subinfostate in maximal_infostates:
            if subinfostate:
                string = "\n".join([string, "Alternative:", "{", repr(subinfostate), "}"])
            else:
                string = "{}"
        return string

    def copy(self):
        """
        Copy InquisitiveState.
        """
        infostates = set(infostate.worlds for infostate in self)
        return InquisitiveState(self.domain, infostates, only_maximal=False)

    def subsists(self, element):
        """
        Checking subsisting. This is undefined for InquisitiveState (defined for DynamicInquisitiveState).
        """
        raise AttributeError("InquisitiveState cannot subsist.")


    def evaluate(self, expr, g):
        """
        Read input expressions, and provide a handler for ``satisfy``
        that blocks further propagation of the ``Undefined`` error.
        :param expr: An ``Expression`` of ``logic``.
        :param g: Assignment
        """
        try:
            parsed = Expression.fromstring(expr)
            return self.satisfy(parsed, g)
        except Undefined:
            return 'Undefined'
            #raise TypeError("Undefined")

    def satisfy(self, parsed, g):
        """
        Recursive interpretation function for a formula of InqBQ.

        Raises an ``Undefined`` error when ``parsed`` is an atomic string
        but is not a symbol or an individual variable.

        :return: Returns a new model (set of sets of possibilities).
        
        :param parsed: An expression of ``logic``.
        """
        if isinstance(parsed, ApplicationExpression):
            function, arguments = parsed.uncurry()
            if isinstance(function, AbstractVariableExpression):
                #It's a predicate expression ("P(x,y)"), so used uncurried arguments
                #check each infostate, if there is any possibility that's not satisfied, delete the whole info state -- the check is done by possibility.world.satisfy (defined in nltk.sem.Model)
                infostates = set([s.worlds for s in self if all(possibility.world.satisfy(parsed, g) for possibility in s)]) #set comprehension to match conditions written out in idpl -- infostate s has to be in the set of infostates and all its possibilities has to be satisfied
                return InquisitiveState(self.domain, infostates, only_maximal=False)

        elif isinstance(parsed, EqualityExpression):
            infostates = set([s.worlds for s in self if all(possibility.world.satisfy(parsed, g) for possibility in s)]) 
            return InquisitiveState(self.domain, infostates, only_maximal=False)

        elif isinstance(parsed, AndExpression):
            infostates = set([s.worlds for s in self if s in self.satisfy(parsed.first, g) and s in self.satisfy(parsed.second, g)])
            return InquisitiveState(self.domain, infostates, only_maximal=False)

        elif isinstance(parsed, NegatedExpression):
            pos_inqstate = self.satisfy(parsed.term, g)
            neg_infostates = set([s.worlds for s in self if not any(subinfo in pos_inqstate for subinfo in s.yieldsubsets(emptyset_included=False))])
            return InquisitiveState(self.domain, neg_infostates, only_maximal=False)

        elif isinstance(parsed, ExistsExpression):
            new_g = g.copy()
            infostates = set()
            #for each indiv add all information states in which that individual is added
            for indiv in self.domain:
                new_g.add(parsed.variable.name, indiv)
                infostates.update(set([s.worlds for s in self.satisfy(parsed.term, new_g)]))
            return InquisitiveState(self.domain, infostates, only_maximal=False)

        elif isinstance(parsed, OrExpression):
            infostates = set([s.worlds for s in self if s in self.satisfy(parsed.first, g) or s in self.satisfy(parsed.second, g)])
            return InquisitiveState(self.domain, infostates, only_maximal=False)

        elif isinstance(parsed, ImpExpression):
            #something wrong here -- check examples
            if_infostates = set()
            antecedent = self.satisfy(parsed.first, g)
            ant_consequent = self.satisfy(parsed.second, g)

            for infostate in self:
                for elem in infostate.yieldsubsets(emptyset_included=True):
                    if elem in antecedent and elem not in ant_consequent:
                        break
                else:
                    if_infostates.add(infostate.worlds)
            if_inq = InquisitiveState(self.domain, if_infostates, only_maximal=False)
            return if_inq

        elif isinstance(parsed, AllExpression):
            new_g = g.copy()
            infostates = set()
            #for each indiv add all information states in which that individual is added
            for indiv in self.domain:
                new_g.add(parsed.variable.name, indiv)
                if infostates:
                    infostates.intersection_update(set([s.worlds for s in self.satisfy(parsed.term, new_g)]))
                else:
                    infostates = set([s.worlds for s in self.satisfy(parsed.term, new_g)])
            return InquisitiveState(self.domain, infostates, only_maximal=False)
        elif isinstance(parsed, BangExpression):
            return self.satisfy(NegatedExpression(NegatedExpression(parsed.term)), g) #Bang is just two negations stacked on top of each other
        elif isinstance(parsed, QuestionExpression):
            return self.satisfy(OrExpression(first=parsed.term, second=NegatedExpression(parsed.term)), g)
        elif isinstance(parsed, ExhExpression):
            temp_inqstate = self.satisfy(parsed.term, g)
            maximal_infostates = temp_inqstate.find_maximal()
            infostates = set()
            for s in temp_inqstate:
                for info in maximal_infostates:
                    if not s.issubset(info) and not s.isdisjoint(info):
                        break
                else:
                    infostates.add(s.worlds)
            return InquisitiveState(self.domain, infostates, only_maximal=False)


#####HELPER FUNCTION######

# - add presuppositions
