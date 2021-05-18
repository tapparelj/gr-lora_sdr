from gnuradio import gr, gr_unittest
from gnuradio import blocks
import numpy as np
import pmt

SYNC_TYPE_VOID = 0
SYNC_TYPE_UPCHIRP = 1
SYNC_TYPE_SYNCWORD = 2
SYNC_TYPE_DOWNCHIRP = 3
SYNC_TYPE_QUARTERDOWN = 4
SYNC_TYPE_PAYLOAD = 5
SYNC_TYPE_UNDETERMINED = 6

def gr_cast(x):
    return [complex(z) for z in x]

def np_cast(x):
    return np.complex64(x)

class TagSink(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self, name='Tag sink', in_sig=[float], out_sig=None)
        self.tags = []

    def work(self, input_items, output_items):
        elems = self.get_tags_in_window(0, 0, len(input_items[0]))
        for t in elems:
            self.tags.append(gr.tag_to_python(t))

        return len(input_items[0])

    def get_tags(self):
        tags = self.tags
        self.tags = []
        return tags

class TagSinkInt(TagSink):
    def __init__(self):
        gr.sync_block.__init__(self, name='Tag sink', in_sig=[np.int32], out_sig=None)
        self.tags = []

class Tagger(gr.sync_block):
    def __init__(self, tags):
        gr.sync_block.__init__(self, name='Tagger', in_sig=[float], out_sig=[float])
        self.tags = tags # dictionary {offset:(name, dict)}

    def work(self, input_items, output_items):
        for idx, _ in enumerate(input_items[0]):
            abs_idx = self.nitems_written(0) + idx
            if abs_idx in self.tags:
                key = pmt.intern(self.tags[abs_idx][0])
                d = pmt.make_dict()
                for k,v in self.tags[abs_idx][1].items():
                    if isinstance(v, str):
                        pmt_v = pmt.intern(v)
                    elif isinstance(v, int):
                        pmt_v = pmt.from_long(v)
                    elif isinstance(v, float):
                        pmt_v = pmt.from_double(v)
                    else:
                        raise TypeError("The type {} is not supported as value in a new_user tag.".format(type(v)))

                    d = pmt.dict_add(d, pmt.intern(k), pmt_v)

                self.add_item_tag(0, abs_idx, key, d)

        output_items[0][:] = input_items[0] # copy input to output
        return len(output_items[0])