from glob import glob as search
import os
import math
import logging
from datetime import datetime
from pathlib import Path
import tempfile
from builtins import input

class Files:
  def __init__(self, directories=["./"], prefixes=["*"], recursive=True) -> None:
    self.config = {}
    self.config['directories'] = directories
    self.config['prefixes'] = prefixes
    self.config['recursive'] = recursive
    self.previous_size = 0
    self.reset(self.config['directories'], self.config['prefixes'], self.config['recursive'])

  def reset(self, directories, prefixes, recursive):
    self.files = []
    self.size = 0
    self.__get_files()

  def __get_files(self):
    for directory in self.config['directories']:
      for prefix in self.config['prefixes']:
        current_search = directory + "/" + prefix
        logging.debug("Searching for files matching the pattern " + current_search)
        matches = search(current_search, recursive=self.config['recursive'])
        if matches:
          self.files.append(matches)
    self.files = self.__flatten(self.files)
    self.size = self.__get_total_size()
    self.pretty_size = self.__convert_size()

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
    for file in self.files:
      logging.info("Removing " + file)
      if os.path.isfile(file) or os.path.islink(file):
        os.remove(file)
      elif os.path.isdir(file):
        self.__rmdir(file)
      else:
        logging.warn("Not removing file " + file + ".")

    self.previous_size = self.size
    self.reset(self.config['directories'], self.config['prefixes'], self.config['recursive'])

    # Return freed space
    return(self.previous_size - self.size)

def clean_system_journal(backup=True, vacuum_time="2d"):
  now=datetime.utcnow()
  now=datetime.isoformat(now)
  journal_backup_dir = "/data/cvpbackup"
  journal_backup_filename = "journalctl-" + now
  journal_backup_file = journal_backup_dir + "/" + journal_backup_filename
  journal_backup_cmd = "/bin/bash -c \"journalctl > " + journal_backup_file + "\""
  journal_cleanup_cmd = "/bin/bash -c \"journalctl --vacuum-time=" + vacuum_time + "d\""

  if backup:
    logging.info("Backing up system journal before cleanup")
    logging.debug("Journal backup file: " + journal_backup_dir + "/" + journal_backup_file)
    os.system(journal_backup_cmd)
  
  logging.info("Cleaning system journal")
  os.system(journal_cleanup_cmd)

  logging.debug("Calculating freed space")
  tmp, journal_tmp_filename = tempfile.mkstemp()
  os.close(tmp)
  journal_backup_cmd = "/bin/bash -c \"journalctl > " + journal_tmp_filename + "\""
  os.system(journal_backup_cmd)

  backup_size = os.stat(journal_backup_file).st_size
  current_size = os.stat(journal_tmp_filename).st_size
  os.remove(journal_tmp_filename)

  logging.debug("Previous journal size: " + str(backup_size))
  logging.debug("Current journal size: " + str(current_size))

  size_diff = (backup_size - current_size)

  # Return freed space
  return(size_diff)

def main():
  system_logs = Files(directories=["/var/log"],prefixes=["*.gz", "*.[0-9]"])
  system_crash_files = Files(directories=["/var/crash"])
  cvp_logs = Files(directories=["/cvpi/logs", "/cvpi/hadoop/logs", "/cvpi/habase/logs", "/cvpi/apps/turbine/logs", "/cvpi/apps/aeris/logs", "/cvpi/apps/cvp/logs"], prefixes=["*.log*", "*.out*"])
  cvp_docker_images = Files(directories=["/cvpi/docker"], prefixes=["*.gz"])
  cvp_rpms = Files(directories=["/RPMS"], prefixes=["*.rpm"])
  cvp_elasticsearch_heap_dumps = Files(directories=["/cvpi/apps/aeris/elasticsearch"], prefixes=["*.hprof"])
  cvp_tmp_upgrade = Files(directories=["/tmp"], prefixes=["upgrade*"], recursive=False)

  menu = {}
  menu['1'] = "Clean system logs (" + system_logs.pretty_size + ")"
  menu['2'] = "Clean system crash files (" + system_crash_files.pretty_size + ")"
  menu['3'] = "Clean CVP logs (" + cvp_logs.pretty_size + ")"
  menu['4'] = "Clean CVP docker images (" + cvp_docker_images.pretty_size + ")"
  menu['5'] = "Clean CVP RPMs (" + cvp_rpms.pretty_size + ")"
  menu['6'] = "Clean Elasticsearch Heap Dumps (" + cvp_elasticsearch_heap_dumps.pretty_size + ")"
  menu['7'] = "Clean CVP temporary upgrade directories (" + cvp_tmp_upgrade.pretty_size + ")"
  menu['9'] = "Clean everything"
  menu['Q'] = "Exit"

  while True:
    options = list(menu.keys())
    options.sort()
    for entry in options:
      print(entry + " - " + menu[entry])

    print()
    selection = input("Choose an option\n")

    if selection == '1':
      freed = system_logs.delete_files()
      message = "System logs - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '2':
      freed = system_crash_files.delete_files()
      message = "System crash files - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '3':
      freed = cvp_logs.delete_files()
      message = "CVP logs - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '4':
      freed = cvp_docker_images.delete_files()
      message = "CVP docker images - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '5':
      freed = cvp_rpms.delete_files()
      message = "CVP RPMs - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '6':
      freed = cvp_elasticsearch_heap_dumps.delete_files()
      message = "CVP Elasticsearch Heap Dumps - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '7':
      freed = cvp_tmp_upgrade.delete_files()
      message = "CVP temporary upgrade files - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == '9':
      freed = system_logs.delete_files()
      freed += system_crash_files.delete_files()
      freed += cvp_logs.delete_files()
      freed += cvp_docker_images.delete_files()
      freed += cvp_rpms.delete_files()
      freed += cvp_elasticsearch_heap_dumps.delete_files()
      freed += cvp_tmp_upgrade.delete_files()
      message = "Full cleanup - Freed " + str(freed) + " bytes"
      logging.info(message)
      print(message)
    elif selection == 'Q' or selection == 'q':
      break
    else:
      print("Unknown option.")
    
if __name__ == "__main__":
  main()