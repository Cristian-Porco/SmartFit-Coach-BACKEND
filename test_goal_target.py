from data.utils import infer_goal_target

infer_goal_target("Voglio migliorare la mia salute generale, tonificarmi e aumentare la mia resistenza.")
# Atteso: "fitness"

infer_goal_target("Il mio obiettivo è aumentare la massa muscolare e scolpire il fisico.")
# Atteso: "bodybuilding"

infer_goal_target("Voglio diventare più forte nei tre sollevamenti principali: squat, panca e stacco.")
# Atteso: "powerlifting"

infer_goal_target("Mi alleno a corpo libero e voglio migliorare nei dip zavorrati e trazioni con peso.")
# Atteso: "streetlifting"