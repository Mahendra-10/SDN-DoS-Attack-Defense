"""
POX Controller: Flood-based forwarding without rate limiting.

This controller implements a simple flooding approach where all packets
are flooded to all ports without any rate limiting or DoS protection.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.packet.ethernet import ethernet
import pox.lib.packet as pkt
from collections import defaultdict
import time

log = core.getLogger()

packet_counts = defaultdict(int)
blocked_hosts = {}
last_reset = time.time()


def _handle_PacketIn(event):
    """
    Handle incoming packets by flooding them to all ports.
    
    This is a basic implementation without any rate limiting
    or DoS protection mechanisms.
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
        if now - last_reset >= 1:
            for key, value in packet_counts.items():
                print(f"{key}: {value}")
            packet_counts.clear()
            last_reset = now

        packet_counts[src] += 1

    # Flood packet to all ports
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    event.connection.send(msg)


def launch():
    """Initialize the controller and register packet handler."""
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("Flood controller started (no rate limiting)")

