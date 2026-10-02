"""Recalcul des scores Bench-Low à partir du tableau 4.1 publié.

Ce module est volontairement indépendant de tout modèle : il lit le CSV
des résultats de référence (CA, UP, latence, mémoire par modèle) et
applique les formules du manuscrit (section 2.3) pour reconstruire les
colonnes ECC et score composite, puis le front de Pareto (tableau 4.2).

Il sert deux usages :

1. **non-régression** — les tests comparent ces recalculs aux valeurs
   publiées du manuscrit (``tests/test_reference_repro.py``) ;
2. **reproductibilité** — n'importe quel lecteur peut vérifier, sur CPU et
   sans dépendance lourde, que le code implémente bien les formules
   annoncées.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from Low-Eval-Kit.pareto import OBJECTIFS_PAR_DEFAUT, front_pareto
from Low-Eval-Kit.scores import ResultatModele

logger = logging.getLogger("loweval.bench_low.runner")

#: Chemin du CSV des résultats de référence (valeurs du tableau 4.1).
CHEMIN_REFERENCE = Path(__file__).resolve().parent / "reference_results.csv"

#: Front de Pareto attendu (tableau 4.2 du manuscrit) — utilisé comme
#: oracle par les tests de non-régression.
FRONT_PARETO_REFERENCE = ("Qwen2-VL-7B", "LLaVA-1.5-7B", "MiniCPM-V-2.8B")

#: Nombre de combinaisons de pondérations de l'analyse de sensibilité (§2.3).
NB_COMBINAISONS_SENSIBILITE = 45


def charger_reference(chemin: Path | str | None = None) -> list[ResultatModele]:
    """Lit le CSV de référence et retourne les résultats sous forme typée.

    Chaque ligne du CSV produit un :class:`loweval.scores.ResultatModele`,
    dont ``__post_init__`` recalcule ECC et composite avec les formules
    officielles — c'est ce recalcul que le test de non-régression compare
    aux valeurs publiées.

    :raises FileNotFoundError: si le CSV de référence est absent.
    """
    chemin = Path(chemin) if chemin else CHEMIN_REFERENCE
    if not chemin.exists():
        raise FileNotFoundError(
            f"CSV de référence introuvable : {chemin}. "
            "Le fichier est versionné dans le dépôt (bench_low/reference_results.csv)."
        )
    resultats: list[ResultatModele] = []
    with chemin.open(newline="", encoding="utf-8") as flux:
        for ligne in csv.DictReader(flux):
            resultats.append(ResultatModele(
                modele=ligne["modele"].strip(),
                ca=float(ligne["ca"]),
                up=float(ligne["up"]),
                latence_ms=float(ligne["latence_ms"]),
                memoire_go=float(ligne["memoire_go"]),
            ))
    logger.info("%d modèles chargés depuis %s", len(resultats), chemin.name)
    return resultats


def recalculer_scores(
    resultats: list[ResultatModele],
) -> list[ResultatModele]:
    """Recalcule ECC et composite sur un lot (idempotente : les valeurs sont
    déjà calculées à la construction ; la fonction documente l'intention et
    offre un point d'ancrage pour les tests)."""
    return list(resultats)


def front_reference(
    resultats: list[ResultatModele],
    objectifs: tuple[str, ...] = OBJECTIFS_PAR_DEFAUT,
) -> list[ResultatModele]:
    """Front de Pareto qualité/coût d'un lot (tableau 4.2 du manuscrit).

    Objectifs : CA, UP et ECC, tous à maximiser. Le front retourné est
    trié par score composite décroissant pour un affichage stable.
    """
    front = front_pareto(resultats, objectifs=objectifs)
    return sorted(front, key=lambda r: r.composite, reverse=True)


def rapport_tableau_41(resultats: list[ResultatModele]) -> list[dict]:
    """Lignes d'export comparables au tableau 4.1 (arrondis du manuscrit)."""
    lignes = [r.en_ligne() for r in resultats]
    return sorted(lignes, key=lambda d: d["Score composite"], reverse=True)
