#!/usr/bin/env python3

import os
import sys
import time
import argparse
import re
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from datetime import date

from customer_name import get_vendor_name, vendor_list

dup_ppin = {}
dup_sn = {}
spr_cpu_type = ["SPR-E5", "SPR-E4"]
emr_cpu_type = ["EMR-A0", "EMR-A1", "EMR (no exact match)"]
valid_cpu_type = spr_cpu_type
#valid_cpu_type = ["SPR-E5", "SPR-E4", "SPR-E3"]

def parse_report(path):
    ppin_list = []
    loop_count = 1
    duration = 0
    cpu_type = None
    result = re.search(r".*shc_report_([0-9]{4})-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)/report\.txt", path)
    if not result:
        print("Invalid path", path)
        return None
    #print(result.groups())
    dt = datetime(int(result.groups()[0]), int(result.groups()[1]), int(result.groups()[2]),
        int(result.groups()[3]), int(result.groups()[4]), int(result.groups()[5]))
    with open(path, 'r') as fp:
        for line in fp:
            result = re.search(r"^\tPPIN *: *(0x[a-fA-F0-9]+)", line)
            if result:
                ppin_list.append(result.groups()[0])
                continue
            result = re.search(r"^\..*LoopCount=([0-9]+).*", line)
            if result:
                loop_count = int(result.groups()[0])
                continue
            result = re.search(r"^DURATION : ([0-9]+) Second.*", line)
            if result:
                duration = int(result.groups()[0])
                continue
            result = re.search(r"^CPU Type *: *(.*)$", line)
            if result:
                cpu_type = str(result.groups()[0])
                continue
    return {"cpu_type" : cpu_type, "date" : dt.strftime("%Y-%m-%dT%H:%M:%S"), "ppin" : ppin_list, "loop_count" : loop_count, "duration" : duration}

def build_map(path, map):
    count = 0
    for p in sorted(Path(path).iterdir(), key=os.path.getmtime):
        p = os.path.basename(p)
        for root, dir, files in os.walk(os.path.join(path, p)):
            if "report.txt" in files:
                #print("Processing", os.path.join(root, "report.txt"))
                if p not in map:
                    report_path = os.path.join(root, "report.txt")
                    count += 1
                    print("[%s] building[%d]  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, report_path))
                    d = parse_report(report_path)
                    if d:
                        map[p] = d
    return map

def save_map(path, map):
    with open(path, 'w') as fp:
        pretty_str = json.dumps(map, indent=4)
        fp.write(pretty_str)

def load_map(path):
    try:
        with open(path, 'r') as fp:
            map = json.load(fp)
            return map
    except IOError:
        return dict()

def dump_ppin_map(map, vendors):
    global dup_ppin
    global dup_sn
    ppin_map = {}
    ppin_count = {key : 0 for key in vendors}
    ppin_count["Total"] = 0
    for entry in map.keys():
        if map[entry]["cpu_type"] not in valid_cpu_type:
            continue
        if map[entry]["loop_count"] == 1:
            continue
        result = re.search(r"^([0-9A-Za-z\-]+)__.*_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
        if result:
            sn = result.groups()[0]
            if sn not in dup_sn:
                dup_sn[sn] = [map[entry]['date'],]
            else:
                dup_sn[sn].append(map[entry]['date'])
                dup_sn[sn].sort()
        else:
            print("Can't find a valid SN that should never happen", entry, file=sys.stderr)
        for ppin in map[entry]["ppin"]:
            if ppin not in ppin_map:
                ppin_map[ppin] = [map[entry]['date'],]
                ppin_count["Total"] += 1
                result = re.search(r"^[0-9A-Za-z\-]+__(.*)_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
                if not result:
                    print("Invalid path", entry, file=sys.stderr)
                else:
                    ppin_count[get_vendor_name(result.groups()[0], True)] += 1
            else:
                if ppin not in dup_ppin:
                    dup_ppin[ppin] = ppin_map[ppin]
                dup_ppin[ppin].append(map[entry]['date'])
                dup_ppin[ppin].sort()
    
    #for entry in dup_ppin:
    #    print(dup_ppin[entry])
    return ppin_count

def dump_ppin_map_by_month(map, year, month, vendors):
    global dup_ppin
    ppin_map = {}
    ppin_count = {key : 0 for key in vendors}
    ppin_count["Total"] = 0
    for entry in map.keys():
        if map[entry]["cpu_type"] not in valid_cpu_type:
            continue
        if map[entry]["loop_count"] == 1:
            continue
        for ppin in map[entry]["ppin"]:
            dt = datetime.fromisoformat(map[entry]["date"])
            if ppin in dup_ppin:
                dt = datetime.fromisoformat(dup_ppin[ppin][-1])
            if year == dt.year and month == dt.month:
                if ppin not in ppin_map:
                    ppin_map[ppin] = None
                    ppin_count["Total"] += 1
                    result = re.search(r"^[0-9A-Za-z\-]+__(.*)_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
                    if not result:
                        print("Invalid path", entry, file=sys.stderr)
                    else:
                        ppin_count[get_vendor_name(result.groups()[0], True)] += 1
    
    return ppin_count

def dump_ppin_map_till(map, fn, till):
    global dup_ppin
    ppin_map = {}
    ppin_map_per_mon = {}
    header = ['ppin', 'count']
    
    if till == "000000":
        ym = date.today()
        till = "%04d%02d" % (ym.year, ym.month)
    till = int(till)

    for entry in map.keys():
        if map[entry]["cpu_type"] not in valid_cpu_type:
            continue
        if map[entry]["loop_count"] != 4:
            continue
        
        for year in range(2022, 2024):
            for month in range(1, 13):
                date_ym = "%04d%02d" % (year, month)
                if int(date_ym) > till:
                    break
                if date_ym not in ppin_map_per_mon:
                    ppin_map_per_mon[date_ym] = {}
                for ppin in map[entry]["ppin"]:
                    dt = datetime.fromisoformat(map[entry]["date"])
                    if ppin in dup_ppin:
                        dt = datetime.fromisoformat(dup_ppin[ppin][-1])

                    if year == dt.year and month == dt.month:
                        if ppin not in ppin_map_per_mon[date_ym]:
                            ppin_map_per_mon[date_ym][ppin] = 1
                            if ppin in dup_ppin:
                                ppin_map_per_mon[date_ym][ppin] = len(dup_ppin[ppin])
                        if ppin not in ppin_map:
                            ppin_map[ppin] = 1
                            if ppin in dup_ppin:
                                ppin_map[ppin] = len(dup_ppin[ppin])
    
    try:
        fn = fn.rstrip('xlsx') + str(till) + '.xlsx'
        writer = pd.ExcelWriter(fn, engine='xlsxwriter')
        if len(ppin_map) > 0:
            ppin_df = pd.DataFrame(list(ppin_map.items()), columns=header)
            ppin_df.to_excel(writer, index=False, sheet_name='full')
        for year in range(2022, 2024):
            for month in range(1, 13):
                date_ym = "%04d%02d" % (year, month)
                if int(date_ym) > till:
                    break
                if date_ym in ppin_map_per_mon and len(ppin_map_per_mon[date_ym]) > 0:
                    ppin_df = pd.DataFrame(list(ppin_map_per_mon[date_ym].items()), columns=header)
                    ppin_df.to_excel(writer, index=False, sheet_name=date_ym)
        writer.close()
    except Exception as error:
        print("Error writing into excel file", fn)
        return
    
    return

def dump_sn_map_till(map, fn, till):
    global dup_sn
    sn_map = {}
    sn_map_per_mon = {}
    header = ['sn', 'count']
    
    if till == "000000":
        ym = date.today()
        till = "%04d%02d" % (ym.year, ym.month)
    till = int(till)

    for entry in map.keys():
        if map[entry]["cpu_type"] not in valid_cpu_type:
            continue
        if map[entry]["loop_count"] != 4:
            continue
        
        result = re.search(r"^([0-9A-Za-z\-]+)__.*_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
        if not result:
            continue
        sn = result.groups()[0]
        
        dt = datetime.fromisoformat(map[entry]["date"])
        if sn in dup_sn:
            dt = datetime.fromisoformat(dup_sn[sn][-1])
        
        for year in range(2022, 2024):
            for month in range(1, 13):
                date_ym = "%04d%02d" % (year, month)
                if int(date_ym) > till:
                    break
                if date_ym not in sn_map_per_mon:
                    sn_map_per_mon[date_ym] = {}
                if year == dt.year and month == dt.month:
                    if sn not in sn_map_per_mon[date_ym]:
                        sn_map_per_mon[date_ym][sn] = len(dup_sn[sn])
                    if sn not in sn_map:
                        sn_map[sn] = len(dup_sn[sn])
    try:
        fn = fn.rstrip('xlsx') + str(till) + '.xlsx'
        writer = pd.ExcelWriter(fn, engine='xlsxwriter')
        if len(sn_map) > 0:
            sn_df = pd.DataFrame(list(sn_map.items()), columns=header)
            sn_df.to_excel(writer, index=False, sheet_name='full')
        for year in range(2022, 2024):
            for month in range(1, 13):
                date_ym = "%04d%02d" % (year, month)
                if int(date_ym) > till:
                    break
                if date_ym in sn_map_per_mon and len(sn_map_per_mon[date_ym]) > 0:
                    sn_df = pd.DataFrame(list(sn_map_per_mon[date_ym].items()), columns=header)
                    sn_df.to_excel(writer, index=False, sheet_name=date_ym)
        writer.close()
    except Exception as error:
        print("Error writing into excel file", fn)
        return

def dump_ppin_map_2p5(map, vendors):
    ppin_map = {}
    ppin_count = {key : 0 for key in vendors}
    ppin_count["Total"] = 0
    for entry in map.keys():
        if map[entry]["cpu_type"] not in valid_cpu_type:
            continue
        if map[entry]["loop_count"] == 1:
            #if entry.find("_2p5_") < 0:
            #    print("Warning! inconsistent loop count and 2p5", entry, file=sys.stderr)
            for ppin in map[entry]["ppin"]:
                if ppin not in ppin_map:
                    ppin_map[ppin] = None
                    ppin_count["Total"] += 1
                    result = re.search(r"^[0-9A-Za-z\-]+__(.*)_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
                    if not result:
                        print("Invalid path", entry, file=sys.stderr)
                    else:
                        ppin_count[get_vendor_name(result.groups()[0], True)] += 1

    return ppin_count

def dump_ppin_map_non_valid_cpu_type(map, vendors, print_non_valid):
    ppin_map = {}
    ppin_count = {key : 0 for key in vendors}
    ppin_count["Total"] = 0
    cpu_type_list = {}
    for entry in map.keys():
        if map[entry]["cpu_type"] not in cpu_type_list:
            cpu_type_list[map[entry]["cpu_type"]] = [entry, ]
        else:
            cpu_type_list[map[entry]["cpu_type"]].append(entry)
        if map[entry]["cpu_type"] != "SPR-E5":
            for ppin in map[entry]["ppin"]:
                if ppin not in ppin_map:
                    ppin_map[ppin] = None
                    ppin_count["Total"] += 1
                    result = re.search(r"^[0-9A-Za-z\-]+__(.*)_shc_report_.*[0-9]{4}-[0-9]+-[0-9]+-[0-9]+-[0-9]+-[0-9]+", entry)
                    if not result:
                        print("Invalid path", entry, file=sys.stderr)
                    else:
                        ppin_count[get_vendor_name(result.groups()[0], True)] += 1
    
    if print_non_valid:
        for x in cpu_type_list:
            if x not in valid_cpu_type:
                print("%s : [size : %d, list : %s]" % \
                    (x, len(cpu_type_list[x]), str(cpu_type_list[x])))
    
    return ppin_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", "-d", required=False, default="/opt/spr-100k-logs/unzipped_log", help="unzipped shc logs folder")
    parser.add_argument("--outfile", "-o", required=False, default="/home/ysheng4/Downloads/ppin.map", help="the output mapping file")
    parser.add_argument("--build", "-b", required=False, default=False, action='store_true', help="to build the un-parsed logs")
    parser.add_argument("--print_non_valid", "-p", required=False, default=False, action='store_true', help="to print the non-valid logs (e.g. SPR-E3)")
    parser.add_argument("--till", "-t", required=False, default="000000", help="please use YYYYMM as input (e.g. 202309)")
    parser.add_argument("--ppin_list", required=False, default=False, action='store_true', help="to print the ppin list in total and per month")
    parser.add_argument("--sn_list", required=False, default=False, action='store_true', help="to print the serial number list in total and per month")
    args = parser.parse_args()

    print("Starting at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    map = load_map(args.outfile)
    if args.build:
        map = build_map(args.directory, map)
        map = build_map(args.directory + "_emr", map)
        save_map(args.outfile, map)

    header = ["Total", *vendor_list]
    # Title
    print("                ", end="")
    for v in header:
        print("%10s" % (v), end="")
    print("")
    
    # SPR
    print("---------------------------------------------- SPR ----------------------------------------------")
    c = dump_ppin_map_non_valid_cpu_type(map, vendor_list, args.print_non_valid)
    print("Non valid PPIN #", end="")
    for v in header:
        print("%10d" % (c[v]), end="")
    print("")
    c = dump_ppin_map_2p5(map, vendor_list)
    print("2p5       PPIN #", end="")
    for v in header:
        print("%10d" % (c[v]), end="")
    print("")

    c = dump_ppin_map(map, vendor_list)
    print("Total     PPIN #", end="")
    for v in header:
        print("%10d" % (c[v]), end="")
    print("")
    for year in range(2022, 2025):
        for month in range(1, 13):
            c = dump_ppin_map_by_month(map, year, month, vendor_list)
            if c and c["Total"] > 0:
                #print("[", year, month, "]", "PPIN #", c)
                print("[%04d %02d] PPIN #" % (year, month), end="")
                for v in header:
                    print("%10d" % (c[v]), end="")
                print("")

    if args.ppin_list:
        dump_ppin_map_till(map, 'ppin-map.xlsx', args.till)
    if args.sn_list:
        dump_sn_map_till(map, 'sn-map.xlsx', args.till)
    
    # EMR
    print("---------------------------------------------- EMR ----------------------------------------------")
    valid_cpu_type = emr_cpu_type
    c = dump_ppin_map_2p5(map, vendor_list)
    print("2p5       PPIN #", end="")
    for v in header:
        print("%10d" % (c[v]), end="")
    print("")

    c = dump_ppin_map(map, vendor_list)
    print("Total     PPIN #", end="")
    for v in header:
        print("%10d" % (c[v]), end="")
    print("")
    for year in range(2022, 2025):
        for month in range(1, 13):
            c = dump_ppin_map_by_month(map, year, month, vendor_list)
            if c and c["Total"] > 0:
                #print("[", year, month, "]", "PPIN #", c)
                print("[%04d %02d] PPIN #" % (year, month), end="")
                for v in header:
                    print("%10d" % (c[v]), end="")
                print("")
    
    print("By", time.ctime(os.path.getmtime('/home/ysheng4/Downloads/ppin.map')))
