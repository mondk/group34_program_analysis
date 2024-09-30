from our_interpret import OurInterpreter, MetodID
import sys, logging
import random

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s") 

bytecode, max_locals,param = MetodID(sys.argv).get_info()



int_range = (-1000,1000)
bool_values = [True, False]


def make_child():
    if type(param) == list:
            return [random.randint(*int_range), random.randint(*int_range)]
    if type(param) == bool:
        return random.choice(bool_values)
    else:
        return [random.randint(*int_range)] 
    
l.debug(make_child())

interpreter = OurInterpreter(bytecode,max_locals,make_child())

result = interpreter.interpret()

print(result)