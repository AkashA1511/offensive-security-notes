#!/usr/bin/env python3
"""
SCA HTML Report Enrichment Script
==================================
Parses a Dependency-Check HTML report, extracts vulnerable packages and
their CVEs, enriches each CVE with NVD + OSV data, and produces a clean
grouped Markdown report + a VAPT-format JSON file.

Usage:
    python script.py [report.html] [enriched_report.md]

Outputs:
    - enriched_report.md   — Markdown report
    - enriched_report.json — VAPT-structured JSON for docx generation
"""

import json
import requests
import time
import re
import sys
from bs4 import BeautifulSoup

# ---------- CONFIG ----------
NVD_API_KEY = "997f0f23-9392-4cfd-8aea-282e29ff1faf"  # https://nvd.nist.gov/developers/request-an-api-key
NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_API_URL = "https://api.osv.dev/v1/query"
MIN_CVE_YEAR = 2022  # Only include CVEs from this year onward


# ---------- HTML PARSING (structural, not regex) ----------
def parse_dependency_check_html(html_content):
    """
    Parse a Dependency-Check HTML report using BeautifulSoup.
    Returns a list of package dicts, each with:
      - package: str (e.g. 'Authlib:1.6.1')
      - file_path: str
      - identifiers: list of {'type': 'purl'|'cpe', 'value': str, 'confidence': str}
      - cves: list of dicts with {'id': str, 'html_desc': str, 'html_cwe': str,
                                    'html_cvss_score': str, 'html_cvss_vector': str}
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    packages = []

    # Find all <h3 class="subsectionheader standardsubsection"> that are NOT notvulnerable
    h3_headers = soup.find_all('h3', class_='subsectionheader')
    for h3 in h3_headers:
        classes = h3.get('class', [])
        # Skip non-vulnerable packages
        if 'notvulnerable' in classes:
            continue
        # Must be a standardsubsection (dependency detail)
        if 'standardsubsection' not in classes:
            continue

        pkg_name = h3.get_text(strip=True)
        if not pkg_name:
            continue

        # The content div is the next sibling <div>
        content_div = h3.find_next_sibling('div')
        if not content_div:
            continue

        # --- File Path ---
        file_path = ""
        # Find <b> containing "File" and "Path"
        for b_tag in content_div.find_all('b'):
            b_text = b_tag.get_text()
            if 'File' in b_text and 'Path' in b_text:
                # The path is in the text node right after this <b> tag
                # Navigate through siblings to get the text
                parent_p = b_tag.parent
                if parent_p:
                    full_text = parent_p.get_text()
                    fp_match = re.search(r'File\s*Path:\s*(.+?)(?:MD5:|$)', full_text, re.DOTALL)
                    if fp_match:
                        file_path = fp_match.group(1).strip()
                        # Clean up any trailing whitespace/newlines
                        file_path = file_path.split('\n')[0].strip()
                break

        # --- Identifiers ---
        identifiers = []
        # Find the Identifiers section (h4 with text "Identifiers")
        for h4 in content_div.find_all('h4'):
            if 'Identifiers' in h4.get_text():
                ident_div = h4.find_next_sibling('div')
                if ident_div:
                    for li in ident_div.find_all('li'):
                        li_text = li.get_text(separator=' ', strip=True)
                        # Extract PURL identifiers (stop at whitespace or paren)
                        purl_match = re.search(r'(pkg:[a-zA-Z0-9._/-]+@[a-zA-Z0-9._-]+)', li_text)
                        if purl_match:
                            conf_match = re.search(r'Confidence\s*:\s*(\w+)', li_text)
                            confidence = conf_match.group(1) if conf_match else "Unknown"
                            identifiers.append({
                                'type': 'purl',
                                'value': purl_match.group(1),
                                'confidence': confidence
                            })
                        # Extract CPE identifiers (stop before parentheses or 'suppress')
                        cpe_match = re.search(r'(cpe:2\.3:[a-zA-Z0-9._:*/-]+)', li_text)
                        if cpe_match:
                            conf_match = re.search(r'Confidence\s*:\s*(\w+)', li_text)
                            confidence = conf_match.group(1) if conf_match else "Unknown"
                            identifiers.append({
                                'type': 'cpe',
                                'value': cpe_match.group(1),
                                'confidence': confidence
                            })
                break

        # --- CVEs (from Published Vulnerabilities section) ---
        cves = []
        for h4 in content_div.find_all('h4'):
            if 'Published Vulnerabilities' in h4.get_text():
                vuln_div = h4.find_next_sibling('div')
                if not vuln_div:
                    continue

                # Each CVE starts with <p><b><a href="...vulnId=CVE-XXX">CVE-XXX</a></b>
                # Find all CVE anchor tags within the vulnerability div
                for p_tag in vuln_div.find_all('p', recursive=True):
                    b_tag = p_tag.find('b')
                    if not b_tag:
                        continue
                    a_tag = b_tag.find('a')
                    if not a_tag:
                        continue
                    cve_text = a_tag.get_text(strip=True)
                    if not re.match(r'CVE-\d{4}-\d{4,}', cve_text):
                        continue

                    # Already collected?
                    if any(c['id'] == cve_text for c in cves):
                        continue

                    # Extract details from the subsequent <p> (same parent context)
                    # The description, CWE, and CVSS follow in the next <p> sibling
                    detail_p = p_tag.find_next_sibling('p')
                    html_desc = ""
                    html_cwe = ""
                    html_cvss_score = ""
                    html_cvss_vector = ""

                    if detail_p:
                        # Description is in <pre> tag
                        pre_tag = detail_p.find('pre')
                        if pre_tag:
                            html_desc = pre_tag.get_text(strip=True)

                        detail_text = detail_p.get_text()

                        # CWE
                        cwe_matches = re.findall(r'(CWE-\d+)\s+([^\n,]+)', detail_text)
                        if cwe_matches:
                            html_cwe = ', '.join(f"{cid} {cname.strip()}" for cid, cname in cwe_matches)

                        # CVSS score
                        score_match = re.search(r'Base Score:\s*\w+\s*\((\d+\.?\d*)\)', detail_text)
                        if score_match:
                            html_cvss_score = score_match.group(1)

                        # CVSS vector
                        vector_match = re.search(r'Vector:\s*(CVSS:3\.\d/[^\s]+)', detail_text)
                        if vector_match:
                            html_cvss_vector = vector_match.group(1)

                    cves.append({
                        'id': cve_text,
                        'html_desc': html_desc,
                        'html_cwe': html_cwe,
                        'html_cvss_score': html_cvss_score,
                        'html_cvss_vector': html_cvss_vector,
                    })

                break  # Only process first Published Vulnerabilities section

        # Only include packages that actually have CVEs
        if cves:
            packages.append({
                'package': pkg_name,
                'file_path': file_path,
                'identifiers': identifiers,
                'cves': cves,
            })

    return packages


def _normalize_key(name):
    """Normalize package name for dedup: lowercase, replace _ with -, strip."""
    return name.lower().replace('_', '-').strip()


def deduplicate_packages(packages):
    """
    Merge packages with the same name (e.g. aiohttp:3.13.2 appearing twice
    from different file paths, or Authlib vs authlib). Keep all unique CVEs
    and file paths.
    """
    merged = {}
    key_to_display = {}  # Keep the first-seen display name
    for pkg in packages:
        key = _normalize_key(pkg['package'])
        if key not in merged:
            key_to_display[key] = pkg['package']
            merged[key] = {
                'package': pkg['package'],
                'file_paths': [pkg['file_path']] if pkg['file_path'] else [],
                'identifiers': list(pkg['identifiers']),
                'cves': list(pkg['cves']),
            }
        else:
            # Add file path if unique
            if pkg['file_path'] and pkg['file_path'] not in merged[key]['file_paths']:
                merged[key]['file_paths'].append(pkg['file_path'])
            # Add unique identifiers
            existing_ids = {(i['type'], i['value']) for i in merged[key]['identifiers']}
            for ident in pkg['identifiers']:
                if (ident['type'], ident['value']) not in existing_ids:
                    merged[key]['identifiers'].append(ident)
                    existing_ids.add((ident['type'], ident['value']))
            # Add unique CVEs
            existing_cves = {c['id'] for c in merged[key]['cves']}
            for cve in pkg['cves']:
                if cve['id'] not in existing_cves:
                    merged[key]['cves'].append(cve)
                    existing_cves.add(cve['id'])

    return list(merged.values())


def filter_cves_by_year(packages, min_year):
    """Remove CVEs older than min_year. Remove packages with no remaining CVEs."""
    filtered = []
    for pkg in packages:
        kept_cves = []
        for cve in pkg['cves']:
            m = re.match(r'CVE-(\d{4})-\d+', cve['id'])
            if m and int(m.group(1)) >= min_year:
                kept_cves.append(cve)
            else:
                print(f"  Skipping {cve['id']} (year < {min_year})")
        if kept_cves:
            pkg['cves'] = kept_cves
            filtered.append(pkg)
    return filtered


# ---------- NVD FETCH ----------
def fetch_nvd_data(cve_id):
    """Return description, CVSS score, CWE, reference for a CVE from NVD API."""
    headers = {'apiKey': NVD_API_KEY} if NVD_API_KEY else {}
    params = {'cveId': cve_id}
    try:
        resp = requests.get(NVD_API_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if 'vulnerabilities' not in data or not data['vulnerabilities']:
            return None

        vuln = data['vulnerabilities'][0]['cve']

        # Description (English preferred)
        description = ''
        for d in vuln.get('descriptions', []):
            if d.get('lang') == 'en':
                description = d.get('value', '')
                break
        if not description and vuln.get('descriptions'):
            description = vuln['descriptions'][0].get('value', '')

        # CVSS v3 — try v3.1 first, then v3.0
        metrics = vuln.get('metrics', {})
        cvss_data = {}
        if metrics.get('cvssMetricV31'):
            cvss_data = metrics['cvssMetricV31'][0].get('cvssData', {})
        elif metrics.get('cvssMetricV30'):
            cvss_data = metrics['cvssMetricV30'][0].get('cvssData', {})

        score = cvss_data.get('baseScore', 'N/A')
        vector = cvss_data.get('vectorString', 'N/A')

        # CWE — use a separate loop variable name to avoid shadowing
        weaknesses = vuln.get('weaknesses', [])
        cwe_list = []
        for weakness in weaknesses:
            for w_desc in weakness.get('description', []):
                val = w_desc.get('value', '')
                if val.startswith('CWE-'):
                    if val not in cwe_list:  # de-duplicate
                        cwe_list.append(val)
        cwe = ', '.join(cwe_list) if cwe_list else 'N/A'

        return {
            'description': description,
            'cvss_score': score,
            'cvss_vector': vector,
            'cwe': cwe,
            'reference': f'https://nvd.nist.gov/vuln/detail/{cve_id}',
        }

    except Exception as e:
        print(f"  NVD error for {cve_id}: {e}")
        return None


# ---------- OSV FETCH ----------
def fetch_fix_for_cve(purl, cve_id):
    """Query OSV for the fixed version of a specific CVE using the package PURL."""
    if not purl:
        return 'N/A'

    payload = {"package": {"purl": purl}}
    try:
        resp = requests.post(OSV_API_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for vuln in data.get('vulns', []):
            # Match by CVE alias
            aliases = vuln.get('aliases', [])
            vuln_id = vuln.get('id', '')
            if cve_id not in aliases and cve_id != vuln_id:
                continue
            # Find the fixed version
            for affected in vuln.get('affected', []):
                for rng in affected.get('ranges', []):
                    for event in rng.get('events', []):
                        if 'fixed' in event:
                            return event['fixed']

        return 'No fixed version found'

    except Exception as e:
        print(f"  OSV error for {cve_id}: {e}")
        return 'Fix info unavailable'


# ---------- BUILD ENRICHED DATA ----------
def enrich_cve(cve_entry, purl):
    """
    Enrich a single CVE with NVD + OSV data.
    Falls back to HTML-extracted data when NVD API fails.
    """
    cve_id = cve_entry['id']
    print(f"  Enriching {cve_id}...")

    # Try NVD API first
    nvd = fetch_nvd_data(cve_id)
    time.sleep(0.6)  # Rate limit: 50 req/30s with API key

    if nvd:
        description = nvd['description']
        cwe = nvd['cwe']
        cvss_score = nvd['cvss_score']
        cvss_vector = nvd['cvss_vector']
        reference = nvd['reference']
    else:
        # Fallback to HTML-extracted data
        print(f"    Using HTML fallback for {cve_id}")
        description = cve_entry.get('html_desc', 'N/A') or 'N/A'
        cwe = cve_entry.get('html_cwe', 'N/A') or 'N/A'
        cvss_score = cve_entry.get('html_cvss_score', 'N/A') or 'N/A'
        cvss_vector = cve_entry.get('html_cvss_vector', 'N/A') or 'N/A'
        reference = f'https://nvd.nist.gov/vuln/detail/{cve_id}'

    # OSV for fix version
    fix = fetch_fix_for_cve(purl, cve_id)
    time.sleep(0.1)

    return {
        'id': cve_id,
        'description': description,
        'cwe': cwe,
        'cwe_detail': cve_entry.get('html_cwe', ''),  # Preserves CWE names from HTML
        'cvss_score': cvss_score,
        'cvss_vector': cvss_vector,
        'reference': reference,
        'fix': fix,
    }


# ---------- MARKDOWN OUTPUT ----------
def generate_markdown(packages, output_file):
    """Generate a clean, grouped Markdown report."""
    lines = []
    lines.append("# Enriched Vulnerability Report\n")
    lines.append(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**CVE Year Filter:** ≥ {MIN_CVE_YEAR}\n")

    total_cves = sum(len(pkg['enriched_cves']) for pkg in packages)
    lines.append(f"**Total Packages:** {len(packages)} | **Total CVEs:** {total_cves}\n")
    lines.append("---\n")

    for pkg in packages:
        lines.append(f"## {pkg['package']}\n")

        # File paths
        file_paths = pkg.get('file_paths', [])
        if file_paths:
            for fp in file_paths:
                lines.append(f"**File Path:** `{fp}`\n")
        else:
            lines.append("**File Path:** N/A\n")

        # Identifiers
        idents = pkg.get('identifiers', [])
        if idents:
            ident_strs = []
            for i in idents:
                ident_strs.append(f"`{i['value']}` (Confidence: {i['confidence']})")
            lines.append(f"**Identifiers:** {', '.join(ident_strs)}\n")
        else:
            lines.append("**Identifiers:** N/A\n")

        lines.append(f"\n### Published Vulnerabilities ({len(pkg['enriched_cves'])})\n")

        for cve in pkg['enriched_cves']:
            lines.append(f"#### [{cve['id']}]({cve['reference']})\n")
            lines.append(f"| Field | Value |")
            lines.append(f"|-------|-------|")
            lines.append(f"| **CWE** | {cve['cwe']} |")
            lines.append(f"| **CVSS v3 Score** | {cve['cvss_score']} |")
            lines.append(f"| **CVSS Vector** | `{cve['cvss_vector']}` |")
            lines.append(f"| **Fix Version** | {cve['fix']} |")
            lines.append(f"| **Reference** | {cve['reference']} |")
            lines.append(f"")
            lines.append(f"**Description:** {cve['description']}\n")

        lines.append("---\n")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\nDone! Saved {output_file} with {len(packages)} package(s), {total_cves} CVE(s).")


# ---------- VAPT JSON OUTPUT ----------
def _cvss_to_severity(score):
    """Map CVSS score to severity label."""
    try:
        s = float(score)
    except (ValueError, TypeError):
        return 'Info'
    if s >= 9.0:
        return 'Critical'
    elif s >= 7.0:
        return 'High'
    elif s >= 4.0:
        return 'Medium'
    elif s > 0:
        return 'Low'
    return 'Info'


def _severity_prefix(severity):
    return {'Critical': 'C', 'High': 'H', 'Medium': 'M', 'Low': 'L', 'Info': 'I'}.get(severity, 'I')


def _parse_cwe_parts(cwe_string):
    """
    Parse CWE string into (id, name) tuples.
    Input:  'CWE-347 Improper Verification of Cryptographic Signature, CWE-863 Incorrect Authorization'
    Output: [('CWE-347', 'Improper Verification of Cryptographic Signature'), ('CWE-863', 'Incorrect Authorization')]
    """
    parts = []
    for segment in re.split(r',\s*(?=CWE-)', cwe_string):
        m = re.match(r'(CWE-\d+)\s*(.*)', segment.strip())
        if m:
            parts.append((m.group(1), m.group(2).strip()))
        elif segment.strip().startswith('CWE-'):
            parts.append((segment.strip(), ''))
    return parts


def generate_vapt_json(packages, output_file):
    """
    Generate a VAPT-format JSON file with one entry per CVE.
    This JSON can be consumed by generate_docx.py to produce Word tables.
    """
    # Counters per severity for reference numbering
    counters = {'C': 0, 'H': 0, 'M': 0, 'L': 0, 'I': 0}
    vulnerabilities = []
    section_num = 1

    for pkg in packages:
        pkg_name_ver = pkg['package']  # e.g. 'Authlib:1.6.1'
        parts = pkg_name_ver.split(':', 1)
        pkg_name = parts[0]
        pkg_version = parts[1] if len(parts) > 1 else ''

        file_paths = pkg.get('file_paths', [])
        identifiers = [i['value'] for i in pkg.get('identifiers', [])]

        for cve in pkg.get('enriched_cves', []):
            severity = _cvss_to_severity(cve['cvss_score'])
            prefix = _severity_prefix(severity)
            counters[prefix] += 1
            ref_no = f"VUL-CODE-{prefix}{counters[prefix]:03d}"

            # CWE: prefer html detail (has names), fallback to NVD IDs
            cwe_detail = cve.get('cwe_detail', '') or cve.get('cwe', '')
            cwe_parts = _parse_cwe_parts(cwe_detail)
            if not cwe_parts:
                # Try NVD cwe field (just IDs like 'CWE-347, CWE-863')
                cwe_parts = _parse_cwe_parts(cve.get('cwe', ''))

            cwe_ids = ', '.join(p[0] for p in cwe_parts) if cwe_parts else cve.get('cwe', 'N/A')
            # Use first CWE name as vulnerability title
            cwe_name = cwe_parts[0][1] if cwe_parts and cwe_parts[0][1] else cwe_ids

            # Countermeasure
            fix = cve.get('fix', 'N/A')
            if fix and fix not in ('N/A', 'No fixed version found', 'Fix info unavailable'):
                countermeasure = f"Upgrade {pkg_name} to version {fix} or higher."
            else:
                countermeasure = "No fixed version available. Check vendor advisory for mitigations."

            vulnerabilities.append({
                'section_number': f"3.1.{section_num}",
                'title': cwe_name,
                'reference_no': ref_no,
                'risk_rating': severity,
                'status': '-',
                'tools_used': 'OWASP Dependency-Check, SCA',
                'category': 'A6 \u2013 Vulnerable and Outdated Component',
                'cwe_id': cwe_ids,
                'cwe_name': cwe_name,
                'cvss_score': str(cve.get('cvss_score', 'N/A')),
                'cvss_vector': cve.get('cvss_vector', 'N/A'),
                'cve_id': cve['id'],
                'package_name': pkg_name,
                'package_version': pkg_version,
                'description': cve.get('description', 'N/A'),
                'identified_by': 'OWASP Dependency-Check (SCA)',
                'identifiers': identifiers,
                'file_paths': file_paths,
                'countermeasures': countermeasure,
                'references': [cve.get('reference', '')],
                'fix_version': fix,
            })
            section_num += 1

    total = sum(counters.values())
    output = {
        'report_meta': {
            'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'cve_year_filter': MIN_CVE_YEAR,
            'total_packages': len(packages),
            'total_vulnerabilities': total,
            'severity_summary': {
                'Critical': counters['C'],
                'High': counters['H'],
                'Medium': counters['M'],
                'Low': counters['L'],
                'Info': counters['I'],
            },
        },
        'vulnerabilities': vulnerabilities,
    }

    json_file = output_file.rsplit('.', 1)[0] + '.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Saved {json_file} with {total} VAPT entries.")
    return json_file


# ---------- MAIN ----------
def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'report.html'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'enriched_report.md'

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. Parse HTML structurally
    print("Parsing HTML report...")
    raw_packages = parse_dependency_check_html(html_content)
    print(f"  Found {len(raw_packages)} vulnerable package section(s)")

    if not raw_packages:
        print("No vulnerable packages found. Check the report format.")
        return

    # 2. Deduplicate packages (same package from multiple file paths)
    packages = deduplicate_packages(raw_packages)
    print(f"  After deduplication: {len(packages)} unique package(s)")

    # 3. Filter by CVE year
    packages = filter_cves_by_year(packages, MIN_CVE_YEAR)
    if not packages:
        print(f"No packages with CVEs from {MIN_CVE_YEAR} onward.")
        return

    total_cves = sum(len(pkg['cves']) for pkg in packages)
    print(f"  After year filter: {len(packages)} package(s) with {total_cves} CVE(s)\n")

    # 4. Enrich each CVE
    for pkg in packages:
        # Find best PURL for OSV queries (versioned PURL preferred)
        purl = ''
        for ident in pkg.get('identifiers', []):
            if ident['type'] == 'purl' and '@' in ident['value']:
                purl = ident['value']
                break

        print(f"Processing {pkg['package']} ({len(pkg['cves'])} CVEs, PURL: {purl or 'none'})...")
        enriched_cves = []
        for cve in pkg['cves']:
            enriched = enrich_cve(cve, purl)
            enriched_cves.append(enriched)

        pkg['enriched_cves'] = enriched_cves

    # 5. Generate Markdown
    generate_markdown(packages, output_file)

    # 6. Generate VAPT JSON (for Word document generation)
    json_file = generate_vapt_json(packages, output_file)
    print(f"\nTo generate the Word document, run:")
    print(f"  python3 generate_docx.py {json_file}")


if __name__ == '__main__':
    main()
