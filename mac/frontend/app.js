// Use relative URL for deployment, fallback to localhost for development
const API_BASE_URL = window.location.origin + "/api";

const textForm = document.getElementById("text-form");
const fileForm = document.getElementById("file-form");
const resultsCard = document.getElementById("results-card");
const errorCard = document.getElementById("error-card");
const errorMessage = document.getElementById("error-message");

const verdictEl = document.getElementById("result-verdict");
const confidenceEl = document.getElementById("result-confidence");
const highlightsEl = document.getElementById("result-highlights");
const insightsEl = document.getElementById("result-insights");
const metadataEl = document.getElementById("result-metadata");

function toggleLoading(form, isLoading) {
  const button = form.querySelector("button");
  if (!button) return;
  button.disabled = isLoading;
  button.textContent = isLoading ? "Analyzing..." : button.dataset.defaultLabel;
}

function initButtons() {
  [textForm, fileForm].forEach((form) => {
    if (!form) return;
    const button = form.querySelector("button");
    if (button && !button.dataset.defaultLabel) {
      button.dataset.defaultLabel = button.textContent;
    }
  });
}

function renderResult(data) {
  resultsCard.hidden = false;
  verdictEl.textContent = `Verdict: ${data.verdict.toUpperCase()}`;
  confidenceEl.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;

  const highlightItems = (data.highlights || [])
    .map((item) => `<li>${item}</li>`)
    .join("");
  highlightsEl.innerHTML = highlightItems
    ? `<h3>Highlights</h3><ul>${highlightItems}</ul>`
    : "";

  const insightItems = (data.insights || [])
    .map(
      (insight) =>
        `<li><strong>${insight.name}</strong>: ${insight.value}${
          insight.weight != null ? ` (weight ${insight.weight})` : ""
        }${insight.description ? ` — ${insight.description}` : ""}</li>`,
    )
    .join("");
  insightsEl.innerHTML = insightItems
    ? `<h3>Insights</h3><ul>${insightItems}</ul>`
    : "";

  const metadata = data.metadata || {};
  const metadataEntries = Object.entries(metadata)
    .filter(([, value]) => {
      if (Array.isArray(value)) return value.length > 0;
      return Boolean(value);
    })
    .map(
      ([key, value]) =>
        `<li><strong>${key.replace(/_/g, " ")}:</strong> ${
          Array.isArray(value) ? value.join(", ") : value
        }</li>`,
    )
    .join("");
  metadataEl.innerHTML = metadataEntries
    ? `<h3>Message metadata</h3><ul>${metadataEntries}</ul>`
    : "";
}

function renderError(error) {
  errorCard.hidden = false;
  errorMessage.textContent = error;
}

function resetFeedback() {
  resultsCard.hidden = true;
  errorCard.hidden = true;
  verdictEl.textContent = "";
  confidenceEl.textContent = "";
  highlightsEl.innerHTML = "";
  insightsEl.innerHTML = "";
  metadataEl.innerHTML = "";
  errorMessage.textContent = "";
}

async function submitTextForm(event) {
  event.preventDefault();
  resetFeedback();
  toggleLoading(textForm, true);

  const payload = {
    subject: document.getElementById("subject").value || null,
    headers: document.getElementById("headers").value || null,
    body: document.getElementById("body").value,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/text`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "Unexpected server error.");
    }

    const data = await response.json();
    renderResult(data);
  } catch (error) {
    renderError(error.message);
  } finally {
    toggleLoading(textForm, false);
  }
}

async function submitFileForm(event) {
  event.preventDefault();
  resetFeedback();
  toggleLoading(fileForm, true);

  const formData = new FormData();
  const fileInput = document.getElementById("file");

  if (!fileInput.files.length) {
    renderError("Please select an .eml file before submitting.");
    toggleLoading(fileForm, false);
    return;
  }

  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/file`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "Unexpected server error.");
    }

    const data = await response.json();
    renderResult(data);
  } catch (error) {
    renderError(error.message);
  } finally {
    toggleLoading(fileForm, false);
  }
}

initButtons();

if (textForm) {
  textForm.addEventListener("submit", submitTextForm);
}

if (fileForm) {
  fileForm.addEventListener("submit", submitFileForm);
}

