# O.P.E.N - Omnicompetent Port Emergence Norm
import socket, sys



# Global constants
LAST_PORT = 65535
OPEN_STRING = "[ O.P.E.N. ]"



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



def scan_port(ip, port):
    pass



def parse_ip_set(raw_text):
    try:
        # split raw text list into potential IP addressses
        delimited_ip_set, clean_ips = raw_text.replace(' ', '').split(','), []

        # process each IP
        for candidate_ip in delimited_ip_set:
            # take the individual ip address and split it into an array of ints
            ip_segments = list(map(int, candidate_ip.split('.')))

            # invalid length or number (0 to 255)
            if (len(ip_segments) != 4) or (max(ip_segments) > 255) or (min(ip_segments) < 0):
                raise ValueError(f'{OPEN_STRING} ERROR: The following IP address is invalid: {candidate_ip}\n' \
                    '\t\tPlease verify it and try again.')

            clean_ips.append(candidate_ip)
        
        return clean_ips
    except ValueError as e:
        print(e.args[0])
        sys.exit(-1)
    except:
        print(f'{OPEN_STRING} ERROR: An exception occured when parsing the provided target IP input.\n' \
              '\t\tPlease double-check your input for any inconsistencies or formatting errors.\n' \
              '\t\tRemember that the target IPs should not be defanged and they should be comma-separated')
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
            raise ValueError(f'{OPEN_STRING} ERROR: The maximum port number indicated exceeds the number of actual ports.\n' \
                             '\t\tThe applicable range is 1-65535 (inclusive).\n' \
                             '\t\tPlease input a valid range of ports and try again.')

        return(clean_ranges)
    except ValueError as e:
        print(e.args[0])
        sys.exit(-1)
    except:
        print(f'{OPEN_STRING} ERROR: An exception occured when parsing the provided port range input.\n' \
        '\t\tPlease double-check your input for any inconsistencies or formatting errors.\n' \
        '\t\tRemember that the port range(s) should be comprised SOLELY of numbers, commas, and dashes.')
        sys.exit(-1)
            


def main():
    raw_target_ips = input('Input target IP address(es) (not defanged, comma-separated):\t')
    raw_port_ranges = input('Input port range(s) (comma- and dash-separated):\t\t')

    # parse ports
    port_ranges = parse_port_ranges(raw_port_ranges)

    # parse IPs
    target_ips = parse_ip_set(raw_target_ips)


    # print('Ports OPEN would scan:')
    # for prange in port_ranges:
    #     for i in range(prange[0], prange[1] + 1):
    #         print(i, end=', ')
    #     print()

    # res = s.connect_ex((target_ip, target_port))
    
    # print(f'Port {target_port} on {target_ip} is {'OPEN' if not res else 'CLOSED'}')



main()