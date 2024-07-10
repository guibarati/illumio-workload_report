#For the items below, replace with the info for the PCE you are connecting to.
#The info has to be within quotes
#########################################
server = 'https://pce235.lab.local:8443'  #####Replace with your PCE address and port
api_user = 'api_1b53c4ca7de48f01f'      #####Replace with your API user
api_key = '783033263852d6756fb67e878780551c801d144ebb0b3f11cffafe20c7e62b82'  #####Replace with your API key
org_id = '1'  #####Replace with your org ID
#########################################



def connect():
    return server, api_user, api_key, org_id
