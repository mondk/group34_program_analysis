import re
from pathlib import Path
#!/usr/bin/env python3
import sys
import json
from typing import Optional

# ignored for now
call = 'jpamb.cases.Simple.assertInteger:(I)V'

regex = re.compile(r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)")



match = regex.search(call)

info = match.groupdict()

class_name = info['class_name'].replace(".","/")+(".json")
file_path = Path("decompiled")/class_name
file_path=str(file_path).replace('\\','/')
method_name = info['method_name']


def parser(file_path, method_name):
    bytecode =[]
    with open(file_path, 'r') as file:
        java_code = file.read()
        json_obj = json.loads(java_code)
        for i in json_obj['methods']:
            if i['name'] == method_name:
                for c in i['code']['bytecode']:
                    bytecode.append(c)
                break
    if len(bytecode) ==0:
        print('Error no bytecode for: ',method_name)
    return bytecode
   

bytecode = parser(file_path, method_name)

for i in bytecode:
    print()
    print(i)

class OurInterpreter:
    bytecode:list
    local:list
    max_local:int
    stack:list
    pc:int
    done: Optional[str] = None

    def interpret(self):
        self.local = [None]*self.max_local
        for i in range(len(bytecode)):
            next = self.bytecode[self.pc]

            if fn := getattr(self, "step_" + next["opr"], None):
                    fn(next)
            else:
                return f"can't handle {next['opr']!r}"
            if self.done:
                return self.done
        return 'out of time'
            
    
    def step_push(self,bc):
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
    
    def step_get(self,bc):
        self.stack.append(bc['static'])
        self.pc +=1
    def step_new(self,bc):
        new_obj = {'class':bc['class']}
        self.stack.append(new_obj)
        self.pc+=1
    def step_dup(self,bc):
        value = self.stack.pop()
        self.stack.append(value)
        self.stack.append(value)
        self.pc+=1
    def step_invoke(self,bc):
        obj = self.stack.pop()

        if obj['class'] 

    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop()
        self.done = "ok"

    
