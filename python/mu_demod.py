#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr
from gnuradio import blocks
import numpy as np
from enum import Enum
import time


SYNC_TYPE_VOID = 0
SYNC_TYPE_UPCHIRP = 1
SYNC_TYPE_SYNCWORD = 2
SYNC_TYPE_DOWNCHIRP = 3
SYNC_TYPE_QUARTERDOWN = 4
SYNC_TYPE_PAYLOAD = 5
SYNC_TYPE_UNDETERMINED = 6

class UserState(Enum):
    NONE = 0
    PREAMBLE = 1
    PAYLOAD = 2

THRESHOLD_sync_error = 4

"""
    Aggregate the output of multiple partial_ml blocks and select the most likely symbols for each user.
"""
class ml_aggreg(gr.basic_block):
    def __init__(self, SF, Ku):
        self.N = 2**SF
        self.Ku = Ku
        self.prev_Mi2 = [0] * self.N   
        self.prev_Ti2 = UserState.NONE
        self.user_states = [UserState.NONE, UserState.NONE]
        self.user_powers = [0, 0]
        self.sync_error = [0, 0]
        self.prev_sync_err = [0,0]
        self.upchirp_syms = [[], []]

        gr.basic_block.__init__(self, name='ML Aggregator',
                          in_sig=[np.float32, (np.complex64, self.N), (np.complex64, self.N)] * self.Ku,
                          out_sig=[np.short, np.short, np.float32]) 

    def two_users(self):
        return (self.user_states[0] != UserState.NONE and self.user_states[1] != UserState.NONE)

    def _is_strong_user(self, u):
        if  self.user_powers[u-1] < self.user_powers[2 - u]:
            return False

        return True

    def is_strong_user(self, u):

        return self._is_strong_user(u)

    def track_user(self, window, u):
        user_power = window['power{}'.format(u)]
        other_power = window['power{}'.format(1 if u == 2 else 2)]
        if user_power > other_power:
            win_state = window['Tu']
        else:
            win_state = window['Ti1']

        if self.user_states[u-1] == UserState.NONE and user_power != 0.0: # Detecting a new user
            self.user_powers[u-1] = user_power
            self.user_states[u-1] = UserState.PREAMBLE

        elif self.user_states[u-1] == UserState.PREAMBLE and win_state == SYNC_TYPE_PAYLOAD: # Moving from preamble to payload
            self.user_states[u-1] = UserState.PAYLOAD
            self.sync_error[u-1] = max(set(self.upchirp_syms[u-1]), key=self.upchirp_syms[u-1].count)

        elif self.user_states[u-1] == UserState.PAYLOAD:
            if win_state == SYNC_TYPE_VOID and user_power == 0: # Multi-user case
                self.user_powers[u-1] = 0.0
                self.user_states[u-1] = UserState.NONE
                self.sync_error[u-1] = 0
                self.upchirp_syms[u-1] = []
            elif not self.two_users() and win_state == SYNC_TYPE_UPCHIRP: # Single-user case, we don't see any void windows
                self.user_powers[u-1] = user_power
                self.user_states[u-1] = UserState.PREAMBLE
                self.sync_error[u-1] = 0
                self.upchirp_syms[u-1] = []

    def track_users(self, window):
        self.track_user(window, 1)
        self.track_user(window, 2)

    def forecast(self, noutput_items, ninput_items_required):
        for i in range(len(ninput_items_required)):
            ninput_items_required[i] = noutput_items

    def process_window(self, window, demod_tags, L, Mi1_vec, Mi2_vec):
        # Parse window tag to track users state
        self.track_users(window)
    
        # Fetch demodulated symbol for strongest user
        k = np.argmax(L)        
            
        if k != 0:
            print ("k != 0" , L)
            
        demod = demod_tags[k].value
        Su = demod['Su']

        # Summing matched filter outputs ...
        Mi1 = Mi1_vec[k]
        Mi2 = Mi2_vec[k]
        M = self.prev_Mi2 + Mi1

        # ... and demodulating Si in case we have two users
        Si = np.argmax(np.abs(M))
        self.prev_Mi2 = Mi2

        payload_syms = [None, None]
        
        for u in range(1,3): # For each user
           
            #The second part takes into account the end of a perfectly synchronized interferer (sto=0.0). For which an additional symbol value should be output
            if self.user_states[u-1] == UserState.PAYLOAD or (self.user_states[u-1] == UserState.NONE and self.prev_Ti2 == SYNC_TYPE_PAYLOAD):
                if self.is_strong_user(u) and window['win_len'] == self.N:
                    
                    payload_syms[u-1] = np.mod(Su - self.sync_error[u-1], self.N)
                    
                    
                elif not self.is_strong_user(u):
                    # quarter downchirp window falls inside a symbol of interferer cutting it in three and not two parts
                    if window['Tu'] == SYNC_TYPE_QUARTERDOWN and window['tau'] >= window['win_len']:
                        self.prev_Mi2 = M
                        
                    # we need to combine the new Mi1 with the previous Mi2, therefore the latter should exist    
                    elif (self.prev_Ti2 == SYNC_TYPE_PAYLOAD or np.ceil(window['tau']) == self.N):
                        #we need to use the previous sync error as it has been reset one to early in the case sto_int == 0
                        if (self.user_states[u-1] == UserState.NONE and self.prev_Ti2 == SYNC_TYPE_PAYLOAD):
                            payload_syms[u-1] = np.mod(Si - self.prev_sync_err[u-1], self.N)
                        else:
                            payload_syms[u-1] = np.mod(Si - self.sync_error[u-1], self.N)
                        
                       
                self.prev_sync_err[u-1] = self.sync_error[u-1]; 

            # If upchirp in preamble, track synchronization errors
            elif self.user_states[u-1] == UserState.PREAMBLE:
                if self.is_strong_user(u) and window['win_len'] == self.N and window['Tu'] == SYNC_TYPE_UPCHIRP:
                    self.upchirp_syms[u-1].append(Su)
                elif not self.is_strong_user(u) and window['Ti1'] == SYNC_TYPE_UPCHIRP:
                    self.upchirp_syms[u-1].append(Si)
             
       
        self.prev_Ti2 = window['Ti2']
        if self.user_states[0] == UserState.PREAMBLE and window['Tu'] == SYNC_TYPE_UPCHIRP and window['win_len'] == self.N:
            SNR_u1 = demod['SNR']
        else:
            SNR_u1 = None

        return payload_syms, SNR_u1

    def general_work(self, input_items, output_items):

        n_windows = len(output_items[0])        
        # Fetch all window tags
        tags = [gr.tag_to_python(x) for x in self.get_tags_in_window(0, 0, len(input_items[0]))]# self.get_tags_in_window(0, 0, len(input_items[0]))#
        win_tags = list(filter(lambda t: t.key == 'new_window', tags))

        out_S1  = output_items[0]
        out_S2  = output_items[1]
        out_SNR = output_items[2]

        n_syms_u1, n_syms_u2, n_snrs = 0, 0, 0

        for i in range(n_windows):
            L   = [input_items[k*3+0][i] for k in range(self.Ku)]
            Mi1 = [input_items[k*3+1][i] for k in range(self.Ku)]
            Mi2 = [input_items[k*3+2][i] for k in range(self.Ku)]

            demod_tags = []
            for k in range(self.Ku):
                tags = [gr.tag_to_python(x) for x in self.get_tags_in_window(k*3, i, i+1)]
                demod_tags += filter(lambda t: t.key == 'partial_ml', tags)

            window = win_tags[i].value
            syms, SNR_u1 = self.process_window(window, demod_tags, L, Mi1, Mi2)
            S1, S2 = syms

            if S1 is not None:
                out_S1[n_syms_u1] = S1
                n_syms_u1 += 1

            if S2 is not None:
                out_S2[n_syms_u2] = S2
                n_syms_u2 += 1

            if SNR_u1:
                out_SNR[n_snrs] = SNR_u1
                n_snrs += 1

        for k in range(self.Ku):
            self.consume(3*k+0, n_windows)
            self.consume(3*k+1, n_windows)
            self.consume(3*k+2, n_windows)

        self.produce(0, n_syms_u1)
        self.produce(1, n_syms_u2)
        self.produce(2, n_snrs)

        return -2 #gr.WORK_CALLED_PRODUCE

class mu_demod(gr.hier_block2):
    """
        Block responsible for the demodulation of the symbols of each user

        This block demodulate the symbols of each user based on the window information transmitted by the synchronization stage. 
        It is composed of 'Ku' partial_ml blocks that each return the likelihood estimate for a different symbol candidate for the synchronized user, as well as the corresponding matched filter output for the symbols of the non-synchronised user.
        The output of each of the 'Ku' branch is then agglomerated to make a decision on the symbols of each users. An estimation of the SNR of the first user frame is also output.

        @param SF spreading factor
        @param Ku Number of candidates selected for the symbols of the synchronized user

    """
    def __init__(self, SF, Ku):
        gr.hier_block2.__init__(self,
            "mu_demod",
            gr.io_signature(1, 1, gr.sizeof_gr_complex),  # Input signature
            gr.io_signature3(3, 3, gr.sizeof_short, gr.sizeof_short, gr.sizeof_float)) # Output signature

        aggregator = ml_aggreg(SF, Ku)

        self.connect((aggregator, 0), (self, 0))
        self.connect((aggregator, 1), (self, 1))
        self.connect((aggregator, 2), (self, 2))

        for i in range(Ku):
            b = partial_ml(SF, i)
        
            self.connect((self, 0), b)
            self.connect((b, 0), (aggregator, i*3+0))
            self.connect((b, 1), (aggregator, i*3+1))
            self.connect((b, 2), (aggregator, i*3+2))
