# Import Python libs
import boto3
import botocore
import paramiko
import join
import string
import random
import time
##############################################################
#set tags
name = 'Yevhen'
surname = 'Nahornyi'
# set key and params for ssh
key = paramiko.RSAKey.from_private_key_file('nahornyi.pem')
clientssh = paramiko.SSHClient()
clientssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
###############################################################
#set params for sftp
port = 22

remotepath = '/home/ec2-user/volume.sh'
localpath = './volume.sh'
##############################################################
# set vaiables for resourses of lib boto3
ec2 = boto3.resource('ec2', 'eu-west-1')
client = boto3.client('ec2', 'eu-west-1')
###############################################################
#get vps ID
response = client.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
print ('VPC ID is:',vpc_id)
##############################################################
#filter for taking instance ID
instances = ec2.instances.filter(
    Filters=[
        {'Name': 'key-name', 'Values': ['nahornyi']},
        {'Name': 'instance-state-name', 'Values': ['pending']}
    ]
)
##############################################################
#main function
def main():
     create_ec2()
     for instance in instances:
         inst_id=instance.id
         print(inst_id)
     time.sleep(60) # wait for the creating instance and getting public ip
     for instance in ec2.instances.all():
         if (instance.id) == inst_id:
            inst_ip=instance.public_ip_address
            print(inst_ip)
     create_secgrp()
#     create_vol()
     response = client.attach_volume(
         Device="/dev/sdf",
         InstanceId=inst_id,
         VolumeId=create_vol(),
         DryRun=False
     )

     transport = paramiko.Transport((inst_ip, port))
     transport.connect(username='ec2-user', pkey=key)
     sftp = paramiko.SFTPClient.from_transport(transport)
     sftp.put(localpath, remotepath)
     sftp.close()
     transport.close()
     clientssh.connect(hostname=inst_ip, username="ec2-user", pkey=key)
     stdin, stdout, stderr = clientssh.exec_command('chmod +x volume.sh')
     stdin, stdout, stderr = clientssh.exec_command('sh /volume.sh')


##########    METHODS     ####################################
##############################################################
# create a new EC2 instance
def create_ec2():
    instance = ec2.create_instances(
        ImageId='ami-040ba9174949f6de4',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='nahornyi',
        Placement={'AvailabilityZone': 'eu-west-1c'},
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}, {'Key': 'Surname', 'Value': surname}]
            }
        ]
    )
# create Security Group for SSH and HTTP access in current VPC
def create_secgrp():
    sgroup = client.describe_vpcs()
    sgroup = client.create_security_group(
        GroupName=''.join(random.choices(string.ascii_uppercase + string.digits, k=3)),
        Description='only allow SSH and HTTP traffic',
        VpcId=vpc_id,
    )
    sgroup_id = sgroup['GroupId']
    # allow incoming 22,80 port
    client.authorize_security_group_ingress(
        GroupId=sgroup_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
#set tag for security group
    ec2.create_tags(Resources=[sgroup_id],
                    Tags=[{'Key': 'Name', 'Value': 'Yevhen'}, {'Key': 'Surname', 'Value': 'Nahornyi'}])

# Createing EBS volume "magnetic", 1GB size
def create_vol():
    vol = ec2.create_volume(
         Size=1,
         AvailabilityZone="eu-west-1c",
         VolumeType="standard",
         TagSpecifications=[
               {
                'ResourceType': 'volume',
                'Tags': [{'Key': 'Name','Value': 'Yevhen'},{'Key': 'Surname','Value': 'Nahornyi'}]
               }
         ]
    )
    time.sleep(60)
    print ('Volume Id: ', vol.id)
    return vol.id

#################################################################

if __name__ == "__main__":
    main()

