// TaxCite's page (G5). ADR-13: nothing the API returns is ever parsed as HTML. Every string reaches the page through
// textContent, nothing is rendered as a link, and badges come only from the answer's structured fields.
"use strict";

const $ = (id) => document.getElementById(id);

function el(tag, text, cls) {
  const e = document.createElement(tag);
  if (text != null) e.textContent = String(text);
  if (cls) e.className = cls;
  return e;
}

const STAGES = {
  decomposing: "Planning the question",
  retrieving: "Searching the sources",
  checking_sufficiency: "Checking the sources are enough",
  synthesizing: "Writing the answer",
  verifying: "Checking every sentence against its source",
  answer: "Done",
  error: "Failed",
};

function api(path, options = {}) {
  const headers = { ...(options.headers || {}), Authorization: `Bearer ${$("key").value.trim()}` };
  return fetch(path, { ...options, headers });
}

async function detail(response) {
  try {
    return (await response.json()).detail || response.statusText;
  } catch {
    return response.statusText;
  }
}

// Server-sent events through fetch: EventSource can't send the Authorization header.
async function* events(path) {
  const response = await api(path);
  if (!response.ok) throw new Error(await detail(response));
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) return;
    buffer += value;
    let end;
    while ((end = buffer.indexOf("\n\n")) >= 0) {
      const fields = {};
      for (const line of buffer.slice(0, end).split("\n")) {
        const at = line.indexOf(": ");
        if (at > 0) fields[line.slice(0, at)] = line.slice(at + 2);
      }
      buffer = buffer.slice(end + 2);
      if (fields.event) yield [fields.event, JSON.parse(fields.data || "{}")];
    }
  }
}

function showAnswer(a) {
  const box = $("answer");
  for (const line of String(a.text || "").split("\n")) if (line.trim()) box.append(el("p", line));
  const cites = [...(a.citations || []), ...(a.derived_citations || [])];
  if (cites.length) {
    const list = el("ul");
    for (const c of cites) {
      const item = el("li");
      item.append(el("span", c, "citation"));
      const authority = (a.authorities || {})[c];
      if (authority && authority.label) item.append(el("span", authority.label, "badge"));
      const opinion = Object.keys(a.treatments || {}).find((o) => c.startsWith(o));
      const treated = opinion && a.treatments[opinion];
      if (treated && treated.status && treated.status !== "none") {
        item.append(el("span", treated.by ? `${treated.status} by ${treated.by}` : treated.status, "treatment"));
      }
      list.append(item);
    }
    box.append(el("h2", "Sources"), list);
  }
  const notes = [];
  if (a.hidden_sentences) notes.push(`${a.hidden_sentences} sentence(s) hidden: they failed verification`);
  if (typeof a.cost_usd === "number") notes.push(`$${a.cost_usd.toFixed(4)}`);
  if (notes.length) box.append(el("p", notes.join(" · "), "muted"));
}

async function ask(event) {
  event.preventDefault();
  const stages = $("stages");
  const box = $("answer");
  stages.replaceChildren();
  box.replaceChildren();
  try {
    const response = await api("/queries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: $("question").value }),
    });
    if (!response.ok) throw new Error(await detail(response));
    const job = await response.json();
    for await (const [name, data] of events(`/queries/${encodeURIComponent(job.id)}/events`)) {
      stages.append(el("li", STAGES[name] || name));
      if (name === "answer") showAnswer(data);
      if (name === "error") box.append(el("p", `The pipeline failed (${data.type}).`, "error"));
    }
  } catch (e) {
    box.append(el("p", e.message, "error"));
  }
}

async function listDocuments() {
  const list = $("documents");
  list.replaceChildren();
  const response = await api("/documents");
  if (!response.ok) return list.append(el("li", await detail(response), "error"));
  for (const d of (await response.json()).documents) {
    const item = el("li");
    item.append(el("span", d.name), el("small", ` · ${d.pages} page(s)`));
    const failed = d.failed_pages || [];
    if (failed.length) item.append(el("small", ` · ${failed.length} page(s) excluded: extraction failed`, "error"));
    const remove = el("button", "Delete");
    remove.type = "button";
    remove.addEventListener("click", async () => {
      await api(`/documents/${encodeURIComponent(d.id)}`, { method: "DELETE" });
      listDocuments();
    });
    item.append(remove);
    list.append(item);
  }
}

async function upload(event) {
  event.preventDefault();
  const file = $("file").files[0];
  if (!file) return;
  const body = new FormData();
  body.append("file", file);
  const response = await api("/documents", { method: "POST", body });
  $("upload-status").textContent = response.ok ? "Uploaded." : await detail(response);
  listDocuments();
}

$("ask").addEventListener("submit", ask);
$("upload").addEventListener("submit", upload);
$("refresh").addEventListener("click", listDocuments);
$("key").addEventListener("change", listDocuments);
