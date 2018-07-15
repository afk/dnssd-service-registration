#!/usr/bin/env python3

import dns.resolver
import dns.update
import dns.query

res = dns.resolver.Resolver()
#res.nameservers = ['8.8.8.8']

domain = 'meeting.timwattenberg.de'

# 1. Discover Registration domain
# RFC 6763 Sec. 11
answers = res.query('dr._dns-sd._udp.' + domain, 'PTR')
for rdata in answers:
    rdomain = str(rdata)
print('Registration Domain:', rdomain)

answers = res.query(rdomain, 'SOA')
for rdata in answers:
    rns = str(rdata.mname)
print('Registration NS:', rns)

answers = res.query('_dns-update._udp.' + rns, 'SRV')
for rdata in answers:
    rhost = str(rdata.target)
    rport = rdata.port
print('Registration Host:', rhost, 'Port', rport)

answers = res.query(rhost, 'A')
for rdata in answers:
    rip = str(rdata)
print('Registration IP:', rip, '\n')

# 2. Build RRs
update = dns.update.Update(domain)

# PTR RR(s)
instance = 'web.'
service = '_http._tcp'
update.add(service, 30, 'PTR', instance + service)
print(update, '\n')

# SRV and TXT RR
update.delete(instance + service)
update.add(instance + service, 30, 'SRV', '0 0 80 ns.meeting.timwattenberg.de.')
update.add(instance + service, 30, 'TXT', 'TXT')

# A/AAAA

# 3. Send DNS update to Server from 1.
response = dns.query.tcp(update, rip, port=rport)
print(response)
