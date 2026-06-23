"""Quanta IAM bootstrap stack.

EDUCATIONAL DEMO: the deploy-role policy is intentionally broad so
`agentcore launch` (which creates ECR repos, a CodeBuild project and helper
roles on the fly) works without hand-holding. Tighten before production use.
"""

from __future__ import annotations

import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct


def _ctx(scope: Construct, key: str, default: str) -> str:
    value = scope.node.try_get_context(key)
    return default if value is None else str(value)


class QuantaBootstrapStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: object) -> None:
        super().__init__(scope, construct_id, **kwargs)

        org = _ctx(self, "github_org", "taoq-ai")
        repo = _ctx(self, "github_repo", "quanta")
        ref = _ctx(self, "github_ref", "*")
        create_oidc = _ctx(self, "create_oidc_provider", "true").lower() != "false"

        # ── GitHub Actions OIDC provider (create or reference existing) ─────
        # Use the native L1 resource (no Lambda-backed custom resource), so the
        # stack has no assets and needs no `cdk bootstrap` S3 bucket.
        cfn_oidc: iam.CfnOIDCProvider | None = None
        if create_oidc:
            cfn_oidc = iam.CfnOIDCProvider(
                self,
                "GitHubOidcProvider",
                url="https://token.actions.githubusercontent.com",
                client_id_list=["sts.amazonaws.com"],
                thumbprint_list=[
                    "6938fd4d98bab03faadb97b34396831e3780aea1",
                    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
                ],
            )
            provider_arn = cfn_oidc.attr_arn
        else:
            provider_arn = (
                f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com"
            )

        github_principal = iam.FederatedPrincipal(
            provider_arn,
            assume_role_action="sts:AssumeRoleWithWebIdentity",
            conditions={
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": f"repo:{org}/{repo}:{ref}",
                },
            },
        )

        # ── AgentCore runtime execution role (assumed by the running agent) ─
        execution_role = iam.Role(
            self,
            "AgentCoreExecutionRole",
            role_name=f"AmazonBedrockAgentCore-{repo}-exec",
            description="Runtime execution role for the Quanta AgentCore agent.",
            assumed_by=iam.ServicePrincipal(
                "bedrock-agentcore.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": self.account},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{self.region}:{self.account}:*"
                    },
                },
            ),
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                sid="InvokeBedrockModel",
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                # Cover both direct foundation models and cross-region inference
                # profiles (EU regions require an inference profile for Claude).
                resources=[
                    "arn:aws:bedrock:*::foundation-model/anthropic.*",
                    f"arn:aws:bedrock:*:{self.account}:inference-profile/*",
                ],
            )
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                sid="PullContainerImage",
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchCheckLayerAvailability",
                ],
                resources=["*"],
            )
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                sid="Observability",
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                    "logs:DescribeLogGroups",
                    "cloudwatch:PutMetricData",
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets",
                ],
                resources=["*"],
            )
        )
        execution_role.add_to_policy(
            iam.PolicyStatement(
                sid="WorkloadIdentity",
                actions=[
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                resources=["*"],
            )
        )

        # ── GitHub Actions deploy role (assumed by CI via OIDC) ─────────────
        deploy_role = iam.Role(
            self,
            "GitHubDeployRole",
            role_name="quanta-github-deploy",
            description="Assumed by GitHub Actions to deploy Quanta to AgentCore.",
            assumed_by=github_principal,
            max_session_duration=cdk.Duration.hours(1),
        )
        if cfn_oidc is not None:
            deploy_role.node.add_dependency(cfn_oidc)
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="AgentCoreControlPlane", actions=["bedrock-agentcore:*"], resources=["*"]
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(sid="ContainerRegistry", actions=["ecr:*"], resources=["*"])
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="CodeBuildImageBuild",
                actions=[
                    "codebuild:CreateProject",
                    "codebuild:UpdateProject",
                    "codebuild:DeleteProject",
                    "codebuild:StartBuild",
                    "codebuild:BatchGetBuilds",
                    "codebuild:BatchGetProjects",
                    "codebuild:ListBuildsForProject",
                ],
                resources=["*"],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="CodeBuildSourceBucket",
                # Scoped to the toolkit's own source bucket; broad actions there
                # cover create/encrypt/lifecycle/tag/version the toolkit sets.
                actions=["s3:*"],
                resources=[
                    "arn:aws:s3:::bedrock-agentcore-codebuild-sources-*",
                    "arn:aws:s3:::bedrock-agentcore-codebuild-sources-*/*",
                ],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="Logs",
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:GetLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams",
                    # Vended-log delivery for AgentCore Memory observability.
                    "logs:PutDeliverySource",
                    "logs:PutDeliveryDestination",
                    "logs:PutDeliveryDestinationPolicy",
                    "logs:CreateDelivery",
                    "logs:GetDelivery",
                    "logs:GetDeliverySource",
                    "logs:GetDeliveryDestination",
                    "logs:DescribeDeliveries",
                    "logs:DescribeDeliverySources",
                    "logs:DescribeDeliveryDestinations",
                    "logs:PutResourcePolicy",
                    "logs:DescribeResourcePolicies",
                ],
                resources=["*"],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="HelperRoleManagement",
                actions=[
                    "iam:CreateRole",
                    "iam:GetRole",
                    "iam:TagRole",
                    "iam:PutRolePolicy",
                    "iam:GetRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:AttachRolePolicy",
                    "iam:DetachRolePolicy",
                    "iam:ListRolePolicies",
                    "iam:ListAttachedRolePolicies",
                    "iam:CreateServiceLinkedRole",
                ],
                resources=[
                    f"arn:aws:iam::{self.account}:role/AmazonBedrockAgentCore*",
                    f"arn:aws:iam::{self.account}:role/service-role/AmazonBedrockAgentCore*",
                    f"arn:aws:iam::{self.account}:role/codebuild-bedrock-agentcore*",
                ],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="PassRuntimeAndBuildRoles",
                actions=["iam:PassRole"],
                resources=[
                    execution_role.role_arn,
                    f"arn:aws:iam::{self.account}:role/AmazonBedrockAgentCore*",
                    f"arn:aws:iam::{self.account}:role/codebuild-bedrock-agentcore*",
                ],
                conditions={
                    "StringEquals": {
                        "iam:PassedToService": [
                            "bedrock-agentcore.amazonaws.com",
                            "codebuild.amazonaws.com",
                        ]
                    }
                },
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="AgentCoreServiceLinkedRole",
                # CreateAgentRuntime provisions one or more service-linked roles
                # under aws-service-role/ (e.g. *BedrockAgentCoreGatewayNetwork,
                # *BedrockAgentCoreRuntime). Allow any SLR so it isn't blocked by
                # a too-narrow service-name/path match.
                actions=["iam:CreateServiceLinkedRole"],
                resources=["arn:aws:iam::*:role/aws-service-role/*"],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="Identity",
                actions=["sts:GetCallerIdentity", "ssm:GetParameter", "ssm:GetParameters"],
                resources=["*"],
            )
        )

        # ── Outputs ─────────────────────────────────────────────────────────
        cdk.CfnOutput(
            self,
            "DeployRoleArn",
            value=deploy_role.role_arn,
            description="Set as GitHub repo variable AWS_DEPLOY_ROLE_ARN.",
        )
        cdk.CfnOutput(
            self,
            "ExecutionRoleArn",
            value=execution_role.role_arn,
            description="Set as GitHub repo variable AGENTCORE_EXECUTION_ROLE_ARN.",
        )
        cdk.CfnOutput(self, "Region", value=self.region, description="Bootstrap region.")
