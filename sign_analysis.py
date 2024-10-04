from dataclasses import dataclass
from typing import TypeAlias, Literal

Sign : TypeAlias = Literal["+"] | Literal["-"] | Literal["0"]

@dataclass
class SignSet:
  signs : set[Sign]

  def __init__(self,input_list):
    self.signs=set()
    input_list.sort(reverse=True)
    print(input_list)
    for i in input_list:
        if i ==0:
            self.signs.add(Literal["0"])
        elif i>0:
           self.signs.add(Literal["+"])
        else:
           self.signs.add(Literal["-"])
   
  def getSet(self):
     
    order = [Literal["0"], Literal["+"], Literal["-"]]
    return [sign for sign in order if sign in self.signs]


test = [-1,3,0]

print(SignSet(test).getSet())

animal ={'Cat','Dog','Ant','Worm','Spider','Horse','Rabbit'}

