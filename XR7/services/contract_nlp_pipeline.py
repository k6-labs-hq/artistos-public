from dataclasses import dataclass


@dataclass
class ContractExtraction:
    text: str
    warnings: list
    terms: list


class ContractNLPPipeline:
    def parse_uploaded_contract(self, filename, content, effective_start=None, effective_end=None):
        return ContractExtraction(text="Stub contract text", warnings=[], terms=[])
