from our_interpret import OurInterpreter, MetodID
import sys, logging
import random

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s") 
call = sys.argv
l.debug(call)
bytecode, max_locals, param = MetodID(call).get_info()



int_range = (-1000,1000)
bool_values = [True, False]


def make_child():
    if param == 'II':
            return [random.randint(*int_range), random.randint(*int_range)]
    if param == 'Z':
        return random.choice(bool_values)
    else:
        return random.randint(*int_range) 
    
l.debug(make_child())

interpreter = OurInterpreter(bytecode,max_locals,make_child())

result = interpreter.interpret()

if result =='ok':
     print('ok;50%')
else:
     print(result+';100%')