import os
import sys

# Necessary if this file is imported from app.py which is in the same dir but we need root for i18n
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(WORKING_DIR)

from i18n.i18n import I18nAuto
i18n = I18nAuto()

badges = """
<div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 10px;">
    <a href="https://github.com/rafaelGodoyEbert" target="_blank"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" style="border-radius: 8px;"></a>
    <a href="https://discord.gg/tAdPHFAbud" target="_blank"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" style="border-radius: 8px;"></a>
    <a href="https://www.youtube.com/@aihubbrasil" target="_blank"><img src="https://img.shields.io/badge/AI_HUB-FF0000?style=for-the-badge&logo=youtube&logoColor=white" style="border-radius: 8px;"></a>
</div>
"""

description = f"""
<div style="text-align: center; color: white;">

    <div style="display: inline-block; padding: 10px 20px; background: rgba(255, 106, 0, 0.1); border: 1px solid rgba(255, 106, 0, 0.3); border-radius: 30px; margin-bottom: 15px;">
        <span style="color: #ff6a00; font-weight: 800; font-size: 0.9em; letter-spacing: 1px;">SQUAD MODERNIZATION V2.0 ALPHA</span>
    </div>

    <h1 style="font-size: 3.5em; font-weight: 900; margin: 0; background: linear-gradient(135deg, #fff 0%, #aaa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -2px;">ViralCutter</h1>
    
    <p style="font-size: 1.2em; color: #a0a0a0; margin-top: 10px; max-width: 700px; margin-left: auto; margin-right: auto;">
        {i18n('Transforme vídeos longos em clipes virais magnéticos com a orquestração de Inteligência Artificial definitiva.')}
    </p>

    <div style="display: flex; justify-content: center; gap: 20px; margin: 30px 0;">
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 15px; min-width: 120px;">
            <div style="color: #ff6a00; font-size: 1.5em; margin-bottom: 5px;">✂️</div>
            <div style="font-weight: 700; font-size: 0.9em;">Smart Cut</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 15px; min-width: 120px;">
            <div style="color: #00d2ff; font-size: 1.5em; margin-bottom: 5px;">📝</div>
            <div style="font-weight: 700; font-size: 0.9em;">Pro Caption</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px 25px; border-radius: 15px; min-width: 120px;">
            <div style="color: #d064ff; font-size: 1.5em; margin-bottom: 5px;">🤖</div>
            <div style="font-weight: 700; font-size: 0.9em;">AI Agents</div>
        </div>
    </div>
</div>
"""