"""bench_low — Recalcul indépendant des scores de référence du manuscrit.

Ce paquet rejoue, sans GPU ni modèle, la chaîne complète de scoring à
partir du seul tableau 4.1 (CA, UP, latence, mémoire par modèle) :

* recalcul des ECC et scores composites (:mod:`bench_low.runner`) ;
* front de Pareto qualité/coût (tableau 4.2) ;
* analyse de sensibilité sur 45 combinaisons de pondérations (§2.3) ;
* export des tableaux comparables au manuscrit (CSV/HTML).

C'est l'outil de **non-régression** du kit : tout changement dans les
formules de :mod:`loweval.scores` doit faire échouer
``tests/test_reference_repro.py``, qui compare ces recalculs aux valeurs
publiées (ECC = 0.876 et S = 0.787 pour Qwen2-VL-7B, front de Pareto à
trois modèles, 45 combinaisons de poids).
"""

from __future__ import annotations

from bench_low.runner import (
    CHEMIN_REFERENCE,  # CSV du tableau 4.1 (valeurs publiées)
    charger_reference,  # lecture → list[ResultatModele]
    front_reference,  # front de Pareto (tableau 4.2)
    rapport_tableau_41,  # lignes comparables au tableau 4.1
    recalculer_scores,  # ECC + composite pour chaque modèle
)

__all__ = [
    "CHEMIN_REFERENCE",
    "charger_reference",
    "front_reference",
    "rapport_tableau_41",
    "recalculer_scores",
]
