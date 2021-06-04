## Setup Notes:

1. Assign EIP (Elastic IP) to your EC2 Machine. Follow [this guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html#using-instance-addressing-eips-allocating) to assign an EIP.
2. Create IAM Policy. Follow [this guide](https://docs.amazonaws.cn/en_us/IAM/latest/UserGuide/access_policies_create-console.html#access_policies_create-json-editor) to create IAM Policy. For step no. 5 of AWS guide, paste the following:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ec2:ReleaseAddress",
                "ec2:DeleteTags",
                "ec2:DescribeNetworkInterfaces",
                "ec2:CreateTags",
                "ec2:AssociateAddress",
                "ec2:AllocateAddress"
            ],
            "Resource": "*"
        }
    ]
}
```
3. Create IAM Role by following [this guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html#create-iam-role). For step number 4, of AWS guide, use the IAM Policy name just created in step number 2. 
4. Attach the created IAM Role to your EC2 Instance by following [this guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html#attach-iam-role).

## Running the script
Options:
1. **Docker**: Please refer readme of this repo. Please ensure you are passing `--network=host` while you run.
2. **CLI**: Please ensure your aws region is configured either via `aws configure` command or run the command `export AWS_DEFAULT_REGION=ap-south-1` before running the script. 


## Connecting to instance

As the EIP of the Instance will keep changing, you should not connect using the primary EIP. You can use one of the following methods:
1. **Private IP**: You can connect to another instance in same subnet and from there you can connect to the private IP of this instance.
   Steps:
   1. Boot another instance (lets call this secondary instance.)
   2. Start ssh-agent. Command: `ssh-agent -s`
   3. SSH Add keys of primary instance. Command: `ssh-add <path-to-key-file-of-primary-instance` 
   4. Connect to secondary instance. Command: `ssh -A -i <path-to-key-file-of-secondary-instance> <user>@<public-ip-of-secondary-instance`
   5. Connect to primary instance. Command: `ssh <user>@<private-ip-of-primary-instance>`
2. **Public IP**: You can assign one more ENI & EIP to this instance and connect on it. For understanding charges of this, please [refer here](https://aws.amazon.com/premiumsupport/knowledge-center/elastic-ip-charges/).
   Steps:
   1. Assign ENI. [reference here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/MultipleIP.html#ManageMultipleIP)
   2. Associate EIP. [reference here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/MultipleIP.html#StepThreeEIP)