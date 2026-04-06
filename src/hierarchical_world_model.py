import numpy as np
import torch as th
import torch.nn as nn
from typing import Tuple

class HierarchicalWorldModel(nn.Module):
    """
    Hierarchical World Model - Phase 3
    يتنبأ بالـ Noosphere + الترددات + الزمن قبل حدوثه
    """
    def __init__(self, grid_size=16, latent_dim=128):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Conv2d(4, 32, kernel_size=3, padding=1),  # freq + phase + amp + time
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64 * grid_size * grid_size, latent_dim)
        )
        
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim + 32, 256),  # + genome
            nn.ReLU(),
            nn.Linear(256, latent_dim)
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64 * grid_size * grid_size // 4),
            nn.Unflatten(1, (64, grid_size//2, grid_size//2)),
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 4, kernel_size=3, stride=2, padding=1, output_padding=1)
        )
        
        self.latent_dim = latent_dim
    
    def forward(self, observation: np.ndarray, genome: np.ndarray) -> Tuple[np.ndarray, float]:
        obs_tensor = th.tensor(observation, dtype=th.float32).unsqueeze(0).unsqueeze(0)  # batch + channels
        latent = self.encoder(obs_tensor)
        
        genome_tensor = th.tensor(genome[:32], dtype=th.float32).unsqueeze(0)
        predicted_latent = self.predictor(th.cat([latent, genome_tensor], dim=1))
        
        predicted_obs = self.decoder(predicted_latent)
        predicted_obs = predicted_obs.squeeze().detach().numpy()
        
        # Time prediction error
        time_error = np.mean(np.abs(predicted_obs[3] - observation[:,:,3]))
        
        return predicted_obs, time_error
