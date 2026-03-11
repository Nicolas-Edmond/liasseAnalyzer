# Skill: Extraction des Capitaux Propres

## Contexte
Les Capitaux Propres reflètent la santé financière structurelle de l'entreprise. Ils sont composés du capital social, des réserves, du report à nouveau et du résultat de l'exercice.

## Cibles d'Analyse
- **Feuillets principaux** : 2051 (Bilan Passif - Liasse Normale) ou 2033-A (Bilan simplifié - Liasse Simplifiée).
- **Lignes spécifiques** :
  - Sur le feuillet 2051 : Rechercher la section "CAPITAUX PROPRES" et la ligne QU (Total I).
  - Sur le feuillet 2033-A : Rechercher la ligne DL (Capitaux propres).

## Règles d'Extraction
1. **Valeurs négatives** : Attention, les capitaux propres peuvent être négatifs s'il y a un report à nouveau débiteur important ou une très forte perte.
2. **Formatage** : Ne retourner que le montant numérique, avec le signe moins si nécessaire (ex: 35000.0 ou -12000.0).
3. **Erreurs communes** : Ne pas confondre avec le "Total du Passif" qui inclut aussi les dettes.
