# AWS Auto Scaling Setup - Content Factory

## 📈 Automatic Scaling Configuration

Configure auto-scaling to automatically handle traffic spikes and reduce costs during low usage periods.

---

## 🎯 What Auto Scaling Provides

- ✅ Automatic capacity adjustment
- ✅ Handle traffic spikes seamlessly
- ✅ Cost optimization during low traffic
- ✅ High availability with multiple AZs
- ✅ Health check replacement
- ✅ Load balancing across instances

---

## 📋 Architecture Overview

```
Internet
    ↓
Application Load Balancer (ALB)
    ↓
Target Group
    ├── EC2 Instance 1 (ContentFactory)
    ├── EC2 Instance 2 (ContentFactory)
    └── EC2 Instance N (auto-scaled)
```

---

## 🔧 Step 1: Create Application Load Balancer

**Using AWS Console:**

1. Go to EC2 → Load Balancers
2. Click "Create Load Balancer"
3. Choose "Application Load Balancer"
4. Configure:
   - **Name:** `content-factory-alb`
   - **Scheme:** Internet-facing
   - **IP address type:** IPv4
   - **VPC:** Select your VPC
   - **Availability Zones:** Select at least 2 AZs
   - **Security Group:** Create new or use existing (allow ports 80, 443)

**Using AWS CLI:**

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name content-factory-alb \
  --subnets subnet-xxxxxx subnet-yyyyyy \
  --security-groups sg-xxxxxx \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Name,Value=ContentFactoryALB
```

---

## 🎯 Step 2: Create Target Group

**Using AWS Console:**

1. EC2 → Target Groups
2. Click "Create target group"
3. Configure:
   - **Target type:** Instances
   - **Name:** `content-factory-targets`
   - **Protocol:** HTTP
   - **Port:** 8000
   - **VPC:** Select your VPC
   - **Health check path:** `/health`
   - **Health check interval:** 30 seconds
   - **Healthy threshold:** 2
   - **Unhealthy threshold:** 2

**Using AWS CLI:**

```bash
# Create target group
aws elbv2 create-target-group \
  --name content-factory-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxx \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2
```

---

## 🔗 Step 3: Configure ALB Listener

**Using AWS Console:**

1. Select your ALB
2. Listeners tab → Add listener
3. Configure:
   - **Protocol:** HTTP
   - **Port:** 80
   - **Default action:** Forward to `content-factory-targets`

**Using AWS CLI:**

```bash
# Create listener
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

---

## 📸 Step 4: Create AMI from Current Instance

**Prepare your instance:**

```bash
# SSH to EC2
ssh -i "your-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com

# Ensure application is working
docker-compose -f docker-compose.prod.yml ps

# Clean up sensitive data
# (Optional: Remove token files if you don't want to share OAuth tokens)
```

**Create AMI:**

```bash
# Using AWS CLI
aws ec2 create-image \
  --instance-id <your-instance-id> \
  --name "content-factory-v1" \
  --description "Content Factory production image" \
  --no-reboot

# Get AMI ID
aws ec2 describe-images \
  --owners self \
  --filters "Name=name,Values=content-factory-v1"
```

**Or using AWS Console:**
1. EC2 → Instances
2. Select your instance
3. Actions → Image and templates → Create image
4. Name: `content-factory-v1`
5. Click "Create image"

---

## 🚀 Step 5: Create Launch Template

**Using AWS Console:**

1. EC2 → Launch Templates
2. Click "Create launch template"
3. Configure:
   - **Name:** `content-factory-template`
   - **AMI:** Select your created AMI
   - **Instance type:** t2.micro (or your preferred size)
   - **Key pair:** Your SSH key
   - **Security groups:** Allow ports 22, 8000
   - **User data:** (Startup script)

**User Data Script:**

```bash
#!/bin/bash
cd /home/ubuntu/content-factory
docker-compose -f docker-compose.prod.yml up -d
```

**Using AWS CLI:**

```bash
aws ec2 create-launch-template \
  --launch-template-name content-factory-template \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "ami-xxxxxx",
    "InstanceType": "t2.micro",
    "KeyName": "your-key-name",
    "SecurityGroupIds": ["sg-xxxxxx"],
    "UserData": "IyEvYmluL2Jhc2gKY2QgL2hvbWUvdWJ1bnR1L2NvbnRlbnQtZmFjdG9yeQpkb2NrZXItY29tcG9zZSAtZiBkb2NrZXItY29tcG9zZS5wcm9kLnltbCB1cCAtZA=="
  }'
```

---

## 📊 Step 6: Create Auto Scaling Group

**Using AWS Console:**

1. EC2 → Auto Scaling Groups
2. Click "Create Auto Scaling group"
3. Configure:
   - **Name:** `content-factory-asg`
   - **Launch template:** `content-factory-template`
   - **VPC:** Your VPC
   - **Availability Zones:** Select 2+ AZs
   - **Load balancing:** Attach to existing load balancer
   - **Target group:** `content-factory-targets`
   - **Health checks:** ELB + EC2
   - **Health check grace period:** 300 seconds
   - **Group size:**
     - Desired capacity: 2
     - Minimum capacity: 1
     - Maximum capacity: 5

**Using AWS CLI:**

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name content-factory-asg \
  --launch-template LaunchTemplateName=content-factory-template \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --target-group-arns <target-group-arn> \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --vpc-zone-identifier "subnet-xxxxxx,subnet-yyyyyy"
```

---

## 📈 Step 7: Configure Scaling Policies

### Target Tracking Scaling (Recommended)

**CPU-based scaling:**

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name content-factory-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 70.0
  }'
```

**Request count scaling:**

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name content-factory-asg \
  --policy-name request-count-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/content-factory-alb/<alb-id>/targetgroup/content-factory-targets/<tg-id>"
    },
    "TargetValue": 1000.0
  }'
```

### Step Scaling (Alternative)

**Scale up policy:**

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name content-factory-asg \
  --policy-name scale-up \
  --scaling-adjustment 1 \
  --adjustment-type ChangeInCapacity \
  --cooldown 300
```

**Scale down policy:**

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name content-factory-asg \
  --policy-name scale-down \
  --scaling-adjustment -1 \
  --adjustment-type ChangeInCapacity \
  --cooldown 300
```

**CloudWatch alarms for step scaling:**

```bash
# Scale up alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-scale-up \
  --alarm-description "Scale up when CPU > 70%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions <scale-up-policy-arn>

# Scale down alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-scale-down \
  --alarm-description "Scale down when CPU < 30%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 30 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions <scale-down-policy-arn>
```

---

## 🔐 Step 8: Update Security Groups

**ALB Security Group:**
- **Inbound:**
  - Port 80 (HTTP) from 0.0.0.0/0
  - Port 443 (HTTPS) from 0.0.0.0/0

**EC2 Instance Security Group:**
- **Inbound:**
  - Port 22 (SSH) from your IP
  - Port 8000 (App) from ALB security group only

```bash
# Allow traffic from ALB to instances
aws ec2 authorize-security-group-ingress \
  --group-id <instance-sg-id> \
  --protocol tcp \
  --port 8000 \
  --source-group <alb-sg-id>
```

---

## 🌐 Step 9: Update DNS and OAuth

**Get ALB DNS name:**

```bash
aws elbv2 describe-load-balancers \
  --names content-factory-alb \
  --query 'LoadBalancers[0].DNSName'
```

**Update your domain CNAME:**
```
Type: CNAME
Name: contentfactory
Value: content-factory-alb-xxxxxxxx.eu-west-3.elb.amazonaws.com
```

**Update Google OAuth redirect URIs:**
- Add: `https://contentfactory.yourdomain.com/api/v1/social-media/youtube/oauth2callback`

**Update APP_BASE_URL:**
```env
APP_BASE_URL=https://contentfactory.yourdomain.com
```

---

## 📊 Step 10: Test Auto Scaling

### Simulate Load

**Install stress testing tool:**

```bash
sudo apt install stress-ng
```

**Generate CPU load:**

```bash
stress-ng --cpu 4 --timeout 300s
```

**Or use Apache Bench:**

```bash
ab -n 10000 -c 100 https://contentfactory.yourdomain.com/health
```

**Monitor scaling:**

```bash
# Watch Auto Scaling activity
watch aws autoscaling describe-auto-scaling-activities \
  --auto-scaling-group-name content-factory-asg \
  --max-records 5

# Monitor instances
watch aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names content-factory-asg \
  --query 'AutoScalingGroups[0].Instances'
```

---

## 💰 Cost Optimization

### Scheduled Scaling

**Scale down during off-hours:**

```bash
# Scale to 1 instance at night (00:00 UTC)
aws autoscaling put-scheduled-action \
  --auto-scaling-group-name content-factory-asg \
  --scheduled-action-name scale-down-night \
  --recurrence "0 0 * * *" \
  --desired-capacity 1 \
  --min-size 1 \
  --max-size 5

# Scale up during business hours (08:00 UTC)
aws autoscaling put-scheduled-action \
  --auto-scaling-group-name content-factory-asg \
  --scheduled-action-name scale-up-day \
  --recurrence "0 8 * * *" \
  --desired-capacity 2 \
  --min-size 1 \
  --max-size 5
```

### Use Spot Instances (Advanced)

Save up to 90% by using Spot Instances for non-critical capacity:

```bash
aws autoscaling create-launch-template \
  --launch-template-name content-factory-template-spot \
  --launch-template-data '{
    "InstanceMarketOptions": {
      "MarketType": "spot",
      "SpotOptions": {
        "MaxPrice": "0.05",
        "SpotInstanceType": "one-time"
      }
    }
  }'
```

---

## 🔍 Monitoring Auto Scaling

### CloudWatch Metrics

**Key metrics to monitor:**
- GroupDesiredCapacity
- GroupInServiceInstances
- GroupMinSize/GroupMaxSize
- GroupTotalInstances

**View metrics:**

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/AutoScaling \
  --metric-name GroupInServiceInstances \
  --dimensions Name=AutoScalingGroupName,Value=content-factory-asg \
  --start-time 2025-10-20T00:00:00Z \
  --end-time 2025-10-21T00:00:00Z \
  --period 300 \
  --statistics Average
```

---

## 🚨 Troubleshooting

### Instances not joining target group

**Check:**
1. Health check path `/health` is accessible
2. Security group allows traffic from ALB
3. Application is running on correct port (8000)

### Scaling not triggering

**Check:**
1. CloudWatch alarms are in "ALARM" state
2. Scaling policies are correctly configured
3. Cooldown period hasn't been exceeded

### High costs

**Solutions:**
1. Reduce max capacity
2. Use scheduled scaling
3. Consider Spot Instances
4. Increase scale-down threshold

---

## ✅ Verification Checklist

- [ ] ALB created and healthy
- [ ] Target group configured
- [ ] AMI created from working instance
- [ ] Launch template configured
- [ ] Auto Scaling group created
- [ ] Scaling policies configured
- [ ] Security groups updated
- [ ] DNS pointing to ALB
- [ ] Load testing successful
- [ ] Instances scale up/down correctly

---

## 📈 Expected Behavior

### Normal Operations
- 2 instances running during business hours
- 1 instance during off-hours (if scheduled)
- Health checks passing every 30 seconds

### Under Load
- CPU > 70% → Scale up by 1 instance
- Continues until load decreases or max capacity (5)
- Waits 5 minutes (cooldown) before next scale

### Recovery
- Unhealthy instance replaced automatically
- New instance launches from AMI
- Health check passes → joins target group

---

## 🎯 Summary

Your Content Factory now has:
- ✅ Application Load Balancer
- ✅ Auto Scaling Group (1-5 instances)
- ✅ Target tracking scaling policies
- ✅ Health check automation
- ✅ High availability across AZs
- ✅ Cost optimization with scaling

**Next:** Implement CI/CD pipeline for automated deployments!
