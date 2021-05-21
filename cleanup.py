from glob import glob as search
import os
import math
#import logging

class Files:
  def __init__(self, directories=["./"], prefixes=["*"], recursive=True) -> None:
    self.files = []
    self.size = 0
    for directory in directories:
      for prefix in prefixes:
        current_search = directory + "/" + prefix
        matches = search(current_search, recursive=recursive)
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

  def list(self):
    return(self.files)

def main():
  system_logs = Files(directories=["/var/log"],prefixes=["*.gz", "*.0", "*.1"])
  cvp_logs = Files(directories=["/cvpi/logs", "/cvpi/hadoop/logs", "/cvpi/habase/logs", "/cvpi/apps/turbine/logs", "/cvpi/apps/aeris/logs"], prefixes=["*.log*", "*.out*"])
  cvp_docker_images = Files(directories=["/cvpi/docker"], prefixes=["*.gz"])
  cvp_rpms = Files(directories=["/RPMS"])

if __name__ == "__main__":
  main()