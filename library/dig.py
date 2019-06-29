
#!/usr/bin/env python
# coding: utf-8

DOCUMENTATION = """
---
module: dig

author:
    - "Alexis Facques" (@alexisfacques)

short_description: Check whether not an address or hostname can be resolved

description:
    - "This module allows to check whether not addresses or hostnames can be
       resolved on a remote host, and returns a populated list of IP adresses."

options:
    nameserver:
        description:
            - The name or IPv4 addresses of nameservers to use. Can either be
              a single string or a list.
        required: false
    type:
        description:
            -  Indicates what type of query is required: ANY, A, MX, SIG, etc.
               type can be any valid query type. If no type argument is
               supplied, dig will perform a lookup for an A record.
        required: false
    name:
        description:
            - The name of the resource record that is to be looked up. Can
              either be a single string or a list.
        required: true
    with_etc_hosts:
        description:
            - Whether or not the module should parse the host's /etc/hosts file
              before looking up the domain name.
        required: false
        default: true
"""

EXAMPLES = """
- dig:
    nameserver:
      - 8.8.8.8
    qtype: A
    name:
      - foo
      - bar
"""

from ansible.module_utils.basic import AnsibleModule

from socket import inet_aton, gethostbyname, gaierror

import dns.resolver
import dns.reversename
from dns.exception import DNSException

class NameserverException(Exception):
   pass

def resolve_name(resolver, name, qtype, with_etc_hosts=True):
    if qtype.upper() == "PTR":
        try:
            name = dns.reversename.from_address(name).to_text
        except dns.exception.SyntaxError:
            pass

    ret = []

    if with_etc_hosts:
        try:
            ret.append( gethostbyname(name) )
            return ret
        except gaierror:
            pass

    for answer in resolver.query(name, qtype):
        s = answer.to_text()
        if qtype.upper() == "TXT":
            s = s[1:-1]  # Strip outside quotes on TXT rdata
        ret.append(s)
    return ret

def get_nameserver_address(ns):
    """
    Check if 'ns' is an IP address. If so, return that, otherwise resolve name
    to address using system's resolver and return the resolved address.
    """
    try:
        inet_aton(ns)
        return ns
    except:
        try:
            return dns.resolver.query(ns)[0].address
        except Exception as e:
            raise NameserverException("Could not resolve %s." % ns)

def main():
    exit_message = dict(failed=False)

    module = AnsibleModule(
        argument_spec=dict(
            nameserver=dict(required=False, type="list"),
            qtype=dict(required=False, default="A"),
            name=dict(required=True, type="list"),
            with_etc_hosts=dict(required=False, type="bool", default=True)
        ),
        # No changes will be made to this environment with this module
        supports_check_mode=True
    )

    try:
        resolver = dns.resolver.Resolver()

        to_resolve_names = module.params["name"]
        qtype = module.params["qtype"]
        with_etc_hosts = module.params["with_etc_hosts"]

        if module.params["nameserver"]:
            nameservers = module.params["nameserver"]
            resolver.nameservers = list( map(lambda ns: get_nameserver_address(ns), nameservers) )

        ret = list( map(lambda n: resolve_name(resolver, n, qtype, with_etc_hosts), to_resolve_names) )
        exit_message = dict(failed=False, addresses=ret)

    except NameserverException as e:
        exit_message = dict(failed=True, msg="Could not resolve nameserver: %s" % e)
    except dns.resolver.NXDOMAIN as e:
        exit_message = dict(failed=True, msg="Unabled to resolve the domain using the nameservers: %s" % e)
    except dns.resolver.NoAnswer:
        exit_message = dict(failed=True, msg="No answer received from nameservers.")
    except dns.resolver.Timeout:
        exit_message = dict(failed=True, msg="Timeout error.")
    except dns.exception.DNSException as e:
        exit_message = dict(failed=True, msg="An error has occured with dnspython: %s" % e )
    except AttributeError as e:
        exit_message = dict(failed=True, msg="AttributeError: %s" % e)
    except Exception as e:
        exit_message = dict(failed=True, msg="An error has occured with the \"dig\" module: %s" % e)

    if exit_message["failed"]:
        module.fail_json(**exit_message)
    else:
        module.exit_json(**exit_message)

if __name__ == "__main__":
    main()
