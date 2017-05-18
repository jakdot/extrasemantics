"""
Expressions of IDPL. Their syntax is similar to predicate logic, which is given in nltk.sem.Expression. However, there are a few new operators -- the exclamamtion mark (!), the inquisitive marker (?), exhaustification (X).
"""

import re

import nltk.sem as sem
from nltk.compat import python_2_unicode_compatible

from nltk.sem.logic import (AbstractVariableExpression, AllExpression, EqualityExpression,
                            AndExpression, ApplicationExpression,
                            ExistsExpression, ImpExpression,
                            NegatedExpression, OrExpression)

class Tokens(sem.logic.Tokens):

    #Exra Operations
    BANG = '!';         BANG_LIST = ['bang', '!']
    EXH = 'X';         EXH_LIST = ['exh', 'X']
    QUESTION = '?';     QUESTION_LIST = ['question', '?']
    NOT = '-';         NOT_LIST = ['not', '-']

    #Extra collections of tokens
    EXTRA_INQ_LIST = BANG_LIST + QUESTION_LIST + EXH_LIST

    TOKENS = sem.logic.Tokens.TOKENS + EXTRA_INQ_LIST

    #Special
    SYMBOLS = [x for x in TOKENS if re.match(r'^[-\\.(),?!&^|>=<]*$', x)]

class LogicParser(sem.logic.LogicParser):
    """
    Parser of logic expressions. It inherits from nltk.sem.logic.LogicParser.
    """

    def __init__(self, type_check=False):
        """
        :param type_check: bool should type checking be performed?
        to their types.
        """
        super(LogicParser, self).__init__(type_check)
        self.operator_precedence = dict(
                           [(x,1) for x in Tokens.LAMBDA_LIST]             + \
                           [(x,2) for x in Tokens.NOT_LIST]                + \
                           [(x,3) for x in Tokens.EXTRA_INQ_LIST]                + \
                           [(sem.logic.APP,4)]                                       + \
                           [(x,5) for x in Tokens.EQ_LIST+Tokens.NEQ_LIST] + \
                           [(x,6) for x in Tokens.QUANTS]                  + \
                           [(x,7) for x in Tokens.AND_LIST]                + \
                           [(x,8) for x in Tokens.OR_LIST]                 + \
                           [(x,9) for x in Tokens.IMP_LIST]                + \
                           [(x,10) for x in Tokens.IFF_LIST]                + \
                           [(None,11)])


    def get_all_symbols(self):
        """This method exists to be overridden"""
        return Tokens.SYMBOLS

    def handle(self, tok, context):
        """This method overrides the nltk method of handle, because there are new operators."""
        if self.isvariable(tok):
            return self.handle_variable(tok, context)

        elif tok in Tokens.LAMBDA_LIST:
            return self.handle_lambda(tok, context)

        elif tok in Tokens.NOT_LIST:
            return self.handle_negation(tok, context)

        elif tok in Tokens.BANG_LIST:
            return self.handle_bang_operator(tok, context)
        
        elif tok in Tokens.EXH_LIST:
            return self.handle_exh_operator(tok, context)

        elif tok in Tokens.QUESTION_LIST:
            return self.handle_question_operator(tok, context)

        elif tok in Tokens.QUANTS:
            return self.handle_quant(tok, context)

        elif tok == Tokens.OPEN:
            return self.handle_open(tok, context)

    def isvariable(self, tok):
        """
        Overwrites nltk because there are new symbols added.
        """
        return tok not in Tokens.TOKENS

    def handle_bang_operator(self, tok, context):
        """
        Create expressions based on inquisitive operators.
        """
        return self.make_BangExpression(self.process_next_expression(Tokens.BANG))

    def make_BangExpression(self, expression):
        return BangExpression(expression)
    
    def handle_exh_operator(self, tok, context):
        """
        Create expressions based on inquisitive operators.
        """
        return self.make_ExhExpression(self.process_next_expression(Tokens.EXH))

    def make_ExhExpression(self, expression):
        return ExhExpression(expression)

    def handle_question_operator(self, tok, context):
        """
        Create expressions based on inquisitive operators.
        """
        return self.make_QuestionExpression(self.process_next_expression(Tokens.QUESTION))

    def make_QuestionExpression(self, expression):
        return QuestionExpression(expression)

@python_2_unicode_compatible
class InquisitiveExpression(sem.Expression):
    def __init__(self, term):
        assert isinstance(term, sem.Expression), "%s is not an Expression" % term
        self.term = term

    @property
    def type(self): return sem.logic.TRUTH_TYPE

    def _set_type(self, other_type=sem.logic.ANY_TYPE, signature=None):
        """:see Expression._set_type()"""
        assert isinstance(other_type, sem.logic.Type)

        if signature is None:
            signature = defaultdict(list)

        if not other_type.matches(TRUTH_TYPE):
            raise IllegalTypeException(self, other_type, sem.logic.TRUTH_TYPE)
        self.term._set_type(sem.logic.TRUTH_TYPE, signature)

    def findtype(self, variable):
        assert isinstance(variable, sem.logic.Variable), "%s is not a Variable" % variable
        return self.term.findtype(variable)

    def visit(self, function, combinator):
        """:see: Expression.visit()"""
        return combinator([function(self.term)])
    
    __hash__ = sem.Expression.__hash__ 

class BangExpression(InquisitiveExpression):
    def __eq__(self, other):
        return isinstance(other, BangExpression) and self.term == other.term

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return Tokens.BANG + "%s" % self.term

class QuestionExpression(InquisitiveExpression):
    def __eq__(self, other):
        return isinstance(other, QuestionExpression) and self.term == other.term

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return Tokens.QUESTION + "%s" % self.term

class ExhExpression(InquisitiveExpression):
    def __eq__(self, other):
        return isinstance(other, ExhExpression) and self.term == other.term

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return Tokens.EXH + "%s" % self.term


class Expression(sem.Expression):
    """
    This is the base abstract object for all logical expressions. It inherits from nltk.sem.logic.Expression.
    """

    _logic_parser = LogicParser()
    _type_checking_logic_parser = LogicParser(type_check=True)

    @classmethod
    def fromstring(cls, s, type_check=False, signature=None):
        if type_check:
            return cls._type_checking_logic_parser.parse(s, signature)
        else:
            return cls._logic_parser.parse(s, signature)

