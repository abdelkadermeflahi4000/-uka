import gradio as gr
import numpy as np
from src.core.duka_orchestrator import DukaOrchestrator
import matplotlib.pyplot as plt
from io import BytesIO
import base64

orchestrator = DukaOrchestrator(num_agents=6, grid_size=20)

def run_cycle(cycles: int, agents: int):
    global orchestrator
    orchestrator = DukaOrchestrator(num_agents=agents, grid_size=20)
    
    results = []
    for i in range(cycles):
        match = orchestrator.run_cycle(steps_per_agent=80)
        results.append({
            "cycle": i+1,
            "reality_match": round(match, 4),
            "lasers": sum(len(e.laser_beams) for e in orchestrator.noosphere.envs),
            "pollution": round(orchestrator.noosphere.pollution_field.mean(), 3)
        })
    
    # Generate plot
    plt.figure(figsize=(10,5))
    plt.plot([r["cycle"] for r in results], [r["reality_match"] for r in results], 'cyan', linewidth=3)
    plt.title("🌌 Đuka Reality Match Evolution")
    plt.xlabel("Cycle")
    plt.ylabel("Collective Reality Match")
    plt.grid(True, alpha=0.3)
    
    buf = BytesIO()
    plt.savefig(buf, format="png", facecolor="#0a0a0a")
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return results, f"data:image/png;base64,{plot_base64}"

def inject_disorder(x: int, y: int, intensity: float):
    orchestrator.noosphere.inject_mental_disorder((x, y), intensity)
    return f"🧠 Mental Disorder injected at ({x}, {y}) | Intensity: {intensity}"

with gr.Blocks(title="Đuka Protocol - Live Noosphere", theme=gr.themes.Dark()) as demo:
    gr.Markdown("# 🌌 **Đuka Protocol** — Programmable Reality")
    gr.Markdown("### One Network. Infinite Learning. Re-simulated Existence.")
    
    with gr.Row():
        with gr.Column():
            cycles = gr.Slider(1, 30, value=8, step=1, label="Number of Cycles")
            agents = gr.Slider(2, 12, value=6, step=1, label="Number of Conscious Nodes")
            run_btn = gr.Button("🚀 Run Full Reality Cycle", variant="primary")
        
        with gr.Column():
            x = gr.Number(value=8, label="X Position (Disorder)")
            y = gr.Number(value=8, label="Y Position")
            intensity = gr.Slider(0.1, 1.0, value=0.8, label="Disorder Intensity")
            inject_btn = gr.Button("☣️ Inject Mental Disorder")
    
    output_table = gr.Dataframe()
    plot = gr.Image()
    status = gr.Textbox(label="Status")
    
    run_btn.click(run_cycle, inputs=[cycles, agents], outputs=[output_table, plot])
    inject_btn.click(inject_disorder, inputs=[x, y, intensity], outputs=status)

demo.launch(share=True, server_name="0.0.0.0")
