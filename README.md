# Zerto VPG Checker

This project is designed to alert the cloud team when a percentage of a Zerto site's VPGs are down, if a site's total throughput is 0, or if the entire ZVM's throughput is 0. It is custom built for the Tonaquint team's infrastructure and only they have permission to use this code.

# Installation

Begin by making a directory called 'Zerto-Alerts' and entering it.

```
cd
mkdir Zerto-Alerts
cd Zerto-Alerts
```

Then run the following to download the monitor and make the installation and run scripts executable.

```
curl -LO https://github.com/DOGE28/Zerto-VPG-Checker/archive/refs/heads/main.zip
unzip main.zip
rm main.zip
cd Zerto-VPG-Checker-main
chmod +x install.sh
chmod +x run.sh
```

> [!Note]
> You may need to download unzip if the above script does not work. ```sudo apt install unzip```


If you haven't run into any errors, you can then run:

```
./install.sh
```

This will install all needed dependencies. Once finished, you will need to input all necessary environment variables into the .env file.

Below is the snippet of code that outlines which sites get monitored. They are grouped into production and infrastructure sites. Copy and paste which group you want into the bottom of alerts.py. The code for INF is already there and ready to go, so if you want production you will need to comment (#) INF out and make sure production is in.

```
###Production Threading
sgu_prod_thread = threading.Thread(target=monitor, args=('sgu prod',))
boi_prod_thread = threading.Thread(target=monitor, args=('boi prod',))
fb_prod_thread = threading.Thread(target=monitor, args=('fb prod',))

sgu_prod_thread.start()
boi_prod_thread.start()
fb_prod_thread.start()

sgu_prod_thread.join()
boi_prod_thread.join()
fb_prod_thread.join()

###Infrastructure Threading
sgu_inf_thread = threading.Thread(target=monitor, args=('sgu inf',))
boi_inf_thread = threading.Thread(target=monitor, args=('boi inf',))
okc_inf_thread = threading.Thread(target=monitor, args=('okc inf',))

sgu_inf_thread.start()
boi_inf_thread.start()
okc_inf_thread.start()

sgu_inf_thread.join()
boi_inf_thread.join()
okc_inf_thread.start()
```
Take note of how the code is organized. First the 'threading.Thread...' class is called for each site, then '.start()' then '.join()'. If it isn't working please review this section and make sure that it is formatted correctly. Also check the .env file.

# Systemd Commands

The install script will get everything ready for the monitor to run continuously, even after restart. But the service still needs to be started initially right after you've finished getting environment variables and setting which sites you want to monitor.

The below command will start the zerto-alerts service:

```
sudo systemctl start zerto-alerts
```

This command will check the status of the service and include important information from the most recent run of the monitor:

```
sudo sustemctl status zerto-alerts
```

Finally, to verify that the script is currently running, use the command:
```
sudo systemdctl status zerto-alerts.service
```
It should show the service as active and you will see the print statements of the script in the output.