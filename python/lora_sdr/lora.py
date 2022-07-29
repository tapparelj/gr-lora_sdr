import numpy as np
# import matplotlib.pyplot as plt

def gen_upchirp(SF):
    N = 2**SF
    n = np.arange(N, dtype=np.float32)

    x = np.exp(2*np.pi*1j*(np.square(n)/(2*N)-n/2))
    return x

def gen_downchirp(SF):
    return np.conj(gen_upchirp(SF))

def gen_preamble(SF, net_id=64, sto_frac=0, R=1):
    # sto_frac \in [0, 1/R[
    N = 2**SF
    n = np.arange(N * R, dtype=np.float32)/R - sto_frac
    #print(n)

    upchirp = np.exp(2*np.pi*1j*(np.square(n)/(2*N)-n/2))
    downchirp = np.conj(upchirp)

    idx_fold = (N - net_id)*R
    # sync_word = np.zeros(N*R, dtype=np.complex64)
    # n1, n2 = n[0:idx_fold], n[idx_fold:-1]
    # sync_word[0:idx_fold]  = np.exp(2*np.pi*1j*(np.square(n1)/(2*N) + net_id*n1/N - n1/2))
    # sync_word[idx_fold:-1] = np.exp(2*np.pi*1j*(np.square(n2)/(2*N) + net_id*n2/N + n2/2))
    sync_word = gen_sym(SF, net_id, sto_frac=sto_frac, R=R)

    quarter_downchirp = downchirp[0:N*R/4]
    preamble = np.concatenate([np.tile(upchirp, 8), np.tile(sync_word, 2), np.tile(downchirp, 2), quarter_downchirp])
    return preamble

def gen_sym(SF, S, sto_frac=0, R=1):
    N = 2**SF
    n = np.arange(N * R, dtype=np.float32)/R - sto_frac

    idx_fold = (N - S)*R
    sym = np.zeros(N*R, dtype=np.complex64)
    n1, n2 = n[0:idx_fold], n[idx_fold:]
    sym[0:idx_fold]  = np.exp(2*np.pi*1j*(np.square(n1)/(2*N) + S*n1/N - n1/2))
    sym[idx_fold:] = np.exp(2*np.pi*1j*(np.square(n2)/(2*N) + S*n2/N - 3*n2/2))

    return sym

def gen_syms(SF, S, sto_frac=0, R=1):
    return np.concatenate([gen_sym(SF, s, sto_frac=sto_frac, R=R) for s in S])

def gen_packet(SF, S, sto_frac=0, R=1):
    preamble = gen_preamble(SF, sto_frac=sto_frac, R=R)
    payload = gen_syms(SF, S, sto_frac=sto_frac, R=R)
    return np.concatenate([preamble, payload])

def demod_sym(SF, x):
    y = np.fft.fft(x * gen_downchirp(SF))
    return np.argmax(np.abs(y))

def add_cfo(SF, x, cfo, R=1):
    n = np.arange(len(x), dtype=np.float32) / R
    return np.multiply(x, np.exp(2*np.pi*1j*n*cfo/2**SF))


if __name__ == '__main__':
    SF = 4
    N = 2**SF
    x = gen_upchirp(SF)

    # R = 4


    # k = 8
    # y = gen_preamble(SF, R=R, sto_frac=0.0)
    # y = add_cfo(SF, y, 0.5, R=R)
    # yk = y[k*N*R+0 : (k+1)*N*R : R]

    # Yk = np.fft.fft(yk * gen_downchirp(SF))

    y = gen_syms(SF, [1, 2, 3, 4])
    print(demod_sym(SF, y[2*N:3*N]))

    # plt.stem(np.abs(Yk))
    # plt.show()

    # print(repr(np.abs(Yk)))
    # print(np.argmax(np.abs(Yk)))
