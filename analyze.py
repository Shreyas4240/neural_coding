import glob
import os
import matplotlib.pyplot as plt
from cl import RecordingView
 
CONDITIONS = ["rate", "temporal", "spatial"]
 
 
def latest_recording_path(condition):
    """Each run auto-generates a timestamped .h5 filename, so grab the
    most recently modified file in that condition's folder."""
    pattern = os.path.join("recordings", condition, "*.h5")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(
            f"No .h5 files found in recordings/{condition}/ — "
            f"did you run step5 with CONDITION='{condition}'?"
        )
    return max(matches, key=os.path.getmtime)
 
 
def load_error_series(path):
    """Returns (timestamps, errors, stimmed_flags) from one recording."""
    timestamps, errors, stimmed = [], [], []
    with RecordingView(path) as recording:
        stream = recording.data_streams["experiment_log"]
        for ts, entry in stream.items():
            timestamps.append(ts)
            errors.append(entry["error"])
            stimmed.append(entry["stimmed"])
    return timestamps, errors, stimmed
 
 
def main():
    fig, axes = plt.subplots(len(CONDITIONS), 1, figsize=(9, 8), sharex=False)
 
    for ax, condition in zip(axes, CONDITIONS):
        path = latest_recording_path(condition)
        timestamps, errors, stimmed = load_error_series(path)
 
        # Normalize timestamps to start at 0 seconds for readability.
        t0 = timestamps[0]
        seconds = [(t - t0) / 1_000_000 for t in timestamps]  # assumes µs units
 
        ax.plot(seconds, errors, linewidth=1)
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
        ax.set_title(f"{condition}  (file: {os.path.basename(path)})")
        ax.set_ylabel("error")
 
        num_stims = sum(stimmed)
        mean_abs_error = sum(abs(e) for e in errors) / len(errors)
        print(f"{condition:10s}  entries={len(errors):5d}  "
              f"stims_fired={num_stims:4d}  mean|error|={mean_abs_error:.2f}")
 
    axes[-1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig("comparison_plot.png", dpi=150)
    print("\nSaved comparison_plot.png")
 
 
if __name__ == "__main__":
    main()