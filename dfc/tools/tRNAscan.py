#! /usr/bin/env python
# coding: UTF8

from .base_tools import StructuralAnnotationTool
from ..models.bio_feature import ExtendedFeature


class tRNAscan(StructuralAnnotationTool):
    """
    tRNAscan class extended from StructuralAnnotationTool class

    Tool type: tRNA
    URL: 
    REF: 

    """
    version = None
    TYPE = "tRNA"
    NAME = "tRNAscan-SE"
    VERSION_CHECK_CMD = ["tRNAscan-SE", "-h", "2>&1"]
    VERSION_PATTERN = r"tRNAscan-SE (.+) \("
    SHELL = True
    def __init__(self, options=None, workDir="OUT"):
        """
        aragorn options:
          -B  --bact            : search for bacterial tRNAs (use bacterial tRNA model)
          -A  --arch            : search for archaeal tRNAs (use archaeal tRNA model)
          -O  --organ           : search for organellar (mitochondrial/chloroplast) tRNAs
          -G  --general         : use general tRNA model (cytoplasmic tRNAs from all 3 domains included)

          -D  --nopseudo        : disable pseudogene checking
          -o  --output <file>   : save final results in <file>
          -b  --brief           : brief output format (no column headers)
          -Q   --forceow  : do not prompt user before overwriting pre-existing result files  (for batch processing)
        :param options:
        :param workDir:
        """
        super(tRNAscan, self).__init__(options, workDir)
        self.model = options.get("model", "--bact")
        self.cmd_options = options.get("cmd_options", "")

    def getCommand(self):
        """
        tRNAscan-SE --bact --nopseudo -b -o tRNAscanSE.tsv genome.fna 2> tRNAscanSE.log
        """
        # TODO: check pseudogene output
        cmd = ["tRNAscan-SE", self.model, self.cmd_options, "--brief --forceow", "--output", self.outputFile,
               self.genomeFasta, "2>", self.logFile]
        return cmd

    def getFeatures(self):

        def _parseResult():
            with open(self.outputFile) as f:
                for line in f:
                    sequence, _, start, end, aa, anticodon, _, _, score = line.strip("\n").split("\t")
                    if int(start) <= int(end):
                        left, right, strand = start, end, "+"
                    else:
                        left, right, strand = end, start, "-"
                    sequence = sequence.strip()  # Remove trailing blank
                    yield sequence, left, right, strand, aa, anticodon, score

        D = {}
        i = 0
        for sequence, left, right, strand, aa, anticodon, score in _parseResult():

            location = self.getLocation(left, right, strand)
            i += 1

            type_ = "tRNA"
            annotations = {"anticodon": anticodon}
            feature = ExtendedFeature(location=location, type=type_, id="{0}_{1}".format(self.__class__.__name__, i),
                                      seq_id=sequence, annotations=annotations)
            feature.qualifiers = {
                "product": ["tRNA-{0}".format(aa)],
                "inference": ["COORDINATES:ab initio prediction:{0}:{1}".format(self.__class__.NAME, self.__class__.version)],
            }
            D.setdefault(sequence, []).append(feature)
        return D


if __name__ == '__main__':
    pass
