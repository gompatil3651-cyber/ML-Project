import streamlit as st
from typing import Dict, Any

def render_recommendation_card(pred_data: Dict[str, Any]):
    """
    Renders an accessible, light-themed visual recommendation card for non-technical users.
    Uses st.html to prevent markdown code block formatting.
    """
    ticker = pred_data.get("ticker", "N/A")
    prediction = pred_data.get("prediction", "HOLD").upper()
    confidence = float(pred_data.get("confidence", 0.50)) * 100
    probs = pred_data.get("probabilities", {"BUY": 0.33, "HOLD": 0.34, "WAIT": 0.33})
    cv_acc = pred_data.get("evaluated_cv_accuracy")

    style_map = {
        "BUY": {
            "bg": "#ECFDF5",
            "border": "#10B981",
            "text": "#065F46",
            "badge_bg": "#10B981",
            "action_text": "Strong Buy Signal",
            "desc": "Technical momentum and sentiment indicators suggest positive forward trajectory (> +3% expected movement)."
        },
        "HOLD": {
            "bg": "#FEF3C7",
            "border": "#F59E0B",
            "text": "#92400E",
            "badge_bg": "#F59E0B",
            "action_text": "Maintain Position",
            "desc": "Expected movement is within standard volatility bands (-3% to +3%). Keep position steady."
        },
        "WAIT": {
            "bg": "#FEF2F2",
            "border": "#EF4444",
            "text": "#991B1B",
            "badge_bg": "#EF4444",
            "action_text": "Wait / Defensive",
            "desc": "Negative momentum or market pressure suggests awaiting a lower support entry (< -3% expected movement)."
        }
    }

    style = style_map.get(prediction, style_map["HOLD"])
    cv_badge_html = f"<div style='border-left: 1px solid #CBD5E1; padding-left: 16px;'><span style='font-size: 11px; color: #64748B;'>Walk-Forward CV</span><br/><strong style='font-size: 14px; color: #0F172A;'>{float(cv_acc)*100:.1f}% Acc</strong></div>" if cv_acc else ""

    html_content = f"""<div style="background: {style['bg']}; border: 2px solid {style['border']}; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div>
<span style="font-size: 13px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">AI Consensus Recommendation</span>
<h2 style="margin: 4px 0 0 0; font-size: 30px; font-weight: 900; color: {style['text']};">
{ticker} &mdash; {prediction}
</h2>
</div>
<div style="background: {style['badge_bg']}; color: white; padding: 10px 24px; border-radius: 30px; font-size: 20px; font-weight: 800; box-shadow: 0 2px 4px rgba(0,0,0,0.12);">
{prediction}
</div>
</div>
<p style="font-size: 15px; color: {style['text']}; margin: 8px 0 16px 0; line-height: 1.5;">
<strong>{style['action_text']}:</strong> {style['desc']}
</p>
<div style="display: flex; align-items: center; gap: 16px; background: white; padding: 14px 20px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.08);">
<div style="flex: 1;">
<div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 6px;">
<span>Confidence Level</span>
<span style="color: {style['text']}; font-weight: 800;">{confidence:.1f}%</span>
</div>
<div style="height: 10px; background: #E2E8F0; border-radius: 6px; overflow: hidden;">
<div style="width: {confidence}%; height: 100%; background: {style['badge_bg']}; border-radius: 6px;"></div>
</div>
</div>
{cv_badge_html}
</div>
<div style="margin-top: 16px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
<div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #E2E8F0;">
<span style="font-size: 12px; color: #10B981; font-weight: 700;">BUY Probability</span>
<div style="font-size: 20px; font-weight: 800; color: #065F46; margin-top: 2px;">{float(probs.get('BUY', 0))*100:.1f}%</div>
</div>
<div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #E2E8F0;">
<span style="font-size: 12px; color: #F59E0B; font-weight: 700;">HOLD Probability</span>
<div style="font-size: 20px; font-weight: 800; color: #92400E; margin-top: 2px;">{float(probs.get('HOLD', 0))*100:.1f}%</div>
</div>
<div style="background: white; border-radius: 10px; padding: 12px; text-align: center; border: 1px solid #E2E8F0;">
<span style="font-size: 12px; color: #EF4444; font-weight: 700;">WAIT Probability</span>
<div style="font-size: 20px; font-weight: 800; color: #991B1B; margin-top: 2px;">{float(probs.get('WAIT', 0))*100:.1f}%</div>
</div>
</div>
</div>"""

    st.html(html_content)
