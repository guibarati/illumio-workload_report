from pce import IllumioPCE
import csv,auth_api,os,json
import datetime

def create_pce_obj():
    pce_fqdn,username,password,org_id = auth_api.connect()
    pce = IllumioPCE(pce_fqdn,username,password,org_id) #type: ignore
    return pce


def get_list_of_applications():
    filename = 'applications.csv'
    list_of_applications = []
    if os.path.exists(filename):
        with open(filename, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                list_of_applications.append(row[0])
    else:
        print('')
        print('WARNING: File applications.csv not found.')
        print('         File applications.csv must be in the same folder as this script.')
        print('         The file should contain a list of application names, one per line and no header.')
        print('')
        exit()
    return list_of_applications


def get_workloads_per_application(pce_obj,application_list):
    workloads_per_application_dict = {}
    for application in application_list:
        workloads_per_application_dict[application] = pce_obj.workloads.labels(application)
    return workloads_per_application_dict


def get_application_workloads_conditions(pce_obj,worklworkloads_per_application_dict):
    applications_workoads_conditions = {}
    for k,v in worklworkloads_per_application_dict.items():
        applications_workoads_conditions[k] = {}
        for workload in v:
            conditions_list = []
            workload_hostname = workload['hostname']
            for condition_type,conditions in workload['agent']['status']['agent_health_errors'].items():
                conditions_list.extend(conditions)
            workload_ven_href = workload['ven']['href']
            workload_ven = pce_obj.vens.filter(href=workload_ven_href)[0]
            for ven_condition in workload_ven['conditions']:
                conditions_list.append(ven_condition['latest_event']['notification_type'])
            if len(conditions_list) > 0:
                if workload_hostname not in applications_workoads_conditions[k]:
                    applications_workoads_conditions[k][workload_hostname] = {}
                applications_workoads_conditions[k][workload_hostname] = conditions_list
    return applications_workoads_conditions #{'app2': {'server122.lab.local': ['security_policy_refresh_failure', 'agent.missed_heartbeats'], 'server127.lab.local': ['security_policy_refresh_failure']},'app3': {...}}


def save_workload_conditions(applications_workoads_conditions):
    with open('workload_conditions.json', 'w') as file:
        json.dump(applications_workoads_conditions, file, indent=4)


def load_previous_conditions(workload_conditions_file):
    if os.path.exists(workload_conditions_file):
        with open(workload_conditions_file, 'r') as file:
            saved_conditions = json.load(file)
    else:
        saved_conditions = {}
    return saved_conditions


def compare_conditions(saved_conditions,applications_workoads_conditions):
    new_conditions = {}
    for application,workloads in applications_workoads_conditions.items():
        if application in saved_conditions:
            for workload in workloads:
                if workload in saved_conditions[application]:
                    if saved_conditions[application][workload] != applications_workoads_conditions[application][workload]:
                        if application not in new_conditions:
                            new_conditions[application] = {}
                        new_conditions[application][workload] = applications_workoads_conditions[application][workload]
                else:
                    if application not in new_conditions:
                        new_conditions[application] = {}
                    new_conditions[application][workload] = applications_workoads_conditions[application][workload]
        else:
            for workload in workloads:
                if application not in new_conditions:
                    new_conditions[application] = {}
                new_conditions[application][workload] = applications_workoads_conditions[application][workload]
    return new_conditions


def report_conditions(new_conditions):
    for application, workloads in new_conditions.items():
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{application}_conditions_{date}.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Workload Name', 'Conditions'])
            for workload, conditions in workloads.items():
                writer.writerow([workload, '; '.join(conditions)])


list_of_applications = get_list_of_applications()
p = create_pce_obj()
w = get_workloads_per_application(p,list_of_applications)
c = get_application_workloads_conditions(p,w) #current conditions
sc = load_previous_conditions('workload_conditions.json') #saved_conditions
nc = compare_conditions(sc,c) #new_conditions
save_workload_conditions(c)
report_conditions(nc)