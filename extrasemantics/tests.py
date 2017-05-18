"""
Testing IDPL.
"""

import unittest
import collections
import re
from itertools import chain, combinations

import numpy as np
import nltk

import extrasemantics as extrasem

class TestPossibilities(unittest.TestCase):
    """
    Testing information states. Identity
    """

    def setUp(self):

        dom = set(['b1', 'c1'])
        vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            vals.append(extrasem.Valuation([('sleep', set(z))]))

        vals2 = vals[0:2]

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])


        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])

    def test_values(self):
        new_assignment = self.g1.add("d1")
        self.assertEqual(self.g1, extrasem.Assignment(values=['b1', 'c1']))
        self.assertNotEqual(self.g1, new_assignment)
        self.assertEqual(type(self.g1), type(new_assignment))
        self.assertEqual(new_assignment, extrasem.Assignment(values=['b1', 'c1', 'd1']))
        new_r = self.r1.add("z")
        self.assertEqual(self.r1, extrasem.ReferentSystem(variables=['x', 'y']))
        self.assertNotEqual(self.r1, new_r)
        self.assertEqual(type(self.r1), type(new_r))
        self.assertEqual(new_r, extrasem.ReferentSystem(variables=['x', 'y', 'z']))
        last_assignment = self.g1.purge("p1")
        self.assertEqual(self.g1, extrasem.Assignment(values=['b1', 'c1']))
        self.assertEqual(last_assignment, extrasem.Assignment(values=['b1']))
        smallest = self.g1.purge()
        self.assertEqual(smallest, extrasem.Assignment(values=None))



class TestInformationStates1(unittest.TestCase):
    """
    Testing information states. Identity
    """

    def setUp(self):

        dom = set(['b1', 'c1'])
        vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            vals.append(extrasem.Valuation([('sleep', set(z))]))

        vals2 = vals[0:2]

        g1 = extrasem.Assignment(values=['b1', 'c1'])

        g2 = extrasem.Assignment(values=['b1'])

        r1 = extrasem.ReferentSystem(variables=['x', 'y'])


        r2 = extrasem.ReferentSystem(variables=['x', 'z'])
        self.info = extrasem.InformationState(dom, [[r1, g1, x] for x in vals])

        self.info2 = extrasem.InformationState(dom, [[r1, g1, x] for x in vals])
        self.info3 = extrasem.InformationState(dom, [[r1, g1, x] for x in vals2])

        possibilities = [[r1, g1, x] for x in vals[:-1]] + [[r1, g2, vals[-1]]]

        self.info4 = extrasem.InformationState(dom, possibilities)

    def test_values(self):
        self.assertTrue(self.info == self.info2)
        self.assertFalse(self.info == self.info3)
        self.assertFalse(self.info == self.info4)

class TestInformationStates2(unittest.TestCase):
    """
    Testing information states. Uniqueness
    """

    def setUp(self):

        dom = set(['b1', 'c1'])
        vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            vals.append(extrasem.Valuation([('sleep', set(z))]))

        vals2 = vals[0:2]

        g1 = extrasem.Assignment(values=['b1', 'c1'])

        g2 = extrasem.Assignment(values=['b1'])

        r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        
        self.possibilities = [[r1, g1, x] for x in vals]
        self.info = extrasem.InformationState(dom, self.possibilities)

        self.rep_possibilities = self.possibilities + [[r1, g1, vals[1]]] 
        self.info2 = extrasem.InformationState(dom, self.rep_possibilities)

    def test_values(self):
        self.assertEqual(4, len(self.possibilities))
        self.assertEqual(5, len(self.rep_possibilities))
        self.assertEqual(4, len(self.info))
        self.assertEqual(4, len(self.info2))
        self.assertTrue(self.info == self.info2)

class TestInformationStates3(unittest.TestCase):
    """
    Testing information states. Expanding and shrinking
    """

    def setUp(self):

        dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))

        self.w = extrasem.Valuation([('dance', set(['b1']))])

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])

        self.g2 = extrasem.Assignment(values=['b1'])

        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        
        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]
        self.info = extrasem.InformationState(dom, self.possibilities)

    def test_values(self):
        self.assertEqual(4, len(self.info))
        new_info = self.info.expand([self.r1, self.g2, self.vals[1]])
        self.assertEqual(4, len(self.info))
        self.assertEqual(5, len(new_info))
        new_info2 = new_info.expand([self.r1, self.g1, self.vals[2]])
        self.assertEqual(5, len(new_info))
        self.assertEqual(5, len(new_info2))
        self.assertTrue(new_info == new_info2)
        new_info3 = new_info.expand([self.r1, self.g1, self.w])
        self.assertEqual(6, len(new_info3))
        self.assertFalse(new_info == new_info3)
        self.assertTrue(new_info == new_info2)
        shrink_info1 = new_info.shrink([self.r1, self.g2, self.vals[1]])
        self.assertEqual(4, len(shrink_info1))
        shrink_info2 = shrink_info1.shrink([self.r1, self.g2, self.w])
        self.assertTrue(shrink_info1 == shrink_info2)

class TestInformationStates4(unittest.TestCase):
    """
    Testing information states. Extending, subsisting
    """

    def setUp(self):

        dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))

        self.w = extrasem.Valuation([('sleep', set(['b1']))])
        self.w2 = extrasem.Valuation([('dance', set(['b1']))])

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])

        self.g2 = extrasem.Assignment(values=['b1', 'c1', 'b1'])

        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        self.r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])
        
        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]
        self.info = extrasem.InformationState(dom, self.possibilities)
        self.info2 = extrasem.InformationState(dom, [[self.r1, self.g1, self.w]])
        self.info3 = extrasem.InformationState(dom, [[self.r1, self.g1, self.w2]])
        
        self.small_possibilities = [[self.r2, self.g2, x] for x in self.vals]
        self.info4 = extrasem.InformationState(dom, self.small_possibilities)
        self.info5 = extrasem.InformationState(dom, [[self.r2, self.g2, self.w]])
        self.info6 = extrasem.InformationState(dom, [[self.r2, self.g2, self.w2]])

    def test_values(self):
        self.assertFalse(self.info == self.info2)
        self.assertTrue(self.info <= self.info2) #the same r, g, w, subset of possibilities
        self.assertFalse(self.info <= self.info3) #differetn w in info3
        self.assertTrue(self.info <= self.info4) #extended r, g in info, the same w
        self.assertTrue(self.info <= self.info5) #extended r, g in info, the same w
        self.assertFalse(self.info <= self.info6) #extended r, g in info, the same w

        self.assertFalse(self.info2 <= self.info) #reversal, see above
        self.assertFalse(self.info4 <= self.info) #reversal, see above
        self.assertFalse(self.info5 <= self.info) #reversal, see above

        self.assertFalse(self.info.subsists(self.info2))
        self.assertTrue(self.info2.subsists(self.info))
        self.assertTrue(self.info.subsists(self.info4))
        self.assertFalse(self.info.subsists(self.info5))
        self.assertTrue(self.info5.subsists(self.info4))

class TestInformationStates5(unittest.TestCase):
    """
    Testing information states. Extending, subsisting
    """

    def setUp(self):

        self.dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(self.dom, r) for r in range(len(self.dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))
        for x in self.vals:
            x['john'] = 'b1'
            x['mary'] = 'c1'

        self.w = extrasem.Valuation([('sleep', set(['b1']))])
        self.w2 = extrasem.Valuation([('dance', set(['b1']))])

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])


        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        #self.r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])
        #self.g2 = extrasem.Assignment(values=['b1', 'c1', 'b1'])
        
        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]
        self.info = extrasem.InformationState(self.dom, self.possibilities)
        
    def test_values(self):
        new_infostate = self.info.evaluate("sleep (mary)")

        tested1 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('c1')])) ])]])
        self.assertEqual(tested1, new_infostate)

        new_infostate = self.info.evaluate("-sleep (john)")

        tested1 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('c1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set()) ])]])
        self.assertEqual(tested1, new_infostate)

        new_infostate = self.info.evaluate("sleep (mary) & sleep(john)")

        tested2 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])] ])
        self.assertEqual(tested2, new_infostate)

        extended_info = self.info.evaluate("exists z. (sleep(z) | -sleep(z)) ") #empty(x) is a dummy prop, always satisfied

        g_extra1 = extrasem.Assignment(values=['b1', 'c1', 'b1'])
        g_extra2 = extrasem.Assignment(values=['b1', 'c1', 'c1'])

        r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])

        info1 = extrasem.InformationState(self.dom, [[r2, g_extra1, x] for x in self.vals] +\
                [[r2, g_extra2, x] for x in self.vals])
        
        self.assertEqual(extended_info, info1)

        extended_info = self.info.evaluate("sleep(mary) -> sleep(john)") 

        tested3 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set()) ])] ])
        
        self.assertEqual(extended_info, tested3)

        extended_info = self.info.evaluate("all z. sleep(z)")

        tested4 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])] ])

        self.assertEqual(extended_info, tested4)

        extended_info = self.info.evaluate("-(all z. sleep(z))")
        
        tested5 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set()) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('c1')])) ])]])
        self.assertEqual(tested5, extended_info)

        extended_info = self.info.evaluate("all z. -(sleep(z))")
        tested6 = extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set()) ])] ])

        self.assertEqual(extended_info, tested6)
        

class TestInqStates1(unittest.TestCase):
    """
    Testing inquisitive states.
    """

    def setUp(self):

        dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])

        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])

        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]
        self.info = extrasem.InformationState(dom, self.possibilities)

        self.inq = extrasem.DynamicInquisitiveState([self.info])
        
        self.possibilities2 = [[self.r1, self.g1, x] for x in self.vals]
        self.info2 = extrasem.InformationState(dom, self.possibilities)

        self.inq2 = extrasem.DynamicInquisitiveState([self.info2])

        self.g2 = extrasem.Assignment(values=['b1', 'c1', 'b1'])

        self.r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])
        
        self.w = extrasem.Valuation([('sleep', set(['b1']))])
        self.small_possibilities = [[self.r2, self.g2, x] for x in self.vals]
        self.info4 = extrasem.InformationState(dom, self.small_possibilities)
        self.info5 = extrasem.InformationState(dom, [[self.r2, self.g2, self.w]])
        self.inq4 = extrasem.DynamicInquisitiveState([self.info4])
        self.inq5 = extrasem.DynamicInquisitiveState([self.info5])

    def test_values(self):
        self.assertTrue(self.inq == self.inq2)
        self.inq.discard(self.info)
        self.assertFalse(self.inq == self.inq2)

        self.assertTrue(self.inq.subsists(self.inq4))
        self.assertTrue(self.inq5.subsists(self.inq4))
        self.assertFalse(self.inq5.subsists(self.inq))

class TestStaticInqStates1(unittest.TestCase):
    """
    Testing inquisitive states, the static version.
    """

    def setUp(self):
        self.dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(self.dom, r) for r in range(len(self.dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))
        for x in self.vals:
            x['john'] = 'b1'
            x['mary'] = 'c1'

        self.inq = extrasem.InquisitiveState(self.dom, [self.vals])
        self.g1 = nltk.Assignment(self.dom, [('x', 'b1'), ('y', 'c1')])

    def test_values(self):
        new_inqstate = self.inq.evaluate("sleep (mary)", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("sleep (mary) & sleep (john)", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("- sleep (mary) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("exists z( sleep (z)) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("sleep (mary) | sleep (john) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("sleep (mary) -> sleep (john) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [ [extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("all x( sleep (x)) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)

        new_inqstate = self.inq.evaluate("? sleep (mary) ", self.g1)
        compared = extrasem.InquisitiveState(self.dom, [[extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')]), extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])]] )
        self.assertEqual(new_inqstate, compared)
        
        new_inqstate = self.inq.evaluate("!(? sleep (mary)) ", self.g1)
        self.assertEqual(new_inqstate, self.inq)

        self.assertEqual(self.inq, self.inq.copy())

class TestInqStates2(unittest.TestCase):
    """
    Testing inquisitive states. Conjunction, simple predicates, new assignments
    """

    def setUp(self):

        self.dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(self.dom, r) for r in range(len(self.dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))
        for x in self.vals:
            x['john'] = 'b1'
            x['mary'] = 'c1'

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])

        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        
        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]

        self.info = extrasem.InformationState(self.dom, self.possibilities)

        self.inq = extrasem.DynamicInquisitiveState([self.info])

    def test_values(self):
        new_inqstate = self.inq.evaluate("sleep (mary)")

        tested1 = extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])], [self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('c1')])) ])]])])
        self.assertEqual(tested1, new_inqstate)

        new_inqstate = self.inq.evaluate("sleep (mary) & sleep(john)")

        tested2 = extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('john', 'b1'), ('mary', 'c1'), ('sleep', set([('b1'), ('c1')])) ])] ])])
        self.assertEqual(tested2, new_inqstate)
        
        extended_inq = self.inq.evaluate("exists z. (!(sleep(z) | -sleep(z)))")

        self.assertEqual(extrasem.DynamicInquisitiveState([self.info]), self.inq)
        
        g_extra1 = extrasem.Assignment(values=['b1', 'c1', 'b1'])

        r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])

        part1  = [[r2, g_extra1, x] for x in self.vals]
        
        g_extra2 = extrasem.Assignment(values=['b1', 'c1', 'c1'])
        
        part2  = [[r2, g_extra2, x] for x in self.vals]

        info1 = extrasem.InformationState(self.dom, part1 + part2)

        self.assertEqual(extended_inq.find_maximal().pop(), info1)
        
        extended_inq2 = extended_inq.evaluate("sleep(z)")

        info1 = extrasem.InformationState(self.dom, [[r2, g_extra1,  extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra1,  extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])]])
        info2 = extrasem.InformationState(self.dom, [[r2, g_extra2,  extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2,  extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])]])
        info3 = extrasem.InformationState(self.dom, [[r2, g_extra1,  extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2,  extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])]])

        self.assertEqual(extended_inq2, extrasem.DynamicInquisitiveState([info1, info2, info3]))

class TestInqStates3(unittest.TestCase):
    """
    Testing inquisitive states. Negation, disjunction, implication, universal quantification
    """

    def setUp(self):

        self.dom = set(['b1',  'c1'])
        self.vals = []
        for z in chain.from_iterable(combinations(self.dom, r) for r in range(len(self.dom)+1)):
            self.vals.append(extrasem.Valuation([('sleep', set(z))]))
        for x in self.vals:
            x['john'] = 'b1'
            x['mary'] = 'c1'

        self.g1 = extrasem.Assignment(values=['b1', 'c1'])

        self.r1 = extrasem.ReferentSystem(variables=['x', 'y'])
        
        self.possibilities = [[self.r1, self.g1, x] for x in self.vals]

        self.info = extrasem.InformationState(self.dom, self.possibilities)

        self.inq = extrasem.DynamicInquisitiveState([self.info])

    def test_values(self):
        extended_inq = self.inq.evaluate("exists z. (-sleep(z))")

        g_extra1 = extrasem.Assignment(values=['b1', 'c1', 'b1'])

        r2 = extrasem.ReferentSystem(variables=['x', 'y', 'z'])

        info1 = extrasem.InformationState(self.dom, [[r2, g_extra1,  extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra1,  extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])
        
        g_extra2 = extrasem.Assignment(values=['b1', 'c1', 'c1'])
        
        info2 = extrasem.InformationState(self.dom, [[r2, g_extra2,  extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2,  extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])
        
        info3 = extrasem.InformationState(self.dom, [[r2, g_extra1,  extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2,  extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([info1, info2, info3]) )

        extended_inq = self.inq.evaluate("-(exists z. sleep(z))")

        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])]) )

        extended_inq = self.inq.evaluate("sleep(mary) | sleep(john)") 
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])]]), extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("(exists z. sleep(z)) | (exists w. (sleep(w)))") 
        
        extended_inq = self.inq.evaluate("sleep(mary) -> sleep(john)") 
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("all z. sleep(z)")

        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[r2, g_extra1, extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2, extrasem.Valuation([('sleep', set(['c1', 'b1'])), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("-(all z. sleep(z))")
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("all z. -(sleep(z))")
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[r2, g_extra1, extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])], [r2, g_extra2, extrasem.Valuation([('sleep', set()), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("!sleep(x)")

        self.assertEqual(extended_inq, self.inq.evaluate("sleep(x)"))
            
        extended_inq = self.inq.evaluate("!(sleep(x) | sleep(y))")
        
        self.assertEqual(extended_inq, extrasem.DynamicInquisitiveState([extrasem.InformationState(self.dom, [[self.r1, self.g1, extrasem.Valuation([('sleep', set(['b1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set(['c1'])), ('john', 'b1'), ('mary', 'c1')])], [self.r1, self.g1, extrasem.Valuation([('sleep', set(['b1', 'c1'])), ('john', 'b1'), ('mary', 'c1')])]])]))

        extended_inq = self.inq.evaluate("?sleep(x)")

        self.assertEqual(extended_inq, self.inq.evaluate("sleep(x) | -sleep(x)"))
            

if __name__ == '__main__':
    unittest.main()
