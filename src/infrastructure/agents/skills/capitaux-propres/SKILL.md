---
name: capitaux-propres
description: Use this skill to extract Capitaux Propres (equity) from French tax documents. Look in Bilan Passif (feuillet 2051 or 2033-A). Can be negative.
---

# Extraction des Capitaux Propres

## Contexte
Les Capitaux Propres reflètent la santé financière structurelle de l'entreprise. Ils sont composés du capital social, des réserves, du report à nouveau et du résultat de l'exercice.

## Cibles d'Analyse
- **Feuillets** : 2051 (Bilan Passif - Liasse Normale) ou 2033-A (Bilan simplifié).
- **Lignes** :
  - Feuillet 2051 : Section "CAPITAUX PROPRES", ligne QU (Total I).
  - Feuillet 2033-A : Ligne DL (Capitaux propres).

## Règles d'Extraction
1. **Valeurs négatives** : Les capitaux propres peuvent être négatifs (report à nouveau débiteur, forte perte).
2. **Formatage** : Montant numérique avec signe si besoin (ex: 35000.0 ou -12000.0).
3. **Exclusion** : Ne pas confondre avec le "Total du Passif".
