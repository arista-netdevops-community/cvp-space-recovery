# cvp-space-recovery

Find and remove unnecessary files to free up disk space in CVP servers through one of the following ways:

A) Manual Process
B) Automated process using crontab

## A) Manual Process

Just copy the script to the CVP server(s) and run `python cleanup.py`. The script may be copied to any directory, such as `/tmp`. You'll be presented with a multiple-choice menu with various options for removing old/unnecessary files.

If you have a CVP cluster, you need to run the script in all nodes since it won't remotely connect to different servers.

### Options
### System Logs
Looks for and removes old logs with the suffix `*.gz` and `*.[0-9]` in the `/var/log` directory and subdirectories.

### System Crash Files
Looks for and removes crash dump files from the `/var/crash` directory.

### Rotated CVP logs
Removes `*.log.*`, `*.out.*`, `*.gc.*`, `*.gz` and `*.[0-9]` files from the following directories:
- /cvpi/logs
- /cvpi/hadoop/logs
- /cvpi/hbase/logs
- /cvpi/apps/turbine/logs
- /cvpi/apps/aeris/logs
- /cvpi/apps/cvp/logs

### Current CVP logs
Removes `*.log`, `*.out` and `*.gc` files from the following directories:
- /cvpi/logs
- /cvpi/hadoop/logs
- /cvpi/hbase/logs
- /cvpi/apps/turbine/logs
- /cvpi/apps/aeris/logs
- /cvpi/apps/cvp/logs

### CVP Docker Images
Removes docker container images from `/cvpi/docker`

### CVP RPMs
Removes all RPM files from `/RPMS`. *This will not free space under / on CVP 2020.3.0+ and will free space from /data instead.*

### Elasticsearch Heap Dumps
Removes `*.hprof` files from `/cvpi/apps/aeris/elasticsearch`. *This will not free space under / on CVP 2020.2.3+ and will free space from /data instead.*

### Temporary upgrade files
Removes files and directories named `upgrade*` under `/tmp`.

### Vacuum system journal
Removes old entries from the system's journal. You'll be asked about how many days of old entries you want to keep, and a backup of older entries will be saved under `/data`.

### Kubelet logs
Removes kubelet log files from `/var/log`. When choosing this option you'll have an option to choose between:
- All kubelet logs: `kubelet.*.root.log.*` files.
- Kubelet error logs: `kubelet.*.root.log.INFO.*` files.
- Kubelet warning logs: `kubelet.*.root.log.WARNING.*` files.
- Kubelet info logs: `kubelet.*.root.log.INFO.*` files.


## B) Automated Process using crontab
Just copy the script to the CVP server(s) into any directory such as `/tmp/` and specify the path and the frequency with which you want to run the script in crontab. 

For example:

	[root@cvp ~]# crontab -l
	* * * * * python /mnt/cleanup.py 2

`2` here is number of days you want to preserve journal logs. For example, If no argument is provided the script will run in the manual process by default as shown in A).
If you have a CVP cluster, you need to run the script in all nodes since it won't remotely connect to different servers.

The script then write to a file in path `/var/log/cleanup.log` everytime the script is executed. This help to identify when was the last cleanup process run.

Sample output of the file cleanup.log is as follows:

	Full cleanup - Freed 3B   Thu Feb 17 17:18:05 2022
	Full cleanup - Freed 0B   Thu Feb 17 17:19:04 2022

You can edit crontab by running `crontab -e` on the CVP server

**Please note**: When executing the script in the automated process, all logs are removed from the mentioned directories in A) except for the "Current CVP logs" to which the CVP components would be currently writing to. If the current CVP logs need to be removed, you would need to follow the manual process of executing the script.






