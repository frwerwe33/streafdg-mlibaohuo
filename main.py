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
    try:
        page.goto(url)
        time.sleep(10)
        
        # 检查页面内容是否包含sleep关键词
        page_content = page.content().lower()
        if "sleep" in page_content:
            try:
                page.get_by_test_id("wakeup-button-viewer").click()
                print(f"{url} - 检测到sleep状态，已执行唤醒操作!")
                sys.stdout.flush()
                List.append(f"{url} - 检测到sleep状态，已执行唤醒操作!")
            except Exception as e:
                print(f"{url} - 检测到sleep状态但唤醒失败: {str(e)}")
                sys.stdout.flush()
                List.append(f"{url} - 检测到sleep状态但唤醒失败: {str(e)}")
        else:
            print(f"{url} - streamlit应用正在运行")
            sys.stdout.flush()
            List.append(f"{url} - streamlit应用正在运行")
            
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
