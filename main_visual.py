from src.noosphere import Noosphere
from src.visualization import NoosphereVisualizer
from src.genetic_engine import GeneticEngine

noosphere = Noosphere(num_agents=8, grid_size=16)

# حقن واقعي
noosphere.inject_mental_disorder((7,8), 0.95, radius=3)
noosphere.inject_pollution((4,12), 0.8)

viz = NoosphereVisualizer(noosphere)

# تشغيل مع تطور
for epi in range(30):
    print(f"Episode {epi} | Collective: {noosphere.collective_reality_match():.4f}")
    # ... (التدريب المختصر)
    noosphere.update_noosphere_field()
    noosphere.share_knowledge()

viz.animate()
