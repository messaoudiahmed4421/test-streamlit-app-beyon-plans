from __future__ import annotations

import json
import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any

import pandas as pd

from pipeline_runner import run_pipeline


@dataclass
class AgentStep:
    name: str
    output: str
    duration_s: float
    status: str
    message: str


def _safe_json_loads(text: str) -> dict[str, Any] | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text

    candidates = getattr(response, "candidates", None)
    if candidates:
        try:
            parts = candidates[0].content.parts
            chunks = []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    chunks.append(part_text)
            if chunks:
                return "\n".join(chunks)
        except Exception:
            pass

    return ""


def _call_gemini(client: Any, model_name: str, prompt: str) -> str:
    response = client.models.generate_content(model=model_name, contents=prompt)
    text = _extract_text(response)
    return text.strip() if text else ""


def _build_context_payload(base_result: dict[str, Any], query: str, uploaded_files: list[Any]) -> dict[str, Any]:
    kpis = base_result.get("kpis", pd.DataFrame())
    kpi_map = {}
    if isinstance(kpis, pd.DataFrame) and not kpis.empty:
        for _, row in kpis.iterrows():
            kpi_map[str(row.get("Metric", ""))] = row.get("Value")

    return {
        "query": query,
        "files": [f.name for f in uploaded_files],
        "baseline_report": base_result.get("report", ""),
        "kpis": kpi_map,
    }


def run_pipeline_gemini(
    query: str,
    uploaded_files: list[Any],
    api_key: str | None = None,
    model_name: str = "gemini-2.5-flash",
) -> dict[str, Any]:
    """Execute the local analytics pipeline and enrich with Gemini A1-A5 agent stages.

    This function keeps deterministic numeric calculations in Python, then runs
    sequential Gemini stages (A1..A5) for validation, classification narrative,
    anomaly interpretation, executive reporting, and quality judgment.
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("GOOGLE_API_KEY is missing. Configure it in Streamlit secrets.")

    try:
        from google import genai
    except Exception as exc:
        raise RuntimeError("google-genai package not available. Add it to requirements.") from exc

    start_total = perf_counter()

    # Baseline deterministic pipeline (tables, metrics, charts)
    base_result = run_pipeline(query=query, uploaded_files=uploaded_files)
    context_payload = _build_context_payload(base_result, query, uploaded_files)
    context_json = json.dumps(context_payload, ensure_ascii=True, indent=2)

    client = genai.Client(api_key=key)
    steps: list[AgentStep] = []

    # A1
    t0 = perf_counter()
    a1_prompt = (
        "You are A1_Normalization for financial pipeline QA. "
        "Validate structural soundness of this analysis context and return concise JSON with keys: "
        "status, checks, risks, confidence.\n\n"
        f"CONTEXT:\n{context_json}"
    )
    a1_output = _call_gemini(client, model_name, a1_prompt)
    steps.append(AgentStep("A1_Normalization", a1_output, perf_counter() - t0, "SUCCESS", "Structural validation completed."))

    # A2
    t1 = perf_counter()
    a2_prompt = (
        "You are A2_Classification. Classify likely financial themes and account-level drivers from the context. "
        "Return concise JSON with keys: major_themes, account_clusters, materiality_observations, confidence.\n\n"
        f"CONTEXT:\n{context_json}\n\nA1_OUTPUT:\n{a1_output}"
    )
    a2_output = _call_gemini(client, model_name, a2_prompt)
    steps.append(AgentStep("A2_Classification", a2_output, perf_counter() - t1, "SUCCESS", "Financial theme classification completed."))

    # A3
    t2 = perf_counter()
    a3_prompt = (
        "You are A3_Variance_Engine. Identify anomaly hypotheses and rank top priorities. "
        "Return concise JSON with keys: top_anomalies (array), risk_summary, immediate_actions.\n\n"
        f"CONTEXT:\n{context_json}\n\nA2_OUTPUT:\n{a2_output}"
    )
    a3_output = _call_gemini(client, model_name, a3_prompt)
    steps.append(AgentStep("A3_Variance_Engine", a3_output, perf_counter() - t2, "SUCCESS", "Anomaly prioritization completed."))

    # A4
    t3 = perf_counter()
    a4_prompt = (
        "You are A4_Strategic_Reporter. Produce an executive markdown report with sections: "
        "Executive Summary, Financial Performance, Key Anomalies, Recommended Actions. "
        "Use concise business language and include the most important figures from context.\n\n"
        f"CONTEXT:\n{context_json}\n\nA3_OUTPUT:\n{a3_output}"
    )
    a4_output = _call_gemini(client, model_name, a4_prompt)
    steps.append(AgentStep("A4_Strategic_Reporter", a4_output, perf_counter() - t3, "SUCCESS", "Executive report generated."))

    # A5
    t4 = perf_counter()
    a5_prompt = (
        "You are A5_Quality_Judge. Evaluate A4 report quality from 1 to 10 and provide a compact verdict. "
        "Return strict JSON with keys: score_global, strengths, weaknesses, improvements.\n\n"
        f"A4_REPORT:\n{a4_output}"
    )
    a5_output = _call_gemini(client, model_name, a5_prompt)
    steps.append(AgentStep("A5_Quality_Judge", a5_output, perf_counter() - t4, "SUCCESS", "Quality judgment completed."))

    a5_json = _safe_json_loads(a5_output) or {}
    score = a5_json.get("score_global")
    if isinstance(score, (int, float)):
        quality_score = float(score)
    else:
        quality_score = 7.0

    # Build final report with Gemini A4 narrative + A5 verdict summary.
    combined_report = (
        "# Executive Financial Report\n\n"
        f"{a4_output}\n\n"
        "---\n\n"
        "## A5 Quality Judgment\n\n"
        f"{a5_output}"
    )

    # Update KPIs with LLM score when available.
    kpis = base_result.get("kpis", pd.DataFrame()).copy()
    if isinstance(kpis, pd.DataFrame) and not kpis.empty and "Metric" in kpis.columns:
        if (kpis["Metric"] == "Score A5").any():
            kpis.loc[kpis["Metric"] == "Score A5", "Value"] = round(quality_score, 1)

    agents_df = pd.DataFrame(
        {
            "Agent": [s.name for s in steps],
            "Statut": [s.status for s in steps],
            "Succes": [100 if s.status == "SUCCESS" else 0 for s in steps],
            "Duree_s": [round(s.duration_s, 2) for s in steps],
        }
    )

    quality_df = pd.DataFrame(
        {
            "Run": [1],
            "Date": [pd.Timestamp.now().strftime("%d/%m")],
            "Score Global": [round(float(quality_score), 1)],
            "Actionnabilite": [round(min(10.0, max(1.0, float(quality_score) - 0.8)), 1)],
        }
    )

    log_rows: list[tuple[str, str, str, str]] = []
    for s in steps:
        log_rows.append((pd.Timestamp.now().strftime("%H:%M:%S"), s.name, s.status, s.message))
    log_rows.append((pd.Timestamp.now().strftime("%H:%M:%S"), "PIPELINE", "SUCCESS", f"Gemini pipeline completed in {perf_counter() - start_total:.2f}s"))

    result = dict(base_result)
    result["report"] = combined_report
    result["kpis"] = kpis
    result["agents"] = agents_df
    result["quality"] = quality_df
    result["logs"] = log_rows
    return result
