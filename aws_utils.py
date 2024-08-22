
import boto3
import time
import requests
import sys

# Initialize boto3 client for EC2 and ELBv2
ec2_client = boto3.client('ec2')
elbv2_client = boto3.client('elbv2')


def start_instances(instance_ids):
    print(f"Starting instances: {instance_ids}")
    ec2_client.start_instances(InstanceIds=instance_ids)
    wait_for_instances_to_run(instance_ids)


def wait_for_instances_to_run(instance_ids):
    print("Waiting for instances to enter running state...")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=instance_ids)
    print("Instances are now running.")


def check_instance_health(instance_id):
    print(f"Checking if instance {instance_id} is accepting requests...")
    instance = ec2_client.describe_instances(InstanceIds=[instance_id])[
        'Reservations'][0]['Instances'][0]
    instance_ip = instance['PublicIpAddress']
    url = f"http://{instance_ip}/docs"

    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(
                    f"Instance {instance_id} at {url} is accepting requests.")
                return instance_ip
        except requests.exceptions.RequestException:
            pass
        print(
            f"Instance {instance_id} at {url} is not ready. Retrying in 5 seconds...")
        time.sleep(5)


def register_instance_to_target_group(instance_id, target_group_arn):
    print(
        f"Registering instance {instance_id} to target group {target_group_arn}")
    elbv2_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id}]
    )
    print(f"Instance {instance_id} registered to target group.")


def verify_instances_in_target_group(instance_ids, target_group_arn):
    print("Verifying that all instances are registered in the target group...")
    response = elbv2_client.describe_target_health(
        TargetGroupArn=target_group_arn)
    registered_instance_ids = [target['Target']['Id']
                               for target in response['TargetHealthDescriptions']]

    for instance_id in instance_ids:
        if instance_id not in registered_instance_ids:
            print(
                f"ERROR: Instance {instance_id} is not registered in the target group!")
            sys.exit(1)  # Exit with a non-zero status code to fail the pipeline
    print("All instances are successfully registered in the target group.")


def instanceStarter(instance_ids: list, target_group_arn: str):
    start_instances(instance_ids)
    active_ips = []

    for instance_id in instance_ids:
        ip = check_instance_health(instance_id)
        active_ips.append(ip)
        register_instance_to_target_group(instance_id, target_group_arn)

    print("Active IPs:", active_ips)

    # Verify instances are in the target group
    verify_instances_in_target_group(instance_ids, target_group_arn)
