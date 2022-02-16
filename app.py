#!/usr/bin/env python3

import aws_cdk as cdk

from life_cycle.life_cycle_stack import LifeCycleStack


app = cdk.App()
LifeCycleStack(app, "life-cycle")

app.synth()
