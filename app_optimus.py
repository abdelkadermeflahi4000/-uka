import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from src.core.duka_orchestrator import DukaOrchestrator
from io import BytesIO
import base64

orchestrator = None

def launch_system(cycles: int, agents: int, use_optimus: bool):
    global orchestrator
    orchestrator = DukaOrchestrator(num_agents=agents, grid_size=20, use_optimus=use_optimus)
    
    history = []
    for i in range(cycles):
        match = orchestrator.run_cycle(steps_per_agent=90)
        history.append(match)
    
    # Plot
    plt.figure(figsize=(10, 5), facecolor='#0a0a0a')
    plt.plot(history, 'cyan', linewidth=3, marker='o')
    plt.title('🌌 Đuka Reality Match + Optimus Modulation')
    plt.xlabel('Cycle')
    plt.ylabel('Collective Reality Match')
    plt.grid(True, alpha=0.3)
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot = base64.b64encode(buf.read()).decode()
    plt.close()
    
    status = f"✅ Completed {cycles} cycles | Final Reality Match: {history[-1]:.4f}"
    if use_optimus:
        status += " | 🤖 Optimus Modulated Live"
    
    return f"data:image/png;base64,{plot}", status

with gr.Blocks(title="Đuka Protocol - Live Optimus", theme=gr.themes.Dark()) as demo:
    gr.Markdown("# 🌌 **Đuka Protocol** — Programmable Reality + Optimus")
    
    with gr.Row():
        cycles = gr.Slider(1, 40, value=10, label="Cycles")
        agents = gr.Slider(2, 12, value=6, label="Agents")
        optimus_check = gr.Checkbox(value=True, label="Enable Optimus Physical Simulation")
    
    run_btn = gr.Button("🚀 Launch Full System", variant="primary", size="large")
    
    plot = gr.Image(label="Reality Evolution")
    status = gr.Textbox(label="Status")
    
    run_btn.click(launch_system, 
                 inputs=[cycles, agents, optimus_check],
                 outputs=[plot, status])

demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
