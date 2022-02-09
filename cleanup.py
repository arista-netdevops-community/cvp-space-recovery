#!/usr/bin/env python
from datetime import datetime
from glob import glob as search
import logging
import math
import os
import re
import subprocess
import sys

log = logging.getLogger('cleanup')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.WARNING)

class Files:
  def __init__(self, name="", directories=["./"], prefixes=["*"], recursive=True, autoconfirm=False, remove_directories=False):
    self.name = name
    self.config = {}
    self.config['directories'] = directories
    self.config['prefixes'] = prefixes
    self.config['recursive'] = recursive
    self.config['autoconfirm'] = autoconfirm
    self.config['remove_directories'] = remove_directories
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
        matches = search(directory + "/" + prefix)
        if self.config['recursive']:
          matches += search(directory + "/" + "*/" + prefix)
          matches += search(directory + "/" + "*/" + "*/" + prefix)
          matches += search(directory + "/" + "*/" + "*/" + "*/" + prefix)
          matches += search(directory + "/" + "*/" + "*/" + "*/" + "*/" + prefix)
          matches += search(directory + "/" + "*/" + "*/" + "*/" + "*/" + "*/" + prefix)
          matches += search(directory + "/" + "*/" + "*/" + "*/" + "*/" + "*/" + "*/" + prefix)
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
    try:
      d = os.listdir(directory)
      for item in d:
          item = directory + "/" + item
          if os.path.isdir(item):
              self.__rmdir(item)
          elif os.path.isfile(item) or os.path.islink(item):
              os.remove(item)
              break
      for item in d:
        rmdir = directory + "/" + item
        if os.path.isdir(rmdir):
          os.rmdir(rmdir)
      try:
        os.rmdir(directory)
      except:
        pass
    except:
      if self.config['remove_directories']:
        matches = search(directory)
        for match in matches:
          os.rmdir(match)

  def list(self):
    return(self.files)

  def delete_files(self):
    if not self.config['autoconfirm']:
      confirm = input("This will delete all files and cannot be undone. Are you sure you want to continue? (y/N) ")
    if confirm.lower() == "y" or confirm.lower() == "yes":
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
      if self.config['remove_directories']:
        for directory in self.config['directories']:
          self.__rmdir(directory)

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

def showMenu(items, sort=True):
  options = list(items.keys())
  if sort:
    options.sort()
  for entry in options:
    print(entry + " - " + items[entry])
  choice = input("Choose an option\n")
  return(choice)

def main():
  system_logs = Files(name="System logs", directories=["/var/log"],prefixes=["*.gz", "*.[0-9]"])
  system_crash_files = Files(name="System crash files", directories=["/var/crash"])
  cvp_logs = Files(name="CVP Rotated logs", directories=["/cvpi/logs", "/cvpi/hadoop/logs", "/cvpi/hbase/logs", "/cvpi/apps/turbine/logs", "/cvpi/apps/aeris/logs", "/cvpi/apps/cvp/logs"], prefixes=["*.log.*", "*.out.*", "*.gc.*", "*.gz", "*.[0-9]"])
  cvp_current_logs = Files(name="CVP Current logs", directories=["/cvpi/logs", "/cvpi/hadoop/logs", "/cvpi/hbase/logs", "/cvpi/apps/turbine/logs", "/cvpi/apps/aeris/logs", "/cvpi/apps/cvp/logs"], prefixes=["*.log", "*.out", "*.gc"])
  cvp_docker_images = Files(name="CVP docker images", directories=["/cvpi/docker"], prefixes=["*.gz"])
  cvp_rpms = Files(name="CVP RPMs", directories=["/RPMS"], prefixes=["*.rpm"])
  cvp_elasticsearch_heap_dumps = Files(name="CVP Elasticsearch Heap Dumps", directories=["/cvpi/apps/aeris/elasticsearch"], prefixes=["*.hprof"])
  cvp_tmp_upgrade = Files(name="Temporary upgrade files", directories=["/tmp/upgrade*"], prefixes=["*"], remove_directories=True)

  kubelet_logs = {}
  kubelet_logs['all'] = Files(name="Kubelet Logs - All", directories=["/var/log"], prefixes=["kubelet.*.root.log.*"])
  kubelet_logs['info'] = Files(name="Kubelet Logs - Info", directories=["/var/log"], prefixes=["kubelet.*.root.log.INFO.*"])
  kubelet_logs['warning'] = Files(name="Kubelet Logs - Warning", directories=["/var/log"], prefixes=["kubelet.*.root.log.WARNING.*"])
  kubelet_logs['error'] = Files(name="Kubelet Logs - Error", directories=["/var/log"], prefixes=["kubelet.*.root.log.ERROR.*"])

  while True:
    os.system('clear')
    menu = {}
    menu['0'] = "Clean old system logs (" + system_logs.pretty_size + ")"
    menu['1'] = "Clean system crash files (" + system_crash_files.pretty_size + ")"
    menu['2'] = "Clean Rotated CVP logs (" + cvp_logs.pretty_size + ")"
    menu['3'] = "Clean Current CVP logs (" + cvp_current_logs.pretty_size + ")"
    menu['4'] = "Clean CVP docker images (" + cvp_docker_images.pretty_size + ")"
    menu['5'] = "Clean CVP RPMs (" + cvp_rpms.pretty_size + ")"
    menu['6'] = "Clean Elasticsearch Heap Dumps (" + cvp_elasticsearch_heap_dumps.pretty_size + ")"
    menu['7'] = "Clean CVP temporary upgrade directories (" + cvp_tmp_upgrade.pretty_size + ")"
    menu['8'] = "Vacuum system journal"
    menu['9'] = "Clean kubelet logs (" + kubelet_logs['all'].pretty_size + ")"
    menu["="] = "=============================================================="
    menu['A'] = "Clean all"
    menu['M'] = "More options"
    menu['Q'] = "Exit"

    extended_menu = {}
    extended_menu['1s'] = "Show old system log files"
    extended_menu['2s'] = "Show old system crash files"
    extended_menu['3s'] = "Show CVP log files"
    extended_menu['4s'] = "Show CVP docker images"
    extended_menu['5s'] = "Show CVP RPM files"
    extended_menu['6s'] = "Show Elasticsearch heap dumps files"
    extended_menu['7s'] = "Show temporary upgrade files"
    extended_menu['9s'] = "Show Kubelet logs"
    extended_menu['R']  = "Reload"

    kubelet_menu = {}
    kubelet_menu['9a'] = "Clean all kubelet logs (" + kubelet_logs['all'].pretty_size + ")"
    kubelet_menu['9i'] = "Clean kubelet info logs (" + kubelet_logs['info'].pretty_size + ")"
    kubelet_menu['9w'] = "Clean kubelet warning logs (" + kubelet_logs['warning'].pretty_size + ")"
    kubelet_menu['9e'] = "Clean kubelet error logs (" + kubelet_logs['error'].pretty_size + ")"

    selection = showMenu(menu)

    if selection.lower() == 'm':
      selection = showMenu(extended_menu)
    elif selection == '9':
      selection = showMenu(kubelet_menu)

    if selection == '0':
      freed = system_logs.delete_files()
      message = "System logs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '0s':
      print(system_logs.list())
    elif selection == '1':
      freed = system_crash_files.delete_files()
      message = "System crash files - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '1s':
      print(system_crash_files.list())
    elif selection == '2':
      freed = cvp_logs.delete_files()
      message = "CVP Rotated logs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '2s':
      print(cvp_logs.list())
    elif selection == '3':
      print("WARNING! This may remove files that may be useful to debug issues.")
      freed = cvp_current_logs.delete_files()
      message = "CVP Current logs - Freed %s.\nPlease restart CVP to free up space used by open log files." % convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '3s':
      print(cvp_current_logs.list())
    elif selection == '4':
      freed = cvp_docker_images.delete_files()
      message = "CVP docker images - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '4s':
      print(cvp_docker_images.list())
    elif selection == '5':
      freed = cvp_rpms.delete_files()
      message = "CVP RPMs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '5s':
      print(cvp_rpms.list())
    elif selection == '6':
      freed = cvp_elasticsearch_heap_dumps.delete_files()
      message = "CVP Elasticsearch Heap Dumps - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '6s':
      print(cvp_elasticsearch_heap_dumps.list())
    elif selection == '7':
      freed = cvp_tmp_upgrade.delete_files()
      message = "CVP temporary upgrade files - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection == '7s':
      print(cvp_tmp_upgrade.list())
    elif selection == '8':
      vacuum_time = input("How many days to keep on the journal? (Default: 2 days)\n")
      if vacuum_time:
        freed = clean_system_journal(vacuum_time=vacuum_time)
      else:
        freed = clean_system_journal()
      message = "System journal vacuum - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == '9a':
      freed = kubelet_logs['all'].delete_files()
      message = "Kubelet logs - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == '9i':
      freed = kubelet_logs['info'].delete_files()
      message = "Kubelet logs (info) - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == '9w':
      freed = kubelet_logs['warning'].delete_files()
      message = "Kubelet logs (warning) - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == '9e':
      freed = kubelet_logs['error'].delete_files()
      message = "Kubelet logs (error) - Freed " + convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == '9s':
      print("--- Info ---")
      print(kubelet_logs['info'].list())
      print("--- Warning ---")
      print(kubelet_logs['warning'].list())
      print("--- Error ---")
      print(kubelet_logs['error'].list())
    elif selection.lower() == 'a':
      print("WARNING! This may remove files that may be useful to debug issues.")
      vacuum_time = input("How many days to keep on the journal? (Default: 2 days)\n")
      freed = system_logs.delete_files()
      freed += system_crash_files.delete_files()
      freed += cvp_logs.delete_files()
      freed += cvp_current_logs.delete_files()
      freed += cvp_docker_images.delete_files()
      freed += cvp_rpms.delete_files()
      freed += cvp_elasticsearch_heap_dumps.delete_files()
      freed += cvp_tmp_upgrade.delete_files()
      freed += kubelet_logs['all'].delete_files()
      if vacuum_time:
        freed += clean_system_journal(vacuum_time=vacuum_time)
      else:
        freed += clean_system_journal()
      message = "Full cleanup - Freed %s.\nPlease restart CVP to free up space used by open log files." %convert_size(freed)
      log.info(message)
      print(message)
    elif selection.lower() == 'q':
      break
    elif selection.lower() == 'r':
      main()
      break
    elif selection.lower() == 'm' or selection.lower() == '9':
      pass
    else:
      print("Unknown option %s." %selection)

    try:
      f = input("\nPress enter to continue")
    except:
      pass
    
if __name__ == "__main__":
  # Python 2-3 compatibility workaround
  try:
    input = raw_input
  except NameError:
    pass
  main()