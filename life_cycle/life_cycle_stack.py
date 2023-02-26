from unicodedata import name
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_ec2 as ec2,
    aws_dlm as dlm,
    aws_sns_subscriptions as subs,
)
import aws_cdk as cdk

vpcID= "vpc-5eb64e38" # Can't hardcore VPC ID, variabe File)
ExistingEBS="vol-036b9ac1db520fc4e" 

class LifeCycleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Build VPC
        # vpc = ec2.Vpc.from_lookup(self,"vpc",vpc_id=vpcID,)

        # EBS Volume
        volume = ec2.Volume.from_volume_attributes(self,"EBS",availability_zone="ap-southeast-2a",volume_id=ExistingEBS)
        volume = ec2.Volume(self, "Volume",
            availability_zone="ap-southeast-2a",
            size=cdk.Size.gibibytes(8),
            encrypted=True)

        cdk.Tags.of(volume).add("backup", "yes")

        cfn_lifecycle_policy = dlm.CfnLifecyclePolicy(self, "MyCfnLifecyclePolicy",
            description="description",
            execution_role_arn='arn:aws:iam::%s:role/service-role/AWSDataLifecycleManagerDefaultRole' % self.account,
            policy_details=dlm.CfnLifecyclePolicy.PolicyDetailsProperty(
                policy_type="EBS_SNAPSHOT_MANAGEMENT",
                resource_types=["VOLUME"],
                schedules=[dlm.CfnLifecyclePolicy.ScheduleProperty(
                    name='DLM_POLICY',
                    copy_tags=False,
                    create_rule=dlm.CfnLifecyclePolicy.CreateRuleProperty(
        #                 # cron_expression="cron(15 12 * * ? *)",
                        interval=1,
                        interval_unit="HOURS",
                        location="CLOUD",
                        times=["17:47"]),
                    retain_rule=dlm.CfnLifecyclePolicy.RetainRuleProperty(
                        count=2))],
                target_tags=[cdk.CfnTag(
                    key="backup",
                    value="yes")]
            ),
            state='ENABLED',
            tags=[cdk.CfnTag(
                key="testing",
                value="yes"
            )]
        )