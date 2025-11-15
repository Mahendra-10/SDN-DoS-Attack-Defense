"""
Visualization module for generating graphs from collected metrics.

Generates plots for:
- Network interface bandwidth
- Controller CPU and memory utilization
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def create_bandwidth_plot(bw_df, interface, timestamps, output_dir):
    """
    Create bandwidth plot for a specific network interface.
    
    Args:
        bw_df: Bandwidth DataFrame
        interface: Interface name (e.g., 's1-eth1')
        timestamps: List of timestamps [start, dos_start, dos_end, end]
        output_dir: Output directory for the plot
    """
    start, dos_start, dos_end, end = timestamps
    
    # Filter data for the interface
    eth_data = bw_df.loc[bw_df[1] == interface][[0, 4]]
    eth_data = eth_data.rename(columns={0: 'epochtime', 4: 'bandwidth'})
    eth_data['time'] = pd.to_datetime(bw_df.loc[bw_df[1] == interface][0], unit='s')
    eth_data = eth_data.drop(['epochtime'], axis=1).set_index('time')
    
    # Filter by time range and smooth
    eth_data.index = pd.to_datetime(eth_data.index)
    eth_data = eth_data[eth_data.index >= start]
    eth_data = eth_data[eth_data.index <= end]
    eth_data['bandwidth'] = eth_data['bandwidth'].rolling(window=3, min_periods=1).mean()
    
    # Create plot
    eth_data.plot(y='bandwidth', legend=False)
    plt.xlabel('Time')
    plt.ylabel('Bandwidth (bytes/sec)')
    plt.title(f'{interface} Bandwidth Over Time')
    plt.grid(True)
    plt.axvline(x=dos_start, color='red', linestyle='--', label='DoS Start')
    plt.axvline(x=dos_end, color='orange', linestyle='--', label='DoS End')
    plt.legend()
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, f'{interface}_bw_plot.png')
    plt.savefig(output_file)
    plt.close()
    print(f"  Created: {output_file}")


def create_controller_plots(controller_file, timestamps, output_dir):
    """
    Create CPU and memory utilization plots for the controller.
    
    Args:
        controller_file: Path to controller usage log file
        timestamps: List of timestamps [start, dos_start, dos_end, end]
        output_dir: Output directory for the plots
    """
    start, dos_start, dos_end, end = timestamps
    
    # Parse controller usage data
    data = []
    with open(controller_file, "r") as f:
        for line in f:
            parts = line.strip().split(", ")
            timestamp_str = parts[0]
            cpu_str = parts[1].replace("CPU: ", "").replace("%", "")
            mem_str = parts[2].replace("MEM: ", "").replace("%", "")        
            data.append({
                "time": pd.to_datetime(timestamp_str),
                "cpu": float(cpu_str),
                "mem": float(mem_str)
            })
    
    con_df = pd.DataFrame(data)
    con_df.set_index("time", inplace=True)
    
    # Create CPU plot
    con_cpu_df = con_df[['cpu']]
    con_cpu_df.index = pd.to_datetime(con_cpu_df.index)
    con_cpu_df = con_cpu_df[con_cpu_df.index >= start]
    con_cpu_df = con_cpu_df[con_cpu_df.index <= end]
    con_cpu_df['cpu'] = con_cpu_df['cpu'].rolling(window=3, min_periods=1).mean()
    con_cpu_df.plot(y='cpu', legend=False)
    plt.xlabel('Time')
    plt.ylabel('CPU (percentage)')
    plt.title('Controller CPU Utilization Over Time')
    plt.grid(True)
    plt.axvline(x=dos_start, color='red', linestyle='--', label='DoS Start')
    plt.axvline(x=dos_end, color='orange', linestyle='--', label='DoS End')
    plt.legend()
    plt.tight_layout()
    
    cpu_output = os.path.join(output_dir, 'cont_cpu_plot.png')
    plt.savefig(cpu_output)
    plt.close()
    print(f"  Created: {cpu_output}")
    
    # Create Memory plot
    con_mem_df = con_df[['mem']]
    con_mem_df.index = pd.to_datetime(con_mem_df.index)
    con_mem_df = con_mem_df[con_mem_df.index >= start]
    con_mem_df = con_mem_df[con_mem_df.index <= end]
    con_mem_df['mem'] = con_mem_df['mem'].rolling(window=3, min_periods=1).mean()
    con_mem_df.plot(y='mem', legend=False)
    plt.xlabel('Time')
    plt.ylabel('Memory (percentage)')
    plt.title('Controller Memory Utilization Over Time')
    plt.grid(True)
    plt.axvline(x=dos_start, color='red', linestyle='--', label='DoS Start')
    plt.axvline(x=dos_end, color='orange', linestyle='--', label='DoS End')
    plt.legend()
    plt.tight_layout()
    
    mem_output = os.path.join(output_dir, 'cont_mem_plot.png')
    plt.savefig(mem_output)
    plt.close()
    print(f"  Created: {mem_output}")


def create_all_graphs(output_dir='results'):
    """
    Generate all visualization graphs from collected metrics.
    
    Args:
        output_dir: Directory containing metrics files and where plots will be saved
    """
    print(f"* Generating graphs from data in: {output_dir}")
    
    # Clean up old plots
    plot_files = ['cont_cpu_plot.png', 'cont_mem_plot.png', 
                  's1-eth1_bw_plot.png', 's1-eth2_bw_plot.png']
    for plot_file in plot_files:
        plot_path = os.path.join(output_dir, plot_file)
        if os.path.exists(plot_path):
            os.remove(plot_path)
    
    # Read timestamps
    timestamps_file = os.path.join(output_dir, 'timestamps.txt')
    if not os.path.exists(timestamps_file):
        print(f"Error: {timestamps_file} not found")
        return
    
    with open(timestamps_file, 'r') as file:
        timestamps = [float(line.strip()) for line in file]
    timestamps = pd.to_datetime(timestamps, unit='s')
    
    start = timestamps[0]
    dos_start = timestamps[1]
    dos_end = timestamps[2]
    end = timestamps[3] if len(timestamps) > 3 else timestamps[2]
    
    # Read bandwidth data
    bandwidth_file = os.path.join(output_dir, 'bandwidth.txt')
    if not os.path.exists(bandwidth_file):
        print(f"Warning: {bandwidth_file} not found, skipping bandwidth plots")
    else:
        bw_df = pd.read_csv(bandwidth_file, header=None)
        
        # Create bandwidth plots for each interface
        for interface in ['s1-eth1', 's1-eth2']:
            if interface in bw_df[1].values:
                create_bandwidth_plot(bw_df, interface, 
                                    [start, dos_start, dos_end, end], 
                                    output_dir)
    
    # Create controller plots
    controller_file = os.path.join(output_dir, 'controller_usage.txt')
    if not os.path.exists(controller_file):
        print(f"Warning: {controller_file} not found, skipping controller plots")
    else:
        create_controller_plots(controller_file, 
                              [start, dos_start, dos_end, end], 
                              output_dir)
    
    print("* Graph generation complete")


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'results'
    create_all_graphs(output_dir)

