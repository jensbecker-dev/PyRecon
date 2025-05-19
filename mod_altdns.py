# Module for generating subdomain permutations
# This module implements techniques similar to those used by the AltDNS tool
# to generate permutations of discovered subdomains 

import os, sys
import configparser

def permute_subdomains(subdomains, words, target_domain):
    """
    Generate permutations of subdomains using common patterns.
    """
    result = set()
    
    for subdomain in subdomains:
        # Remove the target domain part for manipulation
        subdomain_no_tld = subdomain
        if subdomain.endswith(f".{target_domain}"):
            subdomain_no_tld = subdomain[:-len(f".{target_domain}")]
        
        parts = subdomain_no_tld.split('.')
        
        # Add original subdomain
        result.add(subdomain)
        
        # Permutation 1: prefix-original
        for word in words:
            new_subdomain = f"{word}{subdomain_no_tld}.{target_domain}"
            result.add(new_subdomain)
            
            # Also try with separators
            for sep in ['-', '.']:
                new_subdomain = f"{word}{sep}{subdomain_no_tld}.{target_domain}"
                result.add(new_subdomain)
        
        # Permutation 2: original-suffix
        for word in words:
            new_subdomain = f"{subdomain_no_tld}{word}.{target_domain}"
            result.add(new_subdomain)
            
            # Also try with separators
            for sep in ['-', '.']:
                new_subdomain = f"{subdomain_no_tld}{sep}{word}.{target_domain}"
                result.add(new_subdomain)
        
        # Permutation 3: Replace each part with a word
        for i, part in enumerate(parts):
            for word in words:
                new_parts = parts.copy()
                new_parts[i] = word
                new_subdomain = ".".join(new_parts) + f".{target_domain}"
                result.add(new_subdomain)
        
        # Permutation 4: Insert word between parts
        for i in range(1, len(parts)):
            for word in words:
                new_parts = parts.copy()
                new_parts.insert(i, word)
                new_subdomain = ".".join(new_parts) + f".{target_domain}"
                result.add(new_subdomain)
    
    return sorted(list(result))

def run(target_domain, subdomains_list, wordlist=None, threads=10, verbose=False):
    """
    Run AltDNS with the given parameters.
    """
    try:
        # Read the config to get wordlist location if not provided
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        default_wordlist = None
        
        if os.path.exists(config_path):
            config.read(config_path)
            if 'AltDNS' in config and 'wordlist' in config['AltDNS']:
                default_wordlist = os.path.expanduser(config['AltDNS']['wordlist'])
                
        # Use provided wordlist or default from config
        wordlist_path = wordlist or default_wordlist
        
        # Check if we have a wordlist
        if not wordlist_path:
            print("[-] Error: No wordlist specified for AltDNS and no default in config.ini")
            return []
            
        # Check if the wordlist file exists
        if not os.path.isfile(wordlist_path):
            print(f"[-] Error: Wordlist file '{wordlist_path}' does not exist.")
            return []
            
        if verbose:
            print(f"[+] Running AltDNS on {len(subdomains_list)} subdomains with wordlist: {wordlist_path}")
        
        # Read words from wordlist, limit to avoid excessive permutations
        with open(wordlist_path, 'r') as f:
            words_list = [line.strip() for line in f if line.strip()]
            
        # Use a subset of words to prevent memory issues
        if len(words_list) > 100:
            if verbose:
                print(f"[+] Using the first 100 words from {len(words_list)} total words")
            words_list = words_list[:100]  # Use first 100 words for consistency in tutorial
            
        # Generate permutations
        permuted_subdomains = permute_subdomains(subdomains_list, words_list, target_domain)
        
        if verbose:
            print(f"[+] AltDNS generated {len(permuted_subdomains)} permutations")
            
        return permuted_subdomains

    except KeyboardInterrupt:
        print("\n[!] Exiting...")
        sys.exit(0)
        
    except Exception as e:
        print(f"[-] Error running AltDNS: {str(e)}")
        return []
    
def save_to_file(subdomains, output_file):
    """
    Save the permuted subdomains to a file.
    """
    try:
        with open(output_file, 'w') as f:
            for subdomain in subdomains:
                f.write(f"{subdomain}\n")
        print(f"[+] AltDNS permutations saved to {output_file}")

    except Exception as e:
        print(f"[-] Error: {str(e)}") 