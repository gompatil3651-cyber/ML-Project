import streamlit as st
from typing import Dict, Any

def render_sentiment_section(sentiment_data: Dict[str, Any]):
    """
    Renders FinBERT NLP news sentiment analysis breakdown and headlines feed using st.html.
    """
    score = sentiment_data.get("Sentiment_Score", 0.0)
    count = sentiment_data.get("News_Count", 0)
    pos_count = sentiment_data.get("positive_count", 0)
    neu_count = sentiment_data.get("neutral_count", 0)
    neg_count = sentiment_data.get("negative_count", 0)
    label = sentiment_data.get("sentiment_label", "Neutral")
    headlines = sentiment_data.get("headlines", [])

    label_colors = {
        "Bullish": ("#10B981", "#ECFDF5", "#065F46"),
        "Neutral": ("#6B7280", "#F3F4F6", "#374151"),
        "Bearish": ("#EF4444", "#FEF2F2", "#991B1B")
    }
    accent_color, bg_color, text_color = label_colors.get(label, label_colors["Neutral"])
    gauge_pct = max(0.0, min(100.0, ((score + 1.0) / 2.0) * 100))

    banner_html = f"""<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<div>
<span style="font-size: 13px; color: #64748B; font-weight: 700; text-transform: uppercase;">ProsusAI/finbert NLP Sentiment</span>
<h3 style="margin: 4px 0 0 0; font-size: 24px; font-weight: 800; color: #0F172A;">Daily Score: <strong style="color: {accent_color};">{score:+.3f}</strong></h3>
</div>
<div style="background: {bg_color}; border: 1px solid {accent_color}; color: {text_color}; padding: 8px 18px; border-radius: 20px; font-weight: 800; font-size: 14px;">
{label} Sentiment
</div>
</div>
<div style="margin: 16px 0 8px 0;">
<div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; color: #94A3B8; margin-bottom: 6px;">
<span>-1.0 Bearish</span>
<span>0.0 Neutral</span>
<span>+1.0 Bullish</span>
</div>
<div style="height: 10px; background: #E2E8F0; border-radius: 6px; position: relative;">
<div style="position: absolute; left: {gauge_pct}%; top: -3px; width: 16px; height: 16px; border-radius: 50%; background: {accent_color}; border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.3); transform: translateX(-50%);"></div>
</div>
</div>
<div style="display: flex; gap: 24px; font-size: 14px; color: #475569; margin-top: 16px; border-top: 1px solid #F1F5F9; padding-top: 12px;">
<span>Total Articles: <strong style="color: #0F172A;">{count}</strong></span>
<span style="color: #10B981; font-weight: 600;">Positive: {pos_count}</span>
<span style="color: #6B7280; font-weight: 600;">Neutral: {neu_count}</span>
<span style="color: #EF4444; font-weight: 600;">Negative: {neg_count}</span>
</div>
</div>"""

    st.html(banner_html)

    # Scraped Headlines List
    if headlines:
        st.markdown("<h4 style='font-size: 17px; font-weight: 800; color: #0F172A; margin: 16px 0 12px 0;'>Recent Financial Headlines & FinBERT Classification</h4>", unsafe_allow_html=True)
        headlines_html = "<div style=\"display: flex; flex-direction: column; gap: 10px;\">"
        for item in headlines[:8]:
            sent = item.get("sentiment", "neutral").lower()
            badge_bg = "#ECFDF5" if sent == "positive" else ("#FEF2F2" if sent == "negative" else "#F1F5F9")
            badge_color = "#065F46" if sent == "positive" else ("#991B1B" if sent == "negative" else "#475569")
            url = item.get("url") or "#"
            headline_text = item.get("headline", "Financial Update")
            published = item.get("published_at") or "Today"

            headlines_html += f"""<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
<div style="flex: 1; margin-right: 16px;">
<a href="{url}" target="_blank" style="text-decoration: none; color: #0F172A; font-size: 14px; font-weight: 600; line-height: 1.4;">
{headline_text}
</a>
<div style="font-size: 11px; color: #94A3B8; margin-top: 3px;">Published: {published}</div>
</div>
<span style="background: {badge_bg}; color: {badge_color}; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 800; text-transform: uppercase;">
{sent}
</span>
</div>"""
        headlines_html += "</div>"
        st.html(headlines_html)
