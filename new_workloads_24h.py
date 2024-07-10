from pce import IllumioPCE
import time,csv,auth_api
from datetime import datetime, timedelta, timezone


def create_pce_obj():
    pce_fqdn,username,password,org_id = auth_api.connect()
    pce = IllumioPCE(pce_fqdn,username,password,org_id) #type: ignore
    return pce


def check_time(datetime_data, hours):
    time_entry_dt = datetime.fromisoformat(datetime_data.replace("Z", "+00:00"))
    current_time_utc = datetime.now(timezone.utc)
    time_difference = current_time_utc - time_entry_dt
    if time_difference < timedelta(hours=hours):
        return True
    else:
        return False


def get_new_workloads_24h(workload_list):
    new_workloads_24h_list = []
    for workload in workload_list:
        if workload['managed'] == True:
            if check_time(workload['created_at'], 24):
                new_workloads_24h_list.append(workload)
    return new_workloads_24h_list


def get_formatted_workload_info(new_workloads_24h_list):
    formatted_workload_list = []
    for workload in new_workloads_24h_list:
        workload_dict = {}
        workload_dict['hostname'] = workload['hostname']
        workload_dict['ip_address'] = workload['interfaces'][0]['address']
        workload_dict['created_at'] = workload['created_at']
        for label in workload['labels']:
            workload_dict[label['key']] = label['value']
        formatted_workload_list.append(workload_dict)
    return formatted_workload_list
            

def write_to_csv(new_workloads_24h_list):
    date_time = time.strftime("%Y%m%d-%H%M%S")
    file_name = 'new_workloads_24h_' + date_time + '.csv'
    if len(new_workloads_24h_list) > 0:
        headers = [x for x in new_workloads_24h_list[0].keys()]
        with open(file_name, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(new_workloads_24h_list)


def main():
    pce = create_pce_obj()
    workload_list = pce.get_workloads()
    new_workloads_24h_list = get_new_workloads_24h(workload_list)
    formatted_workload_list = get_formatted_workload_info(new_workloads_24h_list)
    write_to_csv(formatted_workload_list)
    



main()