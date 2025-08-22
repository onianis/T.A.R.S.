# O.P.E.N - Omnicompetent Port Emergence Norm
import socket, sys, argparse, ipaddress



# Global constants
LAST_PORT = 65535
FIRST_PORT = 1
TARGET_IP_AMOUNT_LIMIT = 1000
OPEN_STRING = '[ O.P.E.N. ]'



# Global flags
Target_ip_limit_override = False



# start global socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# TODO
def scan_port(ip, port):
    pass



def parse_ip_set(raw_text):
    try:
        # split raw text list into potential IP addressses
        delimited_set, clean_ips = raw_text.replace(' ', '').split(','), []

        # process each IP
        for candidate_entry in delimited_set:
            # check if entry is a network (if it contains '/')
            if '/' in candidate_entry:
                # save network separately
                candidate_network = ipaddress.IPv4Network(candidate_entry).hosts()

                # iterate over network and add all IPs
                for addr in candidate_network:
                    clean_ips.append(addr)

            # check if entry is a range of addresses (if it contains '-')
            elif '-' in candidate_entry:
                range_dash_idx = candidate_entry.index('-')

                # split and parse the range into two (hopefully) valid IP addresses
                range_begin, range_end = \
                    ipaddress.IPv4Address(candidate_entry[:range_dash_idx]), \
                    ipaddress.IPv4Address(candidate_entry[range_dash_idx + 1:])
                
                # iterate over the range and add all the available addresses
                current_ip = range_begin
                while current_ip <= range_end:
                    clean_ips.append(current_ip)
                    current_ip += 1

            # if it's neither, try to parse as a single IP
            else:
                candidate_address = ipaddress.IPv4Address(candidate_entry)
                clean_ips.append(candidate_address)
        
        # sanity check that kicks in when there are too many IPs in the final list
        if len(clean_ips) > TARGET_IP_AMOUNT_LIMIT and not Target_ip_limit_override:
            raise ValueError(f'{OPEN_STRING} WARNING: The total amount of IPs resulting from the provided ranges,\n' \
                f'\t\t\tnetworks, and/or addresses is quite high: {len(clean_ips)}.\n' \
                '\t\tTo allow the scanning such a high amount of IPs, you must override this restriction with the\n' \
                '\t\t\t--enable-huge-scans\n' \
                '\t\tcommand-line flag. Either verify the given IPs, or include the override flag in your command.')

        return clean_ips
    except Exception as e:
        print(f'{OPEN_STRING} ERROR: An exception occured when parsing the provided target IP input.\n' \
            '\t\tPlease double-check your input for any inconsistencies or formatting errors.\n' \
            '\t\tRemember that the target IP(s) should not be defanged, and should be comma-separated.\n\n' \
            '\t\tMore details about the error, from the specific module that failed, are given below:\n')
        print(e.args[0])
        sys.exit(-1) 



def parse_port_ranges(raw_text):
    try:
        # clean up input and split it into possible ranges w/ commas
        delimited, clean_ranges = raw_text.replace(' ', '').split(','), []
        for port_range in delimited:
            if ('-' in port_range):
                dash_idx = port_range.index('-')
                # chop up the provided string according to the location of the dash
                unsorted_range = (int(port_range[:dash_idx]), int(port_range[dash_idx + 1:]))
                # sort the tuple as it is being inserted into the list
                clean_ranges.append((min(unsorted_range), max(unsorted_range)))
            else:
                # if a single-number range was provided, duplicate it for both entries of the tuple
                clean_ranges.append((int(port_range), int(port_range)))

        # check if the maximum registered port exceeds the real-world limit
        max_port = max(abs(num) for port_range in clean_ranges for num in port_range)
        if max_port > LAST_PORT:
            raise ValueError(f'{OPEN_STRING} ERROR: The maximum port number indicated exceeds' \
                ' the number of actual ports.\n' \
                '\t\tThe applicable range is 1-65535 (inclusive).\n' \
                '\t\tPlease input a valid range of ports and try again.')
        
        # check the same thing for the minimum port
        min_port = min(abs(num) for port_range in clean_ranges for num in port_range)
        if min_port < FIRST_PORT:
            raise ValueError(f'{OPEN_STRING} ERROR: The minimum port number indicated is less' \
                ' than the number of the first available port.\n' \
                '\t\tThe applicable range is 1-65535 (inclusive).\n' \
                '\t\tPlease input a valid range of ports and try again.')

        return(clean_ranges)
    except Exception as e:
        print(f'{OPEN_STRING} ERROR: An exception occured when parsing the provided port range input.\n' \
        '\t\tPlease double-check your input for any inconsistencies or formatting errors.\n' \
        '\t\tRemember that the port range(s) should be comprised SOLELY of numbers, commas, and dashes.\n\n' \
        '\t\tMore details about the error, from the specific module that failed, are given below:\n')
        print(e.args[0])
        sys.exit(-1)
            


def main():
    global Target_ip_limit_override

    parser = argparse.ArgumentParser(description='O.P.E.N. - Omnicompetent Port Emergence Norm',
        epilog='T.A.R.S. and O.P.E.N. are projects by Shota Oniani / lavendermerchant. © 2025')

    parser.add_argument('-t', '--targets', metavar='', 
        dest='targets', help='List of IPs to scan. Delimited by commas. No spaces')
    parser.add_argument('-p', '--ports', metavar='', 
        dest='ports', help='List of all port ranges to scan. Defined by dashes. Delimited by commas. No spaces')
    parser.add_argument('--enable-huge-scans', metavar='', action='store_const', const=True,
        dest='enable_huge_scans', help=f'Used to override the limit for target IPs set at the program level: {TARGET_IP_AMOUNT_LIMIT}')

    args = parser.parse_args()

    if (not args.targets) or (not args.ports):
        parser.print_help()
        sys.exit(-1)

    raw_target_ips = args.targets
    raw_port_ranges = args.ports
    # just for cleanliness, set the flag to False instead the default None
    Target_ip_limit_override = (args.enable_huge_scans if args.enable_huge_scans is not None else False)

    # hand off raw input to IP and port parsers
    target_ips = parse_ip_set(raw_target_ips)
    target_ports = parse_port_ranges(raw_port_ranges)


    s.close()



main()