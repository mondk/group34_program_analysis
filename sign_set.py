
from dataclasses import dataclass
from typing import TypeAlias, Literal

Sign: TypeAlias = Literal["+"] | Literal["-"] | Literal["0"]

@dataclass
class SignSet:
    signs: set[Sign]

    def __le__(self, other: 'SignSet') -> bool:
        return self.signs.issubset(other.signs)


    def meet(self, other: 'SignSet') -> 'SignSet':
        intersection_signs = set()
        for sign in self.signs:
            if sign in other.signs:
                intersection_signs.add(sign)
        return SignSet(intersection_signs)

  
    def join(self, other: 'SignSet') -> 'SignSet':
        return SignSet(self.signs.union( other.signs))
    
    @staticmethod
    def abstract(items: set[int]):
        signs=set()
 
        for i in items:
            if i ==0:
                signs.add("0")
            elif i>0:
                signs.add("+")
            else:
                signs.add("-")
        return SignSet(signs)
    
    def __str__(self):
        return str(self.signs)

    
set1 = SignSet.abstract(set([1,0]))
set2 = SignSet.abstract(set([-4,1]))

# is subset
print('Is subet:', set1.__le__(set2))
# Meet (intersection)
print("Meet (⊓):", set1.meet(set2)) 

# Join (union)
print("Join (⊔):", set1.join(set2))  


