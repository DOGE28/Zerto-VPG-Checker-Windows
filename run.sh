echo "Checking if an instance is already running..."

PID=$(pgrep -f "alerts.py")

if [ -n "$PID" ]; then
    echo "An instance is already running. Exiting..."
    kill -9 $PID
    echo "Process $PID has been killed"
    echo "Proceeding..."
else
    echo "No instance is running. Proceeding..."
fi



cd ~/Zerto-Alerts/Zerto-VPG-Checker-main

source ./venv/bin/activate

cd appv2/

python3 alerts.py