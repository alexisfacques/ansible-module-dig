# ansible-module-dig

`ansible-module-dig` is a custom Ansible module allowing you to run DNS
lookup operations from remote Ansible hosts, and returns a list of the resolved
IP(v4) addresses per name. The `dig` module may also be configured to parse the hosts'
`/etc/hosts` file before performing any lookup operation.

This module can thus be used to both:
- **resolve** one or multiple hostname(s);
- **assert** whether or not one or multiple hostname(s) can be resolved (module will **fail** if a hostname cannot be resolved to at least one address).

## `dig` module vs. Ansible `lookup('dig', ... )`

**Make sure to know what you're doing before using this module!** The official way for running DNS lookups in Ansible is by using the [`dig` lookup](https://docs.ansible.com/ansible/2.3/playbooks_lookups.html#more-lookups).

Main issue using lookup filters, like all templating, is that it is
evaluated on the Ansible control machine, and not the targeted host. This could
cause unexpected side effects when running your Ansible plays in complex
networking environments or deployment scenarios, where your control machine
can resolve all hosts of your cluster, but hosts cannot (e.g., running your configuration plays
through an external management network or in offline or highly secured network environments).

This Ansible `dig` module fills this gap by executing lookups from the
remote hosts directly.

## Getting started

### Requirements

The below requirements are needed **on the host that execute** this module.

- `dnspython` for Python.

### Installing

#### The "Ansible role" way

- Clone this repository to your Ansible `role_path`, or install via `ansible-galaxy`;
  ```sh
  ansible-galaxy install alexisfacques.ansible_module_dig
  ```
- Import the role in your playbooks before running any role or task that require the `dig` module:
  ```yaml
  - hosts: all
    roles:
      - alexisfacques.ansible_module_dig
    tasks:
      - name: Ensure google.com can be resolved
        dig:
          qtype: A
          name: google.com
        register: dig_result
  ```

#### The "Ansible library" way

Alternatively, if importing a role is too much of a hassle, you can store this
module in the `library` directory defined in your `ansible.cfg` file
(Default is a sub-directory called `library` in the directory that contains
your playbooks):
```
[defaults]
library = /path/to/your/library
```

## Usage

### Parameters

<table>
  <tr>
    <th>Parameter</th>
    <th>Choices/Defaults</th>
    <th>Comments</th>
  </tr>
  <tr>
    <td>qtype<br></td>
    <td>Default:<br>A</td>
    <td>Indicates what type of query is required: ANY, A, MX, SIG... Type can be any valid query type.</td>
  </tr>
  <tr>
    <td>name<br>- string | list / required</td>
    <td></td>
    <td>The name(s) of the resource(s) that is to be looked up.</td>
  </tr>
  <tr>
    <td>nameserver<br>- string | list<br></td>
    <td></td>
    <td>The name(s) or IPv4 address(es) of nameserver(s) to use.</td>
  </tr>
  <tr>
    <td>with_etc_hosts</td>
    <td>Choice:<br>true<br>false<br><br>Default:<br>true</td>
    <td>Whether or not the module should try to resolve the name using the host's /etc/hosts file(s) prior to running any lookup operation.</td>
  </tr>
</table>

### Return values

<table>
  <tr>
    <th>Key</th>
    <th>Returned</th>
    <th>Description</th>
  </tr>
  <tr>
    <td>addresses</td>
    <td>On success if all names have been resolved to at least 1 IPv4 address.</td>
    <td>A 2D array of IPv4 addresses to each of the looked up name.</td>
  </tr>
</table>

### Example of use

Examples of use can be found [here](./examples/demo.yml).

## Acknowlegments

- [jpmens](https://gist.github.com/jpmens/1b9f662111f119fabaaf)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
