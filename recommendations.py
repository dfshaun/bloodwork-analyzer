def get_marker_recommendations(marker, value, status):
    """Get recommendations for individual markers."""
    recommendations = {
        'TSH': {
            'LOW': {
                'diet': [
                    "Increase iodine-rich foods (seaweed, fish, eggs)",
                    "Include selenium-rich foods (brazil nuts, tuna, sardines)",
                    "Add zinc-rich foods (oysters, beef, pumpkin seeds)",
                ],
                'lifestyle': [
                    "Reduce caffeine intake",
                    "Practice stress management techniques",
                    "Get adequate sleep (7-9 hours)",
                    "Consider avoiding environmental toxins",
                ],
                'supplements': [
                    "Consult healthcare provider about selenium supplementation",
                    "Consider zinc supplementation under medical supervision",
                    "Avoid iodine supplements without medical supervision",
                ],
                'contraindications': [
                    "Avoid stimulants and excessive caffeine",
                    "Don't take iodine supplements without testing",
                    "Certain medications may interact - consult healthcare provider",
                ]
            },
            'HIGH': {
                'diet': [
                    "Limit iodine-rich foods temporarily",
                    "Include anti-inflammatory foods",
                    "Increase cruciferous vegetables (if approved by doctor)",
                ],
                'lifestyle': [
                    "Regular moderate exercise",
                    "Stress management techniques",
                    "Adequate sleep",
                ],
                'supplements': [
                    "Selenium (under medical supervision)",
                    "Consider L-carnitine with medical approval",
                ],
                'contraindications': [
                    "Avoid iodine supplements",
                    "Be cautious with biotin supplements",
                ]
            }
        },
        'Iron': {
            'LOW': {
                'diet': [
                    "Increase iron-rich foods (lean meats, spinach, legumes)",
                    "Include vitamin C-rich foods with meals",
                    "Cook in cast iron cookware",
                ],
                'lifestyle': [
                    "Avoid tea/coffee with meals",
                    "Space calcium supplements away from iron-rich meals",
                ],
                'supplements': [
                    "Consider iron supplementation (discuss form with doctor)",
                    "Vitamin C supplementation may help absorption",
                ],
                'contraindications': [
                    "Don't take iron with calcium supplements",
                    "Certain medications may interfere with absorption",
                ]
            },
            'HIGH': {
                'diet': [
                    "Limit iron-rich foods",
                    "Avoid vitamin C with meals",
                    "Green tea may help reduce absorption",
                ],
                'lifestyle': [
                    "Regular blood donation if approved by doctor",
                    "Avoid raw/rare meats",
                ],
                'supplements': [
                    "Avoid iron supplements",
                    "IP6 may be beneficial (consult doctor)",
                ],
                'contraindications': [
                    "Avoid vitamin C supplements with meals",
                    "Don't take iron supplements",
                ]
            }
        },
        'TIBC': {
            'HIGH': {
                'diet': [
                    "Focus on iron-rich foods",
                    "Include vitamin C sources with meals",
                    "Consider reducing high-tannin beverages",
                ],
                'lifestyle': [
                    "Optimize sleep habits",
                    "Monitor for fatigue symptoms",
                ],
                'supplements': [
                    "Discuss iron supplementation with healthcare provider",
                    "Consider B-complex vitamins",
                ],
                'contraindications': [
                    "Avoid substances that impair iron absorption",
                ]
            }
        },
        'Free T3': {
            'HIGH': {
                'diet': [
                    "Reduce iodine-rich foods temporarily",
                    "Focus on anti-inflammatory foods",
                    "Include selenium-rich foods",
                ],
                'lifestyle': [
                    "Regular gentle exercise",
                    "Stress reduction practices",
                    "Adequate sleep",
                ],
                'supplements': [
                    "Selenium (with medical supervision)",
                    "Magnesium may be beneficial",
                ],
                'contraindications': [
                    "Avoid iodine supplements",
                    "Be cautious with stimulant supplements",
                ]
            }
        },
        # Add more markers as needed
    }
    
    # Default recommendations if no specific ones exist
    default_recs = {
        'diet': ["Maintain a balanced, whole-food diet",
                "Stay well hydrated",
                "Eat plenty of vegetables and fruits"],
        'lifestyle': ["Regular exercise",
                     "Adequate sleep",
                     "Stress management"],
        'supplements': ["Consult healthcare provider for personalized recommendations"],
        'contraindications': ["Always consult healthcare provider before starting supplements"]
    }
    
    marker_recs = recommendations.get(marker, {}).get(status, default_recs)
    return marker_recs

def get_overall_recommendations(analysis_df):
    """Generate overall recommendations based on all markers."""
    all_recommendations = {
        'diet': set(),
        'lifestyle': set(),
        'supplements': set(),
        'contraindications': set()
    }
    
    # Get recommendations for abnormal results
    abnormal_results = analysis_df[analysis_df['Status'] != 'NORMAL']
    
    for _, row in abnormal_results.iterrows():
        marker_recs = get_marker_recommendations(row['Marker'], row['Value'], row['Status'])
        
        for category in all_recommendations:
            if category in marker_recs:
                all_recommendations[category].update(marker_recs[category])
    
    # Convert sets to lists
    return {k: list(v) for k, v in all_recommendations.items()}