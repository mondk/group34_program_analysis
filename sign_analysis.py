from typing import Literal
from sign_set import SignSet
from hypothesis import given
from hypothesis.strategies import integers, sets

class Sign_analysis:

    @staticmethod
    def abstract(items: set[int]):
        signs =set()
    
        for i in items:
            if i ==0:
                signs.add(Literal["0"])
            elif i>0:
                signs.add(Literal["+"])
            else:
                signs.add(Literal["-"])
        return SignSet(list(signs))
    

