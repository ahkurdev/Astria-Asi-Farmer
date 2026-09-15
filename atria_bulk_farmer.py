import urllib.request
import http.cookiejar
import json
import time
import re
import uuid
import sys
import os

DEFAULT_BACKUP_PATH = r"c:\Allan\CODE\TOOLS\FARMER\astria\9router-backup-2026-09-15T05-42-33-258Z.json"
DEFAULT_EXPORT_PATH = r"c:\Allan\CODE\TOOLS\FARMER\astria\harvested_keys.json"
PROVIDER_ID = "openai-compatible-chat-f435c897-67c4-4469-afc1-d4e57b2fddae"
TOKENS_PER_ACCOUNT = 100_000_000

def get_guerrilla_email():
    req = urllib.request.Request("https://api.guerrillamail.com/ajax.php?f=get_email_address", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["email_addr"], data["sid_token"]

def check_guerrilla_otp(sid_token, timeout=40):
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(3)
        req = urllib.request.Request(f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token={sid_token}", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            emails = data.get("list", [])
            for em in emails:
                if "Logto" in em.get("mail_subject", "") or "Atria" in em.get("mail_subject", "") or "verification" in em.get("mail_subject", "").lower():
                    mid = em["mail_id"]
                    req_fetch = urllib.request.Request(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mid}&sid_token={sid_token}", headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req_fetch) as f_res:
                        f_data = json.loads(f_res.read().decode("utf-8"))
                        body = f_data.get("mail_body", "")
                        match = re.search(r'\b\d{6}\b', body)
                        if match:
                            return match.group(0)
    return None

def build_connection_object(email, api_key, custom_name=None):
    conn_id = str(uuid.uuid4())
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
    return {
        "defaultModel": "Atria-Dawn-Preview",
        "apiKey": api_key,
        "testStatus": "active",
        "providerSpecificData": {
            "prefix": "as",
            "apiType": "chat",
            "baseUrl": "https://api.atria-asi.ai/v1",
            "nodeName": "Astria",
            "connectionProxyEnabled": False,
            "connectionProxyUrl": "",
            "connectionNoProxy": ""
        },
        "lastError": None,
        "lastErrorAt": None,
        "errorCode": None,
        "rateLimitedUntil": None,
        "backoffLevel": 0,
        "id": conn_id,
        "provider": PROVIDER_ID,
        "authType": "apikey",
        "name": custom_name or f"as_farm_{email.split('@')[0]}",
        "email": email,
        "priority": 1,
        "isActive": True,
        "createdAt": now_iso,
        "updatedAt": now_iso
    }

def inject_to_9router_backup(target_path, new_connections):
    if not os.path.exists(target_path):
        print(f"[!] Target file '{target_path}' not found!")
        return False

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "providerConnections" not in data:
        data["providerConnections"] = []

    for conn in reversed(new_connections):
        data["providerConnections"].insert(0, conn)

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[+] Successfully injected {len(new_connections)} connection(s) directly into: {target_path}")
    return True

def save_standalone_json(export_path, new_connections):
    export_data = {
        "provider": "Astria (Atria-Dawn-Preview)",
        "baseUrl": "https://api.atria-asi.ai/v1",
        "totalHarvested": len(new_connections),
        "totalTokensGranted": len(new_connections) * TOKENS_PER_ACCOUNT,
        "connections": new_connections,
        "rawApiKeys": [c["apiKey"] for c in new_connections]
    }
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"[+] Successfully saved standalone JSON to: {export_path}")
    return True

def farm_single_account(account_index=1, captcha_token=None):
    print(f"\n--------------------------------------------------", flush=True)
    print(f"[*] Try {account_index} account...", flush=True)
    try:
        email, sid = get_guerrilla_email()
        print(f"    Email: {email}", flush=True)

        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.open("https://api.atria-asi.ai/console")

        # 1. Experience Register (Include captchaToken if present)
        init_payload = {"interactionEvent": "Register"}
        if captcha_token:
            init_payload["captchaToken"] = captcha_token

        req = urllib.request.Request(
            "https://auth.atria-asi.ai/api/experience",
            data=json.dumps(init_payload).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="PUT"
        )
        opener.open(req)

        # 2. Request OTP Code
        req = urllib.request.Request(
            "https://auth.atria-asi.ai/api/experience/verification/verification-code",
            data=json.dumps({"interactionEvent": "Register", "identifier": {"type": "email", "value": email}}).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="POST"
        )
        send_body = json.loads(opener.open(req).read().decode("utf-8"))
        verification_id = send_body.get("verificationId")

        print(f"    Requesting OTP... Waiting for incoming email...", flush=True)
        otp = check_guerrilla_otp(sid)
        if not otp:
            print(f"[-] Try {account_index} account: FAILED (OTP Timeout)", flush=True)
            return None
        print(f"    OTP received: {otp}", flush=True)

        # 3. Verify OTP
        req = urllib.request.Request(
            "https://auth.atria-asi.ai/api/experience/verification/verification-code/verify",
            data=json.dumps({"identifier": {"type": "email", "value": email}, "verificationId": verification_id, "code": otp}).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="POST"
        )
        verify_body = json.loads(opener.open(req).read().decode("utf-8"))

        # 4. Identification
        req = urllib.request.Request(
            "https://auth.atria-asi.ai/api/experience/identification",
            data=json.dumps({"type": "email", "verificationId": verify_body.get("verificationId")}).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="POST"
        )
        opener.open(req)

        # 5. Submit
        req = urllib.request.Request(
            "https://auth.atria-asi.ai/api/experience/submit",
            data=b"{}",
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="POST"
        )
        sub_body = json.loads(opener.open(req).read().decode("utf-8"))
        redirect_url = sub_body.get("redirectTo")
        opener.open(redirect_url)

        # 6. Create API Key
        key_name = f"as_farm_{account_index}_{email.split('@')[0]}"
        req_key = urllib.request.Request(
            "https://api.atria-asi.ai/api/keys",
            data=json.dumps({"name": key_name}).encode("utf-8"),
            headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
            method="POST"
        )
        res_key = opener.open(req_key)
        key_data = json.loads(res_key.read().decode("utf-8"))
        api_key = key_data.get("key")

        if api_key:
            print(f"[+] Try {account_index} account: SUCCESS -> Key: {api_key}", flush=True)
            conn_obj = build_connection_object(email, api_key, custom_name=f"as_auto_{email.split('@')[0]}")
            return {"email": email, "apiKey": api_key, "connection": conn_obj}
        else:
            print(f"[-] Try {account_index} account: FAILED (Could not generate API key)", flush=True)
            return None
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8", errors="ignore")
        if "captcha_required" in body:
            print(f"[-] Try {account_index} account: FAILED (Cloudflare Turnstile CAPTCHA triggered - rate limited on IP)", flush=True)
        else:
            print(f"[-] Try {account_index} account: FAILED (HTTP {he.code}: {body})", flush=True)
        return None
    except Exception as e:
        print(f"[-] Try {account_index} account: FAILED ({e})", flush=True)
        return None

def main():
    print("=================================================================")
    print("        ATRIA AUTOMATED BULK FARMING TOOL v2.1 (EN)              ")
    print("=================================================================\n")

    # 1. Input Total Target
    while True:
        try:
            val = input(">> How many accounts do you want to harvest? (e.g. 5 / 10 / 500): ").strip()
            total_target = int(val)
            if total_target > 0:
                break
            print("Please enter a positive integer greater than 0!")
        except ValueError:
            print("Invalid input! Please enter a valid number.")

    # 2. Input JSON Injection Option
    print("\n>> Would you like to inject directly into your 9router backup JSON file?")
    choice = input("   Choose (y/n) [Default: y]: ").strip().lower()
    inject_direct = (choice != 'n')

    target_json_path = ""
    export_json_path = ""

    if inject_direct:
        print(f"\n   Default target path: {DEFAULT_BACKUP_PATH}")
        custom_path = input("   Press [ENTER] to use default, or enter a custom path: ").strip()
        target_json_path = custom_path if custom_path else DEFAULT_BACKUP_PATH
    else:
        print(f"\n   Harvested keys will be saved to a clean standalone JSON file.")
        print(f"   Default export path: {DEFAULT_EXPORT_PATH}")
        custom_exp = input("   Press [ENTER] to use default, or enter a custom path: ").strip()
        export_json_path = custom_exp if custom_exp else DEFAULT_EXPORT_PATH

    print(f"\n[*] STARTING FARMING PROCESS ({total_target} Target Accounts)...")
    print("=================================================================")

    success_count = 0
    fail_count = 0

    try:
        for i in range(1, total_target + 1):
            result = farm_single_account(account_index=i)
            if result:
                success_count += 1
                conn = result["connection"]
                
                # Instant save / injection per successful account
                if inject_direct:
                    inject_to_9router_backup(target_json_path, [conn])
                else:
                    # Append to standalone json immediately
                    current_conns = []
                    if os.path.exists(export_json_path):
                        try:
                            with open(export_json_path, "r", encoding="utf-8") as f:
                                existing = json.load(f)
                                current_conns = existing.get("connections", [])
                        except Exception:
                            current_conns = []
                    current_conns.append(conn)
                    save_standalone_json(export_json_path, current_conns)
            else:
                fail_count += 1

            print(f"    [Current Status: {success_count} Success | {fail_count} Failed | Total Target: {total_target}]", flush=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Process stopped by user (Ctrl+C). All previous successful accounts are already safely saved!")

    total_tokens = success_count * TOKENS_PER_ACCOUNT
    formatted_tokens = f"{total_tokens:,}"

    print("\n=================================================================")
    print(f"\n>>> {success_count} account success {formatted_tokens} token granted <<<\n")
    print("=================================================================")
    print("All tasks completed! <3")

if __name__ == "__main__":
    main()
