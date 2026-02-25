#!/bin/bash

echo "===== CONFIGURING SLURM ====="

# Enable & Start Munge
sudo systemctl enable munge
sudo systemctl start munge

# Ensure munge key exists
if [ ! -f /etc/munge/munge.key ]; then
    echo "Generating Munge key..."
    sudo /usr/sbin/create-munge-key
    sudo chown munge:munge /etc/munge/munge.key
    sudo chmod 400 /etc/munge/munge.key
    sudo systemctl restart munge
fi

# Create required directories
sudo mkdir -p /var/spool/slurm
sudo mkdir -p /var/log/slurm

sudo chown -R slurm:slurm /var/spool/slurm
sudo chown -R slurm:slurm /var/log/slurm

HOSTNAME=$(hostname)

# Create slurm.conf if not exists
if [ ! -f /etc/slurm/slurm.conf ]; then
    echo "Creating slurm.conf..."

    sudo mkdir -p /etc/slurm

    sudo tee /etc/slurm/slurm.conf > /dev/null <<EOF
ClusterName=localcluster
ControlMachine=$HOSTNAME
SlurmUser=slurm
SlurmdUser=root
StateSaveLocation=/var/spool/slurm
SlurmdSpoolDir=/var/spool/slurm
AuthType=auth/munge
NodeName=$HOSTNAME CPUs=2 State=UNKNOWN
PartitionName=debug Nodes=$HOSTNAME Default=YES MaxTime=INFINITE State=UP
EOF
fi

# Enable and start services
sudo systemctl enable slurmctld
sudo systemctl enable slurmd

sudo systemctl restart slurmctld
sudo systemctl restart slurmd

sleep 3

echo "===== VERIFYING SLURM ====="
sinfo || echo "Slurm may need manual verification."

echo "===== CONFIGURATION COMPLETE ====="