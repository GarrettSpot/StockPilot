# StockPilot Terraform

Provisions the AWS networking and EKS cluster for StockPilot:

- VPC (`10.30.0.0/16`) with two public and two private subnets
- NAT gateway (single, to control cost)
- EKS cluster with one managed node group

```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
terraform destroy
```

> **Cost warning:** an EKS cluster + NAT gateway + worker nodes incur AWS charges.
> Run `terraform destroy` as soon as the demo is finished.
