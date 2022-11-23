# Genomic Drug Target Prediction
### Project aim
This project is separated into two related research directions: 

1) LoF and GoF variant drug target prediction (LoGoVa) 
2) Missense variant drug target prediction (MiVa)

These two are not orthogonal but rather set up in parallel. Most of the methods and ideas for the LoGoVa project should be transferrable to the MiVa project. The reason for the distinction between the two is that assessing pathogenicity of missense variants is not as straightforward as for LoF and GoF mutations. Still, missense variants are important to incorporate into the drug targeting prediction model as the vast majority of coding variants are actually missense variants (https://onlinelibrary.wiley.com/doi/10.1002/humu.24309). To that end, we aim to develop a SOTA missense variant effect prediction model in collaboration with W. Lin out of the Orengo lab at UCL. In the end, these two projects should be reconciled into one drug target prediction model that incorporates variant pathogenicity for both LoGoVas and MiVas.

## LoGoVa drug target prediction
For the LoGoVa project, we focus in particular on LoF and GoF variants that are very likely to be pathogenic, e.g. by virtue of early truncations or likely misfolding leading to functional change. The idea is to build a database for each variant of interest including, but not limited to: 

### Cell-type agnostic model
The first base model will contain 2 features that should be highly predictive of druggability. Ideally we'd want to incorporate genetic sequence in here as well as this would allow for the most generalizability. Maybe via AlphaFold? 
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| <em>Druggability </em>                                       | <em> Calculate a druggability score (are there ground truth labels for this?) (Binary) </em> | Use druggable genome? (read: [1](https://www.nature.com/articles/nrd892) and [2](https://www.frontiersin.org/articles/10.3389/fbinf.2022.958378/full)), use FDA approved targets as ground truth (Wei has access to this). --> rethink this (how to make sequence-based druggability target variable?)| 
| Target safety score, PPIs                                    | Number of PPIs as a measure for safety. (Continuous)| [STRING database](https://string-db.org/)      |
| Target safety score, knockout models                         | Is target crucial for organism/cell health? (Binary)| [Open Targets](https://platform.opentargets.org/target/ENSG00000141510)       |
| Target conservation                                          | Metric indicating to which extent the particular target is conserved from an evolutionary perspective (Continuous)                                                                                                                | [Constraint data on Open Targets](https://platform.opentargets.org/target/ENSG00000141510)      |

### Cell-type specific model
Cell-type specific model extends the above base model with features that are cell type specific. This brings along with it extra overhead because it needs data that has been resolved on a cell-type specific resolution. 
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| Target efficacy, chromatin accessibility and gene expression | Probe target efficacy by calculating the expression and chromatin accessibility of the target (Binary)| [Enformer](https://www.nature.com/articles/s41592-021-01252-x) or [OpenTargets](https://platform.opentargets.org/target/ENSG00000198911)|
| Stringency of gene regulatory sequences                      | Regulatory sequences play a big role in gene expression and so defects in stringent gene regulatory sequences can have pathogenic consequences. How to go about quantifying this (eQTLs)? (Continuous) | Check whether mutation is 1) in non-coding region, 2) significant (p-value in https://www.ebi.ac.uk/eqtl/Data_access/ ) | 

### Removed features
| Data type                                                    |Description                                                                  |Source |
|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------|
| Target safety score                                          | Calculate safety score for the target. Black-box indications as a measure for safety|Doesn't seem openly available via https://go.drugbank.com/. Alternative ways to access this data? |

This data will be used to build an ML model to that predicts <em>druggability (target variable)</em>. This means ground truth labels for druggability are needed. We can start building and training this model on pre-existing datasets without taking pathogenicity into account. The goal is to find targets that are both high quality, meaning they can be effectively drugged against (high druggability score), and also of high impact, meaning that the target is causally implicated in disease (high pathogenicity score). To assess pathogenicity of LoGoVas existing methods such as ClinVar or ANNOVAR can be used. The outlined dataset can be built from the sources in [Data](#data). 

## MiVa drug target prediction
When it comes to missense variants, predicting pathogenicity is a lot more difficult due to the often seemingly subtle nature of these type of variants. Regardless of their ambiguous pathogenicity, missense variants actually make up the largest fraction of occuring coding variants. Hence, incorporating them into our prediction model is important, provided we can effectively predict the variant effect of these missense mutations. In particular, predicting pathogenicity for missense variants is important to identify high impact targets, i.e. genes that are causally involved in severe disease phenotypes. With recent advances in large language and generative AI models, now seems like an ideal time to incorporate sequence-based missense pathogenicity predictions into the drug discovery pipeline. In the end, sequence-based missense pathogenicty prediction can alleviate sparse and unreliable pathogenicity annotations in existing databases as these models are already showing tremendous ability to generalize, e.g. [https://pubmed.ncbi.nlm.nih.gov/34707284/](https://pubmed.ncbi.nlm.nih.gov/34707284/) and [https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1](https://www.biorxiv.org/content/10.1101/2022.08.25.505311v1). When successful, sequence-based pathogenicity will be an important measure in guiding drug target discovery because we want to maximize both the target quality, i.e. can the proposed target be succesfully targeted, and target impact, i.e. is this target associated with a diseased phenotype. As a prototype, https://huggingface.co/spaces/ntranoslab/esm_variants can be used to query over 400M missense variants on their expected pathogenicity.

<b>{To be worked out in more detail in collaboration with W. Lin out of the [Orengo lab](https://www.ucl.ac.uk/orengo-group/welcome-christine-orengos-group) at UCL.}</b>

### Data

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
