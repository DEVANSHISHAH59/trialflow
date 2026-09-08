/* TrialFlow dashboard. Vanilla JS, renders web/data/trialflow.json.
   All figures are computed by the Python engine in /engine; this file only
   presents them. */

'use strict';

const PALETTE = ['#0f5077', '#2f8f83', '#a86611', '#b3261e', '#6b7f8a', '#7fc9bf'];
const RAG = { green: '#1a7f47', amber: '#a86611', red: '#b3261e' };
const PLOTLY_CFG = { displayModeBar: false, responsive: true };
const BASE_LAYOUT = {
  font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size: 12, color: '#17242c' },
  margin: { l: 48, r: 18, t: 14, b: 40 },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  colorway: PALETTE,
  xaxis: { gridcolor: '#eef2f4', zerolinecolor: '#e0e6ea' },
  yaxis: { gridcolor: '#eef2f4', zerolinecolor: '#e0e6ea' },
};

const state = { data: null, view: 'overview', sitesSort: { key: 'risk_score', dir: -1 } };
const $app = document.getElementById('app');

init();

async function init() {
  try {
    const res = await fetch('data/trialflow.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    state.data = await res.json();
  } catch (err) {
    $app.innerHTML = `<div class="card"><h3>Could not load trial data</h3><p class="muted">${err.message}. Run <code>python engine/build.py</code> to regenerate <code>web/data/trialflow.json</code>.</p></div>`;
    return;
  }
  renderChrome();
  document.getElementById('tabs').addEventListener('click', (e) => {
    const btn = e.target.closest('.tab');
    if (!btn) return;
    setView(btn.dataset.view);
  });
  setView('overview');
}

function renderChrome() {
  const s = state.data.overview.study;
  document.getElementById('study-meta').innerHTML =
    `<strong>${s.studyid}</strong> &middot; ${s.phase} &middot; ${s.indication}<br>` +
    `Data cut ${s.data_cut} &middot; target n=${s.target_enrollment}`;
  document.getElementById('footer-meta').textContent =
    `Generated ${state.data.generated_utc} from synthetic data. ${state.data.disclaimer}`;
}

function setView(view) {
  state.view = view;
  document.querySelectorAll('.tab').forEach((t) => {
    t.setAttribute('aria-current', String(t.dataset.view === view));
  });
  window.scrollTo({ top: 0, behavior: 'instant' });
  VIEWS[view]();
}

/* ---------------- helpers ---------------- */

function frag(html) {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content;
}
function mount(html) {
  $app.innerHTML = '';
  $app.appendChild(frag(`<div class="view">${html}</div>`));
}
function esc(v) {
  return String(v ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function fmt(n) {
  return typeof n === 'number' ? n.toLocaleString('en-IE', { maximumFractionDigits: 1 }) : esc(n);
}
function bandFromValue(v, good = 80, ok = 60) {
  return v >= good ? 'green' : v >= ok ? 'amber' : 'red';
}
function kpiCard(k) {
  return `<div class="card kpi"><span class="kpi-label">${esc(k.label)}</span>` +
    `<span class="kpi-value">${esc(k.value)}</span><span class="kpi-sub">${esc(k.sub)}</span></div>`;
}
function plot(id, traces, layout) {
  const node = document.getElementById(id);
  if (!node || !window.Plotly) return;
  const merged = Object.assign({}, BASE_LAYOUT, layout);
  merged.xaxis = Object.assign({}, BASE_LAYOUT.xaxis, (layout || {}).xaxis);
  merged.yaxis = Object.assign({}, BASE_LAYOUT.yaxis, (layout || {}).yaxis);
  Plotly.newPlot(node, traces, merged, PLOTLY_CFG);
}
function tableHTML(columns, rows, opts = {}) {
  const head = columns.map((c) =>
    `<th class="${c.num ? 'num' : ''} ${opts.sortKey === undefined && !opts.sort ? 'no-sort' : ''}" data-key="${c.key}">${esc(c.label)}</th>`
  ).join('');
  const body = rows.map((r) => {
    const tds = columns.map((c) => {
      const raw = c.get ? c.get(r) : r[c.key];
      return `<td class="${c.num ? 'num' : ''}">${c.html ? raw : esc(raw)}</td>`;
    }).join('');
    return `<tr class="${opts.rowClass ? opts.rowClass(r) : ''}" ${opts.rowData ? `data-row="${esc(opts.rowData(r))}"` : ''}>${tds}</tr>`;
  }).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

/* ---------------- views ---------------- */

const VIEWS = {
  overview() {
    const o = state.data.overview;
    const rec = state.data.recruitment;
    const countries = state.data.enrollment_by_country;
    const health = o.health_components || o.health_components;
    const comps = (o.health_components || []).map((c) => {
      const cls = c.rag;
      return `<div class="component-row"><span class="c-name">${esc(c.name.replace(/_/g, ' '))}</span>` +
        `<span class="c-bar"><span class="c-fill ${cls}" style="width:${c.value}%"></span></span>` +
        `<span class="c-val">${fmt(c.value)}</span></div>`;
    }).join('');

    mount(`
      <h2 class="view-head">Executive Trial Overview</h2>
      <p class="view-sub">Study ${esc(o.study.studyid)} &mdash; ${esc(o.study.title)}. One place for the sponsor and clinical operations lead to answer: is this trial healthy?</p>

      <div class="card pad-lg mt-16">
        <div class="health-wrap">
          <div class="health-score">
            <div><span class="num">${o.trial_health}</span><span class="den"> / 100</span></div>
            <div class="pill ${bandFromValue(o.trial_health, 80, 65)}">${esc(o.trial_status)}</div>
            <div class="kpi-sub mt-16">Data quality ${fmt(o.data_quality_score)}% &middot; ${fmt(o.records_to_review)} records to review</div>
          </div>
          <div>
            <h3 style="margin-top:0">Trial health drivers</h3>
            ${comps}
          </div>
        </div>
      </div>

      <div class="grid cols-4 mt-16">${o.kpis.map(kpiCard).join('')}</div>

      <div class="grid cols-2 mt-16">
        <div class="card"><h3>Cumulative recruitment vs plan</h3><div id="chart-rec" class="chart"></div></div>
        <div class="card"><h3>Enrolment by country</h3><div id="chart-country" class="chart"></div></div>
      </div>
    `);

    plot('chart-rec', [
      { x: rec.months, y: rec.plan, name: 'Plan', mode: 'lines', line: { dash: 'dot', color: '#9aa9b2', width: 2 } },
      { x: rec.months, y: rec.actual, name: 'Actual', mode: 'lines', fill: 'tozeroy',
        line: { color: PALETTE[0], width: 2.5 }, fillcolor: 'rgba(15,80,119,.10)' },
    ], { legend: { orientation: 'h', y: 1.12 }, yaxis: { title: 'subjects' } });

    plot('chart-country', [{
      type: 'bar', orientation: 'h',
      x: countries.map((c) => c.enrolled).reverse(),
      y: countries.map((c) => c.country).reverse(),
      marker: { color: PALETTE[1] },
    }], { margin: { l: 110, r: 18, t: 10, b: 36 }, xaxis: { title: 'subjects enrolled' } });
  },

  sites() {
    const rows = state.data.sites.slice();
    const s = state.sitesSort;
    rows.sort((a, b) => (a[s.key] > b[s.key] ? 1 : -1) * s.dir);
    const columns = [
      { key: 'site_id', label: 'Site', get: (r) => `Site ${r.site_id}` },
      { key: 'country', label: 'Country' },
      { key: 'monitor', label: 'CRA' },
      { key: 'enrolled', label: 'Enrolled', num: true },
      { key: 'target_enrollment', label: 'Target', num: true },
      { key: 'recruitment_pct', label: 'Recruit %', num: true, get: (r) => fmt(r.recruitment_pct) },
      { key: 'form_completeness', label: 'Data %', num: true, get: (r) => fmt(r.form_completeness) },
      { key: 'open_queries', label: 'Open Q', num: true },
      { key: 'deviations', label: 'Devs', num: true },
      { key: 'risk_score', label: 'Risk', num: true, html: true,
        get: (r) => `<span class="badge ${r.risk_band}">${fmt(r.risk_score)}</span>` },
    ];
    const topRisk = state.data.sites.slice().sort((a, b) => b.risk_score - a.risk_score).slice(0, 10);

    mount(`
      <h2 class="view-head">Site Performance</h2>
      <p class="view-sub">CTMS-style league table. Site risk is a 0&ndash;100 score (higher is worse) combining recruitment gap, open-query rate, protocol-deviation rate and data incompleteness. Click a row for the drivers and the recommended action.</p>

      <div class="grid cols-3 mt-16">
        <div class="card kpi"><span class="kpi-label">Sites activated</span><span class="kpi-value">${state.data.sites.length}</span><span class="kpi-sub">of ${state.data.overview.study.planned_sites} planned</span></div>
        <div class="card kpi"><span class="kpi-label">High risk</span><span class="kpi-value" style="color:${RAG.red}">${state.data.sites.filter((x) => x.risk_band === 'red').length}</span><span class="kpi-sub">need intervention</span></div>
        <div class="card kpi"><span class="kpi-label">Watch</span><span class="kpi-value" style="color:${RAG.amber}">${state.data.sites.filter((x) => x.risk_band === 'amber').length}</span><span class="kpi-sub">increased monitoring</span></div>
      </div>

      <div class="card mt-16"><h3>Top 10 sites by risk score</h3><div id="chart-siterisk" class="chart"></div></div>

      <div class="card mt-16">
        <h3>All activated sites</h3>
        ${tableHTML(columns, rows, { sort: true, rowClass: () => 'clickable', rowData: (r) => r.site_id })}
        <div id="site-detail"></div>
      </div>
    `);

    plot('chart-siterisk', [{
      type: 'bar', orientation: 'h',
      x: topRisk.map((r) => r.risk_score).reverse(),
      y: topRisk.map((r) => `Site ${r.site_id}`).reverse(),
      marker: { color: topRisk.map((r) => RAG[r.risk_band]).reverse() },
      text: topRisk.map((r) => r.country).reverse(), textposition: 'auto',
    }], { margin: { l: 70, r: 18, t: 10, b: 36 }, xaxis: { title: 'risk score', range: [0, 100] } });

    $app.querySelectorAll('thead th').forEach((th) => th.addEventListener('click', () => {
      const key = th.dataset.key;
      if (!key) return;
      state.sitesSort = { key, dir: state.sitesSort.key === key ? -state.sitesSort.dir : 1 };
      VIEWS.sites();
    }));
    $app.querySelectorAll('tbody tr').forEach((tr) => tr.addEventListener('click', () => {
      showSiteDetail(Number(tr.dataset.row));
    }));
  },

  journey() {
    const p = state.data.patient_journey;
    const vcols = [
      { key: 'visit', label: 'Visit' },
      { key: 'scheduled_date', label: 'Scheduled' },
      { key: 'actual_date', label: 'Actual', get: (r) => r.actual_date || '—' },
      { key: 'status', label: 'Status', html: true, get: (r) => {
        const b = r.status === 'Done' ? 'green' : r.status === 'Missed' ? 'red' : 'grey';
        return `<span class="badge ${b}">${esc(r.status)}</span>`;
      } },
      { key: 'missing_forms', label: 'Missing / incomplete forms', get: (r) => r.missing_forms.length ? r.missing_forms.join(', ') : '—' },
    ];
    mount(`
      <h2 class="view-head">Patient Journey &mdash; EDC data-quality view</h2>
      <p class="view-sub">A simulated EDC completeness layer for one subject: expected visits, what was captured, and which required assessments are still open. This shows the clinical data workflow, not a real EDC system.</p>

      <div class="grid cols-4 mt-16">
        <div class="card kpi"><span class="kpi-label">Subject</span><span class="kpi-value" style="font-size:1.15rem">${esc(p.usubjid)}</span><span class="kpi-sub">Site ${p.site_id} &middot; ${esc(p.country)}</span></div>
        <div class="card kpi"><span class="kpi-label">Arm</span><span class="kpi-value" style="font-size:1.15rem">${esc(p.arm)}</span><span class="kpi-sub">${esc(p.sex)} &middot; age ${p.age}</span></div>
        <div class="card kpi"><span class="kpi-label">Status</span><span class="kpi-value" style="font-size:1.15rem">${esc(p.status)}</span><span class="kpi-sub">disposition</span></div>
        <div class="card kpi"><span class="kpi-label">Data completeness</span><span class="kpi-value" style="color:${RAG[bandFromValue(p.data_completeness, 95, 85)]}">${fmt(p.data_completeness)}%</span><span class="kpi-sub">required CRFs entered</span></div>
      </div>

      <div class="card mt-16"><h3>Visit schedule and capture</h3>${tableHTML(vcols, p.visits)}</div>

      <div class="card mt-16">
        <h3>Open data items for this subject</h3>
        ${p.open_issues.length
          ? `<ul>${p.open_issues.map((i) => `<li>${esc(i)}</li>`).join('')}</ul>`
          : '<p class="muted">No open data items.</p>'}
        <p class="note">Each open item becomes a data query routed to the site for resolution.</p>
      </div>
    `);
  },

  quality() {
    const q = state.data.data_quality;
    const fcols = [
      { key: 'rule', label: 'Rule' },
      { key: 'severity', label: 'Severity', html: true, get: (r) => {
        const b = r.severity === 'Major' ? 'red' : r.severity === 'Moderate' ? 'amber' : 'grey';
        return `<span class="badge ${b}">${esc(r.severity)}</span>`;
      } },
      { key: 'usubjid', label: 'Subject' },
      { key: 'site_id', label: 'Site', num: true },
      { key: 'location', label: 'Location' },
      { key: 'detail', label: 'Detail' },
    ];
    mount(`
      <h2 class="view-head">Clinical Data Quality Engine</h2>
      <p class="view-sub">Five deterministic checks run over the raw EDC tables: missing required data, impossible dates, out-of-range values, duplicate records and cross-form inconsistencies. Every finding is traceable to a subject and a location.</p>

      <div class="grid cols-3 mt-16">
        <div class="card kpi"><span class="kpi-label">Data quality score</span><span class="kpi-value" style="color:${RAG[bandFromValue(q.score, 97, 93)]}">${fmt(q.score)}%</span><span class="kpi-sub">of ${fmt(q.evaluable_points)} evaluable points</span></div>
        <div class="card kpi"><span class="kpi-label">Records to review</span><span class="kpi-value">${fmt(q.records_to_review)}</span><span class="kpi-sub">raised as findings</span></div>
        <div class="card kpi"><span class="kpi-label">Checks</span><span class="kpi-value">${q.by_rule.length}</span><span class="kpi-sub">rule types active</span></div>
      </div>

      <div class="grid cols-2 mt-16">
        <div class="card"><h3>Findings by rule</h3><div id="chart-dqrule" class="chart"></div></div>
        <div class="card"><h3>Findings by site (top 12)</h3><div id="chart-dqsite" class="chart"></div></div>
      </div>

      <div class="card mt-16"><h3>Sample findings</h3>${tableHTML(fcols, q.sample_findings)}
        <p class="note">Showing ${q.sample_findings.length} of ${fmt(q.records_to_review)}.</p></div>
    `);

    plot('chart-dqrule', [{
      type: 'bar',
      x: q.by_rule.map((r) => r.rule),
      y: q.by_rule.map((r) => r.count),
      marker: { color: PALETTE[0] },
    }], { margin: { l: 46, r: 12, t: 10, b: 90 }, xaxis: { type: 'category', tickangle: -25 }, yaxis: { title: 'findings' } });

    const bySite = q.by_site.slice().sort((a, b) => b.findings - a.findings).slice(0, 12);
    plot('chart-dqsite', [{
      type: 'bar', orientation: 'h',
      x: bySite.map((r) => r.findings).reverse(),
      y: bySite.map((r) => `Site ${r.site_id}`).reverse(),
      marker: { color: PALETTE[2] },
    }], { margin: { l: 70, r: 12, t: 10, b: 36 }, xaxis: { title: 'findings' } });
  },

  deviations() {
    const d = state.data.deviations;
    const dcols = [
      { key: 'usubjid', label: 'Subject' },
      { key: 'site_id', label: 'Site', num: true },
      { key: 'visit', label: 'Visit' },
      { key: 'dvterm', label: 'Deviation' },
      { key: 'dvcat', label: 'Category', html: true, get: (r) => {
        const b = r.dvcat === 'Major' ? 'red' : r.dvcat === 'Moderate' ? 'amber' : 'grey';
        return `<span class="badge ${b}">${esc(r.dvcat)}</span>`;
      } },
      { key: 'dvdtc', label: 'Date' },
      { key: 'dvstatus', label: 'Status', html: true, get: (r) =>
        `<span class="badge ${r.dvstatus === 'Open' ? 'amber' : 'grey'}">${esc(r.dvstatus)}</span>` },
    ];
    mount(`
      <h2 class="view-head">Protocol Deviation Engine</h2>
      <p class="view-sub">Out-of-window visits are detected directly from the visit data against the protocol schedule; other deviation types are logged with a category, status and corrective action so they can be trended by site.</p>

      <div class="grid cols-4 mt-16">
        <div class="card kpi"><span class="kpi-label">Total deviations</span><span class="kpi-value">${d.total}</span><span class="kpi-sub">across all sites</span></div>
        ${d.by_category.map((c) => `<div class="card kpi"><span class="kpi-label">${esc(c.category)}</span><span class="kpi-value">${c.count}</span><span class="kpi-sub">${fmt(100 * c.count / d.total)}%</span></div>`).join('')}
      </div>

      <div class="grid cols-2 mt-16">
        <div class="card"><h3>By type</h3><div id="chart-dvtype" class="chart"></div></div>
        <div class="card"><h3>By site (top 10)</h3><div id="chart-dvsite" class="chart"></div></div>
      </div>

      <div class="card mt-16"><h3>Deviation log</h3>${tableHTML(dcols, d.records)}</div>
    `);

    plot('chart-dvtype', [{
      type: 'bar', orientation: 'h',
      x: d.by_type.map((r) => r.count).reverse(),
      y: d.by_type.map((r) => r.type.length > 34 ? r.type.slice(0, 33) + '…' : r.type).reverse(),
      marker: { color: PALETTE[0] },
    }], { margin: { l: 210, r: 12, t: 10, b: 36 }, xaxis: { title: 'count' } });

    plot('chart-dvsite', [{
      type: 'bar',
      x: d.by_site.map((r) => `Site ${r.site_id}`),
      y: d.by_site.map((r) => r.count),
      marker: { color: PALETTE[3] },
    }], { margin: { l: 40, r: 12, t: 10, b: 60 }, xaxis: { type: 'category', tickangle: -30 }, yaxis: { title: 'deviations' } });
  },

  ae() {
    const a = state.data.adverse_events;
    const arms = a.by_arm.map((r) => r.arm);
    const sevs = ['Mild', 'Moderate', 'Severe'];
    const scols = [
      { key: 'usubjid', label: 'Subject' },
      { key: 'site_id', label: 'Site', num: true },
      { key: 'aeterm', label: 'Event' },
      { key: 'aesev', label: 'Severity', html: true, get: (r) => {
        const b = r.aesev === 'Severe' ? 'red' : r.aesev === 'Moderate' ? 'amber' : 'grey';
        return `<span class="badge ${b}">${esc(r.aesev)}</span>`;
      } },
      { key: 'aerel', label: 'Causality' },
      { key: 'arm', label: 'Arm' },
      { key: 'aeout', label: 'Outcome' },
    ];
    mount(`
      <h2 class="view-head">Adverse Event Dashboard</h2>
      <p class="view-sub">Recorded adverse events by severity, system organ class and treatment arm, with the serious events listed. This is a summary of recorded data for operational oversight, not a medical safety assessment.</p>

      <div class="grid cols-4 mt-16">
        <div class="card kpi"><span class="kpi-label">AE reports</span><span class="kpi-value">${a.by_severity.reduce((s, x) => s + x.count, 0)}</span><span class="kpi-sub">all subjects</span></div>
        ${a.by_severity.map((c) => `<div class="card kpi"><span class="kpi-label">${esc(c.severity)}</span><span class="kpi-value">${c.count}</span></div>`).join('')}
      </div>

      <div class="grid cols-2 mt-16">
        <div class="card"><h3>By system organ class</h3><div id="chart-aesoc" class="chart"></div></div>
        <div class="card"><h3>Severity by arm</h3><div id="chart-aearm" class="chart"></div></div>
      </div>

      <div class="card mt-16"><h3>Serious adverse events</h3>${tableHTML(scols, a.serious)}</div>
    `);

    plot('chart-aesoc', [{
      type: 'bar', orientation: 'h',
      x: a.by_soc.map((r) => r.count).reverse(),
      y: a.by_soc.map((r) => r.soc.length > 28 ? r.soc.slice(0, 27) + '…' : r.soc).reverse(),
      marker: { color: PALETTE[1] },
    }], { margin: { l: 190, r: 12, t: 10, b: 36 }, xaxis: { title: 'events' } });

    plot('chart-aearm', sevs.map((sev, i) => ({
      type: 'bar', name: sev,
      x: arms, y: a.by_arm.map((r) => r[sev] || 0),
      marker: { color: [RAG.green, RAG.amber, RAG.red][i] },
    })), { barmode: 'group', legend: { orientation: 'h', y: 1.15 },
      xaxis: { type: 'category' }, yaxis: { title: 'events' } });
  },

  sdtm() {
    const sdtm = state.data.sdtm;
    const stages = ['EDC data', 'Data-quality checks', 'SDTM mapping', 'Clinical data warehouse', 'Trial analytics', 'Product dashboard', 'Risk / action'];
    const pipe = stages.map((s, i) =>
      `<div class="stage"><strong>${i + 1}</strong>${esc(s)}</div>` +
      (i < stages.length - 1 ? '<span class="arrow">&rarr;</span>' : '')
    ).join('');

    const domainCards = Object.entries(sdtm).map(([name, dom]) => {
      const cols = dom.columns.map((c) => `<code>${esc(c)}</code>`).join(' ');
      const sampleCols = dom.columns.slice(0, 7).map((c) => ({ key: c, label: c }));
      return `<div class="card">
        <h3>${esc(name)} &middot; <span class="muted">${fmt(dom.rows)} rows</span></h3>
        <p style="font-size:.82rem;margin:0 0 10px">${cols}</p>
        ${tableHTML(sampleCols, dom.sample)}
      </div>`;
    }).join('');

    mount(`
      <h2 class="view-head">Simplified CDISC SDTM Mapping</h2>
      <p class="view-sub">The raw EDC tables are mapped into SDTM-style domains (DM, AE, VS, SV) using SDTM Implementation Guide variable names, so downstream analysis and submission-style tooling read a familiar structure. This is a demonstration model, not a validated SDTM implementation.</p>

      <div class="card mt-16"><h3>EDC to SDTM to analytics pipeline</h3><div class="pipeline">${pipe}</div></div>

      <div class="grid cols-2 mt-16">${domainCards}</div>

      <div class="card mt-16"><h3>SQL views in the warehouse</h3>
        ${tableHTML(
          [{ key: 'file', label: 'SQL file' }, { key: 'rows', label: 'Rows', num: true }, { key: 'columns', label: 'Columns', get: (r) => r.columns.join(', ') }],
          state.data.sql_catalog || []
        )}
      </div>
    `);
  },

  copilot() {
    const qa = state.data.copilot;
    mount(`
      <h2 class="view-head">Clinical Trial Risk Copilot</h2>
      <p class="view-sub">Ask a question about trial execution. Answers are generated deterministically from the metrics computed by the engine. The copilot summarises predefined analytics and rules; it does not diagnose patients or make medical or treatment recommendations.</p>

      <div class="grid cols-2 mt-16">
        <div class="card"><h3>Questions</h3><div class="copilot-qs" id="copilot-qs">
          ${qa.map((x, i) => `<button class="copilot-q" data-i="${i}" aria-pressed="${i === 0}">${esc(x.q)}</button>`).join('')}
        </div></div>
        <div class="card"><h3>Answer</h3><div id="copilot-answer" class="copilot-answer"></div></div>
      </div>
    `);
    const render = (i) => {
      const x = qa[i];
      let detail = '';
      if (Array.isArray(x.detail) && x.detail.length) {
        if (x.detail[0].site) {
          detail = x.detail.map((d) =>
            `<div class="detail-panel"><h4><span class="dot ${d.band}"></span>${esc(d.site)} &middot; risk ${fmt(d.score)}</h4>` +
            (d.reasons && d.reasons.length ? `<ul>${d.reasons.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>` : '') +
            `<div class="action"><strong>Recommended action:</strong> ${esc(d.action)}</div></div>`
          ).join('');
        } else {
          const keys = Object.keys(x.detail[0]);
          detail = tableHTML(keys.map((k) => ({ key: k, label: k.replace(/_/g, ' ') })), x.detail);
        }
      }
      document.getElementById('copilot-answer').innerHTML =
        `<p class="summary">${esc(x.summary)}</p>${detail}<p class="note mt-16">Deterministic answer over computed metrics. No LLM. No medical advice.</p>`;
    };
    document.getElementById('copilot-qs').addEventListener('click', (e) => {
      const btn = e.target.closest('.copilot-q');
      if (!btn) return;
      document.querySelectorAll('.copilot-q').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
      render(Number(btn.dataset.i));
    });
    render(0);
  },
};

function showSiteDetail(siteId) {
  const s = state.data.sites.find((x) => x.site_id === siteId);
  if (!s) return;
  const panel = document.getElementById('site-detail');
  panel.innerHTML = `
    <div class="detail-panel">
      <h4><span class="dot ${s.risk_band}"></span>Site ${s.site_id} &middot; ${esc(s.country)} &middot; PI ${esc(s.pi_name)} &middot; risk score ${fmt(s.risk_score)}</h4>
      <div class="muted" style="font-size:.85rem">Enrolled ${s.enrolled} of ${s.target_enrollment} (${fmt(s.recruitment_pct)}%) &middot; data completeness ${fmt(s.form_completeness)}% &middot; ${s.open_queries} open queries &middot; ${s.deviations} deviations</div>
      ${s.risk_reasons && s.risk_reasons.length ? `<ul>${s.risk_reasons.map((r) => `<li>${esc(r)}</li>`).join('')}</ul>` : '<p class="muted mt-16">No risk drivers above threshold.</p>'}
      <div class="action"><strong>Recommended action:</strong> ${esc(s.recommended_action)}</div>
    </div>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
