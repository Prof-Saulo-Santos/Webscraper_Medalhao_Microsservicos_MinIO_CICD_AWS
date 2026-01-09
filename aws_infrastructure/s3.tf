resource "aws_s3_bucket" "bronze" {
  bucket = "arxiv-lake-bronze-${var.environment}"
  force_destroy = true # Apenas para ambiente acadêmico/dev
  
  tags = {
    Layer = "Bronze"
  }
}

resource "aws_s3_bucket" "silver" {
  bucket = "arxiv-lake-silver-${var.environment}"
  force_destroy = true 

  tags = {
    Layer = "Silver"
  }
}
