# =========================================================================
# Copyright (C) 2016-2023 LOGPAI (https://github.com/logpai).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================


import sys
sys.path.append("../../")
from logparser.Drain import LogParser
from logparser.utils import evaluator
import os
import pandas as pd
import re


input_dir = "../../data/loghub_2k/"  # The input directory of log file
output_dir = "Drain_result/"  # The output directory of parsing results


benchmark_settings = {
    "Linux": {
        "log_file": "Linux/Linux_shc_messages.log",
        "log_format": "<Month> <Date> <Time> <Level> <Component>:( \[<TSC>\]\[<PID>\])? <Content>",
        #"regex": [r"(\d+\.){3}\d+", r"\d{2}:\d{2}:\d{2}", r"(0x[0-9a-zA-Z]+-0x[0-9a-zA-Z]+)", r"([0-9]+) callbacks suppressed"],
        "regex": {r"(\d+\.){3}\d+" : "<*>", # IP
            r"\d{2}:\d{2}:\d{2}" : "<*>", # time
            r"#011" : "", # escape char
            r"\.obj algo \(" : ".obj-algo-(", # avoid tsl test being messed up
            r"(0x[0-9a-zA-Z]+-0x[0-9a-zA-Z]+)" : "<*>", # memory range
            r"([0-9]+) callbacks suppressed" : "<*> callbacks suppressed", # callbacks should be generic
            r"process ([0-9]+) \([0-9a-zA-Z]+\) " : "process: [<*>] ", # process id should be generic
            r"\[(id:)?[0-9a-zA-Z]{4}\]" : "[<*>]", # test id
            r"Sub-TEST ID: [0-9a-zA-Z]{4}" : "Sub-TEST ID: <*>", # test id
            r"ok +[0-9]+ " : "ok <*> ", # test sequence number
            r"\[sandstone\]\[.*\] test-runtime: [0-9]+\.[0-9]+" : "[sandstone][<*>] test-runtime: <*>" # 
            },
        "st": 0.39,
        "depth": 6,
    },
}

class LogParserEx(LogParser):
    def preprocess(self, line):
        for currentRex in self.rex:
            line = re.sub(currentRex, self.rex[currentRex], line)
        return line

bechmark_result = []
for dataset, setting in benchmark_settings.items():
    print("\n=== Evaluation on %s ===" % dataset)
    #indir = os.path.join(input_dir, os.path.dirname(setting["log_file"]))
    indir = sys.argv[1]
    #log_file = os.path.basename(setting["log_file"])
    log_file = sys.argv[2]
    output_dir = sys.argv[3]

    parser = LogParserEx(
        log_format=setting["log_format"],
        indir=indir,
        outdir=output_dir,
        rex=setting["regex"],
        depth=setting["depth"],
        st=setting["st"],
    )
    parser.parse(log_file)


