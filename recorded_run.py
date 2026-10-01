import cl
from cl import ChannelSet, StimDesign, BurstDesign
 
CONDITION = "spatial"  # "rate", "temporal", or "spatial" — change per run
OUTPUT_DIR = f"recordings/{CONDITION}"  # each condition gets its own folder
 
LEFT_CHANNELS = set(range(0, 10))
RIGHT_CHANNELS = set(range(10, 20))
WINDOW_TICKS = 50
 
FEEDBACK_CHANNELS = ChannelSet(list(range(20, 30)))
FEEDBACK_CHANNELS_POS = ChannelSet(list(range(20, 25)))
FEEDBACK_CHANNELS_NEG = ChannelSet(list(range(25, 30)))
 
BASE_STIM = StimDesign(160, -1.0, 160, 1.0)
 
 
def feedback_rate(neurons, error):
    freq = min(20 + abs(error) * 15, 180)
    neurons.stim(FEEDBACK_CHANNELS, BASE_STIM, BurstDesign(5, freq))
 
 
def feedback_temporal(neurons, error, prev_error):
    if prev_error is not None and (prev_error >= 0) != (error >= 0):
        neurons.stim(FEEDBACK_CHANNELS, BASE_STIM)
 
 
def feedback_spatial(neurons, error):
    burst = BurstDesign(5, 40)
    if error > 0:
        neurons.stim(FEEDBACK_CHANNELS_POS, BASE_STIM, burst)
    elif error < 0:
        neurons.stim(FEEDBACK_CHANNELS_NEG, BASE_STIM, burst)
 
 
def main():
    with cl.open() as neurons:
        # record() is NOT a context manager — it starts recording
        # immediately and returns a handle you stop() later yourself.
        # file_location sets the output directory; the filename itself
        # is auto-generated and timestamped by the system.
        recording = neurons.record(file_location=OUTPUT_DIR)
 
        # A named channel in the recording for your own logged values.
        # 'attributes' declares default/initial values for the stream.
        log = neurons.create_data_stream(
            name="experiment_log",
            attributes={"condition": CONDITION, "error": 0, "stimmed": False},
        )
 
        print(f"Recording to {OUTPUT_DIR}/, condition='{CONDITION}'...\n")
 
        history = []
        prev_error = None
 
        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=10):
            left_count = right_count = 0
            for spike in tick.analysis.spikes:
                if spike.channel in LEFT_CHANNELS:
                    left_count += 1
                elif spike.channel in RIGHT_CHANNELS:
                    right_count += 1
 
            history.append((left_count, right_count))
            if len(history) > WINDOW_TICKS:
                history.pop(0)
 
            left_total = sum(l for l, r in history)
            right_total = sum(r for l, r in history)
            error = right_total - left_total
 
            stimmed = False
            if tick.iteration % WINDOW_TICKS == 0:
                if CONDITION == "rate":
                    feedback_rate(neurons, error)
                    stimmed = True
                elif CONDITION == "temporal":
                    crossed = prev_error is not None and (
                        (prev_error >= 0) != (error >= 0)
                    )
                    feedback_temporal(neurons, error, prev_error)
                    stimmed = crossed
                elif CONDITION == "spatial":
                    feedback_spatial(neurons, error)
                    stimmed = error != 0
 
            # append(timestamp, value) — value can be any dict/list/etc.
            # Use tick.analysis.start_timestamp, not the deprecated
            # neurons.timestamp(), and each call must use a strictly
            # ascending timestamp.
            log.append(
                tick.analysis.start_timestamp,
                {"condition": CONDITION, "error": error, "stimmed": stimmed},
            )
 
            if tick.iteration % 500 == 0:
                print(f"tick={tick.iteration:5d}  error={error:+4d}  "
                      f"stimmed={stimmed}")
 
            prev_error = error
 
        recording.stop()
        print(f"\nDone. Recording saved under {OUTPUT_DIR}/")
 
 
if __name__ == "__main__":
    main()
 