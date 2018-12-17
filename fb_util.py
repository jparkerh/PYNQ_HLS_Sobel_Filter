from pynq import DefaultIP, Xlnk
import numpy

class FrmBufRd(DefaultIP):
    def __init__(self, description):
        super().__init__(description=description)
        
    #Generic driver uses 24-bit RGB888 color format
    #This makes it easy to convert between openCV array and buffer

    bindto = ['xilinx.com:ip:v_frmbuf_rd:2.1']

    def initialize_params(self, width, height):
        #disable framebuffer
        self.write(0x0, 0x0)
        
        #set frame width
        self.write(0x10, int(width))
        
        #set frame height
        self.write(0x18, int(height))
        
        #set row memory displacement (bytes)
        self.write(0x20, int(width * 3))
        
        #set pixel format (always assuming RGB888)
        self.write(0x28, int(20))
        
    def start_fb(self):
        self.write(0x0, 0x1)
        
    def stop_fb(self):
        self.write(0x0, 0x0)
        
    def idle(self):
        return (self.read(0x0) & 0x4)
    
    def set_ptr_address(self, address):
        self.write(0x30, address)
    
class FrmBufWr(DefaultIP):
    def __init__(self, description):
        super().__init__(description=description)
        
    #Generic driver uses 24-bit RGB888 color format
    #This makes it easy to convert between openCV array and buffer

    bindto = ['xilinx.com:ip:v_frmbuf_wr:2.1']

    def initialize_params(self, width, height):
        
        #disable framebuffer
        self.write(0x0, 0x0)
        
        #set frame width
        self.write(0x10, int(width))
        
        #set frame height
        self.write(0x18, int(height))
        
        #set row memory displacement (bytes)
        self.write(0x20, int(width * 3))
        
        #set pixel format (always assuming RGB888)
        self.write(0x28, int(20))
        
    def start_fb(self):
        self.write(0x0, 0x1)
        
    def stop_fb(self):
        self.write(0x0, 0x0)
        
    def idle(self):
        return (self.read(0x0) & 0x4)
    
    def set_ptr_address(self, address):
        self.write(0x30, address)
    
class HLS_video_move():
    
    def __init__(self, push_obj_n, pull_obj_n, width, height):
        self.push_obj = push_obj_n
        self.pull_obj = pull_obj_n
        self.initialized = 0
        
        self.push_obj.initialize_params(width, height)
        self.pull_obj.initialize_params(width, height)
        
        self.initialize_mem(width, height)
        
    def start(self):
        if self.initialized:
            self.push_obj.start_fb()
            self.pull_obj.start_fb()
            
    def start_and_wait(self):
        if self.initialized:
            self.push_obj.start_fb()
            self.pull_obj.start_fb()
            while self.pull_obj.idle():
                pass
            while not self.pull_obj.idle():
                pass
            
    def stop(self):
        self.push_obj.stop_fb()
        self.pull_obj.stop_fb()
        
    def initialize_mem(self, width, height):
        xlnk = Xlnk()
        
        self.source_array = xlnk.cma_array(shape=(height, width, 3), dtype=numpy.uint8)
        self.dest_array = xlnk.cma_array(shape=(height, width, 3), dtype=numpy.uint8)
        
        self.push_obj.set_ptr_address(self.source_array.physical_address)
        self.pull_obj.set_ptr_address(self.dest_array.physical_address)
        
        self.initialized = True
        
        