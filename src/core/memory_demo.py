import numpy as np
import matplotlib.pyplot as plt


# ============================
# 1. Kuramoto Memory Network
# ============================
class KuramotoMemory:
    def __init__(self, n=40, K=1.5):
        self.n = n
        self.K = K

        self.phase = np.random.uniform(0, 2*np.pi, n)
        self.freq = np.random.normal(2.0, 0.15, n)

    def step(self, dt=0.05):
        new_phase = np.copy(self.phase)

        for i in range(self.n):
            coupling = np.sum(np.sin(self.phase - self.phase[i]))
            new_phase[i] += dt * (self.freq[i] + self.K / self.n * coupling)

        self.phase = new_phase

    def coherence(self):
        return np.abs(np.mean(np.exp(1j * self.phase)))

    def get_phase(self):
        return self.phase.copy()


# ============================
# 2. Theta-Gamma Controller
# ============================
class ThetaGammaController:
    def __init__(self, theta_hz=6, gamma_hz=40):
        self.theta_hz = theta_hz
        self.gamma_hz = gamma_hz

    def generate(self, t):
        theta = np.sin(2*np.pi*self.theta_hz*t)
        gamma = np.sin(2*np.pi*self.gamma_hz*t)

        # gamma amplitude modulated by theta
        coupled = ((theta + 1) / 2) * gamma

        return theta, gamma, coupled


# ============================
# 3. Run simulation
# ============================
memory = KuramotoMemory(n=50, K=1.2)
controller = ThetaGammaController()

coherence_history = []

for _ in range(400):
    memory.step()
    coherence_history.append(memory.coherence())


# ============================
# 4. Theta-Gamma signal
# ============================
t = np.linspace(0, 1, 1000)
theta, gamma, coupled = controller.generate(t)


# ============================
# 5. Plot results
# ============================

# --- Plot 1: Memory formation
plt.figure()
plt.plot(coherence_history)
plt.title("Kuramoto Synchronization = Memory Formation")
plt.xlabel("Time")
plt.ylabel("Coherence R")
plt.show()


# --- Plot 2: Theta-Gamma coupling
plt.figure()
plt.plot(t[:300], coupled[:300])
plt.title("Theta-Gamma Coupling = Temporal Memory")
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.show()
