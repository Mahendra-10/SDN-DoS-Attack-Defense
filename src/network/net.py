"""
SDN Network Manager for DoS Attack Simulation and Defense Testing.

This module handles network topology setup, DoS attack simulation,
and metrics collection for evaluating SDN-based defense mechanisms.
"""

from datetime import datetime
import os
import sys
import psutil
from subprocess import Popen, DEVNULL
import time
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.util import dumpNodeConnections

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from src.network.topologies import SimpleTopo, LessSimpleTopo
from src.visualization.create_graphs import create_all_graphs


class MyNetwork:
    """Manages SDN network setup, DoS attacks, and metrics collection."""

    def __init__(self, topology='simple', output_dir='results'):
        """
        Initialize network manager.
        
        Args:
            topology: 'simple' or 'extended' topology
            output_dir: Directory to save results and metrics
        """
        self.output_dir = output_dir
        self.topology_type = topology
        os.makedirs(output_dir, exist_ok=True)
        
        timestamps_file = os.path.join(output_dir, 'timestamps.txt')
        if os.path.exists(timestamps_file):
            os.remove(timestamps_file)
        self.ts_file = open(timestamps_file, 'w')
        
        self.cont_proc = None
        self.net = None

    def clean_env(self):
        """Clean Mininet environment."""
        print("* Cleaning Mininet environment")
        cmd = "sudo mn -c"
        print(f"** Running: {cmd}")
        Popen(cmd, shell=True).wait()
        print("* Done cleaning Mininet environment")
    
    def start_net(self, controller_ip='127.0.0.1', controller_port=6633):
        """Build the topology and initialize the network with a remote controller."""
        controller = RemoteController('c0', ip=controller_ip, port=controller_port)
        
        topo = SimpleTopo() if self.topology_type == 'simple' else LessSimpleTopo()
        self.net = Mininet(topo=topo, controller=controller)
        self.net.start()

        print("Dumping host connections")
        dumpNodeConnections(self.net.hosts)

        print("Testing network connectivity")
        self.net.pingAll()

    def stop_net(self):
        """Stop Mininet with current network."""
        if self.net:
            self.net.stop()

    def clear_metrics(self):
        """Clear previous metrics files."""
        print('* Clearing metrics')
        bandwidth_file = os.path.join(self.output_dir, 'bandwidth.txt')
        controller_usage_file = os.path.join(self.output_dir, 'controller_usage.txt')
        
        if os.path.exists(bandwidth_file):
            os.remove(bandwidth_file)
        if os.path.exists(controller_usage_file):
            os.remove(controller_usage_file)

    def start_metrics(self):
        """Start monitoring bandwidth and controller resources."""
        print('* Starting monitor')
        bandwidth_file = os.path.join(self.output_dir, 'bandwidth.txt')
        cmd = f"bwm-ng -o csv -T rate -C ',' > {bandwidth_file} &"
        Popen(cmd, shell=True).wait()
        
        controller_usage_file = os.path.join(self.output_dir, 'controller_usage.txt')
        # Get absolute path for the script
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../monitoring/cpu_track.py'))
        c_cmd = f"sudo python3 {script_path} {controller_usage_file}"
        self.cont_proc = Popen(c_cmd, shell=True)
        self.ts_file.write(str(time.time())+'\n')

    def stop_metrics(self):
        """Stop monitoring and clean up processes."""
        print('* Stopping monitor')
        cmd = "killall bwm-ng"
        Popen(cmd, shell=True).wait()
        
        if self.cont_proc:
            self.cont_proc.terminate()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'cpu_track.py' in ' '.join(cmdline):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.ts_file.write(str(time.time())+'\n')
        self.ts_file.close()

    def start_dos_attack(self):
        """Start DoS attack from h1 targeting h2."""
        print('* Starting DoS Attack')
        print("** Attack started at:", datetime.now())
        self.ts_file.write(str(time.time())+'\n')
        h1 = self.net.get('h1')
        h2_ip = self.net.get('h2').IP()
        h1.cmd(f"hping3 --flood {h2_ip} &")

    def stop_dos_attack(self):
        """Stop DoS attack."""
        print('* Stopping DoS Attack')
        self.ts_file.write(str(time.time())+'\n')
        cmd = "killall hping3"
        Popen(cmd, shell=True).wait()
        print("** Attack stopped at:", datetime.now())
    
    def create_graphs(self):
        """Generate visualization graphs from collected metrics."""
        print('* Creating Graphs')
        create_all_graphs(self.output_dir)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SDN DoS Attack Simulation')
    parser.add_argument('--topology', choices=['simple', 'extended'], default='simple',
                        help='Network topology to use')
    parser.add_argument('--output', default='results',
                        help='Output directory for results')
    parser.add_argument('--attack-duration', type=int, default=5,
                        help='Duration of DoS attack in seconds')
    parser.add_argument('--controller-ip', default='127.0.0.1',
                        help='SDN controller IP address')
    parser.add_argument('--controller-port', type=int, default=6633,
                        help='SDN controller port')
    
    args = parser.parse_args()
    
    setLogLevel('info')
    net = MyNetwork(topology=args.topology, output_dir=args.output)
    net.clean_env()
    net.clear_metrics()
    net.start_net(controller_ip=args.controller_ip, controller_port=args.controller_port)
    net.start_metrics()
    time.sleep(5)
    
    # Start DoS attack
    net.start_dos_attack()
    time.sleep(args.attack_duration)
    
    # Stop attack and collect recovery metrics
    net.stop_dos_attack()
    time.sleep(15)
    
    net.stop_metrics()
    net.stop_net()
    net.clean_env()
    net.create_graphs()
    
    print(f"\n* Results saved in: {args.output}")

