---
name: chiffre-affaires
description: Use this skill to extract the Chiffre d'Affaires (CA) from French tax documents (Liasses Fiscales, Comptes de résultat). CA = ventes marchandises + production vendue (biens et services) ONLY. Never include "autres produits". If those lines are empty, CA is 0.
---

# Extraction du Chiffre d'Affaires (CA)

## Contexte
Le Chiffre d'Affaires représente exclusivement les ventes de marchandises et la production vendue de biens et services liés à l'activité normale de l'entreprise.

## Cibles d'Analyse (où chercher)
- **Feuillets principaux** :
  - Liasse Normale : Feuillet 2052 (Compte de résultat de l'exercice)
  - Liasse Simplifiée : Feuillet 2033-B (Compte de résultat simplifié)
  - Comptes annuels / Plaquettes : Tableau "Compte de résultat"
- **Lignes spécifiques** :
  - Sur le feuillet 2052 : Rechercher la ligne FL (Chiffre d'affaires net total).
  - Sur le feuillet 2033-B : Rechercher la ligne FG (Chiffre d'affaires net).
  - Le libellé exact contient souvent "Chiffre d'affaires net", "Montant net du chiffre d'affaires".

## Règles d'Extraction STRICTES
1. **Périmètre EXACT** : Le CA est UNIQUEMENT la somme de :
   - Ventes de marchandises
   - Production vendue (biens)
   - Production vendue (services)
2. **Exclusions FORMELLES** : NE JAMAIS INCLURE :
   - Autres produits d'exploitation
   - Production stockée, immobilisée
   - Subventions, reprises
   - Total des produits d'exploitation (ligne FR/FO)
3. **Cas de CA nul (0)** : Si "Vente de marchandises" et "Production vendue" sont vides ou zéro, le CA est 0.0.
4. **Formatage** : Montant numérique positif (ex: 1250000.0 ou 0.0).
