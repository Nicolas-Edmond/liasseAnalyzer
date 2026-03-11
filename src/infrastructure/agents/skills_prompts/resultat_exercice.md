# Skill: Extraction du Résultat de l'Exercice

## Contexte
Le Résultat net est la différence entre tous les produits et toutes les charges de l'exercice. Il peut s'agir d'un bénéfice ou d'une perte.

## Cibles d'Analyse
- **Feuillets principaux** : 2051 (Bilan Passif), 2053 (Compte de résultat), ou 2033-A / 2033-B pour la liasse simplifiée.
- **Lignes spécifiques** :
  - Sur le feuillet 2051 (Passif) : Ligne DI (Bénéfice) ou DJ (Perte).
  - Sur le feuillet 2053 (Compte de résultat) : Ligne HN (Bénéfice ou perte).
  - Sur le feuillet 2033-A (Passif simplifié) : Ligne DK (Résultat de l'exercice).
  - Sur le feuillet 2033-B (Compte de résultat simplifié) : Ligne GG (Bénéfice) ou GH (Perte).

## Règles d'Extraction
1. **Gestion du signe** : 
   - Si c'est un bénéfice, la valeur est positive.
   - Si c'est une perte (ex: ligne DJ, GH, ou montant indiqué entre parenthèses / avec un signe moins), la valeur DOIT être négative.
2. **Formatage** : Ne retourner que le montant numérique, avec le signe (ex: 4500.0 ou -8500.0).
3. **Cohérence** : Le résultat lu au passif du bilan doit être identique à celui lu au compte de résultat.
