# SublimeLog: A bare-bones console logger for Sublime Text 2 & Sublime Text 3.
# Please see README file for license info.


import sublime_plugin
import sys
import sublime
import os
import time


class LogConsoleOutputCommand(sublime_plugin.ApplicationCommand):
    def __init__(self):
        # First we backup the standard input and output pipes.
        self.active = False
        self.ready = True
        self.out_backup = sys.stdout
        self.err_backup = sys.stderr

        # Then we obtain the log filename from the settings, if available. Otherwise use a default value.
        # Path handling should be cross-platform but has only been tested on OS X (for lack of access to other systems).
        settings = sublime.load_settings("SublimeLog.sublime-settings")
        # The following commented-out line seems broken in ST3 Build 3028:
        # self.logfilename = os.path.abspath(str(settings.get("logfile", os.path.join(os.path.expanduser("~"), ".subl.log"))))
        # We therefore use the following verbose workaround:
        self.logfilename = settings.get("logfile")
        if self.logfilename == None:
            self.logfilename = os.path.join(os.path.expanduser("~"), ".subl.log")
        # We open and truncate log file, or create a blank one. In case of an exception we exit.
        try:
            self.logfile = open(self.logfilename, "w", 1)
            self.logfile.truncate(0)
        except:
            sublime.status_message("SublimeLog: Error opening log file (" + self.logfilename + ").")
            self.ready = False
            return

    def run(self):
        # Here we toggle the logger, after ensuring that the log file has been properly opened.
        # There may be a more efficient way to do this but for all intents and purposes the overhead is tiny.
        if self.ready:
            if not self.active:
                self.active = True
                sublime.status_message("SublimeLog: Console logging activated (" + self.logfilename + ").")
                sys.stdout = self
                sys.stderr = self
                print ("=> => => Console logging activated (" + self.logfilename + "). Timestamp: " + time.strftime("%d %b %Y, %X", time.localtime()) + ".")
            else:
                self.active = False
                sublime.status_message("SublimeLog: Console logging deactivated (" + self.logfilename + ").")
                print ("<= <= <= Console logging deactivated (" + self.logfilename + "). Timestamp: " + time.strftime("%d %b %Y, %X", time.localtime()) + ".")
                sys.stdout = self.out_backup
                sys.stderr = self.err_backup
        else:
            sublime.status_message("SublimeLog: Error opening log file (" + str(self.logfilename) + ").")
            return

    def write(self, message):
        # This method overrides sys.stdout.write() and sys.stderr.write().
        # It simply duplicates the contents of the standard output and error pipes into the log file.
        self.out_backup.write(message)
        self.logfile.write(message)
