
document.addEventListener("DOMContentLoaded", () => {
    const projectFile = document.getElementById("projectFile");
    const scanProjectFile = document.getElementById("scanProjectFile");
    const browseButton = document.getElementById("browseButton");
    const selectedFile = document.getElementById("selectedFile");
    const startScanButton = document.getElementById("startScanButton");

    let latestScanResult = null;
let selectedProjectFile = null;
    // 1. Escape HTML to safely display scanner output
    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]);
    }

    // 2. Open a page
    function openPage(pageId) {
        const target = document.getElementById(pageId);

        if (!target) {
            console.warn("Page section not found:", pageId);
            return;
        }

        document.querySelectorAll(".page-section").forEach(section => {
            section.classList.add("hidden");
        });

        target.classList.remove("hidden");

        document.querySelectorAll(".nav-link[data-page]").forEach(link => {
            link.classList.toggle("active", link.dataset.page === pageId);
        });

        const pageTitle = document.getElementById("pageTitle");
        const heading = target.querySelector("h1");

        if (pageTitle && heading) {
            pageTitle.textContent = heading.textContent.trim();
        }

        window.location.hash = pageId;
    }

    // 3. Sidebar navigation
    document.querySelectorAll(".nav-link[data-page]").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            openPage(link.dataset.page);
        });
    });

    // 4. Buttons that navigate to another page
    document.querySelectorAll("[data-go]").forEach(button => {
        button.addEventListener("click", event => {
            event.preventDefault();
            openPage(button.dataset.go);
        });
    });

    // 5. Handle other navigation buttons by their labels
    document.addEventListener("click", event => {
        const button = event.target.closest("button, a");

        if (!button) return;

        if (
            button.matches("[data-go], .nav-link[data-page]") ||
            button.id === "browseButton" ||
            button.id === "startScanButton"
        ) {
            return;
        }

        const label = button.textContent.trim().toLowerCase();

        const routes = [
            { words: ["view reports", "reports", "report history"], page: "scan-history" },
            { words: ["vulnerabilities", "view vulnerabilities"], page: "vulnerabilities" },
            { words: ["ai fixes", "view fixes", "fixes"], page: "ai-fixes" },
            { words: ["scan history", "history", "view history"], page: "scan-history" },
            { words: ["settings"], page: "settings" },
            { words: ["new scan", "configure security scan", "start new scan"], page: "new-scan" },
            { words: ["dashboard", "back to dashboard"], page: "dashboard" }
        ];

        for (const route of routes) {
            if (route.words.some(word => label.includes(word))) {
                event.preventDefault();
                openPage(route.page);
                return;
            }
        }
    });

    // 6. Open the initial page
    function openInitialPage() {
        const pageId = window.location.hash.replace("#", "") || "dashboard";
        const target = document.getElementById(pageId);

        if (target && target.classList.contains("page-section")) {
            openPage(pageId);
        } else {
            openPage("dashboard");
        }
    }

    window.addEventListener("hashchange", () => {
        const pageId = window.location.hash.replace("#", "");
        const target = document.getElementById(pageId);

        if (target && target.classList.contains("page-section")) {
            openPage(pageId);
        }
    });

    openInitialPage();

    // 7. Browse for a ZIP file
    browseButton?.addEventListener("click", () => {
        projectFile?.click();
    });

    // 8. Display the selected file name
 projectFile?.addEventListener("change", () => {
    if (projectFile.files.length > 0) {
        selectedProjectFile = projectFile.files[0];

        if (selectedFile) {
            selectedFile.textContent =
                "Selected file: " + selectedProjectFile.name;
        }
    }
});

    // 9. Display vulnerabilities returned by the backend
    function displayVulnerabilities(scanResult) {
        const section = document.getElementById("vulnerabilities");

        if (!section) {
            console.error("Vulnerabilities section not found.");
            return;
        }

        const panel = section.querySelector(".panel");

        if (!panel) {
            console.error("Vulnerabilities panel not found.");
            return;
        }

        const fileResults = Array.isArray(scanResult.results)
            ? scanResult.results
            : [];

        const issues = fileResults.flatMap(fileResult => {
            const fileIssues = Array.isArray(fileResult.issues)
                ? fileResult.issues
                : [];

            return fileIssues.map(issue => ({
                ...issue,
                file: issue.file || fileResult.file || "Unknown file"
            }));
        });

        const severityColors = {
            HIGH: "#ef4444",
            MEDIUM: "#f59e0b",
            LOW: "#3b82f6",
            CRITICAL: "#dc2626"
        };

        const severityCounts = scanResult.severity_counts || {};

        panel.innerHTML = `
            <div class="panel-heading">
                <div>
                    <h3>Scan Results</h3>
                    <p>
                        ${Number(scanResult.total_files) || fileResults.length}
                        files scanned · ${issues.length} issues detected
                    </p>
                </div>
            </div>

            <div class="stats-grid" style="margin-bottom:24px;">
                <article class="stat-card">
                    <div class="stat-top"><span>Total Issues</span></div>
                    <h2>${issues.length}</h2>
                </article>

                <article class="stat-card">
                    <div class="stat-top"><span>High Severity</span></div>
                    <h2 style="color:#ef4444;">
                        ${Number(severityCounts.HIGH) || 0}
                    </h2>
                </article>

                <article class="stat-card">
                    <div class="stat-top"><span>Medium Severity</span></div>
                    <h2 style="color:#f59e0b;">
                        ${Number(severityCounts.MEDIUM) || 0}
                    </h2>
                </article>

                <article class="stat-card">
                    <div class="stat-top"><span>Low Severity</span></div>
                    <h2 style="color:#3b82f6;">
                        ${Number(severityCounts.LOW) || 0}
                    </h2>
                </article>
            </div>

            ${
                issues.length > 0
                    ? issues.map(issue => {
                        const severity = String(issue.severity || "UNKNOWN").toUpperCase();
                        const color = severityColors[severity] || "#94a3b8";
                        const fix = issue.fix_suggestion || {};

                        return `
                            <article style="
                                padding:20px;
                                margin-bottom:16px;
                                border:1px solid #263244;
                                border-radius:12px;
                                overflow-wrap:anywhere;
                            ">
                                <div style="
                                    display:flex;
                                    justify-content:space-between;
                                    align-items:flex-start;
                                    gap:12px;
                                    flex-wrap:wrap;
                                ">
                                    <h3 style="margin:0;">
                                        ${escapeHTML(issue.title || "Security issue")}
                                    </h3>

                                    <span style="
                                        color:${color};
                                        font-weight:700;
                                        font-size:12px;
                                        padding:5px 10px;
                                        border:1px solid ${color};
                                        border-radius:20px;
                                        white-space:nowrap;
                                    ">
                                        ${escapeHTML(severity)}
                                    </span>
                                </div>

                                <p style="margin:14px 0 8px;">
                                    <strong>File:</strong>
                                    ${escapeHTML(issue.file)}
                                </p>

                                <p style="margin:8px 0;">
                                    <strong>Line:</strong>
                                    ${Number(issue.line) || "N/A"}
                                    &nbsp; | &nbsp;
                                    <strong>Rule:</strong>
                                    ${escapeHTML(issue.test_id || "N/A")}
                                </p>

                                <p style="margin:12px 0;">
                                    <strong>Recommendation:</strong>
                                    ${escapeHTML(
                                        issue.recommendation ||
                                        "Review this issue manually."
                                    )}
                                </p>

                                <div style="
                                    margin-top:14px;
                                    padding:14px;
                                    border-radius:8px;
                                    background:rgba(59,130,246,0.08);
                                ">
                                    <strong>Suggested Fix</strong>

                                    <p style="margin:8px 0;">
                                        ${escapeHTML(
                                            fix.description ||
                                            "Manual review is required for this issue."
                                        )}
                                    </p>

                                    ${
                                        fix.example
                                            ? `<pre style="
                                                white-space:pre-wrap;
                                                overflow-wrap:anywhere;
                                                padding:12px;
                                                border-radius:6px;
                                                background:#111827;
                                                color:#e5e7eb;
                                            "><code>${escapeHTML(fix.example)}</code></pre>`
                                            : ""
                                    }

                                    <small>
                                        ${
                                            fix.fix_available
                                                ? "A suggested fix is available. Review it before applying."
                                                : "No automated fix is currently available for this issue."
                                        }
                                    </small>
                                </div>
                            </article>
                        `;
                    }).join("")
                    : `
                        <div class="empty-state">
                            <div class="empty-icon">
                                <i class="fa-solid fa-shield-halved"></i>
                            </div>
                            <h4>No issues detected</h4>
                            <p>The current scanner did not identify any supported issues.</p>
                        </div>
                    `
            }

            <button type="button" class="secondary-button" id="scanAgainButton">
                <i class="fa-solid fa-rotate"></i> Scan Another Project
            </button>
        `;

        document.getElementById("scanAgainButton")?.addEventListener("click", () => {
            openPage("new-scan");
        });
    }

    // 10. Update dashboard statistics
    function updateDashboard(scanResult) {
        const totalScans = document.getElementById("totalScans");
        const totalVulnerabilities = document.getElementById("totalVulnerabilities");
        const securityScore = document.getElementById("securityScore");

        if (totalScans) {
            totalScans.textContent = "1";
        }

        if (totalVulnerabilities) {
            totalVulnerabilities.textContent =
                String(Number(scanResult.total_issues) || 0);
        }

        if (securityScore) {
            const total = Number(scanResult.total_issues) || 0;
            const high = Number(scanResult.severity_counts?.HIGH) || 0;
            const medium = Number(scanResult.severity_counts?.MEDIUM) || 0;

            const score = total === 0
                ? 100
                : Math.max(0, Math.round(100 - high * 15 - medium * 7 - Math.max(0, total - high - medium) * 3));

            securityScore.textContent = score + "/100";
        }
    }

    // 11. Upload ZIP and run the security scan
    startScanButton?.addEventListener("click", async () => {
        const projectNameInput = document.getElementById("scanProjectName");
        const languageInput = document.getElementById("scanLanguage");
        const scanMessage = document.getElementById("scanMessage");
if (!scanProjectFile || scanProjectFile.files.length === 0) {
            alert("Please select a ZIP file first.");
            return;
        }
const file = scanProjectFile.files[0];

        if (!file.name.toLowerCase().endsWith(".zip")) {
            alert("Please select a ZIP file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("project_name", projectNameInput?.value.trim() || "My Project");
        formData.append("language", languageInput?.value || "auto");

        try {
            startScanButton.disabled = true;
            startScanButton.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Scanning...';

            if (scanMessage) {
                scanMessage.textContent = "Uploading project and scanning code...";
            }

            const response = await fetch(
    "http://127.0.0.1:5000/api/upload",
    {
        method: "POST",
        body: formData
    }
);

            const result = await response.json();
            console.log("SCAN RESULT:", result);

            if (!response.ok) {
                throw new Error(
                    result.error ||
                    result.message ||
                    `Scan failed with status ${response.status}.`
                );
            }

            if (!result.project_id || !result.scan_result) {
                throw new Error("The backend response did not contain scan results.");
            }

            latestScanResult = result.scan_result;

            displayVulnerabilities(latestScanResult);
            updateDashboard(latestScanResult);

            if (scanMessage) {
                scanMessage.textContent =
                    `Scan completed! ${Number(latestScanResult.total_issues) || 0} issues detected.`;
            }

            console.log("Project scan response:", result);

            openPage("vulnerabilities");

        } catch (error) {
            console.error("Scan error:", error);

            if (scanMessage) {
                scanMessage.textContent = "Error: " + error.message;
            }

            alert(
                "Scan failed: " +
                error.message +
                "\n\nMake sure the Python Flask backend is running."
            );

        } finally {
            startScanButton.disabled = false;
            startScanButton.innerHTML =
                '<i class="fa-solid fa-shield-halved"></i> Prepare Scan';
        }
    });

    // 12. Mobile sidebar toggle
    const menuButton = document.getElementById("menuButton");
    const sidebar = document.getElementById("sidebar");

    menuButton?.addEventListener("click", () => {
        sidebar?.classList.toggle("open");
    });

    // 13. Notification button
    document.getElementById("notificationButton")?.addEventListener("click", () => {
        alert(
            latestScanResult
                ? `Latest scan: ${Number(latestScanResult.total_issues) || 0} issues detected.`
                : "No scan notifications yet. Run a security scan first."
        );
    });
});
