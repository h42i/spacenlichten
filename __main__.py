import sys
import os

from spacenlichten import node
from spacenlichten import aliasing

if __name__ == "__main__":
    main_node = node.Node(sys.argv[1], "wlp3s0", aliasing.IP)
    
    main_node.start()
    
    while input() != "die":
        pass
    
    main_node.stop()
