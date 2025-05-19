# Module for interfacing with Sublist3r
# This module runs Sublist3r with our patches and collects the results

import os, sys
import sublist3r
import patch_sublist3r

def run(target_domain, threads, verbose):
    """
    Run Sublist3r with the given parameters.
    """
    try:
        # Apply the patch for VirusTotal API key
        patch_sublist3r.patch_sublist3r()
        
        # Check if the target domain is valid
        if not target_domain:
            print("[-]  Error: Target domain is required.")
            return

        # Run Sublist3r
        subdomains = sublist3r.main(
            domain=target_domain,
            threads=threads,
            savefile=None,
            ports=None,
            silent=False,
            verbose=verbose,
            enable_bruteforce=False,
            engines=None
        )
        return subdomains

    except KeyboardInterrupt:

        print("\n[!]  Exiting...")
        sys.exit(0)

    except Exception as e:

        print(f"[-]  Error: {str(e)}")
        return
    
def save_to_file(subdomains, output_file):
    """
    Save the subdomains to a file.
    """
    try:
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(f"{subdomain}\n")
        print(f"[+]  Subdomains saved to {output_file}")

    except Exception as e:
        print(f"[-]  Error: {str(e)}")