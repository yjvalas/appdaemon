import appdaemon.appapi as appapi
import datetime

#
# App to send email report for devices running low on battery
#
# Args:
#
# threshold = value below which battery levels are reported and email is sent
# always_send = set to 1 to override threshold and force send
# input_select = Name of input_select to monitor followed by comma separated list of values for which on action should be performed
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Battery(appapi.AppDaemon):

  def initialize(self):
    #self.check_batteries({"force": 1})
    time = datetime.time(6, 0, 0)
    self.run_daily(self.check_batteries, time) 
    
  def check_batteries(self, kwargs):
    devices = self.get_state()
    values = {}
    low = []
    for device in devices:
      battery = None
      if "battery" in devices[device]["attributes"]:
        battery = devices[device]["attributes"]["battery"]
      if "battery_level" in devices[device]["attributes"]:
        battery = devices[device]["attributes"]["battery_level"]
      if battery != None:
        if battery < int(self.args["threshold"]):
          low.append(device)
        values[device] = battery
    message = "Bettery Level Report\n\n"
    if low:
      message += "The following devices are low: (< {}) ".format(self.args["threshold"])
      for device in low:
        message = message + device + " "
      message += "\n\n"
    
    message += "Battery Levels:\n\n"
    for device in sorted(values):
      message += "{}: {}\n".format(device, values[device])
      
    if low or ("always_send" in self.args and self.args["always_send"] == "1") or ("force" in kwargs and kwargs["force"] == 1):
      self.notify(message, title="Home Assistant Battery Report", name = "smtp")
    