# cvp-space-recovery

Find and remove unnecessary files to free up disk space in CVP servers through one of the following ways:

A) Interactive mode  
B) Non-interactive mode  
- using crontab    

## A) Interactive mode

Just copy the script to the CVP server(s) and run `python cleanup.py`. The script may be copied to any directory, such as `/mnt`. You'll be presented with a multiple-choice menu with various options for removing old/unnecessary files.

If you have a CVP cluster, you need to run the script in all nodes since it won't remotely connect to different servers.

## B) Non-interactive mode
You can also run the script in automated mode by using arguments telling which kind of cleanup you want to perform. To do so you run it with the following syntax: `python cleanup.py --clean-all`.

Please use `python cleanup.py --help` to see an updated list of all supported operations and options.

Example:

	[root@cvp mnt]# python /mnt/autocleanup_V5.py --clean-all
	2022-02-19 02:14:50,266 - cleanup - WARNING - --- Starting Cleanup in Automatic mode ---
	2022-02-19 02:14:50,266 - cleanup - WARNING - Removing System logs
	2022-02-19 02:14:50,333 - cleanup - WARNING - Removing System crash files
	2022-02-19 02:14:50,334 - cleanup - WARNING - Removing CVP Rotated logs
	2022-02-19 02:14:50,352 - cleanup - WARNING - Removing CVP docker images
	2022-02-19 02:14:50,352 - cleanup - WARNING - Removing CVP RPMs
	2022-02-19 02:14:50,353 - cleanup - WARNING - Removing CVP Elasticsearch Heap Dumps
	2022-02-19 02:14:50,353 - cleanup - WARNING - Removing Temporary upgrade files
	2022-02-19 02:14:50,354 - cleanup - WARNING - Removing Kubelet Logs - All
	2022-02-19 02:14:50,389 - cleanup - WARNING - Cleaning system journal
	2022-02-19 02:14:55,445 - cleanup - WARNING - --- Ending Cleanup --- Freed 0B

### Non-interactive mode using crontab

Just copy the script to the CVP server(s) into any directory such as `/mnt` (persistent across reloads) and specify the path and the frequency with which you want to run the script in crontab.

For example:

       [root@cvp ~]# crontab -l
        * * * * * python /mnt/cleanup.py --clean-all --quiet

`--quiet` or `-q`flag is used avoid stdout on the terminal everytime the script is run. If `--quiet` or `-q` is not used stdout will be written to /var/spool/mail/root. If no argument is provided the script will run in the manual process by default as shown in A).
If you have a CVP cluster, you need to run the script in all nodes since it won't remotely connect to different servers.

The script then writes to a file in path `/var/log/cleanup.log` everytime the script is executed. This helps to identify when was the last cleanup process run.

Sample output of the file `cleanup.log` is as follows:

    2022-02-19 01:43:18,707 - cleanup - WARNING - --- Starting Cleanup in Automatic mode ---
	2022-02-19 01:43:18,708 - cleanup - WARNING - Removing System logs
	2022-02-19 01:43:18,774 - cleanup - INFO - System logs: freed 0B
	2022-02-19 01:43:18,774 - cleanup - WARNING - Removing System crash files
	2022-02-19 01:43:18,774 - cleanup - INFO - System crash files: freed 0B
	2022-02-19 01:43:18,774 - cleanup - WARNING - Removing CVP Rotated logs
	2022-02-19 01:43:18,792 - cleanup - INFO - CVP Rotated logs: freed 0B
	2022-02-19 01:43:18,792 - cleanup - WARNING - Removing CVP docker images
	2022-02-19 01:43:18,793 - cleanup - INFO - CVP docker images: freed 0B
	2022-02-19 01:43:18,793 - cleanup - WARNING - Removing CVP RPMs
	2022-02-19 01:43:18,793 - cleanup - INFO - CVP RPMs: freed 0B
	2022-02-19 01:43:18,793 - cleanup - WARNING - Removing CVP Elasticsearch Heap Dumps
	2022-02-19 01:43:18,793 - cleanup - INFO - CVP Elasticsearch Heap Dumps: freed 0B
	2022-02-19 01:43:18,793 - cleanup - WARNING - Removing Temporary upgrade files
	2022-02-19 01:43:18,794 - cleanup - INFO - Temporary upgrade files: freed 0B
	2022-02-19 01:43:18,794 - cleanup - WARNING - Removing Kubelet Logs - All
	2022-02-19 01:43:18,828 - cleanup - INFO - Kubelet Logs - All(all): freed 0B
	2022-02-19 01:43:18,828 - cleanup - WARNING - Cleaning system journal
	2022-02-19 01:43:18,828 - cleanup - INFO - Backing up current system journal to /data/cvpbackup/journalctl-2022-02-19T01:43:18.828677 before cleanup
	2022-02-19 01:43:23,804 - cleanup - INFO - Vacuum system journal: freed 0B
	2022-02-19 01:43:23,804 - cleanup - WARNING - --- Ending Cleanup --- Freed 0B

You can edit crontab by running `crontab -e` on the CVP server

**Please note**: When executing the script in the interactive mode, all logs are removed from the mentioned directories under OPTIONS below except for the "Current CVP logs" to which the CVP components would be currently writing to. If the current CVP logs need to be removed, you would need to follow the interactive mode of executing the script.


## Options
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




