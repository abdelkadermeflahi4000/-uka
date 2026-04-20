class OscillatoryMemory:
    def __init__(self, node_id, n=64):
        self.node_id = node_id
        self.n = n
        self.phase = np.random.rand(n) * 2*np.pi
        self.freq = np.random.normal(6.0, 0.5, n)
        self.K = np.zeros((n,n))

    def encode(self, input_vector):
        return input_vector_to_phase(input_vector)

    def update(self, encoded):
        self.phase += self.freq + self.coupling()

    def coupling(self):
        return np.sum(np.sin(self.phase[:,None]-self.phase), axis=1)

    def coherence(self):
        return np.abs(np.mean(np.exp(1j*self.phase)))
