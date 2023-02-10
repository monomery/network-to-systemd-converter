# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 10:23:47 2022

@author: monomery
"""

import re
import os
import yaml

wdir="/mnt/c/Users/Mon/Documents/Python Scripts/puma-converter/network-scripts/"
wdir_systemd="/mnt/c/Users/Mon/Documents/Python Scripts/puma-converter/systemd/"
htb_init_dir = "/mnt/c/Users/Mon/Documents/Python Scripts/puma-converter/network-scripts/htb.init"
raw_files = os.listdir(path=wdir)

interface = ''
speed = ''

htb_if = ''
htb_if_qinq = ''
list1 = []
list2 = []
ip_list = []
route_list = []
speed_list = []
ip_link = []
# htb_script = []
multiplier = 1.06




'''{'main': [{'description': 'rappolovo_ooo-roga-i-kopita'}, {'interface': 'eth0.83'}, {'parent': 'eth0'}, {'speed': '100M'}, {'mtu': 1500}], 
'address': ['172.16.1.1/24', '172.16.1.2/24', '172.16.1.4/24'], 
'dhcp': [{'serveraddress': '172.16.1.1/24'}, {'router': '172.16.1.1'}, {'ntp': '172.16.1.1'}, {'dns': '172.162.112.11'}, {'dns': '172.121.121.11'}], 
'routes': ['5.202.2.210/32', '5.202.2.211/32', '5.202.2.212/32']}'''        

def search_speed():
    raw_tc_list = []
    raw_speed_list = []
    temp_list = []
    htb_script = []
    # speed_list = []
    with open(htb_init_dir) as htb_init_file:
        for i in htb_init_file:
            if len(i) != 1:
                raw_tc_list.append(i.split('\n'))     
        for i in raw_tc_list:
            match = re.search(r'/sbin/tc class add dev (\S+) parent 1:2 classid 1:30 htb rate (\S+) ceil \S+ prio 30', i[0])
            if match:
                raw_speed_list.append(match.groups())
                # print(raw_speed_list)
    for i in raw_speed_list:
        temp_list = []
        speed = i[1]
        interface = i[0]
        temp_list.append(interface)
        temp_list.append(speed)
        speed_list.append(list(temp_list))  
        htb_script = f"""tc qdisc add dev {interface} root cake bandwidth {speed}
tc qdisc add dev {interface} handle ffff: ingress
tc filter add dev {interface} parent ffff: protocol ip prio 50 u32 match ip src 0.0.0.0/0 police rate {speed} burst 2m drop flowid :1
"""
        # ip_link.append(f'''ip link set down dev {interface}''')
        # print('\n'.join(htb_script))
        # 08.02.22
        with open(f'{wdir_systemd}/tc-rules/{interface}.tc', 'w') as f:
            f.write(htb_script)
    # with open(f'{wdir_systemd}/ip_link.conf', 'w') as f:
    #     f.write('\n'.join(ip_link))
    return

def search_ip():
    temp_list = []
    interf = []
    ipaddr = []
    vlans_if = []
    for i in raw_files:
        u = re.match(r'^ifcfg-eth(1|0).?(\d+)?.?(\d+)?$', i)
        if u:
            with open(f'{wdir}/{i}') as ifup_file:
                # print(ifup_file.read())
                # for i in ifup_file.read():
                #     print(i)
                # print(ifup_file.read().split())
                for i in ifup_file.read().split():
                    # if_re = re.match(r'NAME="(eth(\S+)?.?(\S+)?)"', i)
                    # if_ip = re.match(r'IPADDR=(\d+.\d+.\d+.\d+)', i)
                    if re.match(r'NAME="eth(\S+)?.?(\S+)?"', i):
                        interf = re.match(r'NAME="?(eth(\S+)?.?(\S+)?)"', i)
                        ifn = interf.group(1)
                        temp_list.append(ifn)
                        vlans_if.append(f'VLAN={ifn}')
                    elif re.match(r'IPADDR=\d+.\d+.\d+.\d+', i):
                        ipaddr = re.match(r'IPADDR="?(\d+.\d+.\d+.\d+)"?', i)
                        temp_list.append(ipaddr.group(1))
                    # if len(temp_list) >= 2:
                    #     print()
                    # elif temp_list:

                    #     print()
                if len(temp_list) >= 2:
                    # print(temp_list)
                    ip_list.append(temp_list)
                # print(temp_list)
                temp_list = []
                    # temp_list = []
                    # print(if_re)
                    # if re.match('NAME="(eth(\S+)?.?(\S+)?)"'):
                    #     print(match.group(1))
                # match = re.match(r'TY\S+\s\S+\s\S+\s\S+\nNAME="(\S+)"\s\S+\s\S+\s\S+\s\S+\s\S+\nIPADDR=(\S+)\s\S+', ifup_file.read())
                # if match:
                #     print(list(match.groups()))
                #     ip_list.append(list(match.groups()))
    #print('\n'.join(sorted(vlans_if,key=len)))
    return ip_list

def search_route():
    #функция для поиска файлов route-, на выходе дает список роутов и их интерфейсы
    temp_list = []
    route_list_reverse = []
    route_list_temp = []
    route_interface = []
    for i in raw_files:
        u = re.match(r'^route-eth(1|0).?(\d+)?.?(\d+)?$', i)
        if u:
            with open(f'{wdir}/{i}') as route_file:
                for i in route_file.readlines():
                    match = re.search(r'(\S+) \S+ \S+ dev (\S+)', i)
                    if match:
                        temp_list.append(match.groups())
                        #print(temp_list)
                        route_list_reverse.append(temp_list[0])
                        temp_list = []
    
    # меняем местами интерфейс и роут
    for i in route_list_reverse:
        temp_list.append(i[1])
        temp_list.append(i[0])
        route_list_temp.append(tuple(temp_list))
        temp_list = []
    # объединяем роуты в один лист
    
    for i in route_list_temp:
        route_interface.append(i[0])

    for i in set(route_interface):  
        for jj in route_list_temp:
            if i == jj[0]:
                temp_list.append(jj[1])
                temp_list.append(i)
        route_list.append(list(set(temp_list)))
        temp_list = []
    #print(route_list)    
    return route_list         

def creating_config():
    # print(ip_list)
    po = []
    po2 = []
    sorted_po = []
    sorted_po2 = []
    vlans = []
    # htb_script = []
    for i in ip_list:
        po.append(list(set(sorted(i))))
        for k in route_list:
            sort_k = sorted(k)
            if i[0] == sort_k[-1]:
                po.append(list(set(sorted(k + i))))
                po.remove(list(set(sorted(i)))) 
    for i in po:
        sorted_po.append(sorted(i))
    for i in sorted_po:
        po2.append(list(set(sorted(i))))
        for k in speed_list:
            if i[-1] == k[0]:
                po2.append(list(set(sorted(k + i))))
                po2.remove(list(set(sorted(i))))            
    for i in po2:
        sorted_po2.append(sorted(i))

    final_config = ['[Match]',
                    '\n',
                    '[Network]',
                    'Description="from old puma"',
                    'DHCPServer=yes',
                    '\n',
                    '[DHCPServer]',
                    'DefaultLeaseTimeSec=1200',
                    'MaxLeaseTimeSec=9200',
                    'PoolOffset=100',
                    'PoolSize=100',
                    '\n',
                    '[Link]',
                    'MTUBytes=1500',
                    '\n']
    for i in sorted_po2:
        conf = final_config.copy()
        conf_netdev = []
        #print(i)
        description = 'from-old-puma'
        address_section = []
        main_section = [{'description': description},]
        routes_section = []
        dhcp_section = []
        yaml_structure ={}
        for k in i:
            if re.match(r'(eth\S+)', k):
                
                conf.insert(1,f'Name={k}')
                vlans.append(f'VLAN={k}')
                if re.match(r'eth0.(\d+)$', k): #ищем обычные интерфейсы
                    global htb_if
                    name_if = k
                    conf_netdev.append(f'[NetDev]\nName={k}\nKind=vlan\n')
                    vlan_id_raw = re.match(r'eth0.(\d+)$', k)
                    vlan_id = vlan_id_raw.group(1)
                    conf_netdev.append(f'[VLAN]\nId={vlan_id}')
                    ip_link.append(f'''networkctl down {k}''')
                    main_section.insert(1, {'vlanid': int(vlan_id)})
                    main_section.insert(2, {'parent': 'eth0'})
                elif re.match(r'eth0.\d+.(\d+)', k): #ищем qinq интерфейсы

                    name_if = k
                    vlan_id_raw = re.match(r'(eth0.\d+).(\d+)', k)
                    vlan_id = vlan_id_raw.group(2)
                    parent = vlan_id_raw.group(1)
                    conf_netdev.append(f'[NetDev]\nName={k}\nKind=vlan\n')
                    conf_netdev.append(f'[VLAN]\nId={vlan_id}')
                    ip_link.append(f'networkctl down {k}')
                    main_section.insert(1, {'vlanid': int(vlan_id)})
                    main_section.insert(2, {'parent': parent})
                    
            elif re.match(r'\S+./\S+', k): #ищем маршруты
                routes_section.append(k)
            elif re.match(r'\d+.\d+.\d+.\d+', k):      #ищем ip-адреса         
                address_section.append(f'{k}/24')
                dhcp_section = [{'serveraddress': k}, {'router': k}, {'ntp': k}, {'dns': k}, {'dns': '172.121.121.11'}]
                # print(address_dict)
                # print(k)
            elif re.match(r'\d+[k|M]bit', k): #ищем скорость

                match_speed = re.search(r'(\d+)([k|M]bit)', k).group()            
                speed = match_speed.strip('bit').upper()
                speed = speed + 'bit'
                main_section.append({'speed': speed})
                # conf.append(f'[CAKE]\nBandwidth={speed}\n')               
            # with open(f'{wdir_systemd}/{name_if}.network', 'w') as f:
            #      f.write(yaml(conf))
            # with open(f'{wdir_systemd}/{name_if}.netdev', 'w') as f:
            #     f.write('\n'.join(conf_netdev))
            # with open(f'{wdir_systemd}/ip_link.conf', 'w') as f:
            #     f.write('\n'.join(ip_link))
        
        
        yaml_structure.setdefault('main', main_section)
        main_section.append({'mtu': 1500})
        if len(main_section) == 4:
            main_section.insert(3, {'speed': None})
        if address_section:
            yaml_structure.setdefault('address', address_section)
        else:
            yaml_structure.setdefault('address', None)
        if dhcp_section:
            yaml_structure.setdefault('dhcp', dhcp_section)
        else:
            dhcp_section = [{'serveraddress': None}, {'router': None}, {'ntp': None}, {'dns': None}, {'dns': None}]
            yaml_structure.setdefault('dhcp', dhcp_section) 
        if routes_section:
            yaml_structure.setdefault('routes', routes_section)
        else:
            yaml_structure.setdefault('routes', None)
        #print(main_section)
        #print(routes_section)

        #print(address_section)
        #print(dhcp_section)
        #print('\n'.join(conf))
        with open(f'{wdir_systemd}/{name_if}-{description}.yaml', 'w') as f:
                 f.write(yaml.dump(yaml_structure, sort_keys=False))
        print(yaml.dump(yaml_structure, sort_keys=False))
    #print('\n'.join(sorted(vlans,key=len)))
     
# print(ip_list)        
def main():    
    search_ip()
    search_route()
    search_speed()
    creating_config()
main()


'''{'main': [{'description': 'rappolovo_ooo-roga-i-kopita'}, {'interface': 'eth0.83'}, {'parent': 'eth0'}, {'speed': '100M'}, {'mtu': 1500}], 
'address': ['172.16.1.1/24', '172.16.1.2/24', '172.16.1.4/24'], 
'dhcp': [{'serveraddress': '172.16.1.1/24'}, {'router': '172.16.1.1'}, {'ntp': '172.16.1.1'}, {'dns': '172.162.112.11'}, {'dns': '172.121.121.11'}], 
'routes': ['5.202.2.210/32', '5.202.2.211/32', '5.202.2.212/32']}'''        

