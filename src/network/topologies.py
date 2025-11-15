"""
Network topology definitions for SDN DoS attack simulation.
"""

from mininet.topo import Topo


class SimpleTopo(Topo):
    """Simple topology with 2 hosts and 1 switch."""
    
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        self.addLink(h1, s1)
        self.addLink(h2, s1)


class LessSimpleTopo(Topo):
    """Extended topology with 3 hosts and 1 switch."""
    
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

