# IDOR-Automation
---

The Development Flow – Phase by Phase
Phase 0: Environment & “Hello Burp” (Week 1, ~3–4 days)
Goal: Get a minimal Burp extension running from your own code.

Day 1:

Install Java JDK 17 (or 21) on Ubuntu via apt or sdkman. Verify java -version.

Install Gradle (also via sdkman or manual download).

Create a minimal Gradle Java project (gradle init or a template).

Understand the project structure: src/main/java, build.gradle.kts, settings.

Day 2:

Add Burp’s Montoya API dependency to build.gradle.kts.

Write the simplest possible extension class: implement BurpExtension, override initialize(), and call api.extension().setName("Hello Burp").

Build the JAR with gradle jar.

Load the JAR into Burp’s Extender tab (on your local Burp).

Verify the extension appears in the list and prints its name.

Day 3:

Add a custom UI tab using api.userInterface().registerSuiteTab().

Create a simple Swing JPanel with a JLabel that says “AuthZ Sidecar – Ready”.

Rebuild, reload, confirm the tab appears and the label shows.

Day 4:

Learn how to reload extensions quickly (Burp’s “Reload” button or auto-reload on build).

Wrap up: you now have a build pipeline and a live extension stub.

Phase 1: Session Capture & Storage (Week 2, ~3–4 days)
Goal: Build the “Session Profiles” part of the UI and capture auth headers from a real request.

Day 5:

Design a simple data class (SessionProfile) with fields: name, List<HttpHeader>.

Create a SessionStore class that holds a Map<String, SessionProfile>.

Add a method to import from a Burp HttpRequest: extract headers whose name is cookie or authorization (case-insensitive).

Day 6:

Start building the Swing UI: a JTable backed by a DefaultTableModel to show profiles.

Add a button “Capture from History”.

When clicked, fetch the last request from Burp’s proxy history (using api.proxy().history()), extract auth headers, and add a new profile row to the table.

Day 7:

Wire the button to the SessionStore.

Test by browsing an authenticated site, clicking Capture, and seeing the profile appear with a preview of the headers.

(Optional) Add a delete button.

Day 8:

Learn to serialize session profiles as JSON (using Gson) and save/load them to a file so they persist across Burp restarts.

Add “Save” and “Load” buttons to the UI.

Phase 2: Manual Replay – Right-Click “Replay as…” (Week 3, ~3–4 days)
Goal: Manually replay any request with a different session and see the response side-by-side.

Day 9:

Understand Burp’s context menu API: register a menu item provider that appears in Repeater and Proxy history.

Add a right‑click menu “AuthZ Sidecar” with sub‑items for each stored profile (e.g., “Replay as Admin”).

Day 10:

On menu click, get the original HttpRequest, replace its auth headers with the chosen profile’s headers, and send it via api.http().sendRequest().

Display the response status and body length in a simple popup dialog (just to confirm it works).

Day 11:

Build a diff viewer dialog: a JDialog with two JTextArea panels (original response body vs. replayed).

Use a simple JLabel to show status codes and lengths.

Highlight the word “admin” or “role” in the replayed response to make it quickly noticeable (basic text highlighting).

Day 12:

Improve the diff viewer: add a basic JSON diff (parse with Gson, compare keys) if content-type is JSON.

Show added/removed fields in a third panel or by coloring the text.

Polish the manual replay flow.

Phase 3: Passive Auto‑Replay & Alerting (Week 4, ~4–5 days)
Goal: Automatically replay every in‑scope proxy request with the shadow session, compare responses, and log suspicious findings.

Day 13:

Create an AuthReplayHandler class that implements ProxyResponseHandler.

In handleResponse(), retrieve the initiating request and original response.

Check if auto‑replay is enabled (a boolean flag in your UI) and if the URL is in scope.

Day 14:

Clone the request, replace auth headers with the shadow profile’s headers.

Send the request asynchronously (use a separate thread) to avoid lagging the browser.

When the alternate response arrives, compare status codes and body length.

If difference detected, add a row to a “Findings” table in your main UI tab.

Day 15:

Improve the diff logic: implement a structured DiffResult class with a “suspicious” flag.

Add rules: e.g., original 401/403 but alternate 200 → suspicious; length differs >20% and both 200 → suspicious; JSON contains privileged keys like admin, role, credit_card.

Update the findings table to show a short summary.

Day 16–17:

Add a findings viewer: double‑click a finding to open the diff viewer (reuse the dialog from Phase 2).

Add buttons to ignore/delete findings and to export findings as a CSV or Markdown report (simple file writing).

Test thoroughly on a vulnerable app (e.g., Web Security Academy access control labs).

Phase 4: IDOR Mutation Engine & Final Polish (Week 5, ~4–5 days)
Goal: Add the semi‑automated IDOR testing feature and refine the tool for daily use.

Day 18:

Design an IdorParameter detector: parse a request’s URL query, body parameters, and path segments.

Identify numeric IDs (sequences of digits), UUIDs, and role‑like strings (user, admin, guest).

Day 19:

Build a mutation generator: for each numeric ID, produce variations (increment, decrement, 0, -1, 9999999, null/empty). For UUIDs, swap with the shadow profile’s user ID (if known). For role strings, produce alternate roles.

Create a list of HttpRequest objects with mutated values.

Day 20:

Add a right‑click menu action “Test IDOR patterns on this request”.

On click, send all mutated requests concurrently (limit to e.g. 10 parallel) and collect responses.

Display results in a compact table: URL, status, length, highlights.

Day 21–22:

Add a blacklist feature to never replay URLs matching certain patterns (e.g., /logout, /payment).

Add a scope toggle “Use Burp’s target scope” or custom regex.

Final polish: tooltips, error handling, a Help button that shows usage tips.

Test on multiple test applications and fix bugs.

Phase 5: Packaging & Sharing (Week 6, ~2 days)
Day 23:

Configure Gradle to build a “fat JAR” that includes all dependencies (Gson, etc.).

Write a README with installation and usage instructions.

(Optional) Publish to GitHub.

Day 24:

Reflect on what you learned, write a blog post if you like, or just enjoy using your own tool on real assessments.
