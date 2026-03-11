# Skill: Extraction du Chiffre d'Affaires (CA)

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
2. **Exclusions FORMELLES** : NE JAMAIS INCLURE les éléments suivants dans le calcul du CA :
   - Autres produits d'exploitation (à ne pas confondre avec le CA)
   - Production stockée
   - Production immobilisée
   - Subventions d'exploitation
   - Reprises sur amortissements et provisions
   - Total des produits d'exploitation (ligne FR ou FO) : ce total inclut d'autres produits et NE DOIT PAS être utilisé comme CA.
3. **Cas de CA nul (0)** : Si les lignes "Vente de marchandises" et "Production vendue" sont vides ou égales à zéro, le Chiffre d'Affaires est de 0.0. Ne cherchez pas à combler avec d'autres produits.
4. **Formatage** : Ne retourner que le montant numérique positif (ex: 1250000.0 ou 0.0).
