# Step 1: Check if Python is installed
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Please install Python and try again."
    exit 1
}

# Step 2: Install Python dependencies
Write-Host "Installing Python dependencies"

# Create a virtual environment
python -m venv venv
./venv/Scripts/Activate.ps1
python -m pip install -r requirements.txt

# Step 3: Set up location information

$locationCount = 1
$continue = $true

# Create/overwrite the .locationinfo file
New-Item -Path . -Name ".locationinfo" -ItemType "file" -Force

while ($continue) {
    $location = Read-Host "Enter the location (IP address) for Location$locationCount"
    $secret = Read-Host "Enter the secret string for Location$locationCount"

    # Write the location and secret to the .locationinfo file
    Add-Content -Path ".\.locationinfo" -Value "`n# Location $locationCount"
    Add-Content -Path ".\.locationinfo" -Value "location$locationCount = $location"
    Add-Content -Path ".\.locationinfo" -Value "secret$locationCount = $secret"

    # Ask if the user wants to add another location
    $addMore = Read-Host "Do you want to add another location? (yes/no)"
    if ($addMore -ne "yes") {
        $continue = $false
    }

    $locationCount++
}

Write-Host "Location and secret information have been saved to .locationinfo"









# Step 3: Install the service
Write-Host "Installing the service..."
python appv2/winservice.py install

# Step 4: Start the service
Write-Host "Starting the service..."
python your_service_script.py start

Write-Host "Installation completed. The service is now running."

