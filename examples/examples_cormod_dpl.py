"""
An example of how to build CorMod (based on Coreference and Modality, Groenendijk, Stokhof, Veltman).

Since this is closely related to Dynamic Predicate Logic (DPL), you can also use it to simulate that dynamic semantic framework.

Currently, the model lacks modality.
"""

from itertools import chain, combinations

import extrasemantics as sem

#We will assume the domain of 2 individuals:
dom = set(['b1',  'c1'])

#all possible values for one predicate -- sleep (powerset of {b1, c1}); dance is the complement of sleep
vals = []
for z in chain.from_iterable(combinations(dom, r) for r in range(len(dom)+1)):
    vals.append(sem.Valuation([('sleep', set(z)), ('dance', dom.difference(set(z))) ]))

#furthermore, we add naming functions, so we can refer to b1 and c1
for x in vals:
    x['john'] = 'b1'
    x['mary'] = 'c1'

#we create an assignment function
g1 = sem.Assignment(values=['b1', 'c1'])

#and a referent system
r1 = sem.ReferentSystem(variables=['x', 'y'])

#all possibilities are put together as triples with identical g1 and r1, but varying worlds
possibilities = [[r1, g1, x] for x in vals]
info = sem.InformationState(dom, possibilities)

#some examples;
e1 = "sleep (mary)"
e2 = "sleep (john) & sleep (mary)"
e3 = "sleep (john) & -sleep (mary)"
e4 = "sleep (john) | sleep (mary)"
e5 = "sleep (john) | -sleep (mary)"
e6 = "exists z(sleep (z)) & exists w(-sleep(w))"
e7 = "exists z(sleep (z)) & exists w(sleep(x))"
print("Original information state: %s"  %info)
for x in (e1, e2, e3, e4, e5, e6, e7):
    print("Information state after updating with: %s" %x)
    print(info.evaluate(x))
    print("--------------------------------------")
    #what is printed is info states that remain after evaluating expressions


e0 = "-(-sleep(mary) & -dance (john))"
e1 = "sleep(mary) | dance(john)"

print(info.evaluate(e0) == info.evaluate(e1))

e0 = "(sleep(mary) -> dance (john))"
e1 = "-sleep(mary) | dance(john)"

print(info.evaluate(e0) == info.evaluate(e1))

e2 = "(exists v(sleep(v)) -> exists z(dance(z)))"
e3 = "-exists v(sleep(v)) | exists z(dance(z))"

print(info.evaluate(e2) == info.evaluate(e3))
