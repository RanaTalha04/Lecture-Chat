const messages = document.querySelector('#messages');
const form = document.querySelector('#chat-form');
const question = document.querySelector('#question');
const send = document.querySelector('#send');
const status = document.querySelector('#status');

function message(text, kind) {
  const item = document.createElement('article');
  item.className = `message ${kind}`;
  item.textContent = text;
  messages.append(item);
  messages.scrollTop = messages.scrollHeight;
  return item;
}

function addSources(sources) {
  const details = document.createElement('details');
  details.className = 'sources'; details.open = true;
  const summary = document.createElement('summary');
  summary.textContent = `Sources (${sources.length})`; details.append(summary);
  sources.forEach((source) => {
    const item = document.createElement('div'); item.className = 'source';
    item.textContent = `${source.source}, page ${source.page} · ${Math.round(source.relevance * 100)}% match — ${source.text}`;
    details.append(item);
  });
  messages.append(details); messages.scrollTop = messages.scrollHeight;
}

async function refreshStatus() {
  const response = await fetch('/api/health'); const data = await response.json();
  status.textContent = `${data.documents} PDFs · ${data.chunks} indexed passages`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault(); const text = question.value.trim(); if (!text) return;
  message(text, 'user'); question.value = ''; send.disabled = true; send.textContent = 'Searching…';
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: text}) });
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Request failed');
    message(data.answer, 'assistant'); addSources(data.sources);
    refreshStatus();
  } catch (error) { message(`Sorry, ${error.message}`, 'assistant'); }
  finally { send.disabled = false; send.textContent = 'Ask'; question.focus(); }
});

document.querySelector('#reindex').addEventListener('click', async (event) => {
  event.currentTarget.disabled = true; status.textContent = 'Building index…';
  try { const response = await fetch('/api/reindex', {method: 'POST'}); const data = await response.json(); if (!response.ok) throw new Error(data.detail); await refreshStatus(); }
  catch (error) { status.textContent = error.message; } finally { event.currentTarget.disabled = false; }
});

document.querySelector('#upload-form').addEventListener('submit', async (event) => {
  event.preventDefault(); const file = document.querySelector('#file').files[0]; if (!file) return;
  status.textContent = 'Uploading…'; const body = new FormData(); body.append('file', file);
  const response = await fetch('/api/documents', {method: 'POST', body}); const data = await response.json();
  status.textContent = response.ok ? `${data.message} Then rebuild the index.` : data.detail;
});
refreshStatus().catch(() => { status.textContent = 'Could not reach the API.'; });
