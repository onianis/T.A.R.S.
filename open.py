# O.P.E.N - Omnicompetent Port Emergence Norm
import socket, sys, argparse, ipaddress, json, os



# Global constants
LAST_PORT = 65535
FIRST_PORT = 1
TARGET_IP_LIMIT = 1000
OPEN_STRING = '[ O.P.E.N. ]'



# start global socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# load language file by locale
def load_messages(lang="en"):
    path = os.path.join(os.path.dirname(__file__), f"lang_{lang}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
msgs = load_messages("en")



# TODO
def scan_port(ip, port):
    pass


# TODO NOW: FINISH IMPLEMENTING THIS FUNCTION FOR ALL EXCEPTIONS.
def handle_error_and_terminate(message, exception):
    print(f'{OPEN_STRING} ERROR: {message}' \
          f'{msgs["twotab"]}{msgs["more_details_below"]}')
    print(exception)
    sys.exit(-1)



def parse_ip_set(raw_text, target_ip_limit_override):
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
        if len(clean_ips) > TARGET_IP_LIMIT and not target_ip_limit_override:
            raise ValueError(f'{msgs["open_string_brackets"]} {msgs["warning_label"]} {"".join(msgs["ip_amount_limit_warning"])}')

        return clean_ips
    # addressValueError - incorrect ip formatting, >255, <1
    except ipaddress.AddressValueError as e:
        sys.exit(-1)
        handle_error_and_terminate("".join(msgs["ipaddress_value_error"]), e)
    except ValueError as e:
        handle_error_and_terminate("".join(msgs["general_ip_parse_value_error"]), e)



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
            raise ValueError(f'{msgs["open_string_brackets"]} {msgs["error_label"]} {"".join(msgs["port_range_max_error"])}')
        
        # check the same thing for the minimum port
        min_port = min(abs(num) for port_range in clean_ranges for num in port_range)
        if min_port < FIRST_PORT:
            raise ValueError(f'{msgs["open_string_brackets"]} {msgs["error_label"]} {"".join(msgs["port_range_min_error"])}')

        return(clean_ranges)
    except (ValueError, TypeError, IndexError) as e:
        handle_error_and_terminate("".join(msgs["general_port_range_error"]), e)
            


def main():
    parser = argparse.ArgumentParser(description=msgs["argparse_description"],
        epilog=msgs["argparse_epilog"])

    parser.add_argument('-t', '--targets', metavar='', 
        dest='targets', help=msgs["argparse_targets_flag_help"])
    parser.add_argument('-p', '--ports', metavar='', 
        dest='ports', help=msgs["argparse_ports_flag_help"])
    parser.add_argument('--enable-huge-scans', metavar='', action='store_const', const=True,
        dest='enable_huge_scans', help=f'{msgs["argparse_enable_huge_scans_flag_help"]} {TARGET_IP_LIMIT}')

    args = parser.parse_args()

    if (not args.targets) or (not args.ports):
        parser.print_help()
        sys.exit(-1)

    raw_target_ips = args.targets
    raw_port_ranges = args.ports
    # just for cleanliness, set the flag to False instead the default None
    target_ip_limit_override = bool(args.enable_huge_scans)

    # hand off raw input to IP and port parsers
    target_ips = parse_ip_set(raw_target_ips, target_ip_limit_override)
    target_ports = parse_port_ranges(raw_port_ranges)


    s.close()



main()