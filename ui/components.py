import streamlit as st


def _safe(value, fallback="Awaiting execution"):
    if value is None or value == "":
        return fallback
    return value


def _title_case(value):
    value = _safe(value)
    return str(value).replace("_", " ").title()


def _severity_color(severity: str) -> str:
    severity = str(severity or "").lower()
    if severity == "critical":
        return "#ef4444"
    if severity == "high":
        return "#f59e0b"
    if severity == "medium":
        return "#38bdf8"
    if severity == "low":
        return "#16a34a"
    return "#64748b"


def _mode_color(mode: str) -> str:
    mode = str(mode or "").lower()
    if mode == "olympus-review":
        return "#ef4444"
    if mode == "sentinel-ready":
        return "#16a34a"
    if mode == "human-review":
        return "#f59e0b"
    return "#64748b"


def _kv_table(rows: list[tuple[str, str]]) -> str:
    html = []
    for label, value in rows:
        html.append(
            f"""
            <div class="kv-row">
                <span>{label}</span>
                <span>{value}</span>
            </div>
            """
        )
    return "".join(html)


def normalize_root_cause(raw_text: str) -> str:
    text = (raw_text or "").strip()
    lowered = text.lower()

    if any(x in lowered for x in ["connection pool", "pool saturation", "database pool", "database connection pool"]):
        return "Database Connection Pool Saturation"

    if any(x in lowered for x in ["configuration drift", "config drift", "recent change"]):
        return "Configuration Drift Detected"

    if any(x in lowered for x in ["latency", "slow response", "response time", "performance degradation"]):
        return "Service Latency Degradation"

    if any(x in lowered for x in ["memory pressure", "oom", "out of memory", "compute saturation", "capacity"]):
        return "Memory Pressure Or Compute Saturation"

    if any(x in lowered for x in ["network", "dns", "packet loss", "dependency", "downstream"]):
        return "Network Or Dependency Path Instability"

    if any(x in lowered for x in ["identity", "auth", "authentication"]):
        return "Identity Path Failure"

    return text if text else "Root cause under evaluation"


def get_root_cause(summary: dict) -> str:
    diagnostics = summary.get("diagnostics", {}).get("result", {})
    finding = diagnostics.get("finding") or diagnostics.get("summary") or ""
    return normalize_root_cause(finding)


def render_platform_overview() -> None:
    cols = st.columns(4)
    cards = [
        ("Platform Status", "Active"),
        ("Routing Model", "Capability-Based"),
        ("Coordination Plane", "TITAN"),
        ("Execution Path", "Governed"),
    ]
    for col, (label, value) in zip(cols, cards):
        col.markdown(
            f"""
            <div class="metric-card compact-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero_banner(summary: dict) -> None:
    detection = summary.get("detection", {})
    remediation = summary.get("remediation", {}).get("result", {})

    incident_id = _safe(detection.get("incident_id") or summary.get("incident_id"))
    service = _safe(detection.get("service"))
    severity = _safe(detection.get("severity"), "unknown")

    execution_mode = remediation.get("execution_mode")
    if not execution_mode:
        execution_mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    root_cause = get_root_cause(summary)

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-left">
                <div class="hero-eyebrow">AUTONOMOUS ENTERPRISE INCIDENT COMMAND</div>
                <div class="hero-title">Incident {incident_id} — {service}</div>
                <div class="hero-subtitle">Root cause: {root_cause}</div>
            </div>
            <div class="hero-right">
                <div class="status-pill" style="background:{_severity_color(severity)};">
                    Severity: {str(severity).upper()}
                </div>
                <div class="status-pill" style="background:{_mode_color(execution_mode)};">
                    Execution: {str(execution_mode).upper()}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_operator_insight(summary: dict) -> None:
    detection = summary.get("detection", {})
    diagnostics = summary.get("diagnostics", {}).get("result", {})
    risk = summary.get("risk", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})

    severity = _safe(detection.get("severity"), "unknown")
    error_rate = _safe(detection.get("error_rate"), "unknown")
    latency = _safe(detection.get("latency"), "unknown")
    confidence = diagnostics.get("confidence", "N/A")
    root_cause = get_root_cause(summary)

    execution_mode = remediation.get("execution_mode")
    if not execution_mode:
        execution_mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    path_text = (
        "OLYMPUS escalation path"
        if str(execution_mode).lower() == "olympus-review"
        else "SENTINEL action path"
    )

    recommendation = risk.get("execution_recommendation")
    if not recommendation:
        recommendation = "escalate" if str(severity).lower() == "critical" else "allow_with_audit"

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="glass-card">
                <div class="hero-eyebrow">PRIMARY ROOT CAUSE HYPOTHESIS</div>
                <div class="insight-title">{root_cause}</div>
                <div class="insight-body">
                    TITAN is surfacing the strongest operational explanation from a governed A2A exchange so operators can immediately understand the most likely system outcome.
                </div>
                <div class="pill-row">
                    <span class="soft-pill">A2A coordination visible</span>
                    <span class="soft-pill">Confidence: {confidence}</span>
                    <span class="soft-pill">Path: {path_text}</span>
                    <span class="soft-pill">Severity: {str(severity).upper()}</span>
                </div>
                <div class="bullet-list">
                    <div>Detector observed elevated service degradation on the payment path.</div>
                    <div>Incident payload shows error rate at {error_rate} and latency at {latency}.</div>
                    <div>Severity posture entered governed {str(severity).lower()} incident handling.</div>
                    <div>Multiple agent perspectives converged on a shared root-cause hypothesis.</div>
                </div>
            </div>
            <div class="glass-card">
                <div class="section-title">Premium operator view</div>
                <div class="operator-line">
                    <div class="operator-label">Primary Inference</div>
                    <div class="operator-value">{root_cause}</div>
                </div>
                <div class="operator-line">
                    <div class="operator-label">Incident Path</div>
                    <div class="operator-value">{_title_case(recommendation)}</div>
                </div>
                <div class="operator-line">
                    <div class="operator-label">Decision Model</div>
                    <div class="operator-value">Multi-agent consensus under policy enforcement</div>
                </div>
                <div class="operator-line" style="border-bottom:none;">
                    <div class="operator-label">Operator Outcome</div>
                    <div class="operator-value">Easy-to-read root cause framing with guided next actions</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_progress(summary: dict) -> None:
    remediation = summary.get("remediation", {}).get("result", {})
    knowledge = summary.get("knowledge", {}).get("result", {})
    detection = summary.get("detection", {})

    execution_mode = str(remediation.get("execution_mode", "")).lower()
    severity = str(detection.get("severity", "")).lower()

    if not execution_mode:
        execution_mode = "olympus-review" if severity == "critical" else "sentinel-ready"

    current_state = (
        "Escalated to OLYMPUS"
        if execution_mode == "olympus-review"
        else "Ready for SENTINEL execution"
    )

    steps = [
        ("Detection", "completed"),
        ("Diagnostics", "completed"),
        ("Knowledge", "completed"),
        ("Risk", "completed"),
        ("Remediation", "completed"),
    ]

    st.markdown(
        f"""
        <div class="workflow-shell">
            <div class="section-title" style="margin-bottom:6px;">Workflow Progress</div>
            <div class="workflow-subtitle">Current State: {current_state}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 0.10, 1, 0.10, 1, 0.10, 1, 0.10, 1])
    for i, (label, state) in enumerate(steps):
        with cols[i * 2]:
            st.markdown(
                f"""
                <div class="progress-stage">
                    <div class="progress-stage-number completed">{i + 1}</div>
                    <div class="progress-stage-text">
                        <div class="progress-stage-label">{label}</div>
                        <div class="progress-stage-state">{state.upper()}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if i < len(steps) - 1:
            with cols[i * 2 + 1]:
                st.markdown('<div class="progress-connector">→</div>', unsafe_allow_html=True)

    if execution_mode == "olympus-review":
        st.markdown(
            """
            <div class="olympus-branch">
                <div class="olympus-branch-label">Escalation Branch</div>
                <div class="olympus-branch-flow">
                    <span class="branch-node titan">TITAN Risk Gate</span>
                    <span class="branch-arrow">→</span>
                    <span class="branch-node olympus">OLYMPUS Review</span>
                    <span class="branch-arrow">→</span>
                    <span class="branch-node final">Final Authority</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    final_decision = remediation.get("final_decision")
    if not final_decision:
        final_decision = "escalate_for_consensus" if execution_mode == "olympus-review" else "recommend_rollback"

    st.markdown(
        f"""
        <div class="summary-strip">
            <div class="summary-item">
                <div class="summary-label">Final Decision</div>
                <div class="summary-value">{_title_case(final_decision)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Execution Mode</div>
                <div class="summary-value">{_title_case(execution_mode)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Severity</div>
                <div class="summary-value">{_title_case(detection.get("severity"))}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Runbook</div>
                <div class="summary-value">{_safe(knowledge.get("runbook_id"))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_compact_kpis(summary: dict) -> None:
    remediation = summary.get("remediation", {}).get("result", {})
    knowledge = summary.get("knowledge", {}).get("result", {})
    detection = summary.get("detection", {})

    final_decision = remediation.get("final_decision")
    execution_mode = remediation.get("execution_mode")
    severity = detection.get("severity")
    runbook = knowledge.get("runbook_id")

    if not execution_mode and severity:
        execution_mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    metrics = [
        ("Final Decision", _title_case(final_decision)),
        ("Execution Mode", _title_case(execution_mode)),
        ("Severity", _title_case(severity)),
        ("Runbook", _safe(runbook)),
    ]

    cols = st.columns(4)
    for col, (label, value) in zip(cols, metrics):
        col.markdown(
            f"""
            <div class="metric-card compact-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_consensus_panels(summary: dict) -> None:
    detection = summary.get("detection", {})
    diagnostics = summary.get("diagnostics", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})

    severity = _safe(detection.get("severity"), "unknown")
    service = _safe(detection.get("service") or diagnostics.get("service"), "payment-api")
    confidence = diagnostics.get("confidence", "N/A")
    root_cause = get_root_cause(summary)

    left, right = st.columns([1.35, 1])

    with left:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Consensus formation path</div>
                <div class="consensus-subtitle">
                    This outcome is produced by multi-agent consensus under policy enforcement, not by a single model response. Current confidence: {confidence}.
                </div>
                <div class="flow-row">
                    <div class="flow-left">Detector → Diagnostician</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-right">Published normalized incident signal for {service} after threshold breach and handed the case to diagnostics.</div>
                </div>
                <div class="flow-row">
                    <div class="flow-left">Diagnostician → Knowledge</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-right">Narrowed the likely fault domain and requested historical pattern validation.</div>
                </div>
                <div class="flow-row">
                    <div class="flow-left">Knowledge → Risk</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-right">Matched operational memory to {root_cause} and returned a governed runbook recommendation.</div>
                </div>
                <div class="flow-row">
                    <div class="flow-left">Risk → TITAN Governance</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-right">Validated business impact and blast radius, then recommended governed path selection based on severity {str(severity).upper()}.</div>
                </div>
                <div class="flow-row" style="border-bottom:none;">
                    <div class="flow-left">TITAN Governance</div>
                    <div class="flow-arrow">→</div>
                    <div class="flow-right">Consensus accepted. Final outcome routed through policy-governed execution authority.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        lowered = root_cause.lower()
        if "database" in lowered or "connection pool" in lowered:
            rejected = [
                "Network outage rejected — no strong regional skew or infrastructure-wide connectivity signal is present.",
                "Authentication failure rejected — no token, secret, or identity anomaly dominates the incident profile.",
                "Downstream dependency failure rejected — symptoms point to local resource contention rather than external upstream collapse.",
            ]
        elif "configuration drift" in lowered:
            rejected = [
                "Broad infrastructure outage rejected — the incident does not show platform-wide collapse.",
                "Database saturation rejected — current signals do not center on pooled connection exhaustion.",
                "Identity failure rejected — authentication is not the dominant operational symptom.",
            ]
        else:
            rejected = [
                "Broad infrastructure outage rejected — current signals do not show multi-service collapse.",
                "Identity path failure rejected — the incident does not center on authentication degradation.",
                "Single noisy metric rejected — the selected hypothesis is supported by converging agent evidence, not one metric alone.",
            ]

        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Rejected hypotheses</div>
                <div class="consensus-subtitle">
                    TITAN increases operator trust by showing why weaker explanations were not selected.
                </div>
                <div class="reject-row">✕ {rejected[0]}</div>
                <div class="reject-row">✕ {rejected[1]}</div>
                <div class="reject-row" style="border-bottom:none;">✕ {rejected[2]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    mode = str(remediation.get("execution_mode", "")).lower()
    if not mode:
        mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    if mode == "olympus-review":
        meaning = "OLYMPUS — Elevated governance escalation"
        text = "Use this path when TITAN blocks autonomous execution and routes the incident to elevated review before action can proceed."
    else:
        meaning = "SENTINEL — Governed execution path"
        text = "Use this path when TITAN can prepare a controlled remediation package for governed execution with auditability and operator oversight."

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-title">Path meaning</div>
            <div class="path-title">{meaning}</div>
            <div class="path-body">{text}</div>
            <div class="pill-row">
                <span class="soft-pill">Readable by operators</span>
                <span class="soft-pill">Directional A2A view</span>
                <span class="soft-pill">Governance-first</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_summary(summary: dict) -> None:
    detection = summary.get("detection", {})
    diagnostics = summary.get("diagnostics", {}).get("result", {})
    knowledge = summary.get("knowledge", {}).get("result", {})
    risk = summary.get("risk", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})
    action_package = remediation.get("action_package", {})

    severity = detection.get("severity")
    execution_mode = remediation.get("execution_mode")
    final_decision = remediation.get("final_decision")

    if not execution_mode and severity:
        execution_mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    if not final_decision and execution_mode:
        final_decision = "escalate_for_consensus" if execution_mode == "olympus-review" else "recommend_rollback"

    decision_rows = [
        ("Incident ID", _safe(detection.get("incident_id") or summary.get("incident_id"))),
        ("Service", _safe(detection.get("service") or diagnostics.get("service"))),
        ("Region", _safe(detection.get("region") or diagnostics.get("region"))),
        ("Severity", _title_case(severity)),
        ("Root Cause Hypothesis", get_root_cause(summary)),
        ("Recommended Action", _safe(knowledge.get("recommended_action"))),
        ("Execution Recommendation", _title_case(risk.get("execution_recommendation"))),
        ("Final Decision", _title_case(final_decision)),
        ("Execution Mode", _title_case(execution_mode)),
    ]

    action_rows = [
        ("Action Type", _safe(action_package.get("action_type"))),
        ("Target Service", _safe(action_package.get("target_service") or detection.get("service") or diagnostics.get("service"))),
        ("Target Region", _safe(action_package.get("target_region") or detection.get("region") or diagnostics.get("region"))),
        ("Approved Runbook", _safe(action_package.get("approved_runbook") or knowledge.get("runbook_id"))),
        ("Recommended Action", _safe(action_package.get("recommended_action") or knowledge.get("recommended_action"))),
    ]

    st.subheader("Decision")

    col1, col2 = st.columns([1.25, 1])
    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Operational Decision</div>
                {_kv_table(decision_rows)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Action Package</div>
                {_kv_table(action_rows)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_governance_panel(summary: dict) -> None:
    detection = summary.get("detection", {})
    diagnostics = summary.get("diagnostics", {}).get("result", {})
    risk = summary.get("risk", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})

    severity = _title_case(detection.get("severity"))
    business_impact = _title_case(risk.get("business_impact"))
    technical_risk = _title_case(risk.get("technical_risk"))
    confidence = diagnostics.get("confidence", "N/A")
    execution_recommendation = risk.get("execution_recommendation")
    mode = str(remediation.get("execution_mode", "")).lower()

    raw_severity = str(detection.get("severity", "")).lower()
    if not mode:
        mode = "olympus-review" if raw_severity == "critical" else "sentinel-ready"

    if not execution_recommendation:
        execution_recommendation = "escalate" if mode == "olympus-review" else "allow_with_audit"

    execution_recommendation = _title_case(execution_recommendation)

    if mode == "olympus-review":
        outcome = "ESCALATE"
        color = "#ef4444"
        routed_to = "OLYMPUS"
        rule = "Critical or high-risk incidents require consensus review before execution."
    elif mode == "human-review":
        outcome = "REVIEW"
        color = "#f59e0b"
        routed_to = "HUMAN REVIEW"
        rule = "Uncertain incidents require human approval before execution."
    else:
        outcome = "ALLOW WITH AUDIT"
        color = "#16a34a"
        routed_to = "SENTINEL"
        rule = "Low-risk incidents may proceed with audit-bound governed execution."

    st.subheader("Governance Decision Gate")

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="governance-header-row">
                <div>
                    <div class="section-title" style="margin-bottom:6px;">Decision Authority (TITAN)</div>
                    <div style="color:#94a3b8;">Policy-driven decision before execution</div>
                </div>
                <div class="status-pill" style="background:{color};">{outcome}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cards = [
        ("Severity", severity),
        ("Business Impact", business_impact),
        ("Technical Risk", technical_risk),
        ("Confidence", str(confidence)),
    ]
    for col, (label, value) in zip(cols, cards):
        col.markdown(
            f"""
            <div class="metric-card compact-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Execution Recommendation</div>
                <div class="metric-value">{execution_recommendation}</div>
                <div style="margin-top:0.8rem;color:#94a3b8;">Routed to: <b style="color:#f8fafc;">{routed_to}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Policy Rule Applied</div>
                <div style="color:#cbd5e1; line-height:1.65;">{rule}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if mode == "olympus-review":
        render_olympus_escalation_visualization(summary)


def render_olympus_escalation_visualization(summary: dict) -> None:
    detection = summary.get("detection", {})
    risk = summary.get("risk", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})

    final_decision = remediation.get("final_decision")
    if not final_decision:
        final_decision = "escalate_for_consensus"

    st.subheader("OLYMPUS Escalation Path")

    left, a1, middle, a2, right = st.columns([1.2, 0.16, 1.2, 0.16, 1.2])

    with left:
        st.markdown(
            f"""
            <div class="glass-card" style="min-height:150px;">
                <div class="section-title">TITAN Risk Gate</div>
                <div style="color:#cbd5e1; line-height:1.7;">
                    <b>Severity:</b> {_safe(detection.get("severity"))}<br>
                    <b>Technical Risk:</b> {_safe(risk.get("technical_risk"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a1:
        st.markdown('<div class="big-arrow">→</div>', unsafe_allow_html=True)
    with middle:
        st.markdown(
            """
            <div class="glass-card" style="min-height:150px;">
                <div class="section-title">OLYMPUS Review</div>
                <div style="color:#cbd5e1; line-height:1.7;">
                    Consensus required before governed execution.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown('<div class="big-arrow">→</div>', unsafe_allow_html=True)
    with right:
        st.markdown(
            f"""
            <div class="glass-card" style="min-height:150px;">
                <div class="section-title">Final Authority</div>
                <div style="color:#cbd5e1; line-height:1.7;">
                    <b>Outcome:</b> {_title_case(final_decision)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_agent_identity_cards(summary: dict) -> None:
    st.subheader("A2A Orchestration")

    diagnostics = summary.get("diagnostics", {}).get("result", {})
    knowledge = summary.get("knowledge", {}).get("result", {})
    risk = summary.get("risk", {}).get("result", {})
    remediation = summary.get("remediation", {}).get("result", {})

    root_cause = get_root_cause(summary)
    runbook = _safe(knowledge.get("runbook_id"))
    recommendation = _title_case(risk.get("execution_recommendation"))
    final_outcome = _title_case(remediation.get("final_decision"))

    st.markdown(
        f"""
        <div class="a2a-card-shell">
            <div class="a2a-card-grid">
                <div class="a2a-node-card">
                    <div class="a2a-node-title">Detection</div>
                    <div class="a2a-node-sub">Normalized incident signal and opened governed flow.</div>
                </div>
                <div class="a2a-node-arrow">→</div>
                <div class="a2a-node-card">
                    <div class="a2a-node-title">Diagnostics</div>
                    <div class="a2a-node-sub">Narrowed fault domain to: {root_cause}</div>
                </div>
                <div class="a2a-node-arrow">→</div>
                <div class="a2a-node-card">
                    <div class="a2a-node-title">Knowledge</div>
                    <div class="a2a-node-sub">Matched governed runbook: {runbook}</div>
                </div>
                <div class="a2a-node-arrow">→</div>
                <div class="a2a-node-card">
                    <div class="a2a-node-title">Risk</div>
                    <div class="a2a-node-sub">Evaluated execution posture: {recommendation}</div>
                </div>
                <div class="a2a-node-arrow">→</div>
                <div class="a2a-node-card">
                    <div class="a2a-node-title">Remediation</div>
                    <div class="a2a-node-sub">Prepared final governed outcome: {final_outcome}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_agent_flow(summary: dict) -> None:
    root_cause = get_root_cause(summary)
    runbook = _safe(summary.get("knowledge", {}).get("result", {}).get("runbook_id"))
    execution_recommendation = _title_case(summary.get("risk", {}).get("result", {}).get("execution_recommendation"))
    final_decision = _title_case(summary.get("remediation", {}).get("result", {}).get("final_decision"))

    steps = [
        ("Detection Agent", "Normalized incoming incident signal into a governed incident package.", "#38bdf8"),
        ("Diagnostics Agent", f"Narrowed the likely fault domain to {root_cause}.", "#8b5cf6"),
        ("Knowledge Agent", f"Matched the dominant incident pattern to governed runbook {runbook}.", "#14b8a6"),
        ("Risk Agent", f"Assessed business impact and selected execution posture: {execution_recommendation}.", "#f59e0b"),
        ("Remediation Agent", f"Prepared the final action package and governed outcome: {final_decision}.", "#ef4444"),
    ]

    for idx, (title, desc, color) in enumerate(steps, start=1):
        st.markdown(
            f"""
            <div class="timeline-card">
                <div class="timeline-index" style="background:{color};">{idx}</div>
                <div class="timeline-content">
                    <div class="timeline-title">{title}</div>
                    <div class="timeline-desc">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_architecture_panel() -> None:
    st.markdown(
        """
        <div class="glass-card">
            <div class="section-title">Architecture View</div>
            <div style="color:#cbd5e1; line-height:1.7;">
                <b>TITAN</b> coordinates a governed incident workflow across specialized agents.
                Detection normalizes the signal, Diagnostics narrows the likely fault domain,
                Knowledge retrieves operational patterns, Risk evaluates blast radius and policy posture,
                and Remediation prepares the governed action package.
                <br><br>
                Final authority remains with the TITAN control plane.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def _derive_trace_responder(event: dict) -> str:
    responder = event.get("responder_agent")
    if responder:
        return str(responder)

    capability = str(event.get("target_capability") or "").lower()
    task = str(event.get("task") or "").lower()

    capability_map = {
        "incident-detection": "detection-agent",
        "incident-diagnostics": "diagnostics-agent",
        "runbook-lookup": "knowledge-agent",
        "incident-risk-assessment": "risk-agent",
        "incident-remediation": "remediation-agent",
        "final-decision": "titan-governance",
        "execute-decision-package": "sentinel-authority",
    }
    if capability in capability_map:
        return capability_map[capability]

    if "detect" in task:
        return "detection-agent"
    if "diagn" in task or "analyze" in task:
        return "diagnostics-agent"
    if "runbook" in task or "lookup" in task:
        return "knowledge-agent"
    if "risk" in task:
        return "risk-agent"
    if "remediation" in task or "prepare" in task:
        return "remediation-agent"
    if "final" in task or "decision" in task:
        return "titan-governance"
    if "execute" in task:
        return "sentinel-authority"

    return "—"


def _derive_trace_summary(event: dict) -> str:
    summary = event.get("summary")
    if summary:
        return str(summary)

    details = event.get("details") or {}
    if not isinstance(details, dict):
        details = {}

    task = str(event.get("task") or "").lower()
    status = str(event.get("status") or "").lower()

    if task == "normalize_incident":
        service = details.get("service", "service")
        severity = details.get("severity", "unknown")
        error_rate = details.get("error_rate", "n/a")
        latency = details.get("latency", "n/a")
        return f"Normalized incident for {service} with severity {severity}; error rate {error_rate}, latency {latency}."

    if task == "analyze_incident":
        finding = details.get("finding") or details.get("summary")
        if finding:
            return str(finding)
        sender = str(event.get("sender_agent") or "")
        if "diagnostics" in sender:
            return "Diagnostics analysis completed and narrowed the likely fault domain."
        return "Incident analysis dispatched for governed diagnostics."

    if task == "lookup_runbook_for_incident":
        runbook = details.get("runbook_id") or details.get("approved_runbook")
        action = details.get("recommended_action")
        if runbook and action:
            return f"Mapped incident to runbook {runbook}; recommended action: {action}."
        if runbook:
            return f"Mapped incident to runbook {runbook}."
        return "Runbook lookup completed against operational memory."

    if task == "assess_incident_risk":
        rec = details.get("execution_recommendation")
        impact = details.get("business_impact")
        if rec and impact:
            return f"Risk assessment completed with recommendation {rec}; business impact {impact}."
        if rec:
            return f"Risk assessment completed with recommendation {rec}."
        return "Risk posture evaluated for governance decisioning."

    if task == "prepare_remediation_plan":
        action_type = details.get("action_type")
        action = details.get("recommended_action")
        if action_type and action:
            return f"Prepared remediation package {action_type}; action: {action}."
        if action:
            return f"Prepared remediation package; action: {action}."
        return "Prepared governed remediation package."

    if task == "finalize_incident_decision":
        final_decision = details.get("final_decision")
        execution_mode = details.get("execution_mode")
        if final_decision and execution_mode:
            return f"Final decision {final_decision}; execution mode {execution_mode}."
        if final_decision:
            return f"Final decision {final_decision}."
        return "Final decision package issued by TITAN governance."

    if task == "execute_action":
        verification = details.get("verification_result")
        action_type = details.get("action_type")
        if action_type and verification:
            return f"Executed {action_type}; post-action verification {verification}."
        if action_type:
            return f"Executed {action_type} through governed execution."
        return "Governed execution completed."

    if details:
        compact = ", ".join(f"{k}={v}" for k, v in list(details.items())[:3])
        return compact

    return "Completed" if status == "completed" else "Awaiting execution"


def render_trace(trace_payload: dict) -> None:
    trace = trace_payload.get("trace", [])
    if not trace:
        st.info("No trace events found for this incident.")
        return

    # Header
    header_cols = st.columns([2.0, 1.2, 1.2, 1.5, 1.5, 1.0, 2.6])
    headers = ["Timestamp", "Sender", "Responder", "Capability", "Task", "Status", "Summary"]
    for col, label in zip(header_cols, headers):
        with col:
            st.markdown(f"**{label}**")

    st.markdown("---")

    for event in trace:
        cols = st.columns([2.0, 1.2, 1.2, 1.5, 1.5, 1.0, 2.6])
        values = [
            _safe(event.get("timestamp"), "—"),
            _safe(event.get("sender_agent"), "—"),
            _derive_trace_responder(event),
            _safe(event.get("target_capability"), "—"),
            _safe(event.get("task"), "—"),
            _safe(event.get("status"), "—"),
            _derive_trace_summary(event),
        ]
        for idx, (col, value) in enumerate(zip(cols, values)):
            with col:
                if idx == 6:
                    st.markdown(f"<div style='white-space: normal; line-height: 1.5;'>{value}</div>", unsafe_allow_html=True)
                else:
                    st.write(value)
        st.markdown("<div style='height: 1px; background: rgba(148,163,184,0.08); margin: 4px 0 10px 0;'></div>", unsafe_allow_html=True)

    with st.expander("Raw trace events", expanded=False):
        st.json(trace)
