# Clinically Informed Genomic Drug Target Prediction
## Project aim
In this work, we develop a machine learning model that prioritizes drug targets on gene-level. This prioritization is done by considering features that are informative of the success of a drug in clinical trials and learning their appropiate feature weights by using target associated clinical trial approval/withdrawal data as training data. Ground truth clinical trial data will not exist for all genes but by training on a subset of targets, we can develop a model that performs the druggability predictions for all genes. Some external validation sources will be needed to assess the accuracy of this method *(What data to use for this purpose?)*. The model will have a two main modules. The first module is a gene characterization module. In this module, we collect features that characterize a gene as idiosyncratically as possible. This module will be used to assess the target quality, i.e. how likely will this target react positively to drugs without hindering normal function? We further distinguish the gene characterization module in two submodules:

1) Cell type-agnostic gene characterization 
2) Cell type-specific gene characterization. 

This is done for practical reasons as the two datasets associated with these submodules will not be homogeneous. In particular, the cell-type specific gene characterization will need additional identifiers to stratify different genes according to cell type. The second module is a pathogenicity module. This module is able to probe what we call the impact of a target, i.e. is this target likely to be causally implicated in disease? This second module will also be separated into two submodules: 

1) LoF and GoF variant (LoGoVa) pathogenicity inference 
2) Missense variant (MiVa) pathogenicity inference

The reason for the distinction between the two is that assessing pathogenicity of missense variants is not as straightforward as for LoF and GoF mutations. For LoF and GoF mutations there already exist great variant effect predictors (ClinVar, ANNOVAR, VEP) whereas there are few comprehensive variant effect predictors for missense mutations that can generalize well. Historically, missense variants have been mostly looked over in the drug discovery literature due to the difficulty in characterizing them. However, missense variants are important to incorporate into drug discovery pipelines as the vast majority of coding variants actually are missense variants (https://onlinelibrary.wiley.com/doi/10.1002/humu.24309). With recent advances in large language AI models, sequence-based pathogenicity prediction methods have shown to be able to characterize missense variants accurately as well as showing promise when it comes to generalizability [https://pubmed.ncbi.nlm.nih.gov/34707284/](https://pubmed.ncbi.nlm.nih.gov/34707284/) and [https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1](https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1). In the end, sequence-based missense pathogenicty prediction will help us to alleviate sparse and unreliable pathogenicity annotations in existing databases which in turn allows us to incorporate missense variant effects into our druggability assessments. To that end, we integrate a SOTA missense variant effect prediction model out of the Orengo Structural Biology lab at UCL into our druggability prediction model in order to include missense variant effects in prioritization. This missense variant pathogenicity prediction model is still in development so until it can be integrated, we use ESM-variants out of UCSF Ntrano's lab, which is a missense variant pathogenicity prediction model based on Meta AI's ESMFold. Altogether, the goal of this model is to prioritize the drug targets in the human coding genome that are both high quality, meaning they can be effectively drugged against (high druggability score), and also of high impact, meaning that the target is implicated in disease (high pathogenicity score). 

TO-DO: Draw architecture diagram with data sources and all modules

TO-DO: Elaborate on ESMVariants which will be used as a placeholder for the UCL collaboration pathogenicity prediction model

## Gene characterization module
### Cell type-agnostic gene characterization
The first module will contain cell type agnostic features that are correlated to druggability:
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| <em>Druggability </em>                                       | <em> Calculate a druggability score (are there ground truth labels for this?) (Binary) </em> | Use druggable genome? (read: [1](https://www.nature.com/articles/nrd892) and [2](https://www.frontiersin.org/articles/10.3389/fbinf.2022.958378/full)), use FDA approved targets as ground truth (Wei has access to this). --> rethink this (how to make sequence-based druggability target variable?)| 
| Target safety score, PPIs                                    | Number of PPIs as a measure for safety. (Continuous)| [STRING database](https://string-db.org/)      |
| Target safety score, knockout models                         | Is target crucial for organism/cell health? (Binary)| [Open Targets](https://platform.opentargets.org/target/ENSG00000141510)       |
| Target conservation                                          | Metric indicating to which extent the particular target is conserved from an evolutionary perspective (Continuous)                                                                                                                | [Constraint data on Open Targets](https://platform.opentargets.org/target/ENSG00000141510)      |

### Cell type-specific gene characterization
Cell type-specific module extends the cell type-agnostic module with features that are cell type-specific. This brings along with it extra overhead because it needs data that has been resolved on a cell type-specific resolution. 
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| Target efficacy, chromatin accessibility and gene expression | Probe target efficacy by calculating the expression and chromatin accessibility of the target (Binary)| [Enformer](https://www.nature.com/articles/s41592-021-01252-x) or [OpenTargets](https://platform.opentargets.org/target/ENSG00000198911), or experimental: DNAse, Meuleman DHS, GTEx|
| Stringency of gene regulatory sequences                      | Regulatory sequences play a big role in gene expression and so defects in stringent gene regulatory sequences can have pathogenic consequences. How to go about quantifying this (eQTLs)? (Continuous) | Check whether mutation is 1) in non-coding region, 2) significant (p-value in https://www.ebi.ac.uk/eqtl/Data_access/ ) | 

### Removed features
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| Target safety score                                          | Calculate safety score for the target. Black-box indications as a measure for safety|Doesn't seem openly available via https://go.drugbank.com/. Alternative ways to access this data? |

This data will be used to build an ML model to that predicts <em>druggability (target variable)</em>. This means ground truth labels for druggability are needed. We can start building and training this model on pre-existing datasets without taking pathogenicity into account. 

## Pathogenicity inference module  
### LoGoVa pathogenicity inference
For the LoGoVa module, we focus in particular on LoF and GoF variants and their pathogenicity. Do note that for this purpose we utilize the variant-level data out of our dataset, e.g. ELGH, and therefore we need to transform the variant-level predictions to the gene-level. The pathogenicity predictions for LoF and GoF variants can be obtained via ClinVar variant_summary.txt (https://ftp.ncbi.nlm.nih.gov/pub/clinvar/README.txt) or alternatively ANNOVAR could be used (https://annovar.openbioinformatics.org/en/latest/user-guide/download/). For a gene, we collect all variants

### MiVa pathogenicity inference 
When it comes to missense variants, inferring pathogenicity is a lot more difficult due to the often seemingly subtle nature of these type of variants. Regardless of their ambiguous pathogenicity, missense variants actually make up the largest fraction of occuring coding variants. Hence, incorporating them into our prediction model is important, provided we can effectively predict the variant effect of these missense mutations. In particular, predicting pathogenicity for missense variants is important to identify high impact targets, i.e. genes that are involved in severe disease phenotypes. With recent advances in large language and generative AI models, now seems like an ideal time to incorporate sequence-based missense pathogenicity predictions into the drug discovery pipeline. In the end, sequence-based missense pathogenicty prediction can alleviate sparse and unreliable pathogenicity annotations in existing databases as these models are already showing tremendous ability to generalize, e.g. [https://pubmed.ncbi.nlm.nih.gov/34707284/](https://pubmed.ncbi.nlm.nih.gov/34707284/) and [https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1](https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1). When successful, sequence-based pathogenicity will be an important measure in guiding drug target discovery because we want to maximize both the target quality, i.e. can the proposed target be succesfully targeted, and target impact, i.e. is this target associated with a diseased phenotype. As a prototype, https://huggingface.co/spaces/ntranoslab/esm_variants can be used to query over 400M missense variants on their expected pathogenicity.

<b>{To be worked out in more detail in collaboration with W. Lin out of the [Orengo lab](https://www.ucl.ac.uk/orengo-group/welcome-christine-orengos-group) at UCL.}</b>

## Feature Engineering
[Feature engineering overview](feature_engineering.pdf)

## Potential Data Sources

- Genomic data
  - East London Genes and Health (ELGH) contains around 50,000 whole exomes of primarily Bangladeshi and Pakistani populations. Also contains electronic health records. https://www.genesandhealth.org/research/scientific-data-downloads
  - UK BioBank (UKBB) is a database that tracks the health of 500,000 participants, including genetic screens. Note that UKBB is not representative of general population. Skew towards population of Caucasian descent between the ages of 40-69.  https://www.ukbiobank.ac.uk/
  - Born in Bradford is a consortium tracking the health of about 13,000 participants from Bradford. Data includes EHR and genomes. https://borninbradford.github.io/datadict/bib/bib_biobank/current_samples/
  - deCODE is a research company that performed whole-genome sequencing experiments for about 2,500 individuals. Couldn't find open access to this dataset online. https://www.decode.com/
  - PROMIS (Patient-Reported Outcomes Measurement Information System) is a set of person-centred measures that evaluates and monitors physical, mental, and social health in adults and children. It can be used with the general population and with individuals living with chronic conditions. Also performed genotyping but could not immediately find this data. https://www.healthmeasures.net/explore-measurement-systems/promis 
  - ClinVar is a freely accessible, public archive of reports on the relationships among human variations and phenotypes, with supporting evidence. ClinVar thus facilitates access to and communication about the relationships asserted between human variation and observed health status, and the history of that interpretation. This resource can be used to assess e.g. haploinsufficiency. https://www.ncbi.nlm.nih.gov/clinvar/
  - OMIM is a comprehensive, authoritative compendium of human genes and genetic phenotypes that is freely available and updated daily. The full-text, referenced overviews in OMIM contain information on all known mendelian disorders and over 16,000 genes. OMIM focuses on the relationship between phenotype and genotype. https://www.omim.org/
  - The Genome Aggregation Database (gnomAD), originally launched in 2014 as the Exome Aggregation Consortium (ExAC), is a coalition of investigators seeking to aggregate and harmonize exome and genome sequencing data from a variety of large-scale sequencing projects, and to make summary data available for the wider scientific community. https://gnomad.broadinstitute.org/
  - ANNOVAR is an efficient software tool to utilize update-to-date information to functionally annotate genetic variants detected from diverse genomes (including human genome hg18, hg19, hg38, as well as mouse, worm, fly, yeast and many others). https://annovar.openbioinformatics.org/en/latest/ 

- Clinical trial status data for drug targets 
  - DrugBank aggregates clinical trial status data for particular targets in a structured fashion, e.g. https://go.drugbank.com/drugs/DB00001. Not immediately clear whether this data is also queryable in this structured way via API. 
  - ClinicalTrials.gov has an API that is queryable. However, organisation seems unstructured compared to DrugBank. https://clinicaltrials.gov/api/gui
  - DGIdb has a druggability assessment tool and drug-gene interaction search engine. The database is queryable through API. https://www.dgidb.org/api
  - Open Targets Genetics is a comprehensive tool highlighting variant-centric statistical evidence to allow both prioritisations of candidate causal variants at trait-associated loci and identification of potential drug targets. Accessible via GraphQL API. https://genetics-docs.opentargets.org/data-access/graphql-api
