# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2012-2013 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os
import sys

logging.basicConfig(level=logging.ERROR)

top_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       os.pardir,
                                       os.pardir))
sys.path.insert(0, top_dir)

import taskflow.engines
from taskflow.patterns import graph_flow as gf
from taskflow.patterns import linear_flow as lf
from taskflow import task


# In this example there are complex dependencies between
# tasks. User shouldn't care about ordering the Tasks.
# GraphFlow resolves dependencies automatically using tasks'
# requirements and provided values.
# Flows of any types can be nested into Graph flow. Subflows
# dependencies will be resolved too.


class Adder(task.Task):

    def execute(self, x, y):
        return x + y


flow = gf.Flow('root').add(
    lf.Flow('nested_linear').add(
        # x2 = y3+y4 = 12
        Adder("add2", provides='x2', rebind=['y3', 'y4']),
        # x1 = y1+y2 = 4
        Adder("add1", provides='x1', rebind=['y1', 'y2'])
    ),
    # x5 = x1+x3 = 20
    Adder("add5", provides='x5', rebind=['x1', 'x3']),
    # x3 = x1+x2 = 16
    Adder("add3", provides='x3', rebind=['x1', 'x2']),
    # x4 = x2+y5 = 21
    Adder("add4", provides='x4', rebind=['x2', 'y5']),
    # x6 = x5+x4 = 41
    Adder("add6", provides='x6', rebind=['x5', 'x4']),
    # x7 = x6+x6 = 82
    Adder("add7", provides='x7', rebind=['x6', 'x6']))

store = {
    "y1": 1,
    "y2": 3,
    "y3": 5,
    "y4": 7,
    "y5": 9,
}

result = taskflow.engines.run(
    flow, engine_conf='serial', store=store)

print("Single threaded engine result %s" % result)

result = taskflow.engines.run(
    flow, engine_conf='parallel', store=store)

print("Multi threaded engine result %s" % result)
