"""
An example of how to build IDPL.

This uses sets of information states, it is built on top of CorMod (DPL).
"""

from itertools import chain, combinations

import extrasemantics as sem

#We will assume the domain of 2 individuals:
dom = set(['b1',  'c1'])

vals = []
temp_dom = set(['b1',  'c1'])
for z in chain.from_iterable(combinations(temp_dom, r) for r in range(len(temp_dom)+1)):
    if not z:
        continue
    vals.append(sem.Valuation([('sleep', set(z)), ('dance', temp_dom.difference(set(z))) ]))

#furthermore, we add naming functions, so we can refer to b1 and c1
for x in vals:
    x['john'] = 'b1'
    x['mary'] = 'c1'

#now we create an assignment function
g1 = sem.Assignment(values=['b1', 'c1'])

#and we create referent system
r1 = sem.ReferentSystem(variables=['x', 'y'])

#all possibilities are put together as triples with identical g1 and r1, but varying worlds
possibilities = [[r1, g1, x] for x in vals]
info = sem.InformationState(dom, possibilities)

inq = sem.DynamicInquisitiveState([info])

#some examples
exp_list = []
exp_list.append("x = john")
exp_list.append("y = john")
exp_list.append("sleep (mary) & dance (john)")
exp_list.append("exists z(sleep (z))")
exp_list.append("(sleep (mary) | sleep (john))")

print("Original state:")
print(inq)
input()

for x in exp_list:
    print("Information state after updating with: %s" %x)
    print(inq.evaluate(x))
    print("--------------------------------------")
    input()
    #what is printed is info states that remain after evaluating expressions

