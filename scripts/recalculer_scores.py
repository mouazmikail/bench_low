# -*- coding: utf-8 -*-
"""Recalcul autonome des scores Bench-Low à partir du référentiel verrouillé.

Ce script est volontairement INDÉPENDANT du Low-Eval Kit : un lecteur peut
vérifier, sur CPU et avec la seule bibliothèque standard, que les formules
publiées (§3.1 du manuscrit) produisent bien les valeurs du tableau 4.1 et
le front du tableau 4.2 — sans installer quoi que ce soit d'autre.

Il lit ``results/reference_results.csv`` (CA, UP, mémoire NF4, latence),
recalcule ECC et le score composite S, reconstruit le front de Pareto par
dominance, puis :

* vérifie les valeurs verrouillées (ECC = 0,876 et S = 0,787 pour
  Qwen2-VL-7B ; front exact à trois modèles) — toute divergence lève une
  erreur et interrompt le script ;
* réécrit ``results/scores_composites.csv`` et ``results/pareto.json``.

Usage : python scripts/recalculer_scores.py
"""

import csv
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins, résolus par rapport à la racine du dépôt
# ---------------------------------------------------------------------------
RACINE = Path(__file__).resolve().parent.parent
CSV_REFERENCE = RACINE / "results" / "reference_results.csv"
CSV_SORTIE = RACINE / "results" / "scores_composites.csv"
JSON_SORTIE = RACINE / "results" / "pareto.json"

# Front de Pareto verrouillé (tableau 4.2) : oracle de non-régression.
FRONT_ATTENDU = {"Qwen2-VL-7B", "LLaVA-1.5-7B", "MiniCPM-V-2.8B"}

# Objectifs du front : maximiser CA, UP et ECC.
OBJECTIFS = ("ca", "up", "ecc")


def recalculer_ecc(memoire_gb: float, latence_ms: float) -> float:
    """Efficience de coût : moyenne de la mémoire et de la latence normalisées.

    Mémoire : décroissance linéaire de 1 Go (score 1) à 32 Go (score 0).
    Latence : décroissance jusqu'à la référence de 10 000 ms, puis plancher.
    """
    m_norm = 1.0 - (memoire_gb - 1.0) / (32.0 - 1.0)
    t_norm = 1.0 - min(1.0, latence_ms / 10_000.0)
    return (m_norm + t_norm) / 2.0


def recalculer_s(ca: float, up: float, ecc: float) -> float:
    """Score composite : S = 0,4·CA + 0,4·UP + 0,2·ECC (poids du §3.1)."""
    return 0.4 * ca + 0.4 * up + 0.2 * ecc


def domine(a: dict, b: dict) -> bool:
    """Vrai si a domine b : au moins aussi bon sur les trois objectifs, et
    strictement meilleur sur l'un d'eux."""
    au_moins_aussi_bon = all(a[o] >= b[o] for o in OBJECTIFS)
    strictement_meilleur = any(a[o] > b[o] for o in OBJECTIFS)
    return au_moins_aussi_bon and strictement_meilleur


def front_pareto(lignes: list[dict]) -> list[str]:
    """Retourne les noms des modèles non dominés (front de Pareto)."""
    return [a["model"] for a in lignes
            if not any(domine(b, a) for b in lignes if b is not a)]


def verifier_verrous(lignes: list[dict], front: list[str]) -> None:
    """Lève une erreur si un verrou publié n'est pas reproduit à l'identique."""
    qwen = next(l for l in lignes if l["model"] == "Qwen2-VL-7B")
    assert round(qwen["ecc"], 3) == 0.876, f"ECC verrouillé divergent : {qwen['ecc']:.3f}"
    assert round(qwen["s"], 3) == 0.787, f"S verrouillé divergent : {qwen['s']:.3f}"
    assert set(front) == FRONT_ATTENDU, f"Front divergent : {sorted(front)}"


def main() -> None:
    """Recalcule, vérifie les verrous, puis réécrit les exports consolidés."""
    with open(CSV_REFERENCE, encoding="utf-8") as flux:
        brut = list(csv.DictReader(flux))

    # Recalcul complet : chaque ligne porte ses valeurs brutes et calculées.
    lignes = []
    for l in brut:
        ca, up = float(l["ca"]), float(l["up"])
        ecc = recalculer_ecc(float(l["memory_gb"]), float(l["latency_ms"]))
        lignes.append({"model": l["model"], "ca": ca, "up": up, "ecc": ecc,
                       "s": recalculer_s(ca, up, ecc),
                       "memory_gb": float(l["memory_gb"]),
                       "latency_ms": float(l["latency_ms"])})
    lignes.sort(key=lambda l: -l["s"])

    front = front_pareto(lignes)
    verifier_verrous(lignes, front)

    # Export CSV : valeurs brutes et recalculées, dans l'ordre du classement.
    with open(CSV_SORTIE, "w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=[
            "model", "ca", "up", "memory_gb", "latency_ms", "ecc", "s"])
        redacteur.writeheader()
        redacteur.writerows(lignes)

    # Export JSON : front et matrice de dominance, comme le tableau 4.2.
    matrice = [{"Modèle": l["model"],
                "Statut": "Non dominé" if l["model"] in front
                else f"Dominé par {next(b['model'] for b in lignes if domine(b, l))}",
                "CA": l["ca"], "UP": l["up"], "ECC": l["ecc"]} for l in lignes]
    JSON_SORTIE.write_text(json.dumps(
        {"objectifs": list(OBJECTIFS), "non_domines": front,
         "matrice_dominance": matrice},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(lignes)} modèles recalculés — verrous ECC/S et front vérifiés.")
    print(f"Exports : {CSV_SORTIE.name} , {JSON_SORTIE.name}")


if __name__ == "__main__":
    main()
