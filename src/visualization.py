import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.animation as animation
from src.noosphere import Noosphere

class NoosphereVisualizer:
    def __init__(self, noosphere: Noosphere):
        self.noosphere = noosphere
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 10))
        self.fig.suptitle('🌌 Đuka Protocol - Noosphere Live Visualization', fontsize=16, color='cyan')
        
        # Custom Colormaps
        self.freq_cmap = LinearSegmentedColormap.from_list('freq', ['darkblue', 'cyan', 'yellow', 'red'])
        self.conscious_cmap = LinearSegmentedColormap.from_list('conscious', ['black', '#00ff88', '#00ffff'])
        
        plt.style.use('dark_background')
    
    def update(self, frame):
        for ax in self.axes.flat:
            ax.clear()
        
        # 1. Frequency Field
        ax = self.axes[0, 0]
        im1 = ax.imshow(self.noosphere.envs[0].frequency_field, cmap=self.freq_cmap, vmin=-1, vmax=1)
        ax.set_title('🔄 Frequency Field + Laser Beams')
        plt.colorbar(im1, ax=ax, fraction=0.046)
        
        # رسم الأشعة
        for beam in self.noosphere.envs[0].laser_beams:
            ax.arrow(beam['start'][1], beam['start'][0],
                    beam['dir'][1]*3, beam['dir'][0]*3,
                    color='white', head_width=0.3)
        
        # 2. Noosphere Field (الوعي الجماعي)
        ax = self.axes[0, 1]
        im2 = ax.imshow(self.noosphere.noosphere_field, cmap=self.conscious_cmap, vmin=-1, vmax=1)
        ax.set_title('🌐 Noosphere Collective Consciousness')
        plt.colorbar(im2, ax=ax, fraction=0.046)
        
        # 3. Pollution + Mental Disorders
        ax = self.axes[0, 2]
        combined = self.noosphere.pollution_field + self.noosphere.mental_disorder_map * 1.5
        im3 = ax.imshow(combined, cmap='hot', vmin=0, vmax=1.5)
        ax.set_title('☣️ Pollution & Mental Disorders')
        plt.colorbar(im3, ax=ax, fraction=0.046)
        
        # 4. Reality Match per Agent
        ax = self.axes[1, 0]
        matches = [a.genome[24:32].mean() for a in self.noosphere.agents]
        ax.bar(range(self.noosphere.num_agents), matches, color='cyan')
        ax.set_title('⭐ Individual Reality Match')
        ax.set_ylim(0, 1.05)
        ax.set_xlabel('Agent ID')
        
        # 5. Genome Diversity
        ax = self.axes[1, 1]
        genomes = np.array([a.genome for a in self.noosphere.agents])
        std = genomes.std(axis=0)
        ax.plot(std, color='magenta', linewidth=2)
        ax.set_title('🧬 Genome Diversity (Std Dev)')
        ax.set_xlabel('Gene Index')
        
        # 6. Collective Stats
        ax = self.axes[1, 2]
        ax.text(0.5, 0.8, f'Collective Reality Match\n{self.noosphere.collective_reality_match():.4f}',
                ha='center', va='center', fontsize=14, color='lime')
        ax.text(0.5, 0.5, f'Active Lasers: {sum(len(e.laser_beams) for e in self.noosphere.envs)}',
                ha='center', va='center', fontsize=12, color='yellow')
        ax.text(0.5, 0.2, f'Pollution Level: {self.noosphere.pollution_field.mean():.3f}',
                ha='center', va='center', fontsize=12, color='red')
        ax.axis('off')
        
        self.fig.tight_layout()
        return self.axes.flat
    
    def animate(self, interval=300):
        ani = animation.FuncAnimation(self.fig, self.update, interval=interval, blit=False)
        plt.show()
