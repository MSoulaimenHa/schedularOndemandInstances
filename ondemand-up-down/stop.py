import os
import argparse
from dotenv import load_dotenv
from aws_utils import stop_instances, get_instance_ids_from_target_group


def service_starter(service_name):
    """Load instance IDs based on the service name from a .env file."""
    load_dotenv()

    if service_name == "staging":
        target_group_arn = os.getenv("STAGING_TARGET_GROUP_ARN")
        instance_ids = get_instance_ids_from_target_group(
            target_group_arn=target_group_arn)
    elif service_name == "refurnishing":
        target_group_arn = os.getenv("REFURNISHING_TARGET_GROUP_ARN")
        instance_ids = get_instance_ids_from_target_group(
            target_group_arn=target_group_arn)

    else:
        raise ValueError(f"""Service name '{
                         service_name}' is not recognized. Please use 'staging' or 'refurnishing'.""")

    # Check if instance IDs are loaded correctly
    if not instance_ids or instance_ids == [""]:
        raise ValueError(f"""No instance IDs found for service '{
                         service_name}'. Check your .env file.""")

    return instance_ids, target_group_arn


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stop AWS EC2 instances based on service name.")

    parser.add_argument("-s", "--service", choices=["staging", "refurnishing"], required=True,
                        help="Specify the service name to load instance IDs (e.g., 'staging' or 'refurnishing').")

    args = parser.parse_args()
    instance_ids, _ = service_starter(args.service)
    stop_instances(instance_ids=instance_ids)
