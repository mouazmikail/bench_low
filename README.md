# Bench-Low — résultats consolidés de l'évaluation frugale

Dépôt de **résultats** du protocole Low-Eval (chapitres 3 et 4 du manuscrit
« Frugal Multimodal Alignment », M. Mikail, CY Cergy Paris Université).
Les mesures sont produites par le
[Low-Eval Kit](../Low-Eval-Kit) à partir du corpus
[Data-Low](../Data-Low), puis publiées ici après passage de la checklist
d'intégrité (MANIFEST.md). Un unique script autonome permet à tout lecteur
de vérifier les chiffres sans rien installer (bibliothèque standard seule).

## Contenu

```
results/
  reference_results.csv   Référentiel verrouillé — tableau 4.1 (6 modèles)
  scores_composites.csv   Scores consolidés (ECC et S recalculés, exports)
  pareto.json             Front de Pareto CA/UP/ECC + matrice de dominance
scripts/
  recalculer_scores.py    Recalcul autonome (stdlib) + vérification des verrous
MANIFEST.md               Manifeste d'intégrité des résultats
LICENSE                   CC BY-NC 4.0
```

## Vérifier les chiffres publiés

```bash
python3 scripts/recalculer_scores.py
```

Le script recalcule ECC et S depuis les formules du §3.1, reconstruit le
front de Pareto par dominance, et refuse toute divergence avec les valeurs
verrouillées (ECC = 0,876 et S = 0,787 pour Qwen2-VL-7B ; front à trois
modèles) avant de réécrire les exports.

## Lecture des fichiers

* `reference_results.csv` — une ligne par modèle : CA, UP, mémoire (Go),
  latence (ms). Les colonnes ECC et S **ne sont jamais saisies à la main** :
  elles sont recalculées par `scripts/compute_scores.py` du kit
  (formules §3.1 : ECC = (M_norm + T_norm)/2, S = 0,4·CA + 0,4·UP + 0,2·ECC).
* `pareto.json` — front non dominé `{Qwen2-VL-7B, LLaVA-1.5-7B,
  MiniCPM-V-2.8B}` (tableau 4.2), verrouillé par `tests/test_pareto.py`.

## Comment ajouter une campagne

1. Produire localement `campaign.json` via `scripts/run_evaluation.py`
   (les 8 métadonnées §7.2 doivent être complètes).
2. Vérifier la répétabilité (CV ≤ 3,2 %) et le κ des annotations associées.
3. Régénérer `scores_composites.csv` et `pareto.json` avec
   `compute_scores.py` — jamais d'édition manuelle.
4. Mettre à jour MANIFEST.md (hash du corpus, versions code/poids).

## Valeurs verrouillées

| Modèle | CA | UP | ECC | S |
|---|---|---|---|---|
| Qwen2-VL-7B | 0,82 | 0,71 | 0,876 | 0,787 |

Toute divergence entre ce dépôt et les résultats d'une nouvelle campagne
doit être expliquée dans le journal des versions du MANIFEST (changement de
poids HF, de matériel ou de protocole) — jamais corrigée silencieusement.
