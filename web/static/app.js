/**
 * Birthday Paradox UI — talks to FastAPI (main.py).
 * Sample:  POST /api/sample
 * Monte:   GET  /stream/monte-carlo?n=...  (SSE)
 */

const groupInput = document.getElementById("group-size");
const sampleBtn = document.getElementById("sample-btn");
const monteBtn = document.getElementById("monte-btn");
const statusEl = document.getElementById("status");
const sampleSection = document.getElementById("sample-result");
const monteSection = document.getElementById("monte-result");
const chipsEl = document.getElementById("birthday-chips");
const matchLine = document.getElementById("match-line");
const progressBar = document.getElementById("progress-bar");
const progressLine = document.getElementById("progress-line");
const probabilityStat = document.getElementById("probability-stat");
const summaryLine = document.getElementById("summary-line");

const simulationCount =
  window.BIRTHDAY_CONFIG?.simulationCount ?? 100_000;

let monteSource = null;

function getGroupSize() {
  return Number.parseInt(groupInput.value, 10);
}

function setBusy(busy, message) {
  sampleBtn.disabled = busy;
  monteBtn.disabled = busy;
  if (message !== undefined) statusEl.textContent = message;
}

function closeMonteStream() {
  if (monteSource) {
    monteSource.close();
    monteSource = null;
  }
}

/** Render each birthday as a pill; highlight duplicates when we know match_text. */
function renderChips(birthdays, matchText) {
  chipsEl.innerHTML = "";
  const matchLabel = matchText ?? null;
  for (const label of birthdays) {
    const span = document.createElement("span");
    span.className = "chip";
    span.textContent = label;
    if (matchLabel && label === matchLabel) {
      span.classList.add("match");
    }
    chipsEl.appendChild(span);
  }
}

function setProgress(completed) {
  const pct = Math.min(100, (completed / simulationCount) * 100);
  progressBar.style.width = `${pct}%`;
}

sampleBtn.addEventListener("click", async () => {
  const n = getGroupSize();
  setBusy(true, "Generating sample…");
  try {
    const res = await fetch("/api/sample", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ num_bdays: n }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail = err.detail;
      throw new Error(
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail.map((d) => d.msg).join(", ")
            : res.statusText,
      );
    }
    const data = await res.json();
    sampleSection.classList.remove("hidden");
    renderChips(data.birthdays, data.match_text);
    matchLine.className = data.has_match
      ? "match-banner has-match"
      : "match-banner no-match";
    matchLine.textContent = data.has_match
      ? `Match found — multiple people share ${data.match_text}.`
      : "No matching birthdays in this sample.";
    statusEl.textContent = "Sample ready.";
  } catch (e) {
    statusEl.textContent = e instanceof Error ? e.message : "Sample failed.";
  } finally {
    setBusy(false);
  }
});

monteBtn.addEventListener("click", () => {
  const n = getGroupSize();
  closeMonteStream();
  monteSection.classList.remove("hidden");
  progressBar.style.width = "0%";
  progressLine.textContent = "Starting…";
  probabilityStat.classList.add("hidden");
  summaryLine.textContent = "";
  setBusy(true, "Running Monte Carlo simulation…");

  monteSource = new EventSource(
    `/stream/monte-carlo?n=${encodeURIComponent(n)}`,
  );

  monteSource.onmessage = (event) => {
    let data;
    try {
      data = JSON.parse(event.data);
    } catch {
      return;
    }
    if (data.type === "progress") {
      setProgress(data.completed);
      progressLine.textContent = `${data.completed.toLocaleString()} of ${simulationCount.toLocaleString()} simulations…`;
    } else if (data.type === "done") {
      setProgress(data.simulation_count);
      progressLine.textContent = `${data.simulation_count.toLocaleString()} simulations complete.`;
      probabilityStat.textContent = `${data.probability}%`;
      probabilityStat.classList.remove("hidden");
      summaryLine.textContent =
        `In ${data.sim_match.toLocaleString()} of those runs, at least two people in a group of ${data.num_bdays} shared a birthday.`;
      closeMonteStream();
      setBusy(false, "Monte Carlo finished.");
    } else if (data.type === "error") {
      statusEl.textContent = data.message;
      closeMonteStream();
      setBusy(false);
    }
  };

  monteSource.onerror = () => {
    closeMonteStream();
    setBusy(false, "Connection lost — try again.");
  };
});

document.querySelectorAll("[data-help-jump]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById("help-heading")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
});
