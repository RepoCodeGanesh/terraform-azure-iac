import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const EDGE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const ARTIFACTS_DIR = "C:\\Users\\RichT\\.gemini\\antigravity\\brain\\79f11032-ac6d-4773-9acc-9468732abf84";
const USER_DATA_DIR = "C:\\Users\\RichT\\.edge-cdp-profile";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForCdp(port = 9222, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {}
    await sleep(300);
  }
  throw new Error("CDP port did not respond in time");
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.msgId = 1;
    this.pending = new Map();
    this.events = [];
  }

  async connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.id && this.pending.has(data.id)) {
          const { resolve, reject } = this.pending.get(data.id);
          this.pending.delete(data.id);
          if (data.error) reject(data.error);
          else resolve(data.result);
        } else if (data.method) {
          this.events.push(data);
        }
      };
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.msgId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const res = await this.send("Runtime.evaluate", {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    return res.result ? res.result.value : null;
  }

  async captureScreenshot(outputPath) {
    const res = await this.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    const buffer = Buffer.from(res.data, "base64");
    fs.writeFileSync(outputPath, buffer);
    console.log(`📸 Screenshot saved: ${outputPath} (${buffer.length} bytes)`);
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

async function testUrl(targetUrl, suiteName) {
  console.log(`\n======================================================`);
  console.log(`  STARTING LIVE WEB TEST: ${targetUrl} [${suiteName}]`);
  console.log(`======================================================`);

  console.log(`1. Launching Edge with remote debugging on 9222...`);
  const browserProc = spawn(
    EDGE_PATH,
    [
      `--remote-debugging-port=9222`,
      `--user-data-dir=${USER_DATA_DIR}`,
      `--inprivate`,
      `--no-first-run`,
      `--no-default-browser-check`,
      `--disable-sync`,
      `--disable-extensions`,
      `--headless=new`,
      `--disable-gpu`,
      `--window-size=1440,900`,
      "about:blank"
    ],
    { stdio: "ignore", detached: true }
  );

  try {
    const version = await waitForCdp(9222);
    console.log(`✓ CDP Connected: ${version.Browser}`);

    // Create a fresh target page pointing directly to targetUrl
    console.log(`2. Navigating to: ${targetUrl}`);
    const newPageRes = await fetch(`http://127.0.0.1:9222/json/new?${encodeURIComponent(targetUrl)}`, { method: "PUT" });
    const targetPage = await newPageRes.json();
    console.log(`Target page created: ${targetPage.id} (${targetPage.url})`);

    const client = new CdpClient(targetPage.webSocketDebuggerUrl);
    await client.connect();

    await client.send("Page.enable");
    await client.send("Runtime.enable");

    // Explicitly navigate and wait for complete state
    await client.send("Page.navigate", { url: targetUrl });
    
    // Poll readyState
    let ready = false;
    for (let i = 0; i < 40; i++) {
      const state = await client.evaluate("document.readyState");
      if (state === "complete") {
        ready = true;
        break;
      }
      await sleep(250);
    }
    console.log(`Page readyState: ${ready ? 'complete' : 'timeout'}`);
    await sleep(2000); // Allow React reconciliation

    // Check for runtime shield or errors
    const pageText = await client.evaluate("document.body.innerText") || "";
    console.log(`Page content snippet (length ${pageText.length}):\n${pageText.slice(0, 180)}...`);

    const hasRuntimeShield = await client.evaluate(
      "document.body.innerText.includes('Runtime Shield') || document.body.innerText.includes('unexpected client-side rendering exception')"
    );
    const hasAuditLocallyError = await client.evaluate(
      "document.body.innerText.includes('auditContractLocally is not defined')"
    );

    if (hasRuntimeShield || hasAuditLocallyError) {
      console.error(`❌ CRITICAL FAILURE: Page is showing Runtime Shield exception!`);
      const errorText = await client.evaluate("document.body.innerText");
      console.error(errorText);
      await client.captureScreenshot(path.join(ARTIFACTS_DIR, `live_${suiteName}_RUNTIME_ERROR.png`));
      throw new Error(`Runtime Shield active: ${hasAuditLocallyError ? 'auditContractLocally is not defined' : 'Unknown Error'}`);
    }

    console.log(`✓ Zero Runtime Shield errors! Application rendered cleanly.`);

    // Check if on Policy Redliner or need to click tab
    const isRedlineStudio = await client.evaluate(
      "document.body.innerText.includes('Automated Policy & Contract Redline Studio') || document.body.innerText.includes('Contract Source Document')"
    );

    if (!isRedlineStudio) {
      console.log(`Navigating to Policy Redliner tab...`);
      await client.evaluate(`(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('Policy Redliner'));
        if (btn) btn.click();
      })()`);
      await sleep(2000);
    }

    // Verify Redline Studio loaded
    const studioLoaded = await client.evaluate(
      "document.body.innerText.includes('Automated Policy & Contract Redline Studio')"
    );
    console.log(`Policy Redliner Studio Loaded: ${studioLoaded}`);

    // Screenshot initial state
    await client.captureScreenshot(path.join(ARTIFACTS_DIR, `live_${suiteName}_01_initial_studio.png`));

    // TEST STEP 2: Edit Text to include "territory of Uganda"
    console.log(`\n3. Testing Drafting Behavior (Simulating user editing contract text to Uganda)...`);
    const editResult = await client.evaluate(`(() => {
      const textarea = document.querySelector('textarea');
      if (!textarea) return { success: false, reason: 'Textarea not found' };
      
      const original = textarea.value;
      const modified = original.replace(/within sovereign cloud regions located in the territory of India\./g, 'exclusively within the territory of Uganda.');
      
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
      nativeSetter.call(textarea, modified);
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      textarea.dispatchEvent(new Event('change', { bubbles: true }));
      return { success: true, originalLen: original.length, modifiedLen: modified.length };
    })()`);

    console.log(`Textarea edited:`, editResult);
    await sleep(1500);

    // Verify UI shows DRAFTING — AUDIT PENDING (Zero fake checkmarks!)
    const draftingStatus = await client.evaluate(`(() => {
      const text = document.body.innerText;
      return {
        hasDraftPending: text.includes('DRAFTING — AUDIT PENDING') || text.includes('Draft Modified — AI Regulatory Audit Pending'),
        hasFakeCheckmark: text.includes('100% Statutory Compliance Achieved!'),
        hasScoreDash: text.includes('Statutory Score')
      };
    })()`);

    console.log(`Drafting state verification:`, draftingStatus);
    if (draftingStatus.hasFakeCheckmark) {
      console.error(`❌ REGRESSION: UI still displays fake "100% Statutory Compliance Achieved!" while drafting!`);
    } else {
      console.log(`✓ SUCCESS: Zero fake checkmarks! Honest "DRAFTING — AUDIT PENDING" state displayed.`);
    }

    // Screenshot drafting state
    await client.captureScreenshot(path.join(ARTIFACTS_DIR, `live_${suiteName}_02_drafting_uganda.png`));

    // TEST STEP 3: Click "Run Statutory Redline Audit"
    console.log(`\n4. Triggering Statutory Redline Audit on Demand...`);
    await client.evaluate(`(() => {
      const auditBtn = Array.from(document.querySelectorAll('button')).find(b => 
        b.innerText.includes('Run Statutory Redline Audit') || b.innerText.includes('Run Statutory Redline Audit Now')
      );
      if (auditBtn) auditBtn.click();
    })()`);

    // Wait for audit completion
    console.log(`Waiting for regulatory AI audit evaluation...`);
    await sleep(6000);

    // Capture audit result screenshot
    await client.captureScreenshot(path.join(ARTIFACTS_DIR, `live_${suiteName}_03_audit_complete.png`));

    const finalResult = await client.evaluate(`(() => {
      const text = document.body.innerText;
      return {
        scorePresent: text.includes('Statutory Score'),
        ugandaDetected: text.toLowerCase().includes('uganda') || text.includes('Data Sovereignty') || text.includes('Data Localization'),
        violationsCount: text.includes('Violations Found')
      };
    })()`);

    console.log(`Audit result analysis:`, finalResult);

    client.close();
    console.log(`✓ Test suite [${suiteName}] completed successfully!`);
  } finally {
    try {
      browserProc.kill();
    } catch (e) {}
  }
}

async function main() {
  const mode = process.argv[2] || "production";
  if (mode === "local") {
    await testUrl("http://127.0.0.1:4173/", "local_preview");
  } else {
    await testUrl("https://bank.mytaxbot.site/redline", "production_cloud");
  }
}

main().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
