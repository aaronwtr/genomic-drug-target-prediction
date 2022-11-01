import pandas as pd
import requests
from tqdm import tqdm
import os
from Bio import SeqIO


class DataPreprocessing:
    def __init__(self, uniparc_path, msa_output):
        """
        :param uniparc_path: path to the UNIPARC dataset.
        :param msa_output: path to where the MSA .fasta file will be saved.
        """
        self.uniparc_path = uniparc_path
        self.msa_output = msa_output
        self.msa_file_name = msa_output.split(os.path.sep)[-1]
        self.uniparc_col_name = "UNIPARC"
        self.gene_col_name = "SYMBOL"
        self._init_verification()

    def _init_verification(self):
        """
        Check whether the path points to a valid .csv file. Also check whether the msa_out put ends in ".fasta".
        """
        if not self.uniparc_path.endswith(".csv"):
            raise TypeError("The path to the UNIPARC dataset must point to a .csv file.")
        if not self.msa_output.endswith(".fasta"):
            raise TypeError("The output file must be of type .fasta.")

    def data_reader(self):
        """
        Read in the raw .csv data and check whether the data contains the required columns.
        :return: raw_data as a pandas dataframe.
        """
        _raw_data = pd.read_csv(self.uniparc_path, sep="\t")
        if self.uniparc_col_name not in _raw_data.columns:
            raise TypeError(f"Change the column name of the column containing the uniparc ids to "
                            f"'{self.uniparc_col_name}'.")
        if self.gene_col_name not in _raw_data.columns:
            raise TypeError(f"Change the column name of the column containing the gene names to "
                            f"'{self.gene_col_name}'.")
        return _raw_data

    def parse_data(self, data):
        """
        Get UNIPARC ids and gene symbols from the dataset and put them in a dictionary.
        """
        uniprot_ids = data[self.uniparc_col_name].tolist()
        gene_names = data[self.gene_col_name].tolist()
        uniprot_ids_dict = {}
        for i in range(len(uniprot_ids)):
            if gene_names[i] not in uniprot_ids_dict:
                uniprot_ids_dict[gene_names[i]] = [uniprot_ids[i]]
            else:
                uniprot_ids_dict[gene_names[i]].append(uniprot_ids[i])
        return self._get_msa(uniprot_ids_dict)

    def _get_msa(self, uniprot_ids_dict):
        """
        Get the multiple sequence alignment from the UNIPROT database.
        :param uniprot_ids_dict: dictionary of UNIPROT IDs and gene names.
        :return: processed MSA data.
        """
        cont_idx, num_variants = self._file_tracker(uniprot_ids_dict)
        if cont_idx == 0:
            with open(self.msa_output, "w") as f:
                f.write("")
            f.close()
        elif cont_idx == num_variants:
            print("Data preprocessing completed!")
            return list(SeqIO.parse(self.msa_output, "fasta"))
        else:
            # TODO: THIS IS GOING WRONG
            print("Data preprocessing was previously started but is incomplete. Continuing from where it left off.")
            all_variants = list(uniprot_ids_dict.values())
            incomplete_variants = all_variants[cont_idx:]
            incomplete_variants_dict = {}
            print("Creating dictionary of the variants that still need parsing...")
            for gene, variants in tqdm(uniprot_ids_dict.items()):
                for variant in variants:
                    for incomplete_variant in incomplete_variants:
                        if variant in incomplete_variant:
                            if gene not in incomplete_variants_dict:
                                incomplete_variants_dict[gene] = [variant]
                            else:
                                incomplete_variants_dict[gene].append(variant)
                print(incomplete_variants_dict)
            uniprot_ids_dict = incomplete_variants_dict

        print("Parsing the data...")
        with open(self.msa_output, "a") as f:
            for gene_name in tqdm(uniprot_ids_dict):
                for uniprot_id in uniprot_ids_dict[gene_name]:
                    url = f"https://www.uniprot.org/uniparc/{uniprot_id}.fasta"
                    response = requests.get(url)
                    fasta_msa = response.text
                    fasta_msa = fasta_msa.replace("status=active", "")
                    fasta_msa = fasta_msa.replace("status=inactive", "")
                    fasta_msa = f"{fasta_msa[0:14]}|{gene_name}{fasta_msa[14:]}"
                    f.write(fasta_msa)
        f.close()
        print("Data preprocessing completed!")
        return list(SeqIO.parse(self.msa_output, "fasta"))

    def _file_tracker(self, uniprot_ids_dict):
        """
        Track whether there already exists output and if it is complete or not.
        """
        num_variants = 0
        if self.msa_file_name in os.listdir():
            with open(self.msa_file_name, "r") as f:
                count = f.read().count(">")
            f.close()
            for gene_name in uniprot_ids_dict:
                num_variants += len(uniprot_ids_dict[gene_name])
            if count != num_variants:
                cont_idx = count - 1
            else:
                cont_idx = num_variants
        else:
            cont_idx = 0
        return cont_idx, num_variants


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = ROOT_DIR.replace("\\", "/")
    UNIPARC_PATH = f"{ROOT_DIR}/all_chrs.HC_LoF.genotype_counts.after_genotype_filtering.csv"
    UNIPARC_PATH = os.path.normpath(UNIPARC_PATH)
    MSA_OUTPUT = f"{ROOT_DIR}/elgh_HC_LoF_MSA.fasta"
    MSA_OUTPUT = os.path.normpath(MSA_OUTPUT)

    DPP = DataPreprocessing(UNIPARC_PATH, MSA_OUTPUT)
    raw_data = DPP.data_reader()
    msa_data = DPP.parse_data(raw_data)
