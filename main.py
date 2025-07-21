from playwright.sync_api import Playwright, sync_playwright
import random
import sys
import json
import os
import time
try:
    from sendNotify import send
except ImportError:
    def send(*args):
        print("未找到通知文件sendNotify.py不启用通知！")

List = []

def save_cookies(page, filename):
    cookies = page.context.cookies()
    with open(filename, 'w') as f:
        f.write(json.dumps(cookies))

def load_cookies(page, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            cookies = json.load(f)
            page.context.add_cookies(cookies)

def check_url_status(page, url):
    max_attempts = 3
    attempt = 0
    
    try:
        page.goto(url)
        time.sleep(10)
        
        while attempt < max_attempts:
            # 检查页面内容是否包含sleep关键词
            page_content = page.content().lower()
            
            if "sleep" in page_content:
                attempt += 1
                print(f"{url} - 检测到sleep状态 (第{attempt}次尝试)")
                sys.stdout.flush()
                
                try:
                    # 尝试多种方式定位唤醒按钮
                    wakeup_clicked = False
                    
                    # 方法1: 通过按钮文本定位
                    try:
                        page.get_by_text("Yes, get this app back up!").click()
                        wakeup_clicked = True
                    except:
                        pass
                    
                    # 方法2: 通过test-id定位（备用）
                    if not wakeup_clicked:
                        try:
                            page.get_by_test_id("wakeup-button-viewer").click()
                            wakeup_clicked = True
                        except:
                            pass
                    
                    # 方法3: 通过CSS选择器定位（备用）
                    if not wakeup_clicked:
                        try:
                            page.locator("button:has-text('Yes, get this app back up!')").click()
                            wakeup_clicked = True
                        except:
                            pass
                    
                    if wakeup_clicked:
                        print(f"{url} - 已执行唤醒操作，等待30秒后检查状态...")
                        sys.stdout.flush()
                        
                        # 等待30秒后刷新页面
                        time.sleep(30)
                        page.reload()
                        time.sleep(5)  # 等待页面加载
                        
                    else:
                        print(f"{url} - 检测到sleep状态但未能找到唤醒按钮")
                        sys.stdout.flush()
                        List.append(f"{url} - 检测到sleep状态但未能找到唤醒按钮")
                        break
                        
                except Exception as e:
                    print(f"{url} - 第{attempt}次唤醒操作失败: {str(e)}")
                    sys.stdout.flush()
                    
                # 如果达到最大尝试次数
                if attempt >= max_attempts:
                    print(f"{url} - 经过{max_attempts}次尝试仍处于sleep状态，唤醒失败!")
                    sys.stdout.flush()
                    List.append(f"{url} - 经过{max_attempts}次尝试仍处于sleep状态，唤醒失败!")
                    break
                    
            else:
                # 没有检测到sleep关键词，说明应用正常运行
                if attempt > 0:
                    print(f"{url} - 唤醒成功! streamlit应用现已正常运行")
                    sys.stdout.flush()
                    List.append(f"{url} - 唤醒成功! streamlit应用现已正常运行")
                else:
                    print(f"{url} - streamlit应用正在运行")
                    sys.stdout.flush()
                    List.append(f"{url} - streamlit应用正在运行")
                break
            
    except Exception as e:
        print(f"访问 {url} 时出错: {str(e)}")
        sys.stdout.flush()
        List.append(f"访问 {url} 时出错: {str(e)}")

def run(playwright: Playwright) -> None:
    browser = None
    context = None
    page = None
    try:
        browser = playwright.firefox.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        accounts = os.getenv('ST_URL', '')
        if not accounts:
            raise ValueError("环境变量 ST_URL 未设置")
        
        urls = accounts.split(';')
        for url in urls:
            if url.strip():
                check_url_status(page, url.strip())
        
        tt = '\n'.join(List)
        send('=====<streamlit保活信息>=====', tt)
    
    except Exception as e:
        print(f"运行出错: {str(e)}")
        sys.stdout.flush()
    finally:
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()

with sync_playwright() as playwright:
    run(playwright)
