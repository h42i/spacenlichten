from subprocess import call
from ipaddress import ip_address

IFCONFIG = 0
IP = 1

class AliasError(Exception):
    pass

class AliasControl:
    def __init__(self, iface, iface_tool=IP):
        self._iface = iface
        self._iface_tool = iface_tool
        
        self._bound_ipv4 = []
        self._viface_counter = 1
        
        self._bound_ipv6 = []
    
    def __del__(self):
        while self._bound_ipv4:
            (stored_ip, stored_prefix_len, stored_number) = self._bound_ipv4[0]
            
            self._ipv4_set_viface_down(stored_ip, stored_prefix_len)
            
        while self._bound_ipv6:
            (stored_ip, stored_prefix_len) = self._bound_ipv6[0]
            
            self._ipv6_remove_alias(stored_ip, stored_prefix_len)

    def _ipv4_configure_viface(self, ip, prefix_len, number):
        result = -1
        
        if self._iface_tool == IFCONFIG:
            result = call(["ifconfig", self._iface + ":" + str(number), ip + "/" + str(prefix_len)])
        elif self._iface_tool == IP:
            result = call(["ip", "addr", "add", ip + "/" + str(prefix_len), "dev", self._iface, "label", self._iface + ":" + str(number)])
        
        if result != 0:
            raise AliasError("Could not configure virtual interface " + self._iface + ":" + str(number) + ".")
        else:
            self._bound_ipv4.append((ip, prefix_len, number))

    def _ipv4_set_viface_up(self, ip, prefix_len):
        result = -1
        
        for ipv4_alias in self._bound_ipv4:
                (stored_ip, stored_prefix_len, stored_number) = ipv4_alias
                
                if stored_ip == ip and stored_prefix_len == prefix_len:
                    if self._iface_tool == IFCONFIG:
                        result = call(["ifconfig", self._iface + ":" + str(stored_number), "up"])
                    elif self._iface_tool == IP:
                        # nothing to do, it's just one step with ip.
                        result = 0
        
        if result != 0:
            raise AliasError("Could not set up virtual interface with ip " + ip + ".")

    def _ipv4_set_viface_down(self, ip, prefix_len):
        result = -1
        
        for ipv4_alias in self._bound_ipv4:
                (stored_ip, stored_prefix_len, stored_number) = ipv4_alias
                
                if stored_ip == ip and stored_prefix_len == prefix_len:
                    if self._iface_tool == IFCONFIG:
                        result = call(["ifconfig", self._iface + ":" + str(stored_number), "down"])
                    elif self._iface_tool == IP:
                        result = call(["ip", "addr", "del", ip + "/" + str(prefix_len), "dev", self._iface, "label", self._iface + ":" + str(stored_number)])
                    
                    if result == 0:
                        self._bound_ipv4.remove(ipv4_alias)
        
        # no such interface has been set up.
        if result != 0:
            raise AliasError("Could not set down virtual interface with ip " + ip + ".")

    def _ipv6_add_alias(self, ip, prefix_len):
        result = -1
        
        if self._iface_tool == IFCONFIG:
            result = call(["ifconfig", self._iface, "inet6", "add", ip + "/" + str(prefix_len)])
        elif self._iface_tool == IP:
            result = call(["ip", "-6", "addr", "add", ip + "/" + str(prefix_len), "dev", self._iface])
            
        if result != 0:
            raise AliasError("Could not add alias to interface " + self._iface + ".")
        else:
            self._bound_ipv6.append((ip, prefix_len))

    def _ipv6_remove_alias(self, ip, prefix_len):
        result = -1
        
        if self._iface_tool == IFCONFIG:
            result = call(["ifconfig", self._iface, "inet6", "del", ip + "/" + str(prefix_len)])
        elif self._iface_tool == IP:
            result = call(["ip", "-6", "addr", "del", ip + "/" + str(prefix_len), "dev", self._iface])
            
        if result != 0:
            raise AliasError("Could not remove alias from interface " + self._iface + ".")
        else:
            for ipv6_alias in self._bound_ipv6:
                (stored_ip, stored_prefix_len) = ipv6_alias
                
                if stored_ip == ip and stored_prefix_len == prefix_len:
                    self._bound_ipv6.remove(ipv6_alias)

    def add_alias(self, ip, prefix_len):
        ip_version = ip_address(ip).version
        
        if ip_version == 4:
            self._ipv4_configure_viface(ip, prefix_len, self._viface_counter)
            self._ipv4_set_viface_up(ip, prefix_len)
            
            self._viface_counter = self._viface_counter + 1
        elif ip_version == 6:
            self._ipv6_add_alias(ip, prefix_len)
    
    def remove_alias(self, ip, prefix_len):
        ip_version = ip_address(ip).version
        
        if ip_version == 4:
            self._ipv4_set_viface_down(ip, prefix_len)
        elif ip_version == 6:
            self._ipv6_remove_alias(ip, prefix_len)
