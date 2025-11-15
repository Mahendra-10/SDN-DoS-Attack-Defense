# Architecture Documentation

## System Overview

This project simulates a Software-Defined Network (SDN) environment to test DoS (Denial of Service) attack detection and mitigation strategies. The architecture consists of several key components:

## Components

### 1. Network Layer (Mininet)

- **Purpose**: Emulates a physical network topology
- **Technology**: Mininet network emulator
- **Topologies**: 
  - Simple: 2 hosts, 1 switch
  - Extended: 3 hosts, 1 switch
- **Location**: `src/network/`

### 2. Control Layer (POX Controller)

- **Purpose**: Centralized network control via OpenFlow protocol
- **Technology**: POX SDN controller framework
- **Modes**:
  - **Flood Controller**: No protection, floods all packets
  - **Rate Limiting Controller**: Implements DoS protection via rate limiting
- **Location**: `src/controllers/`

### 3. Monitoring Layer

- **Purpose**: Collect metrics during experiments
- **Tools**:
  - `bwm-ng`: Network interface bandwidth monitoring
  - `cpu_track.py`: Controller CPU and memory usage
- **Location**: `src/monitoring/`

### 4. Visualization Layer

- **Purpose**: Generate graphs from collected metrics
- **Technology**: Matplotlib, Pandas
- **Outputs**:
  - Bandwidth plots per interface
  - Controller CPU utilization
  - Controller memory utilization
- **Location**: `src/visualization/`

## Data Flow

```
1. Network Initialization (Mininet)
   ↓
2. Controller Connection (POX)
   ↓
3. Monitoring Start (bwm-ng + cpu_track)
   ↓
4. DoS Attack Launch (hping3)
   ↓
5. Controller Response (flood or rate-limit)
   ↓
6. Monitoring Continue
   ↓
7. Attack Stop
   ↓
8. Monitoring Stop
   ↓
9. Graph Generation (create_graphs)
```

## Rate Limiting Algorithm

The rate limiting controller implements a simple but effective algorithm:

1. **Packet Counting**: Track packets per source IP per second
2. **Threshold Check**: If > 50 packets/second, trigger block
3. **Flow Rule Installation**: Install OpenFlow rule to drop packets
4. **Automatic Unblock**: Rule expires after 5 seconds (hard_timeout)

### Configuration

- Rate Threshold: 50 packets/second
- Block Duration: 5 seconds
- Reset Interval: 1 second (packet counter reset)

These values can be modified in `src/controllers/rate_limit.py`:

```python
RATE_THRESHOLD = 50  # packets per second
BLOCK_DURATION = 5   # seconds
```

## Network Topologies

### Simple Topology

```
h1 ---- s1 ---- h2
```

- Host 1 (h1): Attacker
- Switch 1 (s1): OpenFlow switch
- Host 2 (h2): Target

### Extended Topology

```
    h1
    |
    |
h2--s1--h3
```

- Can support multiple hosts
- Enables more complex attack scenarios

## Attack Mechanism

The DoS attack is simulated using `hping3`:

```bash
hping3 --flood <target_ip>
```

This generates a flood of packets from the attacker (h1) to the target (h2).

**Note**: This is a **DoS** (single-source) attack, not DDoS (distributed). For true DDoS simulation, multiple hosts would need to attack simultaneously.

## Metrics Collected

1. **Network Bandwidth**: Per interface (s1-eth1, s1-eth2)
2. **Controller CPU**: Percentage utilization over time
3. **Controller Memory**: Percentage utilization over time
4. **Timestamps**: Start, attack start, attack end, experiment end

## Results Structure

Each experiment run generates:

```
results/
├── timestamps.txt          # Experiment timestamps
├── bandwidth.txt           # Raw bandwidth data (CSV)
├── controller_usage.txt    # Controller resource usage
├── s1-eth1_bw_plot.png     # Bandwidth plot for interface 1
├── s1-eth2_bw_plot.png     # Bandwidth plot for interface 2
├── cont_cpu_plot.png       # Controller CPU utilization
└── cont_mem_plot.png       # Controller memory utilization
```

## Extension Points

The architecture supports easy extension:

1. **New Topologies**: Add to `src/network/topologies.py`
2. **New Defense Mechanisms**: Add controllers to `src/controllers/`
3. **Additional Metrics**: Extend `src/monitoring/`
4. **Custom Visualizations**: Modify `src/visualization/create_graphs.py`

