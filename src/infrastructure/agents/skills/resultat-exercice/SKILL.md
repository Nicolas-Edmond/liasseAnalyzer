---
name: resultat-exercice
description: Use this skill to extract the Résultat de l'exercice (net income/loss) from French tax documents. Benefice is positive, perte is negative.
---

# Extraction du Résultat de l'Exercice

## Contexte
Le Résultat net est la différence entre tous les produits et toutes les charges de l'exercice. Il peut s'agir d'un bénéfice ou d'une perte.

## Cibles d'Analyse
- **Feuillets** : 2051 (Bilan Passif), 2053 (Compte de résultat), 2033-A / 2033-B (liasse simplifiée).
- **Lignes** :
  - Feuillet 2051 : Ligne DI (Bénéfice) ou DJ (Perte).
  - Feuillet 2053 : Ligne HN (Bénéfice ou perte).
  - Feuillet 2033-A : Ligne DK. Feuillet 2033-B : Ligne GG (Bénéfice) ou GH (Perte).

## Règles d'Extraction
1. **Gestion du signe** : Bénéfice = positif. Perte = négatif (ligne DJ/GH ou montant entre parenthèses).
2. **Formatage** : Montant numérique avec signe (ex: 4500.0 ou -8500.0).
3. **Cohérence** : Le résultat au passif du bilan = résultat au compte de résultat.
