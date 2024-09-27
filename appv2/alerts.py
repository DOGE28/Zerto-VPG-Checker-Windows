import zerto as z
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import threading








class Alerts():

    def __init__(self, location):
        self.location = location
        location_values = ['sgu prod', 'boi prod', 'fb prod', 'sgu inf', 'boi inf', 'okc inf']
        if location not in location_values:
            raise ValueError(f"Invalid location... Please choose from the following: {location_values}")
        self.zerto = z.ZertoGet(location)
        self.site_percent = self.zerto.get_percent_vpgs_up()
        self.zvm_throughput = self.zerto.get_throughput_zvm()
        self.site_throughput = self.zerto.get_throughput_sites()
        self.threshold = 90

    def determine(self):
        problems = []

        ###PROBLEM 1: IS ZVM THROUGHPUT 0?
        if self.zvm_throughput <= 0 and self.location != 'boi inf':
            print(self.zvm_throughput)
            problems.append(f"ZVM throughput is 0 for {self.location}")

        ###PROBLEM 2: ARE ANY SITE THROUGHPUTS 0?
        for site in self.site_throughput:
            for key, value in site.items():
                if value <= 0:
                    problems.append(f"Site {key} throughput is 0")

        ###PROBLEM 3: ARE ANY SITE VPG PERCENTAGES BELOW THRESHOLD?
        for site in self.site_percent:
            for key, value in site.items():
                if value < self.threshold:
                    problems.append(f"Site {key} has less than {self.threshold}% of VPGs up")

        self.problems = problems
                    

    def send_alert(self):
        if self.problems == []:
            print("No problems detected")
            return
        print("The following problems have been detected:")
        for problem in self.problems:
            print(problem)


class SendEmails(Alerts):
    def __init__(self, location):
        super().__init__(location)
        if 'inf' in location:
            self.server = "10.101.70.50"
        else:
            self.server = "10.200.201.15"
        self.server = "10.200.201.15"
        self.determine()
        self.sender = "systems@tonaquint.com"
        self.receiver = "tsullivan@tonaquint.com"
        self.subject = f"A problem has been detected at the {self.location.upper()} ZVM"
        self.body = f"""This is a test email
        
        The following problems have been detected at the {self.location.upper()} ZVM:

        {self.problems}

        Please investigate immediately!
        """
        self.port = 25
    
    def get_problems(self):
        return self.problems

    def send(self):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = self.subject
        if self.problems == []:
            print("No problems detected")
            return
        else:
            msg.attach(MIMEText(self.body, 'plain'))
            text = msg.as_string()
            server = smtplib.SMTP(self.server, self.port)
            server.sendmail(self.sender, self.receiver, text)
            server.quit()



###Loop Logic


consecutive_problem_count = 0
def monitor(location: str): #Creates a while loop function that can be called to run the monitoring logic indefinitely
    """
    location: str | The site to monitor, possible values ['sgu prod', 'boi prod', 'fb prod', 'sgu inf', 'boi inf', 'okc inf']
    """
    global consecutive_problem_count

    consecutive_threshold = 3
    while True:

        
        alert = SendEmails(location)
        problems = alert.get_problems()

        if problems == []:
            consecutive_problem_count = 0
            print("No problems detected")
        else:

        
            consecutive_problem_count += 1
            print(consecutive_problem_count)
            print(f"problem detected {problems}")

            if consecutive_problem_count >= 0:
                if consecutive_problem_count == consecutive_threshold:
                    alert.send()
                    print(f"Sending alert for {location}")
                    consecutive_problem_count = 0


        time.sleep(600)

# sgu_prod_thread = threading.Thread(target=monitor, args=('sgu prod',))
# boi_prod_thread = threading.Thread(target=monitor, args=('boi prod',))
# fb_prod_thread = threading.Thread(target=monitor, args=('fb prod',))


# sgu_prod_thread.start()
# boi_prod_thread.start()
# fb_prod_thread.start()


# sgu_prod_thread.join()
# boi_prod_thread.join()
# fb_prod_thread.join()

sgu_inf_thread = threading.Thread(target=monitor, args=('sgu inf',))
boi_inf_thread = threading.Thread(target=monitor, args=('boi inf',))
okc_inf_thread = threading.Thread(target=monitor, args=('okc inf',))

sgu_inf_thread.start()
boi_inf_thread.start()
okc_inf_thread.start()

sgu_inf_thread.join()
boi_inf_thread.join()
okc_inf_thread.start()






