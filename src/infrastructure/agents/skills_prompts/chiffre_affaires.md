# Skill: Extraction du Chiffre d'Affaires (CA)

## Contexte
Le Chiffre d'Affaires représente les ventes de marchandises et la production vendue de biens et services. Il est un indicateur clé de l'activité de l'entreprise.

## Cibles d'Analyse
- **Feuillets principaux** : 2052 (Compte de résultat de l'exercice - Liasse Normale) ou 2033-B (Compte de résultat simplifié - Liasse Simplifiée).
- **Lignes spécifiques** :
  - Sur le feuillet 2052 : Rechercher la ligne FL (Chiffre d'affaires net total).
  - Sur le feuillet 2033-B : Rechercher la ligne FG (Chiffre d'affaires net).
  - Le libellé exact contient souvent "Chiffre d'affaires net".

## Règles d'Extraction
1. **Périmètre** : Additionner les ventes de marchandises et la production vendue (biens et services) si le total n'est pas explicitement indiqué à la ligne FL/FG.
2. **Formatage** : Ne retourner que le montant numérique positif (ex: 1250000.0).
3. **Erreurs communes** : Ne pas confondre avec le "Total des produits d'exploitation" (ligne FR ou FO) qui inclut d'autres produits.
