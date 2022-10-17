# Genetic Drug Targetting and Mutant Allele Classification
### Project aim
In order to prioritize drug targets, particular mutant alleles, which could be loss-of-function (LoF) or gain-of-function (GoF) mutations, should be classified on whether they are either benign or malignant. Furthermore, for the malignant mutant alleles, we can perform further prioritization by looking at clinical trial outcome data for compounds targeting that allele. 
### Data
- DrugBank: Clinical trial data targeting diseased pathways/targets 

- ELGH: Around 50,000 whole exomes of primarily Bangladeshi and Pakistani population. Also contains electronic health records.

- UK BioBank: Database tracking health of 500,000 participants. Note that UKBB is not representative of general population. Skew towards population of caucasian descent between the ages of 40-69. 
### Methods 
- Mutant allele classification: For the LoF and GoF classification, we will build a simple logistic regression model taking inspiration from previous work at the Centre for Translational Bioinformatics. Logistic regression is a nice first step as this architecture allows for binary classification via a threshold, e.g. risk > 50% = malignant mutation, else benign. Moreover, the raw risk probability can be used to prioritize the targets amongst each other, where the targets with the biggest malignant risk would be the most obvious targets. 

- Clinical trial outcome prioritization: ...
