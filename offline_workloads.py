from pce import IllumioPCE
import json,os, datetime, csv, sys, yaml, code


def get_yaml(filename):
    original_dir = os.getcwd()
    try:
        with open(filename) as f:
            yaml_info = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"File {filename} not found")
        print("Run this utility from the same directory as Workloader")
        try:
            folder = input("Optionally enter the full path to the folder containing Workloader and the pce.yaml file: ")
            if folder:
                os.chdir(folder)
                yaml_info = get_yaml(filename)
                os.chdir(original_dir)
        except KeyboardInterrupt:
            sys.exit(1)
    return yaml_info


def get_pce_info(filename,pce_name):
    yaml_info = get_yaml(filename)
    if pce_name not in yaml_info:
        print(f"PCE {pce_name} not found in {filename}")
        sys.exit(1)
    pce = yaml_info[pce_name]
    fqdn = pce['fqdn']
    user = pce['user']
    password = pce['key']
    org_id = pce['org']
    port = pce['port']
    fqdn = f"{fqdn}:{port}"
    return fqdn,user,password,org_id


def create_pce_obj(filename,pce_name):
    pce_fqdn,username,password,org_id = get_pce_info(filename,pce_name)
    pce = IllumioPCE(pce_fqdn,username,password,org_id) #type: ignore
    return pce


def check_offline_workloads(workload_list):
    offline_workloads_list = []
    for workload in workload_list:
        if workload['online'] == False:
            offline_workloads_list.append(workload)
    return offline_workloads_list


def load_offline_workloads():
    filename = 'offline_workloads.json'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            offline_workloads_list = json.load(file)
    else:
        offline_workloads_list = []
    return offline_workloads_list


def compare_offline_workloads(offline_workloads_list):
    new_offline_workloads_list = []
    old_offline_workloads_list = load_offline_workloads()
    for workload in offline_workloads_list:
        if workload not in old_offline_workloads_list:
            new_offline_workloads_list.append(workload)
    return new_offline_workloads_list


def format_offline_workload_info(offline_workloads_list):
    formatted_offline_workload_list = []
    for workload in offline_workloads_list:
        workload_dict = {}
        workload_dict['hostname'] = workload['hostname']
        workload_dict['ip_address'] = workload['interfaces'][0]['address']
        for label in workload['labels']:
            workload_dict[label['key']] = label['value']
        workload_dict['last_heartbeat'] = workload['agent']['status']['last_heartbeat_on']
        formatted_offline_workload_list.append(workload_dict)
    return formatted_offline_workload_list


def report_offline(new_offline_workloads_list):
    if len(new_offline_workloads_list) > 0:
        date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"offline_workloads_{date}.csv"
        headers = [x for x in new_offline_workloads_list[0].keys()]
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(new_offline_workloads_list)


def save_offline_workloads(formatted_offline_workload_list):
    with open('offline_workloads.json', 'w') as file:
        json.dump(formatted_offline_workload_list, file, indent=4)


def main():
    if len(sys.argv) > 1:
        p = create_pce_obj('pce.yaml',sys.argv[1])
    else:
        p = create_pce_obj('pce.yaml','default_pce_name')
    ow = check_offline_workloads(p.workloads) #offline workloads
    fow = format_offline_workload_info(ow) #formatted offline workloads
    now = compare_offline_workloads(fow) #new offline workloads
    save_offline_workloads(now) #save offline workloads
    report_offline(now) #report new offline workloads

main()
#code.interact(local=dict(globals(),**locals()))