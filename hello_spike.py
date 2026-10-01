import cl 

def main():
    with cl.open() as neurons:
        print("connected - starting 1000hz loop for 5s")
        spike_count = 0 

        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=5):
            for spike in tick.analysis.spikes:
                spike_count+=1 
                # only print first 20 spikes 
                if spike_count <= 20:
                    # spike.channel gives which electrode
                    print(f"Spike #{spike_count}: channel={spike.channel}"
                          f"timestamp={spike.timestamp}")
        print(f"\nDone. Detected {spike_count} spikes in 5s")

if __name__ == "__main__":
    main()
                    