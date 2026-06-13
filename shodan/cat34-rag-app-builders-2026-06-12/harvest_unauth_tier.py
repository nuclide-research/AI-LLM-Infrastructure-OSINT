#!/usr/bin/env python3
"""Cat-34 unauth-tier harvest -> hosts.json + ips.txt. Shodan-visible subset (2026-06-12)."""
import json, os
DIR = "/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/cat34-rag-app-builders-2026-06-12"

H = {
 "vanna": [
  ("93.125.18.117","8000","Vanna Agents Chat",["autoinsight.com"]),
  ("109.206.246.193","8000","Vanna Agents Chat",["spk.laws.ms"]),
  ("138.68.234.144","8001","Vanna Agents Chat",[]),
  ("93.125.18.85","8000","Vanna Agents Chat",["autoinsight.com"]),
  ("93.186.251.106","8000","Inmote Agents Chat",["host106-251-186-93.serverdedicati.aruba.it"]),
  ("182.92.206.34","8080","安捷星健康分析 - 智能健康数据平台",[]),
  ("118.253.157.68","8000","Vanna Agents Chat",[]),
  ("171.225.223.209","8010","Vanna Agents Chat",["dynamic-ip-adsl.viettel.vn"]),
  ("93.125.18.103","8000","Vanna Agents Chat",["autoinsight.com"]),
  ("152.136.12.140","8080","Vanna Agents Chat",[]),
  ("93.125.18.112","8000","Vanna Agents Chat",["autoinsight.com"]),
  ("93.125.18.102","8000","Vanna Agents Chat",["autoinsight.com"]),
  ("8.138.192.156","8000","Vanna Agents Chat",[]),
  ("54.20.22.78","","NoHarm Data Agent",["ec2-54-20-22-78.sa-east-1.compute.amazonaws.com","vanna.noharm.ai"]),
 ],
 "qanything": [
  ("47.121.211.168","2345","Application QAnything cannot handle your request",[]),
  ("101.132.145.61","80","QAnything",[]),
  ("43.163.124.91","264","Application QAnything cannot handle your request",[]),
  ("139.155.140.234","8883","Application QAnything cannot handle your request",[]),
  ("111.61.228.51","50002","Application QAnything cannot handle your request",[]),
  ("43.134.107.84","6036","Application QAnything cannot handle your request",[]),
 ],
 "khoj": [
  ("43.153.76.24","6653","Khoj AI - Ask Anything",[]),
  ("20.235.79.57","","Khoj by Axiomaera — Find your leaked data",["khoj.axiomaera.com","khoj.axiomaera.dev"]),
  ("192.9.190.118","","Khoj AI - Ask Anything",["obsidian.the-judsons.com"]),
  ("34.144.216.8","","Khoj — Varaha Science Pipeline",["khoj.varahaag.com"]),
  ("13.232.31.32","80","Khoj",["ec2-13-232-31-32.ap-south-1.compute.amazonaws.com"]),
  ("103.21.58.53","","Apna Ghar Khoj",["uat.apnagharkhoj.com"]),
 ],
 "verba": [
  ("95.217.213.59","8000","Verba",["static.59.213.217.95.clients.your-server.de"]),
  ("178.104.196.159","8000","Verba",["static.159.196.104.178.clients.your-server.de"]),
  ("91.134.133.144","8888","Verba",["vps-92448cb3.vps.ovh.net"]),
 ],
 "privategpt": [
  ("135.148.138.3","","PrivateGPT | Homepage",["vps-3ac4735e.vps.ovh.us","privategpt.me"]),
  ("54.84.56.185","","PrivateGPT",["privategpt.com.br","ec2-54-84-56-185.compute-1.amazonaws.com"]),
  ("20.163.186.2","","PrivateGPT",["microstrategy.com"]),
  ("42.192.203.236","","PrivateGPT Hub",["privategpt.kangxinabcd.xyz"]),
  ("123.57.77.178","8081","PrivateGPT",[]),
 ],
 "quivr": [
  ("43.153.76.24","21311","Quivr - Get a Second Brain with Generative AI",[]),
  ("5.75.178.159","3000","Quivr - Get a Second Brain with Generative AI",["static.159.178.75.5.clients.your-server.de"]),
  ("193.190.253.75","","Login - Overleaf powered by Quivr",["ns.kotnet.org"]),
  ("192.241.143.159","3000","Quivr - Get a Second Brain with Generative AI",["update.smbscanner.com"]),
  ("132.145.102.65","3000","Quivr - Get a Second Brain with Generative AI",[]),
  ("74.235.200.210","3000","Quivr - Get a Second Brain with Generative AI",[]),
  ("139.59.228.151","3000","Quivr - Get a Second Brain with Generative AI",[]),
  ("185.219.135.207","3000","Quivr - Get a Second Brain with Generative AI",[]),
 ],
 "chatbot-ui": [
  ("52.88.142.15","","FTR Chatbot UI v3.4",["ec2-52-88-142-15.us-west-2.compute.amazonaws.com"]),
  ("184.34.33.178","","FTR Chatbot UI v3.4",["ec2-184-34-33-178.us-west-2.compute.amazonaws.com"]),
  ("34.216.57.45","","FTR Chatbot UI v3.4",["ec2-34-216-57-45.us-west-2.compute.amazonaws.com"]),
  ("95.182.99.37","80","Chatbot UI",[]),
  ("144.126.254.179","80","Chatbot UI",[]),
 ],
 "bionic-gpt": [
  ("213.39.39.82","80","hui (bionicgpt html match — verify)",[]),
 ],
}

hosts = []
for plat, rows in H.items():
    for ip, port, title, hn in rows:
        hosts.append({"platform":plat, "ip":ip, "port":port, "title":title, "hostnames":hn})

with open(os.path.join(DIR,"hosts.json"),"w") as f:
    json.dump({"survey":"cat34-rag-app-builders","date":"2026-06-12","tier":"unauth-shodan-visible","hosts":hosts}, f, indent=2, ensure_ascii=False)

ips = sorted({h["ip"] for h in hosts}, key=lambda s: tuple(int(x) for x in s.split(".")))
with open(os.path.join(DIR,"ips.txt"),"w") as f:
    f.write("\n".join(ips)+"\n")

print(f"hosts: {len(hosts)} | unique IPs: {len(ips)}")
print("platforms:", ", ".join(f"{k}={len(v)}" for k,v in H.items()))
