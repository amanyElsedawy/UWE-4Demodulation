import struct
from gnuradio import gr, blocks, filter, digital, analog
from gnuradio.fft import window
import pmt

import numpy as np

class nrzi_decoder(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, name="NRZI Decoder",
            in_sig=[np.uint8], out_sig=[np.uint8])
        self.last = 0
    def work(self, input_items, output_items):
        for i in range(len(input_items[0])):
            c = input_items[0][i] & 1
            output_items[0][i] = 1 if c == self.last else 0
            self.last = c
        return len(output_items[0])

class frame_collector(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self, name="Collector", in_sig=[], out_sig=[])
        self.frames = []
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle)
    def handle(self, msg):
        try:
            d = bytes(pmt.u8vector_elements(pmt.cdr(msg)))
            self.frames.append(d)
        except Exception as e:
            pass

def run_test(invert, gain_mu, descramble_first):
    tb = gr.top_block("test")
    samp_rate = 57600
    baud_rate = 9600
    sps = samp_rate / baud_rate

    # file is short interleaved
    src = blocks.file_source(gr.sizeof_short, r"D:\demodulation\UWEIQ\iq_14011420_435599000_57600.raw", False)
    i2c = blocks.interleaved_short_to_complex(False, False)
    
    # Scale from int16 to float roughly
    scale = blocks.multiply_const_cc(1.0/32768.0)

    # Low pass filter for 9600 FSK
    taps = filter.firdes.low_pass(1.0, samp_rate, 7500, 1500, window.WIN_HAMMING)
    lpf = filter.fir_filter_ccf(1, taps)

    # Quad Demod
    # deviation ~ 2400-3000 Hz
    k = samp_rate / (2 * 3.14159 * 2400)
    if invert:
        k = -k
    demod = analog.quadrature_demod_cf(k)

    # Clock recovery
    clk = digital.clock_recovery_mm_ff(sps, 0.25 * gain_mu**2, 0.5, gain_mu, 0.005)

    # Slicer
    slicer = digital.binary_slicer_fb()

    # Descrambler
    descrambler = digital.descrambler_bb(0x21, 0, 16)

    # NRZI
    nrzi = nrzi_decoder()

    # Deframer
    hdlc = digital.hdlc_deframer_bp(32, 500)
    
    col = frame_collector()

    tb.connect(src, i2c, scale, lpf, demod, clk, slicer)
    if descramble_first:
        tb.connect(slicer, descrambler, nrzi, hdlc)
    else:
        tb.connect(slicer, nrzi, descrambler, hdlc)

    tb.msg_connect(hdlc, "out", col, "in")

    tb.run()
    return col.frames

if __name__ == '__main__':
    print("Testing permutations...")
    best = []
    for inv in [False, True]:
        for gmu in [0.175, 0.3]:
            for d_first in [True, False]:
                print(f"inv={inv}, gmu={gmu}, d_first={d_first}")
                frames = run_test(inv, gmu, d_first)
                print(f" -> Found {len(frames)} frames")
                if len(frames) > len(best):
                    best = frames
                    print("New best!")
    
    with open(r"D:\demodulation\UWEIQ\UWEiq.hex", "w") as f:
        for fr in best:
            hex_str = " ".join(f"{b:02X}" for b in fr)
            print(f"Frame (Hex): {hex_str}")
            f.write(hex_str + "\n")

    with open(r"D:\demodulation\UWEIQ\UWEiq.bin", "wb") as f:
        for fr in best:
            f.write(fr)
    print("Done")
