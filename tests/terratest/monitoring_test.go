package test

import (
	"context"
	"testing"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatchlogs"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMonitoringModule(t *testing.T) {
	t.Parallel()

	terraformOptions := &terraform.Options{
		TerraformDir: "../../terraform/modules/monitoring",

		Vars: map[string]interface{}{
			"project_name": "terratest",
			"environment":"test",
			"aws_region": "us-east-1",
			"alb_arn_suffix": "app/capstone-project-alb/2fdaf772217f4ac0",
			"target_group_arn_suffix": "targetgroup/capstone-project-app-tg/94223f8692b18327",
			"autoscaling_group_name": "capstone-project-app-asg",
		},
	}

	// Clean up after the test
	defer terraform.Destroy(t, terraformOptions)

	// Deploy infrastructure
	terraform.InitAndApply(t, terraformOptions)

	// Read Terraform output
	logGroupName := terraform.Output(t, terraformOptions, "application_log_group_name")

	// Create AWS SDK configuration
	cfg, err := config.LoadDefaultConfig(
		context.TODO(),
		config.WithRegion("us-east-1"),
	)
	require.NoError(t, err)

	// Create CloudWatch Logs client
	client := cloudwatchlogs.NewFromConfig(cfg)

	// Query CloudWatch Log Groups
	result, err := client.DescribeLogGroups(
		context.TODO(),
		&cloudwatchlogs.DescribeLogGroupsInput{
			LogGroupNamePrefix: aws.String(logGroupName),
		},
	)
	require.NoError(t, err)

	// Verify the log group exists
	require.NotEmpty(t, result.LogGroups, "Log group was not found")

	assert.Equal(
		t,
		logGroupName,
		aws.ToString(result.LogGroups[0].LogGroupName),
	)
}