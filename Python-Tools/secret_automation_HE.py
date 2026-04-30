import requests
import time
import re
from bs4 import BeautifulSoup

# ---------- CONFIG ----------
NVD_API_KEY = "your-free-nvd-api-key"   # get from https://nvd.nist.gov/developers/request-an-api-key
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_API_URL = "https://api.osv.dev/v1/query"

# ---------- HTML PARSING ----------
def parse_report_html(html_content):
    """Extract CVE IDs and package identifier from your HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    cve_list = []
    
    # The HTML shows "Published Vulnerabilities" followed by CVE lines.
    # Adjust the selectors to match your real file structure.
    # Example: find all text that matches CVE-XXXX-XXXXX
    text = soup.get_text()
    cve_matches = re.findall(r'CVE-\d{4}-\d{4,}', text)
    cve_ids = list(set(cve_matches))

    # Extract package PURL – again, tailor to your HTML.
    # The snippet has "pkg:pypi/authlib@1.6.1" on a line.
    purl_match = re.search(r'(pkg:[^\s]+)', text)
    package_purl = purl_match.group(1) if purl_match else None

    return cve_ids, package_purl

# ---------- NVD FETCH ----------
def fetch_nvd_data(cve_id):
    """Return description, CVSS score, CWE, references for a CVE."""
    headers = {}
    if NVD_API_KEY:
        headers['apiKey'] = NVD_API_KEY

    params = {'cveId': cve_id}
    try:
        resp = requests.get(NVD_API_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        vuln = data['vulnerabilities'][0]['cve']
        
        # Description
        descriptions = vuln.get('descriptions', [])
        desc = next((d['value'] for d in descriptions if d['lang']=='en'), '')
        
        # CVSS v3 base score & vector
        metrics = vuln.get('metrics', {})
        cvss_v3 = metrics.get('cvssMetricV31', [{}])[0].get('cvssData', {})
        score = cvss_v3.get('baseScore', 'N/A')
        vector = cvss_v3.get('vectorString', '')
        
        # CWE
        weaknesses = vuln.get('weaknesses', [])
        cwe_list = []
        for w in weaknesses:
            for desc in w.get('description', []):
                if desc['value'].startswith('CWE-'):
                    cwe_list.append(desc['value'])
        cwe = ', '.join(cwe_list) if cwe_list else 'N/A'
        
        # References
        references = []
        for ref in vuln.get('references', []):
            references.append(ref['url'])
        
        return {
            'description': desc,
            'cvss_score': score,
            'cvss_vector': vector,
            'cwe': cwe,
            'references': references
        }
    except Exception as e:
        print(f"Error fetching {cve_id}: {e}")
        return None

# ---------- OSV FETCH for fix version ----------
def fetch_fix_from_osv(package_purl):
    """
    Query OSV for the given package PURL.
    Returns the first fixed version found for any vulnerability,
    or a list of suggested upgrades.
    """
    payload = {
        "package": {
            "purl": package_purl
        }
    }
    try:
        resp = requests.post(OSV_API_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        vulns = data.get('vulns', [])
        if not vulns:
            return 'No fixed version found'
        # For each vulnerability, look for a 'fixed' range event
        fixes = set()
        for v in vulns:
            affected = v.get('affected', [])
            for a in affected:
                ranges = a.get('ranges', [])
                for r in ranges:
                    events = r.get('events', [])
                    for e in events:
                        if 'fixed' in e:
                            fixes.add(e['fixed'])
        if fixes:
            # Sort and return the highest fix version (simple string sort works for semver)
            sorted_fixes = sorted(fixes, key=lambda s: list(map(int, s.split('.'))))
            return f"Upgrade to {sorted_fixes[-1]} or later"
        return 'No explicit fixed version; check advisory'
    except Exception as e:
        print(f"OSV error: {e}")
        return 'Fix info unavailable'

# ---------- MAIN ----------
def main():
    # 1. Load your HTML file
    with open('report.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    cve_ids, package_purl = parse_report_html(html_content)
    print(f"Found CVEs: {cve_ids}")
    print(f"Package: {package_purl}")

    # 2. Enrich each CVE
    report_entries = []
    for cve in cve_ids:
        print(f"Processing {cve}...")
        nvd_data = fetch_nvd_data(cve)
        if nvd_data:
            # Optionally fetch fix version from OSV
            fix_info = fetch_fix_from_osv(package_purl)
            entry = {
                'cve': cve,
                'package': package_purl,
                **nvd_data,
                'fix': fix_info
            }
            report_entries.append(entry)
        time.sleep(0.6)   # NVD rate limit without key is 5 req/30s; with key 50 req/30s

    # 3. Generate a Markdown report
    with open('enriched_report.md', 'w', encoding='utf-8') as out:
        out.write("# Enriched Vulnerability Report\n\n")
        for e in report_entries:
            out.write(f"## {e['cve']} - {e['package']}\n")
            out.write(f"**CWE:** {e['cwe']}\n\n")
            out.write(f"**CVSS v3 Score:** {e['cvss_score']}  \n")
            out.write(f"**Vector:** {e['cvss_vector']}\n\n")
            out.write(f"**Description:** {e['description']}\n\n")
            out.write(f"**Fix:** {e['fix']}\n\n")
            out.write("**References:**\n")
            for ref in e['references']:
                out.write(f"- {ref}\n")
            out.write("\n---\n")

    print(f"Done! {len(report_entries)} CVEs written to enriched_report.md")

if __name__ == '__main__':
    main()