import sys

vendor_list = ["Alibaba", "ByteDance", "Inspur", "JD-Cloud", "Baidu", "Tencent", "Unknown"]

prodname_to_vendor = {
"AliServer-Xuanwu1.5-02-2U16HD2P" : "Alibaba",
"AliServer-Xuanwu2.0-00-1UCG42PF" : "Alibaba",
"AliServer-Xuanwu2.0-00-1UCG52PF" : "Alibaba",
"AliServer-Xuanwu2.0-00-3UGG52PF" : "Alibaba",
"AliServer-Xuanwu2.0-02-1UCG52PF" : "Alibaba",
"AliServer-Xuanwu2.0-02-2UMG52PF" : "Alibaba",
"AliServer-Xuanwu2.0-02-3UGG52PF" : "Alibaba",
"AliServer-Xuanwu2.0-0323-2URG52PF" : "Alibaba",
"AS2111TG5" : "Alibaba",
"AS2211TG5" : "Alibaba",
"AS2311TG5" : "Alibaba",
"ByteDance-System" : "ByteDance",
"G220-B3" : "ByteDance",
"G220-B3-F" : "ByteDance",
"J360-G3" : "JD-Cloud",
"0" : "Inspur",
"M120-B3" : "Inspur",
"NA" : "Inspur",
"NF5170-M7-A0-R0-00" : "Inspur",
"NF5180M7" : "Inspur",
"NF5180-M7-A0-F0-00" : "Inspur",
"NF5180-M7-A0-R0-00" : "Inspur",
"NF5180-M7-C0-R0-00" : "Inspur",
"NF5266-M7-A0-R0-00" : "Inspur",
"NF5270-M7-A0-R0-00" : "Inspur",
"NF5280M7" : "Inspur",
"NF5280-M7-A0-F0-00" : "Inspur",
"NF5280-M7-A0-R0-00" : "Inspur",
"NF5280M7C" : "Inspur",
"NF5280-M7-C0-R0-00" : "Inspur",
"NF5466-M7-A0-R0-00" : "Inspur",
"NF5468M7" : "Inspur",
"NF5468-M7-A0-R0-00" : "Inspur",
"NF5476-M7-A0-R0-00" : "Inspur",
"NF5688M7" : "Inspur",
"NF5688-M7-A0-R0-00" : "Inspur",
"NF5688-M7-C0-R0-00" : "Inspur",
"NF5698-M7-A0-R0-00" : "Inspur",
"NF8260M7" : "Inspur",
"NF8260-M7-A0-R0-00" : "Inspur",
"NF8480-M7-A0-R0-00" : "Inspur",
"NS5170-M7-A0-R0-00" : "Inspur",
"NS5170-M7-C0-R0-00" : "Inspur",
"NULL" : "Inspur",
"S520-B3" : "ByteDance",
"SA5212-M7-A0-R0-00" : "Inspur",
"SA5290M7L" : "Alibaba",
"SC5212-M7-A0-R0-00" : "Inspur",
"SSIEISYSTEMHBX-GN7-400-I688" : "Baidu",
"SSIEISYSTEMMA2T-XI7-100D" : "Baidu",
"SSIEISYSTEMA12T-XI7-400D" : "Inspur",
"SSIEISYSTEMA12T-XI7-400D-1" : "Inspur",
"SSIEISYSTEMA12T-XI7-400D-L" : "Inspur",
"TS860-M7-A0-R0-00" : "Inspur",
"XC222" : "Tencent",
"XG262" : "Tencent"}

def get_vendor_name(prod_name):
    if prod_name in prodname_to_vendor:
        return prodname_to_vendor[prod_name]
    else:
        #print("Warning! can't recognize the product name", prod_name, file=sys.stderr)
        return "Unknown"

if __name__ == "__main__":
    print(get_vendor_name(sys.argv[1]))

