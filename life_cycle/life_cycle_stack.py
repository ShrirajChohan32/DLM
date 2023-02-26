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

        policy_doc = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ec2:CreateSnapshot",
                        "ec2:CreateSnapshots",
                        "ec2:DeleteSnapshot",
                        "ec2:DescribeInstances",
                        "ec2:DescribeVolumes",
                        "ec2:DescribeSnapshots",
                        "ec2:EnableFastSnapshotRestores",
                        "ec2:DescribeFastSnapshotRestores",
                        "ec2:DisableFastSnapshotRestores",
                        "ec2:CopySnapshot",
                        "ec2:ModifySnapshotAttribute",
                        "ec2:DescribeSnapshotAttribute",
                        "ec2:DescribeSnapshotTierStatus",
                        "ec2:ModifySnapshotTier"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "ec2:CreateTags"
                    ],
                    resources=["arn:aws:ec2:*::snapshot/*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "events:PutRule",
                        "events:DeleteRule",
                        "events:DescribeRule",
                        "events:EnableRule",
                        "events:DisableRule",
                        "events:ListTargetsByRule",
                        "events:PutTargets",
                        "events:RemoveTargets"
                    ],
                    resources=["arn:aws:events:*:*:rule/AwsDataLifecycleRule.managed-cwe.*"]
                )
            ]
        )

        role = iam.Role(
            self, "MyRole",
            assumed_by=iam.ServicePrincipal("dlm.amazonaws.com"),
            inline_policies={
                "MyPolicy": policy_doc
            }
        )

        cdk.CfnOutput(self,"MyRoleName",value=role.role_arn)


        cfn_lifecycle_policy = dlm.CfnLifecyclePolicy(self, "MyCfnLifecyclePolicy",
            description="description",
            execution_role_arn=role.role_arn,
            # execution_role_arn='arn:aws:iam::%s:role/MyRole' % self.account
            # execution_role_arn='arn:aws:iam::%s:role/service-role/AWSDataLifecycleManagerDefaultRole' % self.account,
            policy_details=dlm.CfnLifecyclePolicy.PolicyDetailsProperty(
                policy_type="EBS_SNAPSHOT_MANAGEMENT",
                resource_types=["VOLUME"],
                schedules=[dlm.CfnLifecyclePolicy.ScheduleProperty(
                    name='DLM_POLICY',
                    copy_tags=False,
                    create_rule=dlm.CfnLifecyclePolicy.CreateRuleProperty(
        #                 # cron_expression="cron(15 12 * * ? *)", for more customised 
                        interval=1,
                        interval_unit="HOURS",
                        location="CLOUD",
                        times=["07:40"]),
                    retain_rule=dlm.CfnLifecyclePolicy.RetainRuleProperty(
                        count=2))],
                target_tags=[cdk.CfnTag(
                    key="backup",
                    value="yes")]
            ),
            state='ENABLED',
            tags=[cdk.CfnTag(
                key="backup",
                value="yes"
            )]
        )