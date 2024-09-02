#!/bin/bash

AWS_REGION=$1 
TARGET_GROUP_ARN=$2


INSTANCE_IDS=$(aws elbv2 describe-target-health \
    --target-group-arn $TARGET_GROUP_ARN \
    --region $AWS_REGION \
    --query 'TargetHealthDescriptions[].Target.Id' \
    --output text)

IP_ADDRESSES=()
echo "IP addresses of instances in target group '$TARGET_GROUP_NAME':"
for INSTANCE_ID in $INSTANCE_IDS; do
    INSTANCE_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --region $AWS_REGION \
        --query 'Reservations[].Instances[].PublicIpAddress' \
        --output text)
    
    IP_ADDRESSES+=("$INSTANCE_IP")
done
if [ ${#IP_ADDRESSES[@]} -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No public IP addresses found for the instances in the Auto Scaling group: $ASG_NAME" 
    exit 1
fi
echo "$(date '+%Y-%m-%d %H:%M:%S') - Public IP addresses: ${IP_ADDRESSES[@]}" 

# JSON payload
PAYLOAD=$(cat <<EOF
{
            "base64_image": "string",
            "image_url": "https://plus.unsplash.com/premium_photo-1706140675031-1e0548986ad1?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bGl2aW5ncm9vbXxlbnwwfHwwfHx8MA%3D%3D",
            "room_type": "living room",
            "architecture_style": "countryside",
  "watermark_type": "proptexx"
}
EOF
)

for IP in "${IP_ADDRESSES[@]}"; do
    START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code} TIME:%{time_total}" -o /dev/null -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        http://$IP/generative-virtual-refurnishing/predict)
    END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$START_TIME - Sent POST request to $IP. $RESPONSE" 
done
