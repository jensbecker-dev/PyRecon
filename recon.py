# Main script for the PyRecon tool
# This script orchestrates the subdomain enumeration process

import os, sys, argparse
import banner
import mod_sublist3r
import mod_altdns
import mod_resolve

def create_output_directory():
    """
    Create an output directory for saving results.
    """
    try:
        output_dir = "results"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
    except Exception as e:
        print(f"[-]  Error: {str(e)}")
        return None

def main():

    # Show banner
    banner.show()

    # Argument parser
    parser = argparse.ArgumentParser(description="Subdomain enumeration using Sublist3r and AltDNS.")
    parser.add_argument("-d", "--domain", required=True, help="Target domain to enumerate subdomains.")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads to use.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("-w", "--wordlist", help="Path to the wordlist file for AltDNS permutations.")
    parser.add_argument("--skip-altdns", action="store_true", help="Skip AltDNS permutation step.")
    parser.add_argument("--resolve", action="store_true", help="Resolve generated subdomains to check which ones exist.")
    args = parser.parse_args()

    subdomains_sublist3r = mod_sublist3r.run(
        target_domain=args.domain,
        threads=args.threads,
        verbose=args.verbose
    )

    if not subdomains_sublist3r:
        print("[-]  No subdomains found.")
        return
    
    print(f"[+]  Found {len(subdomains_sublist3r)} subdomains with Sublist3r.")

    output_dir = create_output_directory()
    if output_dir:
        # Save initial Sublist3r results
        sublist3r_output_file = os.path.join(output_dir, f"{args.domain}_subdomains.txt")
        mod_sublist3r.save_to_file(subdomains_sublist3r, sublist3r_output_file)
        
        # Run AltDNS on the discovered subdomains if not skipped
        if not args.skip_altdns:
            print("[+] Running AltDNS to generate permutations...")
            permuted_subdomains = mod_altdns.run(
                target_domain=args.domain,
                subdomains_list=subdomains_sublist3r,
                wordlist=args.wordlist,
                threads=args.threads,
                verbose=args.verbose
            )
            
            if permuted_subdomains and len(permuted_subdomains) > 0:
                altdns_output_file = os.path.join(output_dir, f"{args.domain}_altdns.txt")
                mod_altdns.save_to_file(permuted_subdomains, altdns_output_file)
                
                # Combine unique results
                all_subdomains = list(set(subdomains_sublist3r + permuted_subdomains))
                print(f"[+] Total unique subdomains (Sublist3r + AltDNS): {len(all_subdomains)}")
                
                combined_output_file = os.path.join(output_dir, f"{args.domain}_combined.txt")
                with open(combined_output_file, 'w') as f:
                    for subdomain in all_subdomains:
                        f.write(f"{subdomain}\n")
                print(f"[+] Combined results saved to {combined_output_file}")
                
                # Resolve subdomains if requested
                if args.resolve:
                    print(f"[+] Resolving subdomains to find which ones exist...")
                    
                    # For performance reasons, limit the number of subdomains to resolve
                    resolve_limit = 500
                    if len(all_subdomains) > resolve_limit:
                        print(f"[*] Limiting resolution to {resolve_limit} subdomains (out of {len(all_subdomains)}) for performance reasons")
                        subdomains_to_resolve = subdomains_sublist3r + permuted_subdomains[:resolve_limit-len(subdomains_sublist3r)]
                    else:
                        subdomains_to_resolve = all_subdomains
                    
                    resolved_subdomains = mod_resolve.resolve_subdomains(
                        subdomains_to_resolve,
                        threads=args.threads,
                        verbose=args.verbose
                    )
                    
                    if resolved_subdomains:
                        print(f"[+] Found {len(resolved_subdomains)} live subdomains")
                        
                        # Save resolved subdomains with their IP addresses
                        resolved_output_file = os.path.join(output_dir, f"{args.domain}_resolved.txt")
                        with open(resolved_output_file, 'w') as f:
                            for subdomain, ips in resolved_subdomains:
                                f.write(f"{subdomain} -> {', '.join(ips)}\n")
                        print(f"[+] Resolved subdomains saved to {resolved_output_file}")
                        
                        # Also save just the subdomain names for easy use with other tools
                        resolved_names_file = os.path.join(output_dir, f"{args.domain}_resolved_names.txt")
                        with open(resolved_names_file, 'w') as f:
                            for subdomain, _ in resolved_subdomains:
                                f.write(f"{subdomain}\n")
                        print(f"[+] Resolved subdomain names saved to {resolved_names_file}")
                    else:
                        print("[-] No live subdomains found")
            else:
                print("[-] AltDNS did not generate any valid permutations.")
        else:
            print("[*] AltDNS step skipped as requested.")

if __name__ == "__main__":

    main()