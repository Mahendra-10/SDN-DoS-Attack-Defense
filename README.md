# SDN DoS Attack Defense

A Software-Defined Networking (SDN) simulation framework for testing DoS (Denial of Service) attack detection and mitigation strategies using POX controller and Mininet.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project simulates a Software-Defined Network environment to study DoS attack patterns and evaluate defense mechanisms. It compares two SDN controller approaches:

1. **Flood Controller**: Basic packet flooding without protection
2. **Rate Limiting Controller**: Implements rate limiting to mitigate DoS attacks

The framework monitors network bandwidth, controller resource utilization, and generates visualizations to analyze attack impact and defense effectiveness.

## ✨ Features

- **Network Simulation**: Uses Mininet for realistic SDN network emulation
- **DoS Attack Simulation**: Flood-based DoS attack using hping3
- **Two Controller Modes**:
  - No protection (flood controller)
  - Rate limiting protection (threshold: 50 packets/second)
- **Real-time Monitoring**: 
  - Network interface bandwidth
  - Controller CPU and memory usage
- **Automated Visualization**: Generates graphs for analysis
- **Configurable Topologies**: Simple and extended network topologies

## 📁 Project Structure

```
SDN-DoS-Attack-Defense/
├── src/
│   ├── network/           # Network topology and management
│   │   ├── topologies.py  # Network topology definitions
│   │   └── net.py         # Network manager and main simulation
│   ├── controllers/       # POX SDN controllers
│   │   ├── flood_cont.py  # Flood controller (no protection)
│   │   └── rate_limit.py  # Rate limiting controller
│   ├── monitoring/        # Resource monitoring tools
│   │   └── cpu_track.py   # Controller CPU/memory monitor
│   └── visualization/     # Data visualization
│       └── create_graphs.py  # Graph generation
├── results/               # Experiment results (generated)
│   ├── no_rate_limit/    # Results without protection
│   └── rate_limit/       # Results with rate limiting
├── scripts/              # Helper scripts
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Prerequisites

- **Operating System**: Linux (Ubuntu recommended) or macOS with Linux VM
- **Python**: Python 3.7+
- **Mininet**: Network emulation platform
- **POX Controller**: SDN controller framework
- **System Tools**:
  - `hping3`: For DoS attack simulation
  - `bwm-ng`: For bandwidth monitoring
  - `sudo` access: Required for Mininet operations

## 📦 Installation

### 1. Install Mininet

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install mininet

# Or build from source
git clone https://github.com/mininet/mininet.git
cd mininet
sudo ./util/install.sh -a
```

### 2. Install POX Controller

```bash
cd ~
git clone https://github.com/noxrepo/pox.git
cd pox
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 4. Install System Tools

```bash
# Ubuntu/Debian
sudo apt-get install hping3 bwm-ng

# macOS (requires Homebrew)
brew install hping bwm-ng
```

## 🚀 Usage

### Step 1: Copy Controller to POX Directory

Choose which controller to use and copy it to your POX directory:

**For Flood Controller (No Protection):**
```bash
cp src/controllers/flood_cont.py ~/pox/pox/misc/
```

**For Rate Limiting Controller:**
```bash
cp src/controllers/rate_limit.py ~/pox/pox/misc/
```

### Step 2: Start POX Controller

In a separate terminal, start the POX controller:

**Flood Controller:**
```bash
cd ~/pox
./pox.py log.level --DEBUG misc.flood_cont
```

**Rate Limiting Controller:**
```bash
cd ~/pox
./pox.py log.level --DEBUG misc.rate_limit
```

Ensure the controller is listening on `localhost:6633` (default).

### Step 3: Run the Simulation

From the project root directory:

```bash
sudo python3 src/network/net.py
```

Or with custom options:

```bash
sudo python3 src/network/net.py \
    --topology simple \
    --output results/my_experiment \
    --attack-duration 10 \
    --controller-ip 127.0.0.1 \
    --controller-port 6633
```

### Command Line Options

- `--topology`: Choose topology (`simple` or `extended`)
- `--output`: Output directory for results (default: `results`)
- `--attack-duration`: Duration of DoS attack in seconds (default: 5)
- `--controller-ip`: SDN controller IP address (default: `127.0.0.1`)
- `--controller-port`: SDN controller port (default: `6633`)

### Step 4: View Results

Results including graphs will be saved in the output directory:
- `*_bw_plot.png`: Network interface bandwidth over time
- `cont_cpu_plot.png`: Controller CPU utilization
- `cont_mem_plot.png`: Controller memory utilization
- `timestamps.txt`: Experiment timestamps
- `bandwidth.txt`: Raw bandwidth data
- `controller_usage.txt`: Controller resource usage data

## 🏗️ Architecture

### Network Topology

**Simple Topology:**
```
    h1 ---- s1 ---- h2
```

**Extended Topology:**
```
    h1
    |
    |
h2--s1--h3
```

### DoS Attack Flow

1. Network is initialized with Mininet
2. POX controller manages switch forwarding
3. Monitoring tools start collecting metrics
4. DoS attack begins: `h1` floods `h2` with packets using `hping3`
5. Controller responds (either floods or rate-limits based on mode)
6. Metrics continue to be collected post-attack
7. Visualizations are generated from collected data

### Rate Limiting Mechanism

The rate limiting controller:
- Tracks packet rate per source IP
- Calculates packets per second (pps)
- Blocks sources exceeding 50 pps for 5 seconds
- Automatically unblocks after timeout

## 📊 Results

The framework generates several visualizations:

1. **Bandwidth Plots**: Show traffic on network interfaces during attack
2. **CPU Utilization**: Controller processing load during attack
3. **Memory Utilization**: Controller memory usage during attack

Compare results between `results/no_rate_limit/` and `results/rate_limit/` to see the effectiveness of rate limiting.

## 🛠️ Troubleshooting

### Controller Connection Issues

If the controller fails to connect:
```bash
# Check if controller is running
netstat -an | grep 6633

# Verify controller logs for errors
```

### Permission Issues

Ensure you have sudo access:
```bash
sudo python3 src/network/net.py
```

### Missing Dependencies

Install missing Python packages:
```bash
pip3 install --upgrade -r requirements.txt
```

### Mininet Cleanup

If Mininet gets stuck:
```bash
sudo mn -c
```

## 📝 Notes

- **DoS vs DDoS**: This project simulates **DoS** (single-source) attacks, not DDoS (distributed attacks). For true DDoS, multiple hosts would need to attack simultaneously.
- **Rate Limiting Parameters**: Default threshold is 50 packets/second with a 5-second block duration. These can be modified in `src/controllers/rate_limit.py`.
- **Controller Performance**: The POX controller runs in a single Python process, so performance metrics may vary based on system resources.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for improvement:

- Support for true DDoS (multiple attackers)
- Additional defense mechanisms
- More sophisticated topologies
- Enhanced visualization features

## 📄 License

This project is open source and available for educational and research purposes.

## 🙏 Acknowledgments

- Mininet project for network emulation
- POX project for SDN controller framework
- OpenFlow protocol for SDN standardization

---

**Note**: This tool is intended for educational and research purposes only. Do not use for unauthorized testing on networks you don't own or have explicit permission to test.
