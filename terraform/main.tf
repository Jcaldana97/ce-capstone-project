terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc_dev" {
  source = "./modules/networking"

  project_name        = var.project_name
  environment         = var.environment
  availability_zones  = var.availability_zones
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  app_subnet_cidrs    = var.app_subnet_cidrs
  data_subnet_cidrs   = var.data_subnet_cidrs

  enable_nat_gateway = true
  single_nat_gateway = true # Cost savings for dev
}

module "security_groups" {
  source = "./modules/security-groups"

  project_name = var.project_name
  vpc_id       = module.vpc_dev.vpc_id
}

module "alb" {
  source = "./modules/alb"

  project_name          = var.project_name
  vpc_id                = module.vpc_dev.vpc_id
  security_group_alb_id = module.security_groups.alb_security_group_id
  alb_public_subnet_id  = module.vpc_dev.public_subnet_ids[0]
}