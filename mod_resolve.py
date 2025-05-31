# Module for DNS resolution of discovered subdomains
# This module verifies which subdomains are actually live by resolving their DNS records

import dns.resolver
import concurrent.futures

def resolve_subdomains(subdomains, threads=10, verbose=False):
    print(f"DEBUG: mod_resolve.resolve_subdomains called with subdomains: {subdomains}, type: {type(subdomains)}") # Hinzugefügte Debug-Zeile
    resolved = []
    # ... restlicher Code
    
    def resolve_single(subdomain):
        try:
            # Try to resolve the A record
            answers = dns.resolver.resolve(subdomain, 'A')
            ip_addresses = [str(answer) for answer in answers]
            if verbose:
                print(f"[+] Resolved: {subdomain} -> {', '.join(ip_addresses)}")
            return subdomain, ip_addresses
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            # Try CNAME as fallback
            try:
                answers = dns.resolver.resolve(subdomain, 'CNAME')
                cname = str(answers[0].target).rstrip('.')
                if verbose:
                    print(f"[+] CNAME: {subdomain} -> {cname}")
                return subdomain, [f"CNAME: {cname}"]
            except:
                return None
        except Exception as e:
            if verbose:
                print(f"[-] Error resolving {subdomain}: {str(e)}")
            return None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_subdomain = {executor.submit(resolve_single, subdomain): subdomain for subdomain in subdomains}
        for future in concurrent.futures.as_completed(future_to_subdomain):
            result = future.result()
            if result:
                resolved.append(result)
    
    return resolved
