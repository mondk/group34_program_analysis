import re
from pathlib import Path
#!/usr/bin/env python3
import sys
import json
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
        print('Error not bytecode for: ',method_name)
    return bytecode
   

bytecode = parser(file_path, method_name)

for i in bytecode:
    print()
    print(i)

