# cvp-space-recovery

Find and remove unecessary files to free up disk space in CVP servers.

## Quickstart

Just run `python cleanup.py`. You'll be presented with a multiple choice menu with various options for removing old/unecessary files.

## Options
### System Logs
Looks for and removes old logs with the suffix `*.gz` and `*.[0-9]` in the `/var/log` directory and subdirectories.

### System Crash Files
Looks for and removes crash dump files from the `/var/crash` directory.

### CVP logs
Removes `*.log` and `*.out` files from the following directories:
- /cvpi/logs
- /cvpi/hadoop/logs
- /cvpi/habase/logs
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
Removes files and directories names `upgrade*` under `/tmp`.

### Vacuum system journal
Removes old entries from the system's journal. You'll be asked about how many days of old entries you want to keep, and a backup of older entries will be saved under `/data`.