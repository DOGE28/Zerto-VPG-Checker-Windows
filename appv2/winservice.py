import time
import servicemanager
import win32serviceutil
import win32service
import win32event
import alerts

class MyPythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Zerto-Alerts"
    _svc_display_name_ = "My Python Background Service"
    _svc_description_ = "This service runs a Python script in the background."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Place your Python program here or import it as a module.
        while self.running:
            # Example: Run your script

            alerts.sgu_prod_thread.start()
            alerts.boi_prod_thread.start()
            alerts.fb_prod_thread.start()

            alerts.sgu_prod_thread.join()
            alerts.boi_prod_thread.join()
            alerts.fb_prod_thread.join()

            #time.sleep(10)  # Sleep for 10 seconds

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyPythonService)
