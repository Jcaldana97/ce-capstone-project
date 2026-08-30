terraform {
  backend "s3" {
    bucket         = "ce-bootcamp-tfstate-juliocesaraldana"
    key            = "capstone-project/terraform.tfstate"
    region         = "us-east-1"
 
    use_lockfile = true
    encrypt      = true
  }
}