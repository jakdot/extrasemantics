"""
A slightly more complex (and slower) examples of how to build IDPL.

This uses sets of information states, i.e., it is built on top of CorMod (DPL).
"""

from itertools import chain, combinations

import extrasemantics as sem

#We will assume the domain of 2 individuals:
dom = set(['b1',  'c1', 'd1', 'e1'])

vals = []
temp_dom = set(['b1',  'c1'])
temp_dom2 = set(['d1',  'e1'])
for z in chain.from_iterable(combinations(temp_dom, r) for r in range(len(temp_dom)+1)):
        like_set = set([('b1', 'd1'), ('c1', 'd1')])
        if not z:
            #vals.append(sem.Valuation([('sleep', set()), ('dreamAbout', set()), ('like', like_set), ('dance', temp_dom) ]))
            continue
        for y in temp_dom2:
            temp_set = set()
            for x in z:
                temp_set.add((x, y))
            vals.append(sem.Valuation([('sleep', set(z)), ('dreamAbout', temp_set), ('like', like_set) ]))

#furthermore, we add naming functions, so we can refer to b1 and c1
for x in vals:
    x['john'] = 'b1'
    x['mary'] = 'c1'
    x['dog'] = 'd1'
    x['elephant'] = 'e1'

#now we create an assignment function
g1 = sem.Assignment(values=['b1', 'c1'])

#and we create referent system
r1 = sem.ReferentSystem(variables=['x', 'y'])

#all possibilities are put together as triples with identical g1 and r1, but varying worlds
possibilities = [[r1, g1, x] for x in vals]
info = sem.InformationState(dom, possibilities)

inq = sem.DynamicInquisitiveState([info])

exp_list = []
exp_list.append("exists u(sleep (u)) & exists v(dreamAbout(u, v))")
exp_list.append("exists u (exists v(dreamAbout (u, v))) & ?like(u, v)")
exp_list.append("exists u (exists v(dreamAbout (u, v)) & like(u, v))")
exp_list.append("X(exists u (exists v(dreamAbout (u, v)))) & ?like(u, v)")
exp_list.append("X(exists u (exists v(dreamAbout (u, v)) & like(u, v)))")
print("Original state:")
print(inq)
input()
for x in exp_list:
    print("Information state after updating with: %s" %x)
    print(inq.evaluate(x))
    input()
    print("--------------------------------------")
    #what is printed is info states that remain after evaluating expressions
