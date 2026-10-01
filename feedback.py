import cl
from cl import ChannelSet, StimDesign, BurstDesign
 
# ---- Which feedback encoding to test this run ----
# Change this and re-run to test the other two. Keep everything else
# identical between runs so the comparison is fair.
CONDITION = "rate"  # "rate", "temporal", or "spatial"
 
LEFT_CHANNELS = set(range(0, 10))
RIGHT_CHANNELS = set(range(10, 20))
WINDOW_TICKS = 50
 
# Channels used to deliver feedback stim — kept separate from the
# sensing channels above so we're not stimulating the same electrodes
# we're trying to read from.
FEEDBACK_CHANNELS = ChannelSet(list(range(20, 30)))
FEEDBACK_CHANNELS_POS = ChannelSet(list(range(20, 25)))
FEEDBACK_CHANNELS_NEG = ChannelSet(list(range(25, 30)))
 
BASE_STIM = StimDesign(160, -1.0, 160, 1.0)  # biphasic, negative leading edge
 
 
def feedback_rate(neurons, error):
    # Burst frequency scales with the size of the error. Capped at 180 Hz
    # to stay under the CL1's 200 Hz per-channel stim limit.
    freq = min(20 + abs(error) * 15, 180)
    burst = BurstDesign(5, freq)
    neurons.stim(FEEDBACK_CHANNELS, BASE_STIM, burst)
 
 
def feedback_temporal(neurons, error, prev_error):
    # Only fire a single, precisely-timed pulse at the moment the error
    # crosses zero (the cursor passing through center) — information is
    # in *when* it happens, not how much.
    if prev_error is not None and (prev_error >= 0) != (error >= 0):
        neurons.stim(FEEDBACK_CHANNELS, BASE_STIM)
 
 
def feedback_spatial(neurons, error):
    # Same stim strength every time; which *location* fires depends on
    # the sign of the error.
    burst = BurstDesign(5, 40)
    if error > 0:
        neurons.stim(FEEDBACK_CHANNELS_POS, BASE_STIM, burst)
    elif error < 0:
        neurons.stim(FEEDBACK_CHANNELS_NEG, BASE_STIM, burst)
 
 
def main():
    with cl.open() as neurons:
        print(f"Connected. Running condition='{CONDITION}' for 10 seconds...\n")
 
        history = []
        prev_error = None
 
        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=10):
            left_count = 0
            right_count = 0
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
 
            # Only deliver feedback once per window's worth of ticks,
            # not every single tick — keeps us well under stim rate
            # limits and makes each feedback event meaningful.
            if tick.iteration % WINDOW_TICKS == 0:
                if CONDITION == "rate":
                    feedback_rate(neurons, error)
                elif CONDITION == "temporal":
                    feedback_temporal(neurons, error, prev_error)
                elif CONDITION == "spatial":
                    feedback_spatial(neurons, error)
 
            if tick.iteration % 500 == 0:
                print(f"tick={tick.iteration:5d}  error={error:+4d}  "
                      f"stims_this_tick={len(tick.analysis.stims)}")
 
            prev_error = error
 
        print(f"\nDone. Condition '{CONDITION}' ran cleanly with feedback "
              "stims being delivered.")
 
 
if __name__ == "__main__":
    main()