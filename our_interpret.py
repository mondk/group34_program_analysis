import re
from pathlib import Path
#!/usr/bin/env python3
import sys, logging
import json
from typing import Optional, TypeAlias, Literal
l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")
# ignored for now



class MetodID:
    bytecode:list
    max_local:int
    param:None
    call:str

    def __init__(self,call):
        self.call = call

    def get_info(self):
        self.parse_call()
        return self.bytecode,self.max_local,self.param
    def parse_call(self):
        call = self.call[1].replace("'", "")
        call=call.replace("'", "")
        #'jpamb.cases.Simple.justReturn:()I'
        regex = re.compile(r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)")

        match = regex.search(call)
        info = match.groupdict()
        class_name = info['class_name'].replace(".","/")+(".json")
        file_path = Path("decompiled")/class_name
        file_path=str(file_path).replace('\\','/')
        method_name = info['method_name']

        self.parse_file(file_path,method_name)
        self.param = info['params']
        

    def parse_file(self,file_path, method_name):
        self.bytecode =[]
        max_locals =0
        with open(file_path, 'r') as file:
            java_code = file.read()
            json_obj = json.loads(java_code)
            for i in json_obj['methods']:
                if i['name'] == method_name:
                    for c in i['code']['bytecode']:
                        self.bytecode.append(c)
                    max_locals=i['code']['max_locals']
                    break
        if len(self.bytecode) ==0:
            print('Error no bytecode for: ',method_name)
        self.max_local=max_locals
    def parse_param(self,s:str):

        if s == '()':
            return []
        # Handle boolean case
        if s== "'(true)'":
            return [True]
        elif s == "'(false)'":
            return [False]
        if s== '(true)':
            return [True]
        elif s == '(false)':
            return [False]
        
        # Handle list of integers case
        match = re.search(r'\((-?\d+(?:,\s*-?\d+)*)\)', s)
        l.debug(match)
        if match:
            # Split by commas and convert to integers
            return [int(x) for x in match.group(1).split(',')]
        l.debug(s)
        raise ValueError("Input string does not match expected format")


class OurInterpreter:
    bytecode:list
    local:list
    max_local:int
    stack:list
    pc:int
    done: Optional[str] = None
    time:int
    state_mem:dict 

    def __init__(self, bytecode, max_local,param):
        self.bytecode = bytecode
        self.max_local = max_local
        self.pc = 0
        self.local = [None] * self.max_local
        self.stack = [] 
        self.time = 1000
        self.state_mem ={}
        self.heap = []
        if type(param)==list:
            l.debug(param)
            for i in range(0,len(param)):
                l.debug(max_local)
                self.local[i] = param[i]
                
        else:
            self.local=param

    def interpret(self):
        
        for i in range(self.time):
            next = self.bytecode[self.pc]
            
            if self.pc in self.state_mem:
                for d in self.state_mem[self.pc]:
                    if d['local'] == self.local and d['stack'] == self.stack:
                        if d['count'] > 10:
                            return '*'
                        else:
                            d['count']+=1
                
            l.debug(next['opr'])
            #l.debug(self.pc)
            #l.debug(self.local)
            l.debug(self.stack)
            
            if self.done:
                return self.done
            if fn := getattr(self, "step_" + next["opr"], None):
                    fn(next)
                    
                    if self.pc in self.state_mem:
                         for d in self.state_mem[self.pc]:
                            if d['local'] == self.local and d['stack'] == self.stack:
                                    d['count']+=1
                    else:
                        self.state_mem[self.pc] = [{'local':self.local,'stack':self.stack,'count':0}]
                        
            else:
                return f"can't handle {next['opr']!r}"
            if self.done:
                return self.done
            
        return 'out of time'
            
    
    def step_push(self,bc):
        if bc['value'] is None:
            self.stack.append(None)
        else:
            self.stack.append(bc['value']['value'])
        self.pc+=1
    def step_load(self,bc):
        value = self.local[bc['index']]
        self.stack.append(value)
        self.pc+=1
    def step_store(self,bc):
        value = self.stack.pop()
        self.local[bc['index']] = value
        self.pc+=1
    def step_ifz(self,bc):
        value = self.stack.pop()
        condition = bc['condition']
        l.debug(value)
        if type(value)==bool:
            if value:
                value =1
            else:
                value =0
        jump= False
        if condition =='eq':
            jump = value==0
        elif condition =='ne':
            jump = value!=0
        elif condition =='gt':
            jump = value>0
        elif condition =='ge':
            jump = value>=0
        elif condition == 'lt':
            jump = value<0
        elif condition == 'le':
            jump = value<=0
        if jump:
            self.pc=bc['target']
        else:
            self.pc+=1
        
    def step_goto(self,bc):
        self.pc = bc['target']
    
    def step_cast(self, bc):

        cast_type = bc['to']
        value = self.stack.pop()
        new_value:None
        if cast_type =='short':
            new_value = self.int_to_short(value)
        if cast_type == 'byte':
            new_value = self.int_to_byte(value)
        if cast_type == 'char':
            new_value = chr(value)
        self.stack.append(new_value)
        self.pc+=1
    @staticmethod 
    def int_to_short(value):
        # Apply a mask to simulate 16-bit signed integer range (-32768 to 32767)
            short_value = (value & 0xFFFF)
            if short_value >= 0x8000:  # If the value exceeds 32767
                short_value -= 0x10000  # Convert to negative (two's complement)
            return short_value
    @staticmethod
    def int_to_byte(value):
        # Apply a mask to simulate 8-bit signed integer range (-128 to 127)
            byte_value = (value & 0xFF)
            if byte_value >= 0x80:  # If the value exceeds 127
                byte_value -= 0x100  # Convert to negative (two's complement)
            return byte_value
        

    def step_get(self,bc):
        self.stack.append(False)
        self.pc +=1
    def step_new(self,bc):
        new_obj = AssertionError('assertion error')
        self.stack.append(new_obj)
        self.pc+=1
    def step_dup(self,bc):
        value = self.stack.pop()
        self.stack.append(value)
        self.stack.append(value)
        self.pc+=1
    def step_invoke(self, bc):
        
        method_info = bc['method']
        method_name = method_info['name']
        
        if method_name == 'assertIf':
            obj = self.stack.pop()
            try:
                assert obj
                
            except:
                self.done = 'assertion error'
        elif method_name == 'assertFalse':
            try:
                assert False
                
            except:
                self.done = 'assertion error'
        
        self.pc += 1

    def step_throw(self,bc):
        #l.debug('nig')
        exception = self.stack.pop()
        self.done = 'assertion error'
        self.pc+=1
        
    
    def step_binary(self,bc):
        bin_type = bc['operant']
        a = self.stack.pop()
        b = self.stack.pop()
       
        res=0
        if bin_type =='add':
            res = a+b
        elif bin_type == 'sub':
            res = a-b
        elif bin_type == 'div':
           
            if a==0:
                self.done ='divide by zero'
            else:
                if b==0:
                    res =0
                else:
                    res= a/b
        elif bin_type == 'mul':
            res=a*b
        elif bin_type == 'rem':
            res = a%b
        self.stack.append(res)
        self.pc+=1

    #maybe
    def step_put(self,bc):
        value =self.stack.pop()
        bc['static'] = value
        self.pc+=1
        
    def step_if(self,bc):
        value1 = self.stack.pop()
        value2 = self.stack.pop()
        condition = bc['condition']
        jump= False
        if condition =='eq':
            jump = value1==value2
        elif condition =='ne':
            jump = value1!=value2
        elif condition =='gt':
            jump = value1>value2
        elif condition =='ge':
            jump = value1>=value2
        elif condition == 'lt':
            jump = value1 < value2
        elif condition == 'le':
            jump = value1 <= value2
        if jump:
            self.pc=bc['target']
        else:
            self.pc+=1
    
    def step_incr(self,bc):
        index = bc['index']
        self.local[index]+=bc['amount']
        self.pc+=1

    
    def step_newarray(self,bc):
        dim = bc['dim']
        self.heap.append([0]*(dim+1))
        self.pc+=1
    
    def step_array_store(self,bc):
        index = self.stack.pop(0)
        value = self.stack.pop(0)
       
        l.debug(index)
        l.debug(value)
        if self.heap ==[]:
            self.done = 'null pointer'
        else:
            try:
                self.heap[0][index] = value
            except Exception:
                l.debug(Exception.add_note)
                self.done = 'out of bounds'
        self.pc+=1
    
    def step_array_load(self,bc):
        index = self.stack.pop()
        value = self.heap[0][index]
        self.stack.append(value)
        self.pc+=1

    def step_arraylength(self,bc):
        if self.heap!=[]:
            length = len(self.heap[0])
            self.stack.append(length)
            self.pc+=1
        else:
            self.done = 'null pointer'
    
    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop()
        
        if self.done == None:
            self.done = "ok"

