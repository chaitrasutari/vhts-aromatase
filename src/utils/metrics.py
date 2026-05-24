import pandas as pd

def calculate_enrichment_factor(y_true, y_prob, top_percent=0.01):
    """
    Calculates the Enrichment Factor at a given top percentage.
    EF = (Hit rate in top X%) / (Background hit rate)
    """
    df = pd.DataFrame({'y_true': y_true, 'y_prob': y_prob}).sort_values(by='y_prob', ascending=False)
    cutoff_idx = max(1, int(len(df) * top_percent))
    
    hit_rate_top = df.head(cutoff_idx)['y_true'].sum() / cutoff_idx
    hit_rate_background = df['y_true'].sum() / len(df)
    
    if hit_rate_background == 0:
        return 0.0
    return hit_rate_top / hit_rate_background