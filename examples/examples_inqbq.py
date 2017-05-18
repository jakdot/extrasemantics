"""
An example of how to build Inquisitive state, representing context in inquisitive semantics.

This uses sets of information states.
"""

import nltk
from itertools import chain, combinations

import extrasemantics as sem

#We will assume the domain of 2 individuals:
dom = set(['b1',  'c1'])

#adding another predicate:
vals = []
for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
        vals.append(sem.Valuation([('sleep', set(z)), ('dance', dom.difference(set(z))) ]))

#furthermore, we add naming functions, so we can refer to b1 and c1
for x in vals:
    x['john'] = 'b1'
    x['mary'] = 'c1'

#now we create an assignment function
g1 = nltk.Assignment(dom, [])

inq = sem.InquisitiveState(dom, [vals])

#some examples
exp_list = []
exp_list.append("mary = john")
exp_list.append("sleep (mary) & dance (john)")
exp_list.append("exists z(sleep (z))")
exp_list.append("X(exists z(sleep (z)))") #X - exhaustivitity
exp_list.append("?sleep (mary)")
exp_list.append("?sleep (mary) & ? sleep(john)")
exp_list.append("all x ?(sleep (x))")
#exp_list.append("sleep (mary) | sleep (john)")
#exp_list.append("sleep (mary) -> ?sleep (john)")
#exp_list.append("?sleep (mary) -> ?sleep (john)")
print("Original inquisitive state:")
print(inq)
input()
for x in exp_list:
    print("Information state after updating with: %s" %x)
    print(inq.evaluate(x, g1))
    print("--------------------------------------")
    input()
    #what is printed is info states that remain after evaluating expressions

