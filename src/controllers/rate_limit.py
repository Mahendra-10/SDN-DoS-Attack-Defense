"""
POX Controller: Flood-based forwarding with rate limiting for DoS protection.

This controller implements rate limiting to mitigate DoS attacks by blocking
hosts that exceed a threshold packet rate (default: 50 packets/second).
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.packet.ethernet import ethernet
import pox.lib.packet as pkt
from collections import defaultdict
import time

log = core.getLogger()

# Rate limiting configuration
RATE_THRESHOLD = 50  # packets per second
BLOCK_DURATION = 5   # seconds

packet_counts = defaultdict(int)
blocked_hosts = {}
last_reset = time.time()


def _handle_PacketIn(event):
    """
    Handle incoming packets with rate limiting protection.
    
    If a source IP exceeds the rate threshold, it will be blocked
    for a specified duration.
    """
    global last_reset
    now = time.time()
    
    do_rl = True
    try:
        packet = event.parsed
        ip_packet = packet.find('ipv4')
        src = ip_packet.srcip
    except:
        do_rl = False

    if do_rl:
        # Reset packet counts every second
        if now - last_reset >= 1:
            for key, value in packet_counts.items():
                print(f"{key}: {value}")
            packet_counts.clear()
            last_reset = now

        packet_counts[src] += 1

        # Rate limiting: block if threshold exceeded
        if packet_counts[src] > RATE_THRESHOLD:
            log.warning(f"Rate limit exceeded for {src}: {packet_counts[src]} pps")
            match = of.ofp_match()
            match.dl_type = packet.type
            match.nw_src = src
            msg = of.ofp_flow_mod()
            msg.match = match
            msg.priority = 1000
            msg.hard_timeout = BLOCK_DURATION
            msg.actions = []  # Empty actions = drop packet
            event.connection.send(msg)
            log.info(f"Blocked {src} for {BLOCK_DURATION} seconds")

    # Flood packet to all ports
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)


def launch():
    """Initialize the controller and register packet handler."""
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info(f"Rate limiting controller started (threshold: {RATE_THRESHOLD} pps)")

