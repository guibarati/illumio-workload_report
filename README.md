### This repo contains:  
- One package representing the PCE class `/pce`
- One script holding the API credentials `auth_api.py`
- One script to report any new workload added to the PCE in the past 24 hours `new_workloads_24h.py`
- One script to report any new workload health condition since the last saved condition report `workload_health.py`

### Usage:
1. Edit `auth_api.py` with PCE URL, API key, API secret, and org ID.  
This module stores the information necessary to connect and authenticate to the PCE.  
It is used by all other modules.  

2. Schedule the module `new_workloads_24h.py` to run every 24h.  
This module will create a CSV report with all workloads added in the past 24 hours.  
The 24 hours are considered from the time the script is run.  
If the script is not run in 24 hours intervals new workloads may be missed if they were added more than 24 hours before the time the script runs.  
If new workloads were added in the last 24 hours from the time the script runs, it will create a CSV with the name format `new_workloads_24h_yyyymmdd-hhmmss.csv`.  
If no new workload were added in the last 24 hours from the time the script runs, no CSV report will be created.  

3. Run the module `workload_health.py` to get a report of workloads with warning or error health status.  
    3.1. Before running this module, create a file in the same folder named `applications.csv` with the format  
    3.1.1. No header  
    3.1.2. One application label name per line (any label of any type can be entered and all workloads with that label will be queried for health warnings)  
  
3.2 This module will create:  
    3.2.1 A file named `workload_conditions.json` to save the latest health information for the workloads in the selected applications.  
    3.2.2 One CSV report per application if:   
    There is 1 or more workloads with that application label with a health warning and:  
    The workload had no health warnings on the last report or;   
    The health warning in the workload is different than the previously saved health warning for that workload.

3.2.3 The file name will be `$applicaitonname_conditions_yyyy_mm_dd.csv`


## Compiling into exe:
1. The script can be compiled into an exe file to run on Windows systems and avoid the need to import individual libraries.

2. To compile the script:  
2.1 Install the PyInstaller module:  
2.1.2 `python -m pip install PyInstaller`  
2.2 Use PyInstaller to compile the script:  
2.2.1 `python -m PyInstaller --onefile [script_name.py]`

The exe file will be created under the 'dist' folder. The 'dist' folder will be in the same folder where the PyInstaller runs.

 
