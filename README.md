# Neural Coding: Feedback Encoding Comparison on Cortical Labs CL1

Comparing three stimulation encoding schemes — rate, temporal, and spatial — for closed-loop feedback to cultured neurons performing a cursor-centering task on Cortical Labs' CL1 platform.

## Research Question

To what extent does the method of feedback encoding (rate, temporal, spatial) affect how quickly and reliably neurons learn cursor centering?

| Condition | Neural Encoding Principle |
|---|---|
| Rate | Burst frequency scales with the size of the error |
| Temporal | A single, precisely-timed pulse fires only at the moment of a zero-crossing |
| Spatial | Feedback is always the same strength, but routed to a different electrode group depending on error sign |

Stimulation is capped at 180 Hz per channel, safely under Cortical Labs' 200 Hz hardware limit.

## Experimental Design

- Channels 0–9 are treated as "left," channels 10–19 as "right"
- A sliding 50-tick window of spike counts from each group produces one decision variable, `error` (positive = drifting right, negative = drifting left, zero = perfectly centered)
- Feedback is delivered on a separate set of channels (20–29) — distinct from the sensing channels, since we don't want to stimulate the same electrodes we're reading from

## Repo Structure

| File | Purpose |
|---|---|
| `hello_spikes.py` | Minimal connection test — confirms install and prints raw spikes |
| `decode.py` | Left/right channel grouping and rolling-window `error` calculation |
| `feedback.py` | The three feedback-encoding functions (`feedback_rate`, `feedback_temporal`, `feedback_spatial`) |
| `recorded_run.py` | Full closed-loop experiment, wrapped in `neurons.record()` and a custom data stream |
| `analyze.py` | Loads recorded `.h5` files back and plots `error` over time per condition |

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install cl-sdk matplotlib
```

Optional, for reproducible simulator runs — create a `.env` file:
```
CL_SDK_RANDOM_SEED=42
```

## Usage

Run the experiment once per condition, changing `CONDITION` at the top of `recorded_run.py` to `"rate"`, `"temporal"`, or `"spatial"` each time:

```bash
mkdir -p recordings/rate recordings/temporal recordings/spatial
python recorded_run.py
```

Then analyze all three recordings together:

```bash
python analyze.py
```

This prints a summary table and saves `comparison_plot.png`.

## Baseline Validation Results

All three conditions were run for 10 seconds (10,000 ticks) each against the **CL SDK Simulator's** random spike source. This is the control condition — the simulator does not respond to stimulation, so no learning is possible — and establishes the expected "chance" result before testing against real CL1 neurons.

| Condition | Log Entries | Stimulations Fired | MAE |
|---|---|---|---|
| Rate | 10,000 | 200 | 0.62 |
| Temporal | 10,000 | 1 | 0.73 |
| Spatial | 10,000 | 103 | 0.67 |

**Interpretation:**
- Stimulation counts match each condition's logic: rate fires on every 50-tick window boundary (10,000 / 50 = 200); spatial fires on roughly half of those windows (only when `error ≠ 0`); temporal fires only on sign-crossings, which are rare in sparse, non-learning data (1 occurrence)
- Similar MAE across all three conditions is the expected result for a non-learning baseline — no condition should outperform another on random data, and none did

**Known issue to resolve before real CL1 time:** the temporal condition triggered on only 1 out of 10,000 ticks. That may be too sparse to drive learning even on real neurons, and is worth revisiting (e.g., firing on a crossing *or* every N windows) before committing hardware time to this condition as currently defined.

## Next Steps

- [ ] Loosen the temporal condition's trigger to fire more often
- [ ] Request Cortical Cloud access for real CL1 runs
- [ ] Re-run all three conditions against real neurons using the same methodology
- [ ] Compare learning curves (not just baseline chance) across conditions

## License

TBD