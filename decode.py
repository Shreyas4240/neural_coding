import cl 

# aribitrary for now - change for cl1 compute 
LEFT_CHANNELS = set(range(0, 10)) # ch 0-9 
RIGHT_CHANNELS = set(range(10, 20)) # 10-19 

# big window = smooth signal, but slower reaction
WINDOW_TICKS = 50 

def main():
    with cl.open() as neurons:
        print("connected")
        history = [] 
        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=5):
            left_this_tick = 0
            right_this_tick = 0 

            for spike in tick.analysis.spikes:
                if spike.channel in LEFT_CHANNELS:
                    left_this_tick += 1 
                elif spike.channel in RIGHT_CHANNELS:
                    right_this_tick += 1
                
            history.append((left_this_tick, right_this_tick))
            if len(history) > WINDOW_TICKS:
                history.pop(0)
            
            left_total = sum(l for l, r in history)
            right_total = sum(r for l, r in history)

            error = right_total - left_total 

            if tick.iteration % 500 == 0:
                print(f"tick={tick.iteration:5d}  left={left_total:3d}  "
                      f"right={right_total:3d}  error={error:+4d}")
        print("\n Done")

if __name__ == "__main__":
    main()