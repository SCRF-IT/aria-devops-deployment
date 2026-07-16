from openai import OpenAI
from tavily import TavilyClient
import os, sys, threading, time, json, subprocess, datetime

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY",""))

MODELS = [
    "openrouter/auto",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-3-12b-it:free",
    "google/gemma-3-4b-it:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
]

PROMPT_FILE = os.path.expanduser("~/system_prompt.txt")
MEMORY_FILE = os.path.expanduser("~/aria_memory.json")

ESC = "\033"
CYAN = ESC + "[96m"
RESET = ESC + "[0m"

BANNER = (
    "\n" + CYAN +
    "  ╔══════════════════════════════════════════╗\n"
    "  ║     ___    ____  _______                 ║\n"
    "  ║    /   |  / __ \/  _/   |                ║\n"
    "  ║   / /| | / /_/ // // /| |                ║\n"
    "  ║  / ___ |/ _, _// // ___ |                ║\n"
    "  ║ /_/  |_/_/ |_/___/_/  |_|                ║\n"
    "  ╠══════════════════════════════════════════╣\n"
    "  ║  Adaptive Reasoning Intelligence         ║\n"
    "  ║  v2.0 -- built by Sensufrog             ║\n"
    "  ╚══════════════════════════════════════════╝"
    + RESET
)

HELP = "\033[90m  clear|reload|memory|exit|/search|/research|/code|/nmap|/harden\033[0m\n"

def load_memory():
    try:
        with open(MEMORY_FILE) as f: return json.load(f)
    except: return {}

def save_memory(mem):
    with open(MEMORY_FILE,"w") as f: json.dump(mem,f,indent=2)

def memory_context(mem):
    if not mem: return ""
    return "[ARIA MEMORY]\n" + "\n".join(f"- {k}: {v}" for k,v in mem.items())

def load_system(mem):
    base = open(PROMPT_FILE).read().strip() if os.path.exists(PROMPT_FILE) else "You are ARIA, a highly capable reasoning AI."
    ctx = memory_context(mem)
    return f"{base}\n\n{ctx}" if ctx else base

def spinner(stop_event, label="thinking"):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r\033[96m{frames[i%len(frames)]}\033[0m {label}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r"+" "*35+"\r")
    sys.stdout.flush()

def run_spinner(label="thinking"):
    stop = threading.Event()
    t = threading.Thread(target=spinner,args=(stop,label))
    t.start()
    return stop,t

def web_search(query,label="searching"):
    stop,t = run_spinner(label)
    try:
        r = tavily.search(query=query,max_results=4)
        stop.set();t.join()
        return "[WEB: "+query+"]\n"+"\n".join(f"[{i+1}] {x['title']}: {x['content'][:250]}" for i,x in enumerate(r.get("results",[])))
    except Exception as e:
        stop.set();t.join()
        return f"[Search error: {e}]"

def deep_research(query):
    stop,t = run_spinner("researching")
    try:
        r = tavily.search(query=query,max_results=5,search_depth="advanced")
        stop.set();t.join()
        return "[RESEARCH: "+query+"]\n\n"+"\n\n".join(f"SOURCE {i+1} - {x['title']}\n{x['content'][:400]}" for i,x in enumerate(r.get("results",[])))
    except Exception as e:
        stop.set();t.join()
        return f"[Research error: {e}]"

def run_code(code):
    stop,t = run_spinner("executing")
    try:
        r = subprocess.run(["python3","-c",code],capture_output=True,text=True,timeout=10)
        stop.set();t.join()
        return "[OUTPUT]\n"+(r.stdout.strip() or r.stderr.strip() or "(no output)")
    except Exception as e:
        stop.set();t.join()
        return f"[Error: {e}]"

def run_nmap(host):
    stop,t = run_spinner(f"scanning {host}")
    try:
        r = subprocess.run(["nmap","-sV","--open","-T4",host],capture_output=True,text=True,timeout=60)
        stop.set();t.join()
        return f"[NMAP: {host}]\n{r.stdout or r.stderr}"
    except FileNotFoundError:
        stop.set();t.join()
        return "[nmap not found - run: pkg install nmap]"
    except Exception as e:
        stop.set();t.join()
        return f"[nmap error: {e}]"

def harden_tips():
    return """[HARDENING]
1.  pkg update && pkg upgrade
2.  Disable ADB when unused
3.  WireGuard VPN on untrusted networks
4.  nmap your LAN: nmap -sV 192.168.1.0/24
5.  Check open ports: ss -tulnp
6.  Revoke unused app permissions
7.  Strong passwords + Bitwarden
8.  2FA everywhere (Aegis)
9.  Disable BT/NFC when unused
10. Check rogue devices: arp -a
11. Private DNS: 1.1.1.1 or NextDNS
12. Audit ~/.bashrc for injections"""

SEARCH_TRIGGERS = ["search","look up","find","current","latest","today","news","who is","what is","when did","where is","how much","price","weather","score","recent","live","now","2024","2025","2026"]

def should_search(msg):
    return any(t in msg.lower() for t in SEARCH_TRIGGERS)

def try_models(history,system):
    stop,t = run_spinner("thinking")
    try:
        for model_id in MODELS:
            try:
                is_gemma = "gemma" in model_id
                msgs = history if is_gemma else [{"role":"system","content":system}]+history
                r = client.chat.completions.create(model=model_id,messages=msgs)
                stop.set();t.join()
                return r.choices[0].message.content
            except Exception as e:
                if any(c in str(e) for c in ["429","402","404","400"]): continue
                stop.set();t.join()
                raise
    finally:
        stop.set();t.join()
    return "\033[91mAll models unavailable.\033[0m"

def chat(history,system,msg):
    history.append({"role":"user","content":msg})
    reply = try_models(history,system)
    history.append({"role":"assistant","content":reply})
    return reply

def extract_memory(mem,msg,reply):
    low = msg.lower()
    if "my name is" in low:
        name = low.split("my name is")[-1].strip().split()[0]
        mem["user_name"] = name
    if any(x in low for x in ["sensufrog","justin"]):
        mem["user_handle"] = "Sensufrog"
    mem["last_seen"] = datetime.datetime.now().strftime("%Y-%m-%d")
    save_memory(mem)

mem = load_memory()
system = load_system(mem)
history = []

print(BANNER)
print(HELP)
if mem: print(f"\033[90m  memory: {len(mem)} entries loaded\033[0m\n")

while True:
    try:
        msg = input("\033[93mYou:\033[0m ").strip()
    except (KeyboardInterrupt,EOFError):
        print("\n\033[90m  ARIA offline.\033[0m\n"); break
    if not msg: continue
    if msg.lower()=="exit": print("\033[90m  ARIA offline.\033[0m\n"); break
    if msg.lower()=="clear": history=[]; print("\033[90m  cleared.\033[0m\n"); continue
    if msg.lower()=="reload": system=load_system(mem); print("\033[90m  reloaded.\033[0m\n"); continue
    if msg.lower()=="memory": print("\033[90m"+json.dumps(mem,indent=2)+"\033[0m\n"); continue
    if msg.lower()=="/harden": print(f"\033[96mARIA:\033[0m {harden_tips()}\n"); continue
    if msg.lower().startswith("/code "):
        code=msg[6:].strip(); result=run_code(code)
        print(f"\033[90m{result}\033[0m\n")
        reply=chat(history,system,f"Code:\n{code}\nOutput:\n{result}\nAnalyze.")
        extract_memory(mem,msg,reply); print(f"\033[96mARIA:\033[0m {reply}\n"); continue
    if msg.lower().startswith("/nmap "):
        host=msg[6:].strip(); result=run_nmap(host)
        print(f"\033[90m{result}\033[0m\n")
        reply=chat(history,system,f"Nmap {host}:\n{result}\nAnalyze vulnerabilities.")
        extract_memory(mem,msg,reply); print(f"\033[96mARIA:\033[0m {reply}\n"); continue
    if msg.lower().startswith("/research "):
        query=msg[10:].strip(); result=deep_research(query)
        print(f"\033[90m{result[:400]}...\033[0m\n")
        reply=chat(history,system,f"{result}\nSynthesize into a clear research summary.")
        extract_memory(mem,msg,reply); print(f"\033[96mARIA:\033[0m {reply}\n"); continue
    if msg.lower().startswith("/search "):
        query=msg[8:].strip(); result=web_search(query)
        print(f"\033[90m{result[:300]}...\033[0m\n")
        reply=chat(history,system,result)
        extract_memory(mem,msg,reply); print(f"\033[96mARIA:\033[0m {reply}\n"); continue
    if should_search(msg) and os.environ.get("TAVILY_API_KEY"):
        result=web_search(msg)
        history.append({"role":"user","content":msg+"\n\n"+result})
        reply=try_models(history,system)
        history.append({"role":"assistant","content":reply})
    else:
        reply=chat(history,system,msg)
    extract_memory(mem,msg,reply)
    print(f"\033[96mARIA:\033[0m {reply}\n")
