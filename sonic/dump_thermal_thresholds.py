#!/usr/bin/env python3

import json

def _filter_and_reorder_thermals(thermals, orders):
    name_idx = {th.get_name() : i for i, th in enumerate(thermals)}
    res = []
    for pattern in orders:
        for name, idx in name_idx.items():
            if pattern in name:
                res.append(thermals[idx])
    return res

def _get_all_thermals():
    import sonic_py_common
    import sonic_platform

    chassis = sonic_platform.platform.Platform().get_chassis()
    thermals = chassis.get_all_thermals()
    if "wedge" not in sonic_py_common.device_info.get_platform().lower():
        return thermals

    wedge_th_order = ["core-0", "outlet-middle", "inlet-middle", "inlet-left",
                      "switch", "inlet-right", "outlet-right", "outlet-left" ]
    return _filter_and_reorder_thermals(thermals, wedge_th_order)

def dump_thermal_thresholds_api2():
    output = dict()
    for index, thermal in enumerate(_get_all_thermals()):
        high_crit = thermal.get_high_critical_threshold()
        high_err = thermal.get_high_threshold()
        high_warn = thermal.get_high_warning_threshold()
        low_warn = thermal.get_low_warning_threshold()

        if high_crit==None and high_err==None and high_warn==None and low_warn==None:
            continue

        output[str(index + 1)] = {
            "error": int(high_err*1000),
            "shutdown": int(high_crit*1000),
            "warning_lower": int(low_warn*1000),
            "warning_upper": int(high_warn*1000),
        }
    print(json.dumps(output, indent=4))


if __name__ == '__main__':
    dump_thermal_thresholds_api2()
