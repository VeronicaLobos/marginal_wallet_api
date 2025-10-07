# This resource generates a short, random string that will be appended
# to all resource names. This ensures that every deployment is unique and
# avoids naming conflicts from previously failed runs.

resource "random_string" "suffix" {
  length  = 4
  special = false
  upper   = false
}
