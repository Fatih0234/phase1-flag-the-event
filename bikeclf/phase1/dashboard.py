"""Streamlit dashboard for analyzing evaluation runs and inspecting errors."""
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import confusion_matrix

from bikeclf.config import RUNS_DIR, VALID_LABELS, MODEL_DISPLAY_NAMES


@st.cache_data
def discover_runs() -> List[Dict[str, Any]]:
    """Discover all available evaluation runs.

    Returns:
        List of run metadata dictionaries
    """
    if not RUNS_DIR.exists():
        return []

    runs = []
    for run_dir in sorted(RUNS_DIR.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue

        config_path = run_dir / "config.json"
        metrics_path = run_dir / "metrics.json"

        if config_path.exists() and metrics_path.exists():
            with config_path.open("r") as f:
                config = json.load(f)

            with metrics_path.open("r") as f:
                metrics = json.load(f)

            runs.append(
                {
                    "name": run_dir.name,
                    "path": str(run_dir),
                    "timestamp": config.get("timestamp_utc", "Unknown"),
                    "prompt_version": config.get("prompt_version", "Unknown"),
                    "model_id": config.get("model_id", "Unknown"),
                    "accuracy": metrics.get("accuracy", 0.0),
                    "macro_f1": metrics.get("macro_f1", 0.0),
                    "total_predictions": config.get("successful_predictions", 0),
                    "failed_predictions": config.get("failed_predictions", 0),
                }
            )

    return runs


@st.cache_data
def load_run_data(run_path: str) -> Tuple[List[Dict], Dict, Dict]:
    """Load predictions, metrics, and config for a run.

    Args:
        run_path: Path to run directory

    Returns:
        Tuple of (predictions, metrics, config)
    """
    run_dir = Path(run_path)

    # Load predictions
    predictions = []
    predictions_path = run_dir / "predictions.jsonl"
    with predictions_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))

    # Load metrics
    with (run_dir / "metrics.json").open("r") as f:
        metrics = json.load(f)

    # Load config
    with (run_dir / "config.json").open("r") as f:
        config = json.load(f)

    # Load errors if exists
    errors = []
    errors_path = run_dir / "errors.jsonl"
    if errors_path.exists():
        with errors_path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    errors.append(json.loads(line))

    return predictions, metrics, config, errors


def create_confusion_matrix_plot(predictions: List[Dict]) -> go.Figure:
    """Create interactive confusion matrix plot.

    Args:
        predictions: List of prediction records

    Returns:
        Plotly figure
    """
    gold_labels = [p["gold_label"] for p in predictions]
    pred_labels = [p["pred"]["label"] for p in predictions]

    cm = confusion_matrix(gold_labels, pred_labels, labels=VALID_LABELS)

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=VALID_LABELS,
            y=VALID_LABELS,
            text=cm,
            texttemplate="%{text}",
            textfont={"size": 16},
            colorscale="Blues",
            showscale=True,
        )
    )

    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted Label",
        yaxis_title="Gold Label",
        width=500,
        height=500,
    )

    return fig


def get_misclassified_predictions(predictions: List[Dict]) -> pd.DataFrame:
    """Extract misclassified predictions into a DataFrame.

    Args:
        predictions: List of prediction records

    Returns:
        DataFrame with misclassified predictions
    """
    misclassified = []

    for pred in predictions:
        gold = pred["gold_label"]
        predicted = pred["pred"]["label"]

        if gold != predicted:
            misclassified.append(
                {
                    "id": pred["id"],
                    "gold_label": gold,
                    "pred_label": predicted,
                    "confidence": pred["pred"]["confidence"],
                    "subject": pred["subject"],
                    "description": pred["description"],
                    "evidence": ", ".join(pred["pred"]["evidence"]),
                    "reasoning": pred["pred"]["reasoning"],
                    "latency_ms": pred["meta"]["latency_ms"],
                    "attempts": pred["meta"]["attempts"],
                    "text_length": len(pred["description"]),
                }
            )

    return pd.DataFrame(misclassified)


def get_length_analysis(predictions: List[Dict]) -> pd.DataFrame:
    """Analyze performance by text length buckets.

    Args:
        predictions: List of prediction records

    Returns:
        DataFrame with length-based analysis
    """
    length_data = []

    for pred in predictions:
        text_length = len(pred["description"])
        is_correct = pred["gold_label"] == pred["pred"]["label"]

        length_data.append(
            {
                "id": pred["id"],
                "text_length": text_length,
                "is_correct": is_correct,
                "gold_label": pred["gold_label"],
                "pred_label": pred["pred"]["label"],
                "confidence": pred["pred"]["confidence"],
            }
        )

    df = pd.DataFrame(length_data)

    # Create length buckets
    bins = [0, 100, 200, 300, 500, 1000, float("inf")]
    labels = ["0-100", "100-200", "200-300", "300-500", "500-1000", "1000+"]
    df["length_bucket"] = pd.cut(df["text_length"], bins=bins, labels=labels)

    return df


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Bike Classification Dashboard",
        page_icon="🚴",
        layout="wide",
    )

    st.title("🚴 Bike Relevance Classification Dashboard")
    st.markdown("Analyze evaluation runs, inspect errors, and explore performance patterns")

    # Sidebar: Run selection
    st.sidebar.header("Select Evaluation Run")

    runs = discover_runs()

    if not runs:
        st.error(
            f"No evaluation runs found in {RUNS_DIR}\n\n"
            "Run an evaluation first:\n"
            "```bash\n"
            "python -m bikeclf.phase1.eval evaluate --prompt v001\n"
            "```"
        )
        return

    # Sidebar filters
    model_options = sorted({r["model_id"] for r in runs})
    prompt_options = sorted({r["prompt_version"] for r in runs})

    selected_models = st.sidebar.multiselect(
        "Filter by Model:",
        options=model_options,
        default=model_options,
        format_func=lambda m: MODEL_DISPLAY_NAMES.get(m, m),
    )
    selected_prompts = st.sidebar.multiselect(
        "Filter by Prompt Version:",
        options=prompt_options,
        default=prompt_options,
    )

    filtered_runs = [
        r
        for r in runs
        if r["model_id"] in selected_models
        and r["prompt_version"] in selected_prompts
    ]

    if not filtered_runs:
        st.warning("No runs match the current filters.")
        return

    # Create run selector
    run_options = [
        (
            f"{r['name']} | {r['prompt_version']} | "
            f"{MODEL_DISPLAY_NAMES.get(r['model_id'], r['model_id'])} "
            f"(Acc: {r['accuracy']:.3f}, F1: {r['macro_f1']:.3f})"
        )
        for r in filtered_runs
    ]

    selected_idx = st.sidebar.selectbox(
        "Choose a run:",
        range(len(run_options)),
        format_func=lambda i: run_options[i],
    )

    selected_run = filtered_runs[selected_idx]

    # Display run metadata
    st.sidebar.markdown("---")
    st.sidebar.subheader("Run Details")
    st.sidebar.markdown(f"**Prompt Version:** {selected_run['prompt_version']}")
    st.sidebar.markdown(f"**Model:** {selected_run['model_id']}")
    st.sidebar.markdown(f"**Timestamp:** {selected_run['timestamp'][:19]}")
    st.sidebar.markdown(f"**Total Predictions:** {selected_run['total_predictions']}")
    if selected_run["failed_predictions"] > 0:
        st.sidebar.markdown(
            f"**Failed Predictions:** {selected_run['failed_predictions']}"
        )

    # Load run data
    predictions, metrics, config, errors = load_run_data(selected_run["path"])

    # Main dashboard
    st.header(f"📊 Run: {selected_run['name']}")

    # Metrics overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Accuracy", f"{metrics['accuracy']:.3f}")

    with col2:
        st.metric("Macro F1", f"{metrics['macro_f1']:.3f}")

    with col3:
        total_correct = sum(
            1 for p in predictions if p["gold_label"] == p["pred"]["label"]
        )
        st.metric("Correct Predictions", f"{total_correct}/{len(predictions)}")

    with col4:
        total_misclassified = len(predictions) - total_correct
        st.metric("Misclassified", total_misclassified)

    # Per-class metrics
    st.subheader("📈 Per-Class Performance")

    per_class_df = pd.DataFrame(
        [
            {
                "Label": label,
                "Precision": metrics["per_class"][label]["precision"],
                "Recall": metrics["per_class"][label]["recall"],
                "F1": metrics["per_class"][label]["f1"],
                "Support": metrics["per_class"][label]["support"],
            }
            for label in VALID_LABELS
        ]
    )

    st.dataframe(
        per_class_df.style.format(
            {"Precision": "{:.3f}", "Recall": "{:.3f}", "F1": "{:.3f}"}
        ),
        use_container_width=True,
    )

    # Confusion matrix
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Confusion Matrix")
        fig_cm = create_confusion_matrix_plot(predictions)
        st.plotly_chart(fig_cm, use_container_width=True)

    with col2:
        st.subheader("📊 Label Distribution")

        # Gold vs Predicted distribution
        gold_counts = pd.Series([p["gold_label"] for p in predictions]).value_counts()
        pred_counts = pd.Series(
            [p["pred"]["label"] for p in predictions]
        ).value_counts()

        dist_df = pd.DataFrame(
            {
                "Gold": gold_counts,
                "Predicted": pred_counts,
            }
        )

        fig_dist = px.bar(
            dist_df,
            barmode="group",
            title="Gold vs Predicted Label Distribution",
            labels={"value": "Count", "index": "Label"},
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    # Misclassified predictions
    st.subheader("❌ Misclassified Predictions")

    misclassified_df = get_misclassified_predictions(predictions)

    if len(misclassified_df) > 0:
        st.markdown(f"**Total Misclassified:** {len(misclassified_df)}")

        # Filter by label
        col1, col2, col3 = st.columns(3)

        with col1:
            filter_gold = st.multiselect(
                "Filter by Gold Label:",
                options=VALID_LABELS,
                default=VALID_LABELS,
            )

        with col2:
            filter_pred = st.multiselect(
                "Filter by Predicted Label:",
                options=VALID_LABELS,
                default=VALID_LABELS,
            )

        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                options=["confidence", "text_length", "id"],
                index=0,
            )

        # Apply filters
        filtered_df = misclassified_df[
            (misclassified_df["gold_label"].isin(filter_gold))
            & (misclassified_df["pred_label"].isin(filter_pred))
        ].sort_values(by=sort_by, ascending=(sort_by != "confidence"))

        st.dataframe(
            filtered_df[
                [
                    "id",
                    "gold_label",
                    "pred_label",
                    "confidence",
                    "subject",
                    "text_length",
                ]
            ],
            use_container_width=True,
        )

        # Detailed inspection
        st.markdown("---")
        st.subheader("🔍 Detailed Inspection")

        selected_id = st.selectbox(
            "Select a case to inspect:",
            options=filtered_df["id"].tolist(),
        )

        if selected_id:
            case = filtered_df[filtered_df["id"] == selected_id].iloc[0]

            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**Labels:**")
                st.markdown(
                    f"- **Gold:** `{case['gold_label']}` | **Predicted:** `{case['pred_label']}`"
                )
                st.markdown(f"- **Confidence:** {case['confidence']:.3f}")
                st.markdown(f"- **Text Length:** {case['text_length']} chars")
                st.markdown(f"- **Latency:** {case['latency_ms']} ms")
                st.markdown(f"- **Attempts:** {case['attempts']}")

                st.markdown("**Subject:**")
                st.info(case["subject"])

            with col2:
                st.markdown("**Evidence:**")
                if case["evidence"]:
                    st.success(case["evidence"])
                else:
                    st.warning("No evidence provided")

                st.markdown("**Reasoning:**")
                st.text_area("", case["reasoning"], height=100, disabled=True)

            st.markdown("**Full Description:**")
            st.text_area("", case["description"], height=200, disabled=True)

    else:
        st.success("✅ No misclassifications! Perfect accuracy!")

    # Failed predictions (errors)
    if errors:
        st.subheader("⚠️ Failed Predictions (Validation Errors)")
        st.markdown(f"**Total Failed:** {len(errors)}")

        errors_df = pd.DataFrame(
            [
                {
                    "id": e["id"],
                    "gold_label": e["gold_label"],
                    "subject": e["subject"],
                    "error": e["error"],
                    "attempts": e["attempts"],
                }
                for e in errors
            ]
        )

        st.dataframe(errors_df, use_container_width=True)

    # Length-based analysis
    st.subheader("📏 Performance by Text Length")

    length_df = get_length_analysis(predictions)

    # Aggregate by bucket
    bucket_stats = (
        length_df.groupby("length_bucket")
        .agg(
            {
                "is_correct": ["sum", "count", "mean"],
                "confidence": "mean",
            }
        )
        .reset_index()
    )

    bucket_stats.columns = [
        "Length Bucket",
        "Correct",
        "Total",
        "Accuracy",
        "Avg Confidence",
    ]

    st.dataframe(
        bucket_stats.style.format(
            {"Accuracy": "{:.3f}", "Avg Confidence": "{:.3f}"}
        ),
        use_container_width=True,
    )

    # Plot accuracy by length
    fig_length = px.bar(
        bucket_stats,
        x="Length Bucket",
        y="Accuracy",
        title="Accuracy by Text Length Bucket",
        labels={"Accuracy": "Accuracy"},
        text="Accuracy",
    )
    fig_length.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    st.plotly_chart(fig_length, use_container_width=True)

    # Confidence distribution
    st.subheader("🎲 Confidence Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Overall confidence
        confidences = [p["pred"]["confidence"] for p in predictions]
        fig_conf = px.histogram(
            confidences,
            nbins=20,
            title="Confidence Distribution (All Predictions)",
            labels={"value": "Confidence", "count": "Count"},
        )
        st.plotly_chart(fig_conf, use_container_width=True)

    with col2:
        # Confidence by correctness
        correct_conf = [
            p["pred"]["confidence"]
            for p in predictions
            if p["gold_label"] == p["pred"]["label"]
        ]
        incorrect_conf = [
            p["pred"]["confidence"]
            for p in predictions
            if p["gold_label"] != p["pred"]["label"]
        ]

        fig_conf_split = go.Figure()
        fig_conf_split.add_trace(
            go.Histogram(x=correct_conf, name="Correct", opacity=0.7, nbinsx=20)
        )
        fig_conf_split.add_trace(
            go.Histogram(x=incorrect_conf, name="Incorrect", opacity=0.7, nbinsx=20)
        )

        fig_conf_split.update_layout(
            title="Confidence Distribution (Correct vs Incorrect)",
            xaxis_title="Confidence",
            yaxis_title="Count",
            barmode="overlay",
        )
        st.plotly_chart(fig_conf_split, use_container_width=True)

    # Error breakdown by type
    st.subheader("🔬 Error Breakdown")

    # Create error type analysis
    error_types = []
    for pred in predictions:
        gold = pred["gold_label"]
        predicted = pred["pred"]["label"]

        if gold != predicted:
            error_types.append(
                {
                    "Error Type": f"{gold} → {predicted}",
                    "Count": 1,
                }
            )

    if error_types:
        error_df = (
            pd.DataFrame(error_types)
            .groupby("Error Type")
            .sum()
            .sort_values("Count", ascending=False)
            .reset_index()
        )

        fig_errors = px.bar(
            error_df,
            x="Error Type",
            y="Count",
            title="Most Common Misclassification Patterns",
            text="Count",
        )
        fig_errors.update_traces(textposition="outside")
        st.plotly_chart(fig_errors, use_container_width=True)


if __name__ == "__main__":
    main()
