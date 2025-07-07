output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "elastic_ips" {
  description = "Elastic IPs assigned to services"
  value = {
    printers_service    = aws_eip.printers_service.public_ip
    monitoring_service  = aws_eip.monitoring_service.public_ip
    calibration_service = aws_eip.calibration_service.public_ip
  }
}

output "service_urls" {
  description = "URLs for accessing the services through ALB"
  value = {
    printers_service    = "http://${aws_lb.main.dns_name}:8000"
    monitoring_service  = "http://${aws_lb.main.dns_name}:8001"
    calibration_service = "http://${aws_lb.main.dns_name}:8002"
  }
}

output "service_docs_urls" {
  description = "URLs for accessing the service documentation"
  value = {
    printers_service    = "http://${aws_lb.main.dns_name}:8000/docs"
    monitoring_service  = "http://${aws_lb.main.dns_name}:8001/docs"
    calibration_service = "http://${aws_lb.main.dns_name}:8002/docs"
  }
}

output "database_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "database_connection_string" {
  description = "Database connection string (without password)"
  value       = "postgresql://${var.db_username}:***@${aws_db_instance.postgres.endpoint}/${var.db_name}"
  sensitive   = true
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "target_group_arns" {
  description = "ARNs of the ALB target groups"
  value = {
    printers    = aws_lb_target_group.printers.arn
    monitoring  = aws_lb_target_group.monitoring.arn
    calibration = aws_lb_target_group.calibration.arn
  }
}

output "security_group_ids" {
  description = "IDs of the security groups"
  value = {
    alb       = aws_security_group.alb.id
    services  = aws_security_group.services.id
    database  = aws_security_group.database.id
  }
}

output "cloudwatch_log_groups" {
  description = "Names of CloudWatch log groups"
  value = {
    printers    = aws_cloudwatch_log_group.printers.name
    monitoring  = aws_cloudwatch_log_group.monitoring.name
    calibration = aws_cloudwatch_log_group.calibration.name
  }
}

output "nat_gateway_ip" {
  description = "Public IP of the NAT Gateway"
  value       = aws_eip.nat.public_ip
}

output "deployment_summary" {
  description = "Summary of the deployment"
  value = {
    project_name    = var.project_name
    environment     = var.environment
    region          = var.aws_region
    vpc_cidr        = var.vpc_cidr
    public_subnets  = var.public_subnets
    private_subnets = var.private_subnets
    services = {
      printers_service    = "Running on ECS Fargate"
      monitoring_service  = "Running on ECS Fargate"
      calibration_service = "Running on ECS Fargate"
    }
    database = "PostgreSQL RDS"
    load_balancer = "Application Load Balancer"
    elastic_ips = "3 IPs elásticas asignadas"
  }
} 