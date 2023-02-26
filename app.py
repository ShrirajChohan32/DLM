#!/usr/bin/env python3

import aws_cdk as cdk

from life_cycle.life_cycle_stack import LifeCycleStack

env_dev=cdk.Environment(account='1234567890', region='ap-southeast-2')

app = cdk.App()
LifeCycleStack(app, "life-cycle",env=env_dev)

app.synth()
