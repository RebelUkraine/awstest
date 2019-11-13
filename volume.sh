#!/bin/sh
sudo mkfs.ext4 /dev/xvdf
sudo mkdir /mnt/xvdf
sudo mount /dev/xvdf /mnt/xvdf
sudo sh -c "echo '/dev/xvdf     /mnt/xvdf      ext4        defaults      0       0' >> /etc/fstab"
