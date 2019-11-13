Create EC2 instance in existing VPC.
Create security group which allows only 22 and 80 inbound ports and attach it to the instance.
Create new EBS volume with "magnetic" type, 1GB size and attach it to the instance.
Connect to the instance via ssh, format and mount additional volume.
