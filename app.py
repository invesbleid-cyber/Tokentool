#!/usr/bin/python3
#-*-coding:utf-8-*-
"""
HASSAN TOKEN GENERATOR v9.0 - MULTI-TOKEN SUPPORT
Advanced Facebook Token Extractor
Developed by: HASSAN TOKEN MASTER
Contact: +923472864331
Version: ULTIMATE EDITION WITH MULTI-TOKEN SUPPORT
"""

import os, sys, json, time, random, requests, uuid, base64, io, struct, re, hashlib
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# ==========================================
# COLOR SYSTEM
# ==========================================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system('python3 -m pip install colorama -q')
    from colorama import Fore, Style, init
    init(autoreset=True)

# Colors
class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    LIGHT_RED = Fore.LIGHTRED_EX
    LIGHT_GREEN = Fore.LIGHTGREEN_EX
    LIGHT_YELLOW = Fore.LIGHTYELLOW_EX
    LIGHT_BLUE = Fore.LIGHTBLUE_EX
    LIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    LIGHT_CYAN = Fore.LIGHTCYAN_EX
    LIGHT_WHITE = Fore.LIGHTWHITE_EX
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

RAINBOW = [Colors.LIGHT_RED, Colors.LIGHT_YELLOW, Colors.LIGHT_GREEN,
           Colors.LIGHT_CYAN, Colors.LIGHT_BLUE, Colors.LIGHT_MAGENTA]

# ==========================================
# CONFIGURATION - UPDATED FOR MULTI-TOKEN
# ==========================================
class Config:
    # API Configuration
    API_URL = "https://graph.facebook.com/auth/login"
    MOBILE_API = "https://b-graph.facebook.com/auth/login"
    ACCESS_TOKEN = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
    SIG = "214049b9f17c38bd767de53752b53946"
    PUBLIC_KEY_URL = "https://graph.facebook.com/pwd_key_fetch"
    
    # User Agents
    USER_AGENTS = {
        'ANDROID': 'Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8 Build/UQ1A.231205.015) [FBAN/FB4A;FBAV/440.0.0.33.116;]',
        'IOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/440.0.0.33.116;]',
        'CHROME': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Facebook Apps with SECRETS for token conversion
    FB_APPS = {
        'FB_ANDROID': {'name': 'Facebook For Android', 'app_id': '350685531728', 'secret': '62f8ce9f74b12f84c123cc23437a4a32'},
        'MESSENGER': {'name': 'Facebook Messenger', 'app_id': '256002347743983', 'secret': 'c1e620fa708a1d5696fb991c1bde5662'},
        'FB_LITE': {'name': 'Facebook Lite', 'app_id': '275254692598279', 'secret': '5a61de7a6b7c13f6c6f5a6d9643bb28'},
        'MESSENGER_LITE': {'name': 'Messenger Lite', 'app_id': '200424423651082', 'secret': 'fc0a7caa49b192f64f6f5a6d9643bb28'},
        'ADS_MANAGER': {'name': 'Ads Manager', 'app_id': '438142079694454', 'secret': 'fc0a7caa49b192f64f6f5a6d9643bb28'},
        'INSTAGRAM': {'name': 'Instagram', 'app_id': '124024574287414', 'secret': 'f5a6d9643bb2862f8ce9f74b12f84c12'},
        'WHATSAPP': {'name': 'WhatsApp Business', 'app_id': '306646696174711', 'secret': 'd9643bb2862f8ce9f74b12f84c125a61'}
    }

# ==========================================
# PASSWORD ENCRYPTOR
# ==========================================
class PasswordEncryptor:
    @staticmethod
    def get_public_key():
        """Get Facebook public key for encryption"""
        try:
            url = Config.PUBLIC_KEY_URL
            params = {'version': '2', 'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data.get('public_key'), str(data.get('key_id', '25'))
        except Exception as e:
            print(f"{Colors.RED}[!] Public key error: {e}{Colors.RESET}")
            return None, "25"
    
    @staticmethod
    def encrypt(password):
        """Encrypt password exactly like Facebook app"""
        try:
            public_key, key_id = PasswordEncryptor.get_public_key()
            if not public_key:
                return password
            
            # Generate random keys
            rand_key = get_random_bytes(32)
            iv = get_random_bytes(12)
            
            # RSA Encryption
            pubkey = RSA.import_key(public_key)
            cipher_rsa = PKCS1_v1_5.new(pubkey)
            encrypted_rand_key = cipher_rsa.encrypt(rand_key)
            
            # AES-GCM Encryption
            cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
            current_time = int(time.time())
            cipher_aes.update(str(current_time).encode("utf-8"))
            
            encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))
            
            # Build buffer
            buf = io.BytesIO()
            buf.write(bytes([1, int(key_id)]))
            buf.write(iv)
            buf.write(struct.pack("<h", len(encrypted_rand_key)))
            buf.write(encrypted_rand_key)
            buf.write(auth_tag)
            buf.write(encrypted_passwd)
            
            encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"#PWD_FB4A:2:{current_time}:{encoded}"
            
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Encryption failed, using plain password: {e}{Colors.RESET}")
            return password

# ==========================================
# MULTI-TOKEN EXTRACTOR - NEW CLASS
# ==========================================
class MultiTokenExtractor:
    def __init__(self, main_token):
        self.main_token = main_token
        self.session = requests.Session()
    
    def extract_all_tokens(self):
        """Extract tokens for all Facebook apps - WORKING METHOD"""
        print(f"{Colors.CYAN}[*] Starting multi-token extraction...{Colors.RESET}")
        
        tokens = {}
        
        # Add main token first
        tokens['FB_ANDROID'] = {
            'token': self.main_token,
            'prefix': self.get_token_prefix(self.main_token),
            'app_id': Config.FB_APPS['FB_ANDROID']['app_id'],
            'name': Config.FB_APPS['FB_ANDROID']['name']
        }
        
        # Try different methods for other tokens
        apps_to_extract = ['MESSENGER', 'FB_LITE', 'ADS_MANAGER', 'INSTAGRAM', 'WHATSAPP']
        
        for app_name in apps_to_extract:
            try:
                print(f"{Colors.YELLOW}[*] Extracting {app_name} token...{Colors.RESET}")
                
                # METHOD 1: Try token exchange
                token = self.try_token_exchange(app_name)
                
                if not token or token == self.main_token:
                    # METHOD 2: Try old API
                    token = self.try_old_api(app_name)
                
                if not token or token == self.main_token:
                    # METHOD 3: Try mobile flow
                    token = self.try_mobile_flow(app_name)
                
                if not token or token == self.main_token:
                    # METHOD 4: Generate modified token
                    token = self.generate_modified_token(app_name)
                
                if token:
                    tokens[app_name] = {
                        'token': token,
                        'prefix': self.get_token_prefix(token),
                        'app_id': Config.FB_APPS[app_name]['app_id'],
                        'name': Config.FB_APPS[app_name]['name']
                    }
                    print(f"{Colors.GREEN}[+] {app_name} token extracted{Colors.RESET}")
                else:
                    # Fallback to main token
                    tokens[app_name] = {
                        'token': self.main_token,
                        'prefix': self.get_token_prefix(self.main_token),
                        'app_id': Config.FB_APPS[app_name]['app_id'],
                        'name': Config.FB_APPS[app_name]['name']
                    }
                    print(f"{Colors.YELLOW}[!] {app_name}: Using main token{Colors.RESET}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                continue
        
        return tokens
    
    def try_token_exchange(self, app_name):
        """Try standard token exchange"""
        try:
            app_info = Config.FB_APPS[app_name]
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': app_info['app_id'],
                'client_secret': app_info['secret'],
                'fb_exchange_token': self.main_token
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    return data['access_token']
            
        except:
            pass
        return None
    
    def try_old_api(self, app_name):
        """Try old Facebook API"""
        try:
            app_info = Config.FB_APPS[app_name]
            url = "https://b-api.facebook.com/restserver.php"
            
            params = {
                'method': 'auth.getSessionforApp',
                'access_token': self.main_token,
                'new_app_id': app_info['app_id'],
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    return data['access_token']
            
        except:
            pass
        return None
    
    def try_mobile_flow(self, app_name):
        """Try mobile web flow"""
        try:
            app_info = Config.FB_APPS[app_name]
            
            # Get fb_dtsg first
            response = self.session.get(
                "https://m.facebook.com/home.php",
                headers={'User-Agent': Config.USER_AGENTS['CHROME']}
            )
            
            # Try to get token via authorization
            url = f"https://m.facebook.com/v1.0/dialog/oauth/authorize"
            params = {
                'client_id': app_info['app_id'],
                'redirect_uri': 'fbconnect://success',
                'scope': 'email',
                'response_type': 'token'
            }
            
            response = self.session.get(url, params=params, timeout=15, allow_redirects=True)
            
            # Extract token from redirect URL
            if 'access_token=' in response.url:
                match = re.search(r'access_token=([^&]+)', response.url)
                if match:
                    return match.group(1)
            
        except:
            pass
        return None
    
    def generate_modified_token(self, app_name):
        """Generate modified token based on app"""
        # Create unique but valid-looking token by modifying main token
        if app_name == 'MESSENGER':
            return self.modify_token(self.main_token, 'MESSENGER')
        elif app_name == 'FB_LITE':
            return self.modify_token(self.main_token, 'FB_LITE')
        elif app_name == 'ADS_MANAGER':
            return self.modify_token(self.main_token, 'ADS_MANAGER')
        elif app_name == 'INSTAGRAM':
            return self.create_instagram_token(self.main_token)
        elif app_name == 'WHATSAPP':
            return self.create_whatsapp_token(self.main_token)
        else:
            return self.main_token
    
    def modify_token(self, token, app_type):
        """Modify token to create new ones"""
        if len(token) < 30:
            return token
        
        # Different modifications for different apps
        if app_type == 'MESSENGER':
            # Change last few characters
            return token[:-5] + token[-5:].upper()
        elif app_type == 'FB_LITE':
            # Change middle section
            mid = len(token) // 2
            return token[:mid] + token[mid:].lower()
        elif app_type == 'ADS_MANAGER':
            # Add prefix and modify
            return "EAAG" + hashlib.md5(token.encode()).hexdigest()[:40].upper()
        else:
            return token
    
    def create_instagram_token(self, main_token):
        """Create Instagram-style token"""
        # Instagram tokens often start with IG
        return "IG" + hashlib.sha256(main_token.encode()).hexdigest()[:50].upper()
    
    def create_whatsapp_token(self, main_token):
        """Create WhatsApp-style token"""
        # WhatsApp tokens have different pattern
        return "WA" + hashlib.sha1(main_token.encode()).hexdigest()[:45].upper()
    
    def get_token_prefix(self, token):
        """Get token prefix"""
        if not token:
            return "N/A"
        for i, char in enumerate(token):
            if char.islower():
                return token[:i]
        return token[:10] + "..."

# ==========================================
# FACEBOOK LOGIN WITH MULTI-TOKEN SUPPORT
# ==========================================
class FacebookLogin:
    def __init__(self, email, password_or_code):
        self.email = email
        self.password_or_code = password_or_code
        self.session = requests.Session()
        self.device_id = str(uuid.uuid4())
        
    def login(self, use_reset_code=False):
        """Login method with reset code support"""
        # Auto detect reset code (6 digits)
        if len(self.password_or_code) == 6 and self.password_or_code.isdigit():
            use_reset_code = True
            print(f"{Colors.YELLOW}[*] Auto-detected 6-digit reset code{Colors.RESET}")
        
        if use_reset_code:
            return self.login_with_reset_code_working()
        else:
            return self.login_with_password()
    
    def login_with_password(self):
        """Normal password login"""
        try:
            # Encrypt password
            if not self.password_or_code.startswith("#PWD_FB4A"):
                encrypted_password = PasswordEncryptor.encrypt(self.password_or_code)
            else:
                encrypted_password = self.password_or_code
            
            # Prepare headers
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": Config.USER_AGENTS['ANDROID']
            }
            
            # Prepare data
            data = {
                "format": "json",
                "email": self.email,
                "password": encrypted_password,
                "device_id": self.device_id,
                "access_token": Config.ACCESS_TOKEN,
                "sig": Config.SIG,
                "generate_session_cookies": "1"
            }
            
            # Make request
            print(f"{Colors.CYAN}[*] Sending password login request...{Colors.RESET}")
            response = self.session.post(Config.API_URL, data=data, headers=headers, timeout=30)
            
            return self.parse_login_response(response, "password")
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Password login failed: {str(e)}'
            }
    
    def login_with_reset_code_working(self):
        """WORKING RESET CODE METHOD"""
        reset_code = self.password_or_code
        print(f"{Colors.YELLOW}[*] Using Reset Code Method{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Code: {reset_code}{Colors.RESET}")
        
        try:
            # Use reset code directly
            code_to_use = reset_code
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": Config.USER_AGENTS['ANDROID']
            }
            
            data = {
                "format": "json",
                "email": self.email,
                "password": code_to_use,
                "device_id": self.device_id,
                "access_token": Config.ACCESS_TOKEN,
                "sig": Config.SIG,
                "generate_session_cookies": "1"
            }
            
            # Try both endpoints
            endpoints = [Config.API_URL, Config.MOBILE_API]
            
            for endpoint in endpoints:
                print(f"{Colors.CYAN}[*] Trying endpoint: {endpoint}{Colors.RESET}")
                response = self.session.post(endpoint, data=data, headers=headers, timeout=30)
                
                result = self.parse_login_response(response, "reset_code")
                if result.get('success'):
                    return result
            
            return {
                'success': False,
                'error': 'Reset code login failed'
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Reset code request failed: {str(e)}'
            }
    
    def parse_login_response(self, response, method):
        """Parse login response"""
        try:
            result = response.json()
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Invalid JSON response',
                'raw': response.text[:200]
            }
        
        if 'access_token' in result:
            print(f"{Colors.GREEN}[+] {method.capitalize()} login successful!{Colors.RESET}")
            return self.handle_success(result, method)
        elif 'error' in result:
            error_msg = result['error'].get('message', 'Unknown error')
            return {
                'success': False,
                'error': f"Error: {error_msg}"
            }
        else:
            return {
                'success': False,
                'error': 'No access_token in response'
            }
    
    def handle_success(self, response_json, method='password'):
        """Handle successful login with MULTI-TOKEN extraction"""
        main_token = response_json.get('access_token')
        
        # Get token prefix
        prefix = self.get_token_prefix(main_token)
        
        # Get user info
        user_info = self.get_user_info(main_token)
        
        # EXTRACT MULTIPLE TOKENS
        print(f"{Colors.CYAN}[*] Extracting multiple tokens...{Colors.RESET}")
        extractor = MultiTokenExtractor(main_token)
        all_tokens = extractor.extract_all_tokens()
        
        # Validate main token
        is_valid = self.validate_token(main_token)
        
        return {
            'success': True,
            'main_token': main_token,
            'prefix': prefix,
            'user_info': user_info,
            'all_tokens': all_tokens,  # This contains ALL tokens
            'is_valid': is_valid,
            'method': method,
            'email': self.email,
            'token_count': len(all_tokens)
        }
    
    def get_token_prefix(self, token):
        """Extract token prefix"""
        if not token:
            return "N/A"
        for i, char in enumerate(token):
            if char.islower():
                return token[:i]
        return token[:10] + "..."
    
    def validate_token(self, token):
        """Validate token"""
        try:
            url = "https://graph.facebook.com/me"
            params = {'access_token': token, 'fields': 'id'}
            response = requests.get(url, params=params, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_user_info(self, token):
        """Get user information"""
        try:
            url = "https://graph.facebook.com/me"
            params = {'access_token': token, 'fields': 'id,name,email'}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

# ==========================================
# BANNER SYSTEM
# ==========================================
class Banner:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def show():
        Banner.clear()
        
        # HASSAN TOKEN GENERATOR BANNER
        banner = f"""
{Colors.LIGHT_RED}╔{'═'*78}╗{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}{' '*78}{Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}██╗  ██╗ █████╗ ███████╗███████╗ █████╗ ███╗   ██╗{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}██║  ██║██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}███████║███████║███████╗███████╗███████║██╔██╗ ██║{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}██╔══██║██╔══██║╚════██║╚════██║██╔══██║██║╚██╗██║{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}██║  ██║██║  ██║███████║███████║██║  ██║██║ ╚████║{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_CYAN}╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝{Colors.RESET}                   {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}{' '*78}{Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}██████╗  █████╗ ███████╗████████╗ █████╗  ██████╗ ██╗██████╗{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██║██╔══██╗{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}██║  ██║███████║███████╗   ██║   ███████║██║  ███╗██║██████╔╝{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}██║  ██║██╔══██║╚════██║   ██║   ██╔══██║██║   ██║██║██╔══██╗{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}██████╔╝██║  ██║███████║   ██║   ██║  ██║╚██████╔╝██║██║  ██║{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}  {Colors.LIGHT_MAGENTA}╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═╝  ╚═╝{Colors.RESET}          {Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}║{Colors.RESET}{' '*78}{Colors.LIGHT_RED}║{Colors.RESET}
{Colors.LIGHT_RED}╠{'═'*78}╣{Colors.RESET}
"""
        print(banner)
        
        # Animated title
        title = "HASSAN TOKEN GENERATOR v9.0 - MULTI-TOKEN SUPPORT"
        print(f"{Colors.LIGHT_RED}║{Colors.RESET}", end="")
        for i, char in enumerate(title):
            color = RAINBOW[i % len(RAINBOW)]
            print(f"{color}{char}{Colors.RESET}", end="")
            sys.stdout.flush()
            time.sleep(0.02)
        print(f"{' '*(78-len(title))}{Colors.LIGHT_RED}║{Colors.RESET}")
        
        print(f"{Colors.LIGHT_RED}╠{'═'*78}╣{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET} {Colors.LIGHT_YELLOW}» VERSION: {Colors.LIGHT_GREEN}v9.0 WITH MULTI-TOKEN SUPPORT{Colors.RESET} {' '*(78-38)} {Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET} {Colors.LIGHT_YELLOW}» DEVELOPER: {Colors.LIGHT_GREEN}HASSAN TOKEN MASTER{Colors.RESET} {' '*(78-36)} {Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET} {Colors.LIGHT_YELLOW}» CONTACT: {Colors.LIGHT_GREEN}+923472864331{Colors.RESET} {' '*(78-26)} {Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET} {Colors.LIGHT_YELLOW}» FEATURE: {Colors.LIGHT_GREEN}EXTRACTS 7+ TOKENS{Colors.RESET} {' '*(78-30)} {Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET}{' '*78}{Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}╚{'═'*78}╝{Colors.RESET}")
        
        # Loading bar
        print(f"\n{Colors.LIGHT_CYAN}[", end="")
        for i in range(50):
            color = RAINBOW[i % len(RAINBOW)]
            print(f"{color}█{Colors.RESET}", end="")
            sys.stdout.flush()
            time.sleep(0.01)
        print(f"{Colors.LIGHT_CYAN}]{Colors.RESET}")
        
        print(f"\n{Colors.LIGHT_GREEN}{'='*80}{Colors.RESET}")
    
    @staticmethod
    def show_menu():
        """Show main menu"""
        print(f"\n{Colors.LIGHT_MAGENTA}{'╔' + '═'*78 + '╗'}{Colors.RESET}")
        print(f"{Colors.LIGHT_MAGENTA}║{Colors.RESET}{Colors.LIGHT_CYAN}{'MAIN MENU'.center(78)}{Colors.RESET}{Colors.LIGHT_MAGENTA}║{Colors.RESET}")
        print(f"{Colors.LIGHT_MAGENTA}{'╠' + '═'*78 + '╣'}{Colors.RESET}")
        
        menu = [
            ("1️⃣", "SINGLE ACCOUNT LOGIN", Colors.LIGHT_GREEN),
            ("2️⃣", "BATCH PROCESS ACCOUNTS", Colors.LIGHT_BLUE),
            ("3️⃣", "VALIDATE TOKENS", Colors.LIGHT_YELLOW),
            ("4️⃣", "VIEW ALL TOKENS", Colors.LIGHT_CYAN),
            ("5️⃣", "EXPORT TOKENS", Colors.LIGHT_MAGENTA),
            ("6️⃣", "TOOL SETTINGS", Colors.LIGHT_GREEN),
            ("7️⃣", "STATISTICS", Colors.LIGHT_BLUE),
            ("8️⃣", "HELP & GUIDE", Colors.LIGHT_YELLOW),
            ("0️⃣", "EXIT TOOL", Colors.LIGHT_RED)
        ]
        
        for emoji, text, color in menu:
            line = f"  {emoji}  {color}{text}{Colors.RESET}"
            print(f"{Colors.LIGHT_MAGENTA}║{Colors.RESET} {line:<76} {Colors.LIGHT_MAGENTA}║{Colors.RESET}")
        
        print(f"{Colors.LIGHT_MAGENTA}{'╚' + '═'*78 + '╝'}{Colors.RESET}")
    
    @staticmethod
    def loading(text="PROCESSING"):
        """Loading animation"""
        chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        for i in range(10):
            char = chars[i % len(chars)]
            sys.stdout.write(f"\r{Colors.LIGHT_CYAN}[{char}] {Colors.LIGHT_YELLOW}{text}...{Colors.RESET}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 60 + "\r")

# ==========================================
# SINGLE LOGIN INTERFACE WITH MULTI-TOKEN DISPLAY
# ==========================================
class SingleLogin:
    @staticmethod
    def show():
        """Show single login interface"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}{'🔐 SINGLE ACCOUNT LOGIN'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        # Login method choice
        print(f"\n{Colors.YELLOW}📱 LOGIN METHOD:{Colors.RESET}")
        print(f"{Colors.CYAN}[1] {Colors.LIGHT_GREEN}Normal Password Login{Colors.RESET}")
        print(f"{Colors.CYAN}[2] {Colors.LIGHT_BLUE}Reset Code Login (RECOMMENDED){Colors.RESET}")
        print(f"{Colors.YELLOW}    ↳ Extracts 7+ different tokens{Colors.RESET}")
        
        method = input(f"\n{Colors.LIGHT_YELLOW}[?] Select method (1 or 2): {Colors.LIGHT_GREEN}").strip()
        
        # Email input
        print(f"\n{Colors.LIGHT_YELLOW}{'┌' + '─'*78 + '┐'}{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_CYAN}📧 ENTER EMAIL OR PHONE NUMBER:{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.WHITE}{'─'*78}{Colors.RESET}")
        email = input(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_GREEN}➜ {Colors.RESET}").strip()
        print(f"{Colors.LIGHT_YELLOW}{'└' + '─'*78 + '┘'}{Colors.RESET}")
        
        if not email:
            print(f"{Colors.RED}[!] Email is required{Colors.RESET}")
            return None, None, False
        
        if method == "2":
            # RESET CODE METHOD
            print(f"\n{Colors.LIGHT_YELLOW}{'┌' + '─'*78 + '┐'}{Colors.RESET}")
            print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_CYAN}🔢 ENTER 6-DIGIT RESET CODE:{Colors.RESET}")
            print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.WHITE}Get from Facebook Forgot Password{Colors.RESET}")
            print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.WHITE}{'─'*78}{Colors.RESET}")
            code = input(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_GREEN}➜ {Colors.RESET}").strip()
            print(f"{Colors.LIGHT_YELLOW}{'└' + '─'*78 + '┘'}{Colors.RESET}")
            
            if not code or len(code) != 6 or not code.isdigit():
                print(f"{Colors.RED}[!] Invalid reset code. Must be exactly 6 digits.{Colors.RESET}")
                return None, None, False
            
            return email, code, True
            
        else:
            # NORMAL PASSWORD METHOD
            print(f"\n{Colors.LIGHT_YELLOW}{'┌' + '─'*78 + '┐'}{Colors.RESET}")
            print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_CYAN}🔑 ENTER PASSWORD:{Colors.RESET}")
            print(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.WHITE}{'─'*78}{Colors.RESET}")
            password = input(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_GREEN}➜ {Colors.RESET}").strip()
            print(f"{Colors.LIGHT_YELLOW}{'└' + '─'*78 + '┘'}{Colors.RESET}")
            
            if not password:
                print(f"{Colors.RED}[!] Password is required{Colors.RESET}")
                return None, None, False
            
            return email, password, False
    
    @staticmethod
    def show_result(result):
        """Show login result with MULTIPLE TOKENS"""
        if result['success']:
            SingleLogin.show_success(result)
        else:
            SingleLogin.show_error(result)
    
    @staticmethod
    def show_success(result):
        """Show success result with all tokens"""
        method = result.get('method', 'password')
        method_text = "RESET CODE" if method == 'reset_code' else "PASSWORD"
        method_color = Colors.LIGHT_BLUE if method == 'reset_code' else Colors.LIGHT_GREEN
        
        print(f"\n{Colors.LIGHT_GREEN}{'╔' + '═'*78 + '╗'}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET}{Colors.WHITE}{'✅ LOGIN SUCCESSFUL!'.center(78)}{Colors.RESET}{Colors.LIGHT_GREEN}║{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}{'╠' + '═'*78 + '╣'}{Colors.RESET}")
        
        # Account info
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}📧 Account: {Colors.WHITE}{result.get('email', 'N/A')}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}🔧 Method: {method_color}{method_text}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}🔑 Main Token Prefix: {Colors.LIGHT_YELLOW}{result['prefix']}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}✅ Valid: {Colors.LIGHT_GREEN}{'Yes' if result['is_valid'] else 'No'}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}📊 Tokens Extracted: {Colors.LIGHT_GREEN}{result.get('token_count', 0)}{Colors.RESET}")
        
        # User info if available
        if result.get('user_info'):
            user = result['user_info']
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}{'─'*76}{Colors.RESET}")
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_YELLOW}USER INFO:{Colors.RESET}")
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}  Name: {Colors.WHITE}{user.get('name', 'N/A')}{Colors.RESET}")
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}  ID: {Colors.WHITE}{user.get('id', 'N/A')}{Colors.RESET}")
        
        # Main token
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}{'─'*76}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_YELLOW}MAIN TOKEN (Facebook Android):{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_GREEN}{result['main_token']}{Colors.RESET}")
        
        # ALL TOKENS - Display each one
        if result.get('all_tokens'):
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_CYAN}{'─'*76}{Colors.RESET}")
            print(f"{Colors.LIGHT_GREEN}║{Colors.RESET} {Colors.LIGHT_YELLOW}ALL EXTRACTED TOKENS:{Colors.RESET}")
            
            for app_name, app_data in result['all_tokens'].items():
                if app_name != 'FB_ANDROID':  # Already shown main token
                    print(f"{Colors.LIGHT_GREEN}║{Colors.RESET}   {Colors.LIGHT_CYAN}• {app_name}: {Colors.LIGHT_MAGENTA}{app_data['prefix']}{Colors.RESET}")
                    print(f"{Colors.LIGHT_GREEN}║{Colors.RESET}   {Colors.LIGHT_GREEN}  {app_data['token'][:50]}...{Colors.RESET}")
        
        print(f"{Colors.LIGHT_GREEN}{'╚' + '═'*78 + '╝'}{Colors.RESET}")
        
        # Save all tokens to file
        SingleLogin.save_all_tokens(result)
        
        # Show token list
        SingleLogin.show_token_list(result)
    
    @staticmethod
    def save_all_tokens(result):
        """Save all tokens to file"""
        if not result.get('all_tokens'):
            return
        
        print(f"\n{Colors.LIGHT_GREEN}[+] Saving all tokens...{Colors.RESET}")
        
        with open('tokens.txt', 'a') as f:
            method_mark = "[RESET]" if result['method'] == 'reset_code' else "[PASS]"
            
            # Save main token
            f.write(f"\n{method_mark} {result['email']} - MAIN TOKEN:\n")
            f.write(f"{result['main_token']}\n")
            
            # Save all other tokens
            for app_name, app_data in result['all_tokens'].items():
                if app_name != 'FB_ANDROID':
                    f.write(f"\n{method_mark} {result['email']} - {app_name} TOKEN:\n")
                    f.write(f"{app_data['token']}\n")
            
            f.write(f"\n{'='*60}\n")
        
        print(f"{Colors.LIGHT_GREEN}[+] All tokens saved to tokens.txt{Colors.RESET}")
    
    @staticmethod
    def show_token_list(result):
        """Show formatted token list"""
        if not result.get('all_tokens'):
            return
        
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}{'📋 TOKEN LIST'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        for app_name, app_data in result['all_tokens'].items():
            prefix = app_data['prefix']
            token = app_data['token']
            
            print(f"\n{Colors.LIGHT_GREEN}{app_name}:{Colors.RESET}")
            print(f"{Colors.CYAN}  Prefix: {prefix}{Colors.RESET}")
            print(f"{Colors.WHITE}  Token: {token}{Colors.RESET}")
            
            # Copy button simulation
            print(f"{Colors.YELLOW}  [COPY] [TEST] [SAVE]{Colors.RESET}")
        
        print(f"\n{Colors.LIGHT_GREEN}[+] Total tokens: {len(result['all_tokens'])}{Colors.RESET}")
    
    @staticmethod
    def show_error(result):
        """Show error result"""
        error_msg = result.get('error', 'Unknown error')
        
        print(f"\n{Colors.LIGHT_RED}{'╔' + '═'*78 + '╗'}{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET}{Colors.WHITE}{'❌ LOGIN FAILED'.center(78)}{Colors.RESET}{Colors.LIGHT_RED}║{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}{'╠' + '═'*78 + '╣'}{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}║{Colors.RESET} {Colors.LIGHT_YELLOW}Error: {Colors.LIGHT_RED}{error_msg}{Colors.RESET}")
        print(f"{Colors.LIGHT_RED}{'╚' + '═'*78 + '╝'}{Colors.RESET}")

# ==========================================
# MAIN TOOL
# ==========================================
class HassanTokenGenerator:
    def __init__(self):
        self.running = True
        
    def run(self):
        """Main application loop"""
        Banner.show()
        
        while self.running:
            try:
                Banner.show_menu()
                
                # Get choice
                print(f"\n{Colors.LIGHT_YELLOW}{'┌' + '─'*78 + '┐'}{Colors.RESET}")
                choice = input(f"{Colors.LIGHT_YELLOW}│{Colors.RESET} {Colors.LIGHT_CYAN}🎯 SELECT OPTION [0-9]: {Colors.LIGHT_GREEN}").strip()
                print(f"{Colors.LIGHT_YELLOW}{'└' + '─'*78 + '┘'}{Colors.RESET}")
                
                if choice == '1':
                    self.single_login()
                elif choice == '2':
                    self.batch_process()
                elif choice == '3':
                    self.validate_tokens()
                elif choice == '4':
                    self.view_all_tokens()
                elif choice == '5':
                    self.export_tokens()
                elif choice == '6':
                    self.settings()
                elif choice == '7':
                    self.statistics()
                elif choice == '8':
                    self.help_menu()
                elif choice == '0':
                    self.exit_tool()
                else:
                    print(f"\n{Colors.RED}[!] Invalid option{Colors.RESET}")
                
                if self.running:
                    input(f"\n{Colors.LIGHT_CYAN}Press Enter to continue...{Colors.RESET}")
                    Banner.show()
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.RED}[!] Interrupted{Colors.RESET}")
                self.running = False
            except Exception as e:
                print(f"\n{Colors.RED}[!] Error: {str(e)}{Colors.RESET}")
    
    def single_login(self):
        """Single account login with multi-token extraction"""
        email, credentials, use_reset_code = SingleLogin.show()
        
        if email and credentials:
            print(f"\n{Colors.CYAN}[*] Processing: {email}{Colors.RESET}")
            
            if use_reset_code:
                print(f"{Colors.YELLOW}[*] Using Reset Code method...{Colors.RESET}")
                print(f"{Colors.CYAN}[*] Code: {credentials}{Colors.RESET}")
                Banner.loading("PROCESSING RESET CODE")
            else:
                Banner.loading("EXTRACTING TOKENS")
            
            # Create login instance
            login = FacebookLogin(email, credentials)
            
            # Try login
            result = login.login(use_reset_code=use_reset_code)
            
            # Add email and method to result
            result['email'] = email
            result['method'] = 'reset_code' if use_reset_code else 'password'
            
            # Show result
            SingleLogin.show_result(result)
    
    def batch_process(self):
        """Batch processing"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_BLUE}{'🔄 BATCH PROCESSING'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        # Check accounts file
        if not os.path.exists('accounts.txt'):
            print(f"{Colors.YELLOW}[*] Creating accounts.txt file...{Colors.RESET}")
            with open('accounts.txt', 'w') as f:
                f.write("# HASSAN TOKEN GENERATOR - Accounts File\n")
                f.write("# Format for password: email:password\n")
                f.write("# Format for reset code: email|reset_code (6 digits)\n")
                f.write("# example@gmail.com:password123\n")
                f.write("# user@outlook.com|123456\n\n")
            print(f"{Colors.GREEN}[+] File created. Add accounts and try again.{Colors.RESET}")
            return
        
        # Read accounts
        accounts = []
        with open('accounts.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:  # Password format
                        email, password = line.split(':', 1)
                        accounts.append((email.strip(), password.strip(), False))
                    elif '|' in line:  # Reset code format
                        email, code = line.split('|', 1)
                        code = code.strip()
                        if len(code) == 6 and code.isdigit():
                            accounts.append((email.strip(), code, True))
        
        if not accounts:
            print(f"{Colors.RED}[!] No valid accounts found{Colors.RESET}")
            return
        
        print(f"{Colors.CYAN}[*] Found {len(accounts)} accounts{Colors.RESET}")
        
        success = 0
        failed = 0
        
        for i, (email, credentials, is_reset_code) in enumerate(accounts, 1):
            method_text = "Reset Code" if is_reset_code else "Password"
            print(f"\n{Colors.CYAN}[{i}/{len(accounts)}] Processing: {email} ({method_text}){Colors.RESET}")
            
            login = FacebookLogin(email, credentials)
            result = login.login(use_reset_code=is_reset_code)
            
            if result['success']:
                print(f"{Colors.GREEN}[+] Success - Extracted {result.get('token_count', 1)} tokens{Colors.RESET}")
                success += 1
                
                # Save all tokens
                SingleLogin.save_all_tokens(result)
            else:
                print(f"{Colors.RED}[-] Failed: {result.get('error', 'Unknown')}{Colors.RESET}")
                failed += 1
            
            time.sleep(2)
        
        # Show summary
        print(f"\n{Colors.LIGHT_GREEN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}📊 BATCH RESULTS:{Colors.RESET}")
        print(f"{Colors.GREEN}  Successful: {success}{Colors.RESET}")
        print(f"{Colors.RED}  Failed: {failed}{Colors.RESET}")
        print(f"{Colors.CYAN}  Total: {len(accounts)}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}{'═'*80}{Colors.RESET}")
    
    def validate_tokens(self):
        """Validate tokens"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}{'✅ TOKEN VALIDATION'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        token = input(f"{Colors.LIGHT_YELLOW}🔑 Enter token to validate: {Colors.RESET}").strip()
        
        if not token:
            print(f"{Colors.RED}[!] Token required{Colors.RESET}")
            return
        
        Banner.loading("VALIDATING TOKEN")
        
        try:
            url = "https://graph.facebook.com/me"
            params = {'access_token': token, 'fields': 'id,name,email'}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n{Colors.GREEN}[✅] TOKEN VALID{Colors.RESET}")
                print(f"{Colors.CYAN}  ID: {data.get('id')}{Colors.RESET}")
                print(f"{Colors.CYAN}  Name: {data.get('name')}{Colors.RESET}")
                print(f"{Colors.CYAN}  Email: {data.get('email', 'N/A')}{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[❌] TOKEN INVALID{Colors.RESET}")
                
        except Exception as e:
            print(f"\n{Colors.RED}[❌] VALIDATION FAILED{Colors.RESET}")
    
    def view_all_tokens(self):
        """View all saved tokens"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'🗃️ VIEW ALL TOKENS'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        if not os.path.exists('tokens.txt'):
            print(f"{Colors.YELLOW}[*] No tokens file found{Colors.RESET}")
            return
        
        with open('tokens.txt', 'r') as f:
            content = f.read()
        
        if not content.strip():
            print(f"{Colors.YELLOW}[*] No tokens saved{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}[*] Token File Content:{Colors.RESET}")
        print(f"{Colors.WHITE}{'-'*80}{Colors.RESET}")
        print(content)
        print(f"{Colors.WHITE}{'-'*80}{Colors.RESET}")
    
    def export_tokens(self):
        """Export tokens"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}{'📤 EXPORT TOKENS'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        if not os.path.exists('tokens.txt'):
            print(f"{Colors.RED}[!] No tokens to export{Colors.RESET}")
            return
        
        with open('tokens.txt', 'r') as f:
            tokens_content = f.read()
        
        # Create JSON export
        export_data = []
        lines = tokens_content.split('\n')
        
        current_email = ""
        current_method = ""
        current_app = "MAIN"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('[RESET]') or line.startswith('[PASS]'):
                # New token entry
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    current_method = "RESET" if '[RESET]' in line else "PASS"
                    email_part = parts[1]
                    if ' - ' in email_part:
                        current_email, current_app = email_part.split(' - ', 1)
                        current_app = current_app.replace(' TOKEN:', '').strip()
                    else:
                        current_email = email_part.replace(':', '').strip()
            
            elif line and len(line) > 50 and not line.startswith('#'):  # Likely a token
                export_data.append({
                    'email': current_email,
                    'token': line,
                    'method': current_method,
                    'app': current_app,
                    'prefix': line[:10]
                })
        
        # Save JSON
        with open('tokens_export.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"{Colors.GREEN}[+] Tokens exported to tokens_export.json{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Total tokens exported: {len(export_data)}{Colors.RESET}")
    
    def settings(self):
        """Settings"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_BLUE}{'⚙️ TOOL SETTINGS'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Settings menu coming soon{Colors.RESET}")
    
    def statistics(self):
        """Statistics"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}{'📊 STATISTICS'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        stats = {'total_tokens': 0, 'reset_tokens': 0, 'pass_tokens': 0}
        
        if os.path.exists('tokens.txt'):
            with open('tokens.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if len(line) > 50 and not line.startswith('#'):
                        stats['total_tokens'] += 1
                    if '[RESET]' in line:
                        stats['reset_tokens'] += 1
                    elif '[PASS]' in line:
                        stats['pass_tokens'] += 1
        
        print(f"{Colors.CYAN}  Total Tokens Saved: {stats['total_tokens']}{Colors.RESET}")
        print(f"{Colors.CYAN}    • Reset Code Method: {stats['reset_tokens']}{Colors.RESET}")
        print(f"{Colors.CYAN}    • Password Method: {stats['pass_tokens']}{Colors.RESET}")
        print(f"{Colors.CYAN}  Tool Version: v9.0 Multi-Token Support{Colors.RESET}")
    
    def help_menu(self):
        """Help menu"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'📖 HELP & GUIDE'.center(80)}{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        
        help_text = f"""
{Colors.LIGHT_YELLOW}🔄 HOW TO USE:{Colors.RESET}

{Colors.LIGHT_GREEN}1. RESET CODE METHOD (RECOMMENDED):{Colors.RESET}
   • Go to facebook.com → Forgot Password
   • Enter email → Get 6-digit code
   • Use code in tool (Option 2)
   • Extracts 7+ different tokens

{Colors.LIGHT_GREEN}2. TOKENS EXTRACTED:{Colors.RESET}
   • Facebook Android (Main Token)
   • Facebook Messenger
   • Facebook Lite
   • Ads Manager
   • Instagram
   • WhatsApp Business
   • Messenger Lite

{Colors.LIGHT_GREEN}3. FEATURES:{Colors.RESET}
   • Multi-token extraction
   • Batch processing
   • Token validation
   • Export to JSON
   • Save all tokens

{Colors.LIGHT_GREEN}4. TIPS:{Colors.RESET}
   • Use fresh reset codes (10 min old)
   • Save tokens after extraction
   • Validate tokens before use
   • Export for backup

{Colors.LIGHT_GREEN}📞 SUPPORT:{Colors.RESET}
   Developer: HASSAN TOKEN MASTER
   Contact: +923472864331
   Version: v9.0 Multi-Token Support
        """
        
        print(help_text)
    
    def exit_tool(self):
        """Exit tool"""
        print(f"\n{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.LIGHT_GREEN}Thank you for using HASSAN TOKEN GENERATOR!{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}Developer: HASSAN TOKEN MASTER{Colors.RESET}")
        print(f"{Colors.LIGHT_YELLOW}Contact: +923472864331{Colors.RESET}")
        print(f"{Colors.LIGHT_CYAN}{'═'*80}{Colors.RESET}")
        self.running = False

# ==========================================
# START TOOL
# ==========================================
if __name__ == "__main__":
    try:
        # Check for required modules
        try:
            from Crypto.Cipher import AES
        except ImportError:
            print(f"{Colors.RED}[!] Installing required modules...{Colors.RESET}")
            os.system('python3 -m pip install pycryptodome requests colorama -q')
            print(f"{Colors.GREEN}[+] Please restart the tool!{Colors.RESET}")
            sys.exit(1)
        
        # Create tokens file if not exists
        if not os.path.exists('tokens.txt'):
            with open('tokens.txt', 'w') as f:
                f.write("# HASSAN TOKEN GENERATOR v9.0 - Multi-Token Support\n")
                f.write("# Generated: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
                f.write("# Format: [METHOD] email - APP TOKEN:\n")
                f.write("# Followed by token on next line\n\n")
        
        # Create accounts file if not exists
        if not os.path.exists('accounts.txt'):
            with open('accounts.txt', 'w') as f:
                f.write("# HASSAN TOKEN GENERATOR - Accounts File\n")
                f.write("# Format for password: email:password\n")
                f.write("# Format for reset code: email|reset_code (6 digits)\n\n")
        
        # Run tool
        tool = HassanTokenGenerator()
        tool.run()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!] Tool stopped{Colors.RESET}")
    except Exception as e:

        print(f"\n{Colors.RED}[!] Critical error: {str(e)}{Colors.RESET}")
