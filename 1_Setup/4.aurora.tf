resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "aurora_subnet_group"
  subnet_ids = [module.vpc.private_subnets[0], module.vpc.private_subnets[1]]
}

module "aurora" {
  source  = "terraform-aws-modules/rds-aurora/aws"

  name           = "aurora-db-mysql"
  engine         = "aurora-mysql"
  engine_version = "8.0"
  instance_class = "db.r6g.large"
  instances     = {
    one = {}
  }

  master_username             = "admin"
  master_password             = "Administrator"
  manage_master_user_password = false
  database_name               = "airflow"
  vpc_id                      = module.vpc.vpc_id
  db_subnet_group_name        = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids      = split(" ", module.security_group_aurora.security_group_id)
  skip_final_snapshot         = true
  apply_immediately           = true

  depends_on = [ module.vpc, module.security_group_aurora ]

}