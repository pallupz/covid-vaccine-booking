import time
import boto3
import requests
from ec2_metadata import ec2_metadata

network_interface_id = None
re_assignment_failed = False

def wait_for_new_ip(ip):
    reflected = False
    while not reflected:
        try:
            resp = requests.get('https://ifconfig.me', timeout=(1, 1))
            if resp.status_code == 200 and resp.text == ip:
                print(f"{ip} ready to use.")
                reflected = True
            else:
                print(f"{ip} not reflected. ip still is {resp.text}.")
                time.sleep(1)
        except requests.exceptions.Timeout:
            print('Request to ifconfig.me timed out.')


def detect_network_interface_id():
    """
    This method will fail on non-ec2 instances. Meaning it is not on ec2.
    :return: returns primary interface's eni-id
    """
    return ec2_metadata.network_interfaces[ec2_metadata.mac].interface_id


def handle_rate_limited():
    global re_assignment_failed
    global network_interface_id

    if not re_assignment_failed:
        try:
            if network_interface_id is None:
                network_interface_id = detect_network_interface_id()
            print(
                "\n================================= AWS Re-assignment ===============================\n"
            )
            ip = re_assign_ip(network_interface_id)
            if type(ip) is bool and ip is False:
                re_assignment_failed = True
            else:
                wait_for_new_ip(ip)
            re_assignment_failed = not ip
        except Exception:
            re_assignment_failed = True
    else:
        print('Rate-limited by CoWIN. Waiting for 5 seconds.\n'
              '(You can reduce your refresh frequency. Please note that other devices/browsers '
              'using CoWIN/Umang/Arogya Setu also contribute to same limit.)')
        time.sleep(5)


def re_assign_ip(eni_id):
    try:
        client = boto3.client('ec2')
        response = client.describe_network_interfaces(
            NetworkInterfaceIds=[
                eni_id,
            ],
        )
        if 'NetworkInterfaces' in response and len(response['NetworkInterfaces']) == 1:
            association = response['NetworkInterfaces'][0]['Association']
            print(f"Public Ip of {eni_id} is {association['PublicIp']}")
            print('Requesting new ip...')
            new_allocation = client.allocate_address(
                TagSpecifications=[
                    {
                        'ResourceType': 'elastic-ip',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'Refreshed IP'
                            },
                        ]
                    },
                ]
            )
            print(f"New allocated id {new_allocation['AllocationId']} and public ip is {new_allocation['PublicIp']}")
            client.associate_address(
                AllocationId=new_allocation['AllocationId'],
                NetworkInterfaceId=eni_id,
                PrivateIpAddress=response['NetworkInterfaces'][0]['PrivateIpAddress']
            )
            print(f"Associated IP.")
            print(f"Releasing IP.")
            client.release_address(AllocationId=association['AllocationId'])
            print(f"Released IP.")
            return new_allocation['PublicIp']
    except Exception as e:
        print(f"Error in IP Reassignment : {str(e)}")
        return False
