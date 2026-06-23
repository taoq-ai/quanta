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
        model_id = _ctx(self, "bedrock_model_id", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        create_oidc = _ctx(self, "create_oidc_provider", "true").lower() != "false"

        # ── GitHub Actions OIDC provider (create or reference existing) ─────
        provider_url = "https://token.actions.githubusercontent.com"
        oidc_provider: iam.IOpenIdConnectProvider
        if create_oidc:
            oidc_provider = iam.OpenIdConnectProvider(
                self,
                "GitHubOidcProvider",
                url=provider_url,
                client_ids=["sts.amazonaws.com"],
            )
        else:
            arn = f"arn:aws:iam::{self.account}:oidc-provider/token.actions.githubusercontent.com"
            oidc_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self, "GitHubOidcProviderExisting", arn
            )

        github_principal = iam.OpenIdConnectPrincipal(
            oidc_provider,
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
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/{model_id}",
                    f"arn:aws:bedrock:*::foundation-model/{model_id}",
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
                actions=[
                    "s3:CreateBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:GetBucketLocation",
                    "s3:PutBucketPolicy",
                    "s3:PutEncryptionConfiguration",
                ],
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
