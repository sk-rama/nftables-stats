import argparse


template_01 = '''#!/usr/sbin/nft -f

flush ruleset


# define variables

#
# table declaration
#
# add table filter
add table inet table-filter


#
# chain declaration
#
#add chain filter input { type filter hook input priority 0; policy drop; }
add chain inet table-filter chain-input { type filter hook input priority 400; policy accept; }
add chain inet table-filter chain-output { type filter hook output priority 400; policy accept; }
'''

template_02 = 'add chain inet table-filter chain-udp-{udp_number}\n'

template_03 = '''
#
# rule declaration
#
#add rule filter input ct state established,related counter accept

add rule inet table-filter chain-input counter
add rule inet table-filter chain-output counter
'''

template_04 = '''# rules for chain chain-udp-{udp_number}
add rule inet table-filter chain-input udp dport {{ {udp_number} }} counter goto chain-udp-{udp_number}
add rule inet table-filter chain-output udp sport {{ {udp_number} }} counter goto chain-udp-{udp_number}
add rule inet table-filter chain-udp-{udp_number} ip protocol udp udp dport {{ {udp_number} }} counter accept
add rule inet table-filter chain-udp-{udp_number} ip protocol udp udp sport {{ {udp_number} }} counter accept

'''


def plugin_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--from", dest="of", type=int, default=50001, help="layer 4 port from start")
    parser.add_argument("-t", "--to", dest="to", type=int, default=50005, help="layer 4 port to end") 
    return parser.parse_args()


if __name__ == "__main__":
    args = plugin_arguments()

    temp_template_02 = ''
    temp_template_04 = ''
    for number in range(args.of, args.to + 1, 1):
        temp_template_02 = temp_template_02 + template_02.format(udp_number=number) 
        temp_template_04 = temp_template_04 + template_04.format(udp_number=number)
    print(template_01)
    print(temp_template_02)    
    print(template_03)
    print(temp_template_04)

