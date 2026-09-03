package test

import (
	"context"
	"testing"

	awsSdk "github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	ec2sdk "github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/aws/aws-sdk-go-v2/service/ec2/types"

	"github.com/gruntwork-io/terratest/modules/aws"
	"github.com/gruntwork-io/terratest/modules/terraform"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNetworkingModule(t *testing.T) {
	t.Parallel()

	terraformOptions := &terraform.Options{
		TerraformDir: "../../terraform/modules/networking",

		Vars: map[string]interface{}{
			"project_name": "terratest",
			"environment": "test",
			"vpc_cidr": "10.50.0.0/16",
			"availability_zones": []string{"us-east-1a", "us-east-1b"},
			"public_subnet_cidrs": []string{"10.50.1.0/24", "10.50.2.0/24"},
			"app_subnet_cidrs": []string{"10.50.11.0/24", "10.50.12.0/24"},
			"data_subnet_cidrs": []string{"10.50.21.0/24", "10.50.22.0/24"},
			"enable_nat_gateway": true,
			"single_nat_gateway": true,
			"tags": map[string]string{
				"Owner": "Terratest",
			},
		},
	}

	defer terraform.Destroy(t, terraformOptions)

	terraform.InitAndApply(t, terraformOptions)

	// Read outputs
	vpcID := terraform.Output(t, terraformOptions, "vpc_id")

	// Verify VPC
	vpc := aws.GetVpcById(t, vpcID, "us-east-1")
	assert.Equal(t, "10.50.0.0/16", vpc.CidrBlock)

	// Verify subnet count
	subnets := aws.GetSubnetsForVpc(t, vpcID, "us-east-1")
	assert.Len(t, subnets, 6)

	// AWS SDK v2 configuration
	cfg, err := config.LoadDefaultConfig(
		context.TODO(),
		config.WithRegion("us-east-1"),
	)
	require.NoError(t, err)

	ec2Client := ec2sdk.NewFromConfig(cfg)

	// Describe NAT Gateways in the VPC
	natResult, err := ec2Client.DescribeNatGateways(
		context.TODO(),
		&ec2sdk.DescribeNatGatewaysInput{
			Filter: []types.Filter{
				{
					Name: awsSdk.String("vpc-id"),
					Values: []string{vpcID},
				},
			},
		},
	)
	require.NoError(t, err)

	assert.Len(t, natResult.NatGateways, 1)
}