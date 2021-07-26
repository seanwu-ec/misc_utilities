#!/usr/bin/env python3

import sonic_platform
from tabulate import tabulate
import time
import click
import os

def is_user_root():
    return os.geteuid() == 0

def get_chassis():
    return sonic_platform.platform.Platform().get_chassis()

def get_method_list(obj):
    return [func for func in dir(obj) if callable(getattr(obj, func)) and not func.startswith("__")]

def try_get(obj, func):
    try:
        return getattr(obj, func)()
    except Exception as e:
        return type(e).__name__



class Dumper():
    '''Dump ordinary get APIs and their results'''
    HEADER = ['method', 'result']

    def __init__(self, devlist, exemption):
        self.__devlist = devlist
        self.__exemption = exemption

    def dump(self):
        if len(self.__devlist) == 0:
            print(f'{type(self)}: WARN:no dev in dev_list')
            return
        devtype = type(self.__devlist[0])
        mlist_all = sorted(get_method_list(devtype))
        mlist = [func for func in mlist_all if func not in self.__exemption]
        for i, dev in enumerate(self.__devlist):
            table = [[func, try_get(dev, func)] for func in mlist]
            print(f'****** Dump {devtype} idx({i}) ******')
            print(tabulate(table, self.HEADER, tablefmt='simple', stralign='left'))
            print('')


class ChassisTester(Dumper):
    def __init__(self, chassis):
        exemption = {'get_all_components', 'get_all_fan_drawers', 'get_all_fans', 'get_all_modules',
                    'get_all_psus', 'get_all_sfps', 'get_all_thermals', 'get_component',
                    'get_eeprom', 'get_fan', 'get_fan_drawer', 'get_psu', 'get_thermal',
                    'get_module', 'install_component_firmware', 'get_sfp', 'get_thermal_manager',
                    'get_watchdog', 'get_firmware_version', 'set_status_led', 'set_system_led',
                    'get_module_index' }
        super().__init__([chassis], exemption)

    '''
    TODO: special tests in this peripheral
        - get_firmware_version
        - set_status_led
        - set_system_led
    '''

class ThermalTester(Dumper):
    def __init__(self, chassis):
        exemption = { 'set_high_critical_threshold', 'set_high_threshold',
                      'set_low_critical_threshold', 'set_low_threshold', 'dump_sysfs' }
        super().__init__(chassis.get_all_thermals(), exemption)


class PsuTester(Dumper):
    def __init__(self, chassis):
        exemption = { 'dump_sysfs', 'get_all_fans', 'get_all_thermals', 'get_fan', 'get_thermal',
                      'set_status_led', 'set_status_master_led' }
        super().__init__(chassis.get_all_psus(), exemption)

    '''
    TODO: special tests in this peripheral
        - set_status_led
        - set_status_master_led
    '''

# TODO: Verify this, ... no Component on AS7326
class ComponentTester(Dumper):
    def __init__(self, chassis):
        exemption = {'auto_update_firmware', 'get_available_firmware_version',
                     'get_firmware_update_notification', 'install_firmware', 'update_firmware'}
        super().__init__(chassis.get_all_components(), exemption)


class FanTester(Dumper):
    def __init__(self, chassis):
        exemption = {'dump_sysfs', 'set_speed', 'set_status_led'}
        self.__fans = self.__get_all_fans(chassis)
        super().__init__(self.__fans, exemption)

    def __get_all_fans(self, chassis):
        fans = []
        for drawer in chassis.get_all_fan_drawers():
            fans += drawer.get_all_fans()
        if not fans:
            print('WARN: FanDrawer not implemented, thermalctld might be not happy about it')
            fans = chassis.get_all_fans()
        return fans

    def __dump_fan_speed(self):
        header = ['name', 'presence', 'target_speed', 'speed']
        funcs = ['get_name', 'get_presence', 'get_target_speed', 'get_speed']
        table = []
        for fan in self.__fans:
            table.append([try_get(fan, func) for func in funcs] )
        print(tabulate(table, header, tablefmt='simple', stralign='right'))

    def __set_fan_speed(self, speed):
        for fan in self.__fans:
            fan.set_speed(speed)

    def test_speed_tolerance(self):
        for fan in self.__fans:
            if fan.get_presence() is False:
                continue

            target = fan.get_target_speed()
            speed = fan.get_speed()
            tolerance = try_get(fan, 'get_speed_tolerance')
            if isinstance(tolerance, int) == False:
                tolerance = 15
            if speed < target - tolerance or speed > target + tolerance:
                print(f'{fan.get_name()} fail, target speed({target}), '\
                      f'tolerance({tolerance}), result speed({speed})')

    def set_speed_test(self):
        speeds = [60, 80, 100]
        poll_intv = 1 # in second
        times = 6

        for speed in speeds:
            print(f'+++++ set speed to {speed} start +++++')
            for i in range(times):
                self.__set_fan_speed(speed)
                time.sleep(poll_intv)
                self.__dump_fan_speed()
                if i == times - 1 :
                    self.test_speed_tolerance()
            print(f'----- set speed to {speed} end -----')

    '''
    TODO: special tests in this peripheral
        - set_speed
        - set_status_led
    TODO: test API to export
        - speed_test
        - set_speed
        - show
    '''

class SfpTester(Dumper):
    def __init__(self, chassis):
        exemption = {'_PddfSfp__read_eeprom_specific_bytes', 'dump_sysfs', 'get_all_thermals',
                     'get_thermal', 'read_eeprom', 'reset', 'set_lpmode', 'set_power_override',
                     'tx_disable', 'write_eeprom', 'tx_disable_channel'}
        super().__init__(chassis.get_all_sfps(), exemption)

    '''
    TODO: special tests in this peripheral
        - get_thermal
        - read_eeprom
        - write_eeprom
        - reset
        - set_lpmode
        - set_power_override
        - tx_disable
        - tx_disable_channel
    '''

class EepromTester(Dumper):
    def __init__(self, chassis):
        exemption = {}
        super().__init__([chassis.get_eeprom()], exemption)

################## click shell #######################

@click.group()
def root():
    "SONiC API2.0 tester"
    pass

@root.group()
def chassis():
    """chassis command group"""
    pass

@root.group()
def thermal():
    """thermal command group"""
    pass

@root.group()
def psu():
    """psu command group"""
    pass

@root.group()
def component():
    """component command group"""
    pass

@root.group()
def fan():
    """fan command group"""
    pass

@root.group()
def sfp():
    """sfp command group"""
    pass

################## dump commands #######################

@chassis.command()
def dump():
    """dump chassis info"""
    ChassisTester(get_chassis()).dump()

@thermal.command()
def dump():
    """dump all thermals info"""
    ThermalTester(get_chassis()).dump()

@psu.command()
def dump():
    """dump all PSUs info"""
    PsuTester(get_chassis()).dump()

@component.command()
def dump():
    """dump all components info"""
    ComponentTester(get_chassis()).dump()

@fan.command()
def dump():
    """dump all fans info"""
    FanTester(get_chassis()).dump()

@sfp.command()
def dump():
    """dump all sfp info"""
    SfpTester(get_chassis()).dump()

################## other commands #######################

@fan.command()
def speed_test():
    """perform a set_speed() -> get_speed() test"""
    if is_user_root() is False:
        raise PermissionError('You need root privilege to do this')
    FanTester(get_chassis()).set_speed_test()



if __name__ == "__main__":
    root()
