# Setup Guide:

## Few Clicks Setup (Simple)
1. After you have signed up for AWS, create key pair [here](https://console.aws.amazon.com/ec2/v2/home?region=ap-south-1#CreateKeyPair:).
   - Name: Any name you like
   - File format: pem (if you are using MacOS or Linux), ppk (if you are using Windows)
2. ![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png) by [clicking here](https://console.aws.amazon.com/cloudformation/home?region=ap-south-1#/stacks/new?stackName=vaccination_stack).
   - Specify template: Upload a template file
   - download [this file](aws.template) and Choose it on the wizard.
   - InstanceType: t2.micro (or what ever you like)
   - KeyName: select key that you created in step 1.
   - SubnetId: select the default one from dropdown. In case you have multiple here, select the one with public access.
   - VpcId: select the default one from the dropdown. In case you have multiple here, select the one associated with the SubnetId selected.
   - check `I acknowledge that AWS CloudFormation might create IAM resources.` and hit `Create stack`
   - Keep pressing the refresh button till you see `CREATE_COMPLETE`. 
   - Go to the outputs tab and note down `InstanceIPAddress`
3. Create your personal access token from [here](https://github.com/settings/tokens/new?scopes=read:packages).
4. Connect to your instance based. Username is `ec2-user`
   - If you are using MacOS/Linux, follow [this guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html) 
     command: `ssh -i /path/to/downloaded/key/file ec2-user@<ip>` 
   - If you are using Windows, follow [this guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/putty.html)
5. Change `<YOUR_TOKEN_FROM_STEP_3>` and `<GITHUB_USERNAME>` from the following script and run it.
   ```bash
   export PAT=<YOUR_TOKEN_FROM_STEP_3>
   echo $PAT | docker login docker.pkg.github.com -u <GITHUB_USERNAME> --password-stdin
   docker run --rm \
     -v $(pwd)/configs:/configs \
     -e "TZ=Asia/Kolkata" \
     --network="host" \
     -it \
     docker.pkg.github.com/bombardier-gif/covid-vaccine-booking/cowin:latest
   ```
6. To clean up the resources, go to AWS Cloud Formation [AWS Cloud Formation](https://console.aws.amazon.com/cloudformation/home?region=ap-south-1) and delete the stack.
   
## Do It Yourself (For those who are familiar with AWS)
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