from builtins import input
from datetime import datetime
from glob import glob as search
from pathlib import Path
import logging
import math
import os
import subprocess
import re
import sys

log = logging.getLogger('cleanup')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.WARNING)

class Files:
  def __init__(self, name="", directories=["./"], prefixes=["*"], recursive=True):
    self.name = name
    self.config = {}
    self.config['directories'] = directories
    self.config['prefixes'] = prefixes
    self.config['recursive'] = recursive
    self.previous_size = 0
    self.reset(self.config['directories'], self.config['prefixes'], self.config['recursive'])

  def reset(self, directories, prefixes, recursive):
    log.debug("Initializing %s" % self.name)
    self.files = []
    self.size = 0
    self.__get_files()

  def __get_files(self):
    for directory in self.config['directories']:
      for prefix in self.config['prefixes']:
        current_search = directory + "/" + prefix
        log.debug("Searching for files matching the pattern " + current_search)
        try:
          matches = search(current_search, recursive=self.config['recursive'])
        except TypeError:
          matches = search(current_search)
          matches += search(current_search + "/**")
          matches += search(current_search + "/**/**")
          matches += search(current_search + "/**/**/**")
          matches += search(current_search + "/**/**/**/**")
          matches += search(current_search + "/**/**/**/**/**")
        if matches:
          self.files.append(matches)
    self.files = self.__flatten(self.files)
    self.size = self.__get_total_size()
    self.pretty_size = self.__convert_size()
    log.debug("Files in %s: %s" %(self.config['directories'], self.files))

  def __flatten(self, list):
    list = [item for sublist in list for item in sublist]
    return(list)

  def __get_total_size(self):
    size = 0
    for file in self.files:
      size = size + os.stat(file).st_size
    return(size)

  def __convert_size(self):
    if self.size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(self.size, 1024)))
    p = math.pow(1024, i)
    s = round(self.size / p, 2)
    return "%s %s" % (s, size_name[i])

  def __rmdir(self, directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            self.__rmdir(item)
        else:
            item.unlink()
    directory.rmdir()

  def list(self):
    return(self.files)

  def delete_files(self):
    log.warning("Removing %s" % self.name)
    for file in self.files:
      log.info("Removing " + file)
      if os.path.isfile(file) or os.path.islink(file):
        try:
          os.remove(file)
        except Exception as e:
          log.warning("Could not remove %s: %s" % (file, e))
      elif os.path.isdir(file):
        self.__rmdir(file)
      else:
        log.debug("Not removing file " + file + ".")

    self.previous_size = self.size
    self.reset(self.config['directories'], self.config['prefixes'], self.config['recursive'])

    # Return freed space
    return(self.previous_size - self.size)

def convert_size(size):
  if size == 0:
      return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size, 1024)))
  p = math.pow(1024, i)
  s = round(size / p, 2)
  return "%s %s" % (s, size_name[i])

def clean_system_journal(backup=True, vacuum_time="2"):
  now=datetime.utcnow()
  now=datetime.isoformat(now)
  journal_backup_dir = "/data/cvpbackup"
  journal_backup_filename = "journalctl-" + now
  journal_backup_file = journal_backup_dir + "/" + journal_backup_filename
  journal_backup_cmd = "/bin/bash -c \"journalctl > " + journal_backup_file + "\""
  journal_cleanup_cmd = "/bin/bash -c \"journalctl --vacuum-time=" + vacuum_time + "d\""
  log.warning("Cleaning system journal")

  if backup:
    log.info("Backing up current system journal to %s before cleanup" % (journal_backup_file))
    try:
      os.system(journal_backup_cmd)
    except Exception as e:
      log.warning("Could not back up journal: %s" % e)
  
  output = subprocess.check_output(journal_cleanup_cmd, stderr=subprocess.STDOUT, shell=True).decode()

  size_diff = re.search('freed (.+) of archived journals', output).groups()[0]
  if 'B' in size_diff:
    size_diff = float(size_diff.split('B')[0])
  elif 'K' in size_diff:
    size_diff = float(size_diff.split('K')[0])
    size_diff = size_diff * 1024
  elif 'M' in size_diff:
    size_diff = float(size_diff.split('M')[0])
    size_diff = size_diff * 1024 * 1024
  elif 'G' in size_diff:
    size_diff = float(size_diff.split('G')[0])
    size_diff = size_diff * 1024 * 1024 * 1024
  else:
    log.warning("Could not parse size unit. Freed space will be inacurate.")
    size_diff = 0

  # Return freed space
  return(int(size_diff))

def main():
  system_logs = Files(name="System logs", directories=["/var/log"],prefixes=["*.gz", "*.[0-9]"])
  system_crash_files = Files(name="System crash files", directories=["/var/crash"])
  cvp_logs = Files(name="CVP logs", directories=["/cvpi/logs", "/cvpi/hadoop/logs", "/cvpi/habase/logs", "/cvpi/apps/turbine/logs", "/cvpi/apps/aeris/logs", "/cvpi/apps/cvp/logs"], prefixes=["*.log*", "*.out*"])
  cvp_docker_images = Files(name="CVP docker images", directories=["/cvpi/docker"], prefixes=["*.gz"])
  cvp_rpms = Files(name="CVP RPMs", directories=["/RPMS"], prefixes=["*.rpm"])
  cvp_elasticsearch_heap_dumps = Files(name="CVP Heap Dumps", directories=["/cvpi/apps/aeris/elasticsearch"], prefixes=["*.hprof"])
  cvp_tmp_upgrade = Files(name="Temporary upgrade files", directories=["/tmp"], prefixes=["upgrade*"], recursive=False)

  while True:
    menu = {}
    menu['1'] = "Clean system logs (" + system_logs.pretty_size + ")"
    menu['2'] = "Clean system crash files (" + system_crash_files.pretty_size + ")"
    menu['3'] = "Clean CVP logs (" + cvp_logs.pretty_size + ")"
    menu['4'] = "Clean CVP docker images (" + cvp_docker_images.pretty_size + ")"
    menu['5'] = "Clean CVP RPMs (" + cvp_rpms.pretty_size + ")"
    menu['6'] = "Clean Elasticsearch Heap Dumps (" + cvp_elasticsearch_heap_dumps.pretty_size + ")"
    menu['7'] = "Clean CVP temporary upgrade directories (" + cvp_tmp_upgrade.pretty_size + ")"
    menu['8'] = "Vacuum system journal"
    menu['9'] = "Clean everything"
    menu['Q'] = "Exit"

    options = list(menu.keys())
    options.sort()
    for entry in options:
      print(entry + " - " + menu[entry])

    print("\n")
    selection = input("Choose an option\n")

    if selection == '1':
      freed = system_logs.delete_files()
      message = "System logs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '2':
      freed = system_crash_files.delete_files()
      message = "System crash files - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '3':
      freed = cvp_logs.delete_files()
      message = "CVP logs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '4':
      freed = cvp_docker_images.delete_files()
      message = "CVP docker images - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '5':
      freed = cvp_rpms.delete_files()
      message = "CVP RPMs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '6':
      freed = cvp_elasticsearch_heap_dumps.delete_files()
      message = "CVP Elasticsearch Heap Dumps - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '7':
      freed = cvp_tmp_upgrade.delete_files()
      message = "CVP temporary upgrade files - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '8':
      vacuum_time = input("How many days to keep on the journal? (Default: 2 days)\n")
      if vacuum_time:
        freed = clean_system_journal(vacuum_time=vacuum_time)
      else:
        freed = clean_system_journal()
      message = "System journal vacuum - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '9':
      vacuum_time = input("How many days to keep on the journal? (Default: 2 days)\n")
      freed = system_logs.delete_files()
      freed += system_crash_files.delete_files()
      freed += cvp_logs.delete_files()
      freed += cvp_docker_images.delete_files()
      freed += cvp_rpms.delete_files()
      freed += cvp_elasticsearch_heap_dumps.delete_files()
      freed += cvp_tmp_upgrade.delete_files()
      if vacuum_time:
        freed += clean_system_journal(vacuum_time=vacuum_time)
      else:
        freed += clean_system_journal()
      message = "Full cleanup - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == 'Q' or selection == 'q':
      break
    else:
      print("Unknown option.")
    
if __name__ == "__main__":
  main()