# Networking Basics for Support Work

Network troubleshooting is most effective when it follows the path a request takes: physical/link connectivity, local addressing, routing, name resolution, and finally the application service. This chapter uses read-only inspection and approved test destinations; it does not teach scanning unrelated devices.

## The basic path

1. **Link:** Is Ethernet connected or is Wi-Fi associated with the approved access point?
2. **Address:** Does the interface have an address and prefix appropriate for this network?
3. **Route:** Is there a route to the intended destination, and is the default gateway expected?
4. **Name resolution:** Can the configured resolver translate an approved hostname?
5. **Service:** Is the authorized service listening and responding on its expected port?

These layers help distinguish a DNS issue from a missing route or a failed application. A device can have an IP address while still lacking a working gateway, DNS, or remote service.

## Key terms

- **IP address:** a logical address assigned to an interface, statically or by DHCP.
- **Prefix/subnet:** the network portion used to decide whether a destination is local or routed elsewhere.
- **DHCP:** a protocol commonly used to lease addresses and related network settings.
- **Gateway/router:** the next hop used for destinations outside the local subnet.
- **DNS:** the naming system that maps hostnames to addresses.
- **TCP and UDP:** transport protocols with different delivery and connection behavior; a port number identifies an application endpoint, not a machine by itself.
- **Firewall:** policy that allows or blocks traffic according to addresses, ports, interfaces, and connection state.

## Read-only baseline

On Linux systems with `ip` and `getent` available:

```bash
ip -brief link
ip -brief address
ip route
getent hosts example.org
```

Use a hostname approved by the organization rather than treating `example.org` as a required target. `getent hosts` asks the configured name-service path; it does not prove that every application protocol works. Record the command's result and timestamp without sharing private addresses or host identifiers publicly.

Some minimal installations may not have the `ip` utility or a name-service configuration that supports `getent`. Record the missing prerequisite and use the approved local console or system interface; do not install software during first-line triage unless that is part of the authorized support plan.

## DNS versus connectivity

If an authorized IP-based service works but its approved hostname does not, investigate name resolution. If the address and route are missing, DNS is not the first problem to solve. Avoid hard-coding an address as a long-term workaround: services can move, and HTTPS certificates usually identify names rather than arbitrary addresses.

Never publish raw DNS logs or network inventories without review. They can reveal staff names, site structure, internal services, or operational locations.

## Safe service checks

For a service on a system you own or administer, first inspect local state and documentation. A local loopback check may be appropriate when the service owner has approved it. Do not probe public hosts, scan neighboring devices, or change firewall rules as a substitute for confirming scope.

Before testing, write down:

- the authorized source and destination;
- the service and port expected;
- the permitted test method and time window;
- the expected result and stop condition;
- who will receive the sanitized results.

If no service owner or approved target is identified, stop at local configuration inspection and escalate.

## Worked diagnostic scenario

**Observed:** the wireless interface is associated and has an address; the routing table lacks the expected default route; the hostname lookup fails.

**Reasoning:** because the default route is absent, first confirm the approved network's addressing and gateway configuration with its administrator. A failed hostname lookup is not enough to conclude that DNS alone is broken.

**Verification:** after an authorized configuration correction, inspect the route table again and test only the approved resolver/service. Record both the before and after states.

## Further study

For interface behavior and address configuration, consult the `ip(8)` and `ip-route(8)` manual pages on the target distribution. Network-manager commands, resolver status tools, and firewall interfaces differ across Raspberry Pi OS, Debian, and other distributions; each practical recipe must name its tested platform and optional dependencies.
