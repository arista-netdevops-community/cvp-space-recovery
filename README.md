# cvp-space-recovery

Find and remove unnecessary files to free up disk space in CVP servers.

## Quickstart

Just copy the script to the CVP server(s) and run `python cleanup.py`. The script may be copied to any directory, such as `/tmp`. You'll be presented with a multiple-choice menu with various options for removing old/unnecessary files.

If you have a CVP cluster, you need to run the script in all nodes since it won't remotely connect to different servers.

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