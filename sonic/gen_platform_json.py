#!/usr/bin/env python3
import json

def get_getall_funcs(obj):
    '''Returns a list of get_all_XXXX() of given obj.'''
    return [func for func in dir(obj) if callable(getattr(obj, func)) and func.startswith("get_all_")]

def func_to_key(method):
    '''e.g. return "thermals" while "get_all_thermals" is given'''
    return method[len('get_all_'):]

def try_call(obj, func):
    try:
        return getattr(obj, func)()
    except Exception as e:
        return None

class NameGroupGetter():
    def __init__(self, chassis):
        self.__chassis = chassis

    def get(self):
        '''
        Returns a dict represents the hierarchy of pheripherals and the their
        names obtained by get_name().
        '''
        def serialize(obj, data):
            '''data is a dict'''
            data['name'] = try_call(obj, 'get_name')
            for func in get_getall_funcs(obj):
                children = try_call(obj, func)
                if children==None or len(children)==0:
                    continue
                key = func_to_key(func)
                data[key] = list()
                serialize_list(children, data[key])

        def serialize_list(objs, data):
            '''data is a list'''
            for obj in objs:
                subdata = dict()
                data.append(subdata)
                serialize(obj, subdata)

        def chassis_post_process(data):
            '''drop fans if fan_drawers exists.'''
            if 'fans' in data and 'fan_drawers' in data:
                data.pop('fans', None)

        obj = {'chassis': dict()}
        serialize(self.__chassis, obj['chassis'])
        chassis_post_process(obj['chassis'])
        return obj

def main():
    import sonic_platform.platform
    ch = sonic_platform.platform.Platform().get_chassis()
    names = NameGroupGetter(ch).get()
    with open('platform.json', 'w') as f:
        json.dump(names, f, indent=4)
    print('Done!')

if __name__ == "__main__":
    main()
