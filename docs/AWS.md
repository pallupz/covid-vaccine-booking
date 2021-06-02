Setup Notes:

- Your EC2 Machine should be assigned with two ENI (Elastic Network Interfaces). 
  The first one (primary) should be public with EIP (Elastic IP) assigned, and you should not connect using this as this will change when you get rate-limited. You should connect to your machine using second ENI. 
- You can pass IAM Secrets as ENV Variables or by using aws configure or attach as instance profile. All three methods are supported.
- Following permissions are need for this to work. This IAM Policy should be attached to either instance (if you are using instance role) or the user (if you are using ENV Variables or aws configure to pass secrets)

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