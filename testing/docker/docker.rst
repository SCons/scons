==================================
Basic working with docker registry
==================================

Install required packages
=========================

Ensure that the following packages are installed on your local machine::

    docker.io >= v18.09
    docker-compose >= v1.17

User and group
==============

Add your local user to the `docker` group, e.g. by::

    sudo usermod -aG docker ${USER}

. After this step logout and login again, so that the change has been applied and the new group
is in effect.


Configuring docker daemon
=========================

Reconfigure by editing `/etc/docker/daemon.json` as *root*::

    {
      "debug": false
    }

.

Then reboot the machine or simply restart the daemon as *root* with::

    sudo systemctl restart docker.service

To check that the docker daemon was configured correctly, do a::

    docker info

which should result in an output similar to::

    Client:
     Debug Mode: false

    Server:
     Containers: 0
      Running: 0
      Paused: 0
      Stopped: 0
     Images: 0
     Server Version: 19.03.6
     Storage Driver: overlay2
      Backing Filesystem: extfs
      Supports d_type: true
      Native Overlay Diff: true
     Logging Driver: json-file
     Cgroup Driver: cgroupfs
     Plugins:
      Volume: local
      Network: bridge host ipvlan macvlan null overlay
      Log: awslogs fluentd gcplogs gelf journald json-file local logentries splunk syslog
     Swarm: inactive
     Runtimes: runc
     Default Runtime: runc
     Init Binary: docker-init
     containerd version:
     runc version:
     init version:
     Security Options:
      apparmor
      seccomp
       Profile: default
     Kernel Version: 4.15.0-88-generic
     Operating System: Ubuntu 18.04.4 LTS
     OSType: linux
     Architecture: x86_64
     CPUs: 4
     Total Memory: 6.997GiB
     Name: ubuntu
     ID: H2N5:VOZ6:UO6V:B36O:MD6Q:7GXR:M4QY:7EBB:NC6R:HQCQ:7ARF:CZBH
     Docker Root Dir: /var/lib/docker
     Debug Mode: false
     Registry: https://index.docker.io/v1/
     Labels:
     Experimental: false
     Insecure Registries:
      127.0.0.0/8
     Live Restore Enabled: false
    
    WARNING: No swap limit support

Setup resolv.conf if necessary
===============================

Docker uses `etc/resolv.conf` DNS information and passes that automatically to containers. If the file is not configured
properly or if entries are not valid, the server adds automatically public Google DNS nameservers
(8.8.8.8 and 8.8.4.4) to the container's DNS configuration.

