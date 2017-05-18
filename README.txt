extrasemantics
--------------

Python package that builds on nltk.

It creates several semantic frameworks not present in nltk.sem.

In particular:

(i) dynamic semantics of Dynamic Predicate Logic-style (this is built on Coreference and Modality, by Groenendijk, Stokhof, Veltman)

(ii) inquisitive semantics

(iii) dynamic inquisitive semantics

See the folder examples for examples on each of these frameworks.

Installing extrasemantics
-------------------------

Clone this package and in the root folder, run:

python setup.py install

Requirements
------------

Requires nltk.

Modifying extrasemantics
------------------------

To ensure that modifications do not break the current code, run unittests in the folder extrasemantics.
