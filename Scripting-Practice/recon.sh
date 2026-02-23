#!/usr/bin/env bash

echo "=============================="
echo "   Simple Recon Automation"
echo "=============================="

read -p "Enter target domain: " target

mkdir -p recon/$target
cd recon/$target || exit

echo "[+] Running Subfinder..."
subfinder -d "$target" -silent > subfinder.txt

echo "[+] Running Sublist3r..."
sublist3r -d "$target" -o sublist3r.txt > /dev/null

echo "[+] Running Assetfinder..."
assetfinder --subs-only "$target" > assetfinder.txt

echo "[+] Counting results"

echo "Subfinder:"
wc -l subfinder.txt

echo "Sublist3r:"
wc -l sublist3r.txt

echo "Assetfinder:"
wc -l assetfinder.txt

echo "[+] Merging results..."

cat subfinder.txt sublist3r.txt assetfinder.txt | sort -u > all_subdomains.txt

echo "Total Unique Subdomains:"
wc -l all_subdomains.txt

echo "[+] Probing Alive Domains..."

httpx -l all_subdomains.txt -status-code -title -tech-detect -silent > alive.txt

echo "Alive Domains:"
wc -l alive.txt

echo "[✓] Recon Completed"
echo "Results saved in recon/$target/"
