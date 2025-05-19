#!/usr/bin/env python3
import os
import sys
import sublist3r
import configparser
import re

# Define the color constants used by Sublist3r
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
Y = '\033[33m'  # yellow

def patch_sublist3r():
    """
    Patch the Sublist3r module to use a VirusTotal API key
    and fix other known issues
    """
    try:
        # Read the API key from config
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        
        if not os.path.exists(config_path):
            print("[-] Warning: config.ini not found. Creating with default settings.")
            with open(config_path, 'w') as f:
                f.write("[VirusTotal]\napi_key = YOUR_VIRUSTOTAL_API_KEY_HERE\n\n[General]\noutput_dir = results\n")
            return None
        
        config.read(config_path)
        
        # ===== Fix DNSdumpster CSRF token issue =====
        print("[+] Patching Sublist3r DNSdumpster module...")
        
        # Create patched version of DNSdumpster.enumerate method
        def patched_dnsdumpster_enumerate(self):
            self.print_(G + "[-] Searching now in %s.." % (self.engine_name) + W)
            
            try:
                resp = self.session.get(self.base_url, headers=self.headers, timeout=self.timeout)
                
                # Completely replace the CSRF token extraction with a more robust version
                # that doesn't rely on the specific format of the DNSdumpster page
                try:
                    # Try to get the CSRF token using the original method first
                    csrf_regex = re.compile('name="csrfmiddlewaretoken" value="(.*?)"', re.DOTALL)
                    token = csrf_regex.findall(resp.text)
                    
                    if token and len(token) > 0:
                        token = token[0]
                    else:
                        # Fallback: Look for any input with name="csrfmiddlewaretoken"
                        csrf_regex = re.compile('input[^>]*name=["\']csrfmiddlewaretoken["\'][^>]*value=["\'](.*?)["\']', re.DOTALL | re.IGNORECASE)
                        token = csrf_regex.findall(resp.text)
                        
                        if token and len(token) > 0:
                            token = token[0]
                        else:
                            # Last resort: generate a random token
                            import random, string
                            token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(64))
                            print(Y + "[!] Warning: CSRF token not found in DNSdumpster response. Using random token." + W)
                except:
                    # If all else fails, use a dummy token
                    token = "dummytoken"
                    print(Y + "[!] Warning: CSRF token extraction failed. Using dummy token." + W)
                
                # Continue with the rest of the enumerate method
                self.headers['csrfmiddlewaretoken'] = token
                self.headers['referer'] = self.base_url
                
                data = {
                    'csrfmiddlewaretoken': token,
                    'targetip': self.domain
                }
                
                resp = self.session.post(self.base_url, headers=self.headers, data=data, timeout=self.timeout)
                
                # Extract the subdomains using regex
                subdomain_regex = re.compile('((?:[a-z0-9]+[.])+%s)' % self.domain)
                subdomains = subdomain_regex.findall(resp.text)
                
                # Add unique subdomains to the list
                for subdomain in subdomains:
                    if subdomain not in self.subdomains and subdomain != self.domain:
                        self.subdomains.append(subdomain.strip())
                
                return self.subdomains
            except Exception as e:
                print(R + f"[!] Error in DNSdumpster enumeration: {str(e)}" + W)
                return self.subdomains
        
        # Replace the DNSdumpster enumerate method
        import re  # Make sure re is imported
        sublist3r.DNSdumpster.enumerate = patched_dnsdumpster_enumerate
        
        # ===== Apply VirusTotal API key patch =====
        if 'VirusTotal' in config and 'api_key' in config['VirusTotal']:
            vt_api_key = config['VirusTotal']['api_key']
            if vt_api_key == "YOUR_VIRUSTOTAL_API_KEY_HERE":
                print("[-] Warning: Please update your VirusTotal API key in config.ini")
            else:
                # Patch the Virustotal class to use the API key
                print("[+] Patching Sublist3r to use VirusTotal API key...")
                
                # Create a patched version that adds the API key
                def patched_vt_send_req(self, url):
                    headers = {'X-ApiKey': vt_api_key}
                    try:
                        resp = self.session.get(url, headers=headers, timeout=self.timeout)
                    except Exception as e:
                        self.print_(e)
                        resp = None
                    return self.get_response(resp)
                
                # Replace the method
                sublist3r.Virustotal.send_req = patched_vt_send_req
                
                print("[+] Sublist3r patched successfully to use VirusTotal API key")
        else:
            print("[-] Warning: VirusTotal API key not found in config.ini")
        
        print("[+] All patches applied successfully")
        return True
    
    except Exception as e:
        print(f"[-] Error patching Sublist3r: {str(e)}")
        return None

if __name__ == "__main__":
    patch_sublist3r()
